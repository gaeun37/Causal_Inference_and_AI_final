#!/usr/bin/env python3
"""Steps 3-6 + figures. Deterministic, offline, no LLM, no randomness.

Reads curated tables -> builds Knowledge Graph (graph/), Causal DAG (graph/),
the cleaning log (data/cleaned/cleaning_log.csv), summaries + the demo backdoor
adjustment (outputs/), and renders four SVG figures (figures/).
"""
from pathlib import Path
import csv, math
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[1]
CUR, GRAPH, OUT, FIG, CLEAN = (ROOT/"data"/"curated", ROOT/"graph", ROOT/"outputs",
                               ROOT/"figures", ROOT/"data"/"cleaned")
for d in (GRAPH, OUT, FIG): d.mkdir(exist_ok=True)

def rd(p):
    with open(p, newline="", encoding="utf-8") as f: return list(csv.DictReader(f))
def wr(p, rows, fn=None):
    if not rows: return
    fn = fn or list(rows[0].keys())
    with open(p,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fn); w.writeheader(); w.writerows(rows)

# ---------------- Step 3 outputs: cleaning log + summaries ----------------
def summaries():
    ex = rd(CUR/"real_extractions.csv")
    # cleaning log from verified raw->corrected pairs (auditable corrections)
    clog=[{"extraction_id":e["extraction_id"],"raw_ocr_quote":e["raw_ocr_quote"],
           "corrected_quote":e["corrected_quote"],"change_type":"OCR correction / normalization",
           "verification_status":e["verification_status"]}
          for e in ex if e["raw_ocr_quote"].strip()]
    CLEAN.mkdir(parents=True, exist_ok=True)
    wr(CLEAN/"cleaning_log.csv", clog)
    # extraction summary by role
    by_role=Counter(e["role_in_dag"] for e in ex)
    wr(OUT/"extraction_summary.csv",
       [{"role_in_dag":k,"count":by_role[k]} for k in sorted(by_role)])
    # claim-type table (Step 9: separate asserted vs analyst-added vs text-supported)
    by_ct=Counter(e["claim_type"] for e in ex)
    wr(OUT/"claim_type_summary.csv",
       [{"claim_type":k,"count":by_ct[k],
         "meaning":{"text-supported":"framing role with a direct supporting quote",
                    "asserted-causation":"a cause-effect claim made by the newspaper/actors",
                    "analyst-added":"structure added by the analyst (e.g. confounder Z)"}.get(k,"")}
        for k in sorted(by_ct)])
    return ex

# ---------------- Step 4: Knowledge Graph ----------------
def build_kg(ex):
    arts = rd(CUR/"articles.csv"); seen=set(); nodes=[]; edges=[]
    def n(i,l,t,**p):
        if i in seen: return
        r={"id":i,"label":l,"type":t}; r.update(p); nodes.append(r); seen.add(i)
    def e(s,d,r,**p):
        row={"source":s,"target":d,"relationship":r}; row.update(p); edges.append(row)
    for a in arts:
        n(a["issue_id"], f"{a['newspaper']} {a['date']}", "Issue",
          date=a["date"], context=a["context_Z"])
        n(a["article_id"], a["title"][:60], "Article", page=a["page"],
          newspaper=a["newspaper"], date=a["date"])
        e(a["issue_id"], a["article_id"], "CONTAINS")
        e(a["article_id"], a["issue_id"], "DERIVED_FROM")
    for x in ex:
        ext=x["extraction_id"]; q=f"quote_{ext}"; c=f"claim_{ext}"
        n(ext, x["label"], "Extraction", role=x["role_in_dag"], verification=x["verification_status"])
        if x["raw_ocr_quote"].strip():
            n(q, x["corrected_quote"][:70], "SupportingQuote", verified=("verified" in x["verification_status"]))
            e(ext, q, "SUPPORTED_BY")
        ctype={"text-supported":"FramingClaim","asserted-causation":"AssertedCausalClaim",
               "analyst-added":"AnalystAssumption"}.get(x["claim_type"],"Claim")
        n(c, x["label"], ctype, role=x["role_in_dag"])
        e(c, ext, "REPRESENTED_AS")
        if x["raw_ocr_quote"].strip(): e(c, q, "EVIDENCE")
        if x["article_id"] not in ("analyst001",):
            e(x["article_id"], ext, "HAS_EXTRACTION")
    wr(GRAPH/"nodes.csv", nodes,
       fn=["id","label","type","date","context","page","newspaper","role","verification","verified"])
    wr(GRAPH/"edges.csv", edges)
    # kg_summary
    kg=[{"metric":"nodes","value":len(nodes)},{"metric":"edges","value":len(edges)},
        {"metric":"verified_quotes","value":sum(1 for n_ in nodes if n_.get("verified")=="True" or n_.get("verified") is True)},
        {"metric":"issues","value":sum(1 for n_ in nodes if n_["type"]=="Issue")},
        {"metric":"articles","value":sum(1 for n_ in nodes if n_["type"]=="Article")},
        {"metric":"asserted_causal_claims","value":sum(1 for n_ in nodes if n_["type"]=="AssertedCausalClaim")}]
    wr(OUT/"kg_summary.csv", kg)

# ---------------- Step 5: DAG ----------------
def build_dag():
    nodes=[
     ["Z","Contextual confounders","confounder","newspaper orientation/locale, prior labor context, industrial interest, actual disorder"],
     ["X","Protest pressure framing","treatment","strike framed as strong social pressure"],
     ["M1","Demand-legitimacy framing","mediator","wage/hours/child-labor grievance framed as legitimate"],
     ["Y1","Development-oriented improvement response","outcome","investigation, hearings, negotiation, wage settlement"],
     ["M2","Disorder/conflict framing","mediator","riot, mob, shots, arrests, public danger"],
     ["Y2","Order-control response","outcome","militia, police, arrests, suppression, order restoration"],
    ]
    wr(GRAPH/"dag_nodes.csv", [dict(zip(["id","label","type","description"],r)) for r in nodes])
    edges=[
     ["Z","X","confounding","analyst-added"],["Z","M1","confounding","analyst-added"],
     ["Z","Y1","confounding","analyst-added"],["Z","M2","confounding","analyst-added"],
     ["Z","Y2","confounding","analyst-added"],
     ["X","M1","causal_path","text-supported interpretation across issue sequence"],
     ["M1","Y1","causal_path","text-supported interpretation across issue sequence"],
     ["X","M2","causal_path","text-supported interpretation across issue sequence"],
     ["M2","Y2","causal_path","text-supported interpretation across issue sequence"],
    ]
    wr(GRAPH/"dag_edges.csv", [dict(zip(["source","target","edge_type","support"],r)) for r in edges])

# ---------------- Step 6: backdoor adjustment (honest) ----------------
def inference():
    rows=rd(CUR/"demo_effect_data.csv")
    for r in rows:
        for k in ("X_protest_pressure","Y1_improvement_response","Y2_order_control_response"):
            r[k]=int(r[k])
    def rate(o,x=None,z=None):
        f=[r for r in rows if (x is None or r["X_protest_pressure"]==x) and (z is None or r["Z_context"]==z)]
        return sum(r[o] for r in f)/len(f) if f else math.nan
    zs=sorted(set(r["Z_context"] for r in rows))
    pz={z:sum(1 for r in rows if r["Z_context"]==z)/len(rows) for z in zs}
    res=[]
    for o in ("Y1_improvement_response","Y2_order_control_response"):
        naive=rate(o,1)-rate(o,0)
        do1=sum(rate(o,1,z)*pz[z] for z in zs); do0=sum(rate(o,0,z)*pz[z] for z in zs)
        res.append({"outcome":o,"P_Y_given_X1":round(rate(o,1),3),"P_Y_given_X0":round(rate(o,0),3),
                    "naive_difference":round(naive,3),"P_Y_do_X1":round(do1,3),"P_Y_do_X0":round(do0,3),
                    "ATE_demo_adjusted":round(do1-do0,3),"interpretation":"demo only; not a historical effect"})
        for z in zs:
            res.append({"outcome":o+" by "+z,"P_Y_given_X1":round(rate(o,1,z),3),"P_Y_given_X0":round(rate(o,0,z),3),
                        "naive_difference":round(rate(o,1,z)-rate(o,0,z),3),"P_Y_do_X1":"","P_Y_do_X0":"",
                        "ATE_demo_adjusted":"","interpretation":"within-stratum (conditional) difference"})
    wr(OUT/"demo_backdoor_adjustment_results.csv", res)
    diag=[
     {"query":"Effect of X on Y1 (historical)","estimand_possible":"No",
      "reason":"Real corpus has X=1 in essentially every article: no X=0 comparison group; unobserved confounding; asserted not experimental.",
      "interpretation":"Not identifiable from this corpus"},
     {"query":"Effect of X on Y1 (demo)","estimand_possible":"Demo only",
      "reason":"Synthetic X=0 units added; Z adjusted by the backdoor formula.",
      "interpretation":"naive +0.022 -> adjusted +0.101 (modest, context-conditional, NOT historical)"},
     {"query":"Effect of X on Y2 (demo)","estimand_possible":"Demo only",
      "reason":"Synthetic X=0 units added; Z adjusted by the backdoor formula.",
      "interpretation":"naive +0.195 -> adjusted +0.121 (raw overstates link; NOT historical)"},
     {"query":"Mediated effect via M1 / M2","estimand_possible":"No",
      "reason":"M1/M2 are mediators on the X->Y paths; conditioning would block the total effect.",
      "interpretation":"diagnostic only (not adjusted for)"},
     {"query":"Historical effect of strike on social progress","estimand_possible":"No",
      "reason":"Small textual corpus, no true counterfactual.","interpretation":"not claimed"},
    ]
    wr(OUT/"identification_diagnostic_table.csv", diag)
    return res

# ============================ FIGURES ============================
FONT="'Segoe UI','Helvetica Neue',Arial,sans-serif"
PAL={"X":("#364fc7","#dbe4ff"),"M1":("#0b7285","#c5f6fa"),"Y1":("#2b8a3e","#d3f9d8"),
     "M2":("#d9480f","#ffe8cc"),"Y2":("#c92a2a","#ffe3e3"),"Z":("#5f3dc4","#e5dbff")}
def hdr(w,h,t,s=""):
    o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">',
       '<defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L0,8 L10,4 z" fill="#495057"/></marker>'
       '<marker id="arrowd" markerWidth="12" markerHeight="12" refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L0,8 L10,4 z" fill="#868e96"/></marker>'
       '<filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.14"/></filter></defs>',
       f'<rect width="{w}" height="{h}" fill="#fbfcfe"/>',
       f'<text x="{w/2}" y="40" text-anchor="middle" font-size="23" font-weight="700" fill="#212529">{t}</text>']
    if s: o.append(f'<text x="{w/2}" y="64" text-anchor="middle" font-size="13.5" fill="#868e96">{s}</text>')
    return o
def node(cx,cy,w,h,k,t,sub):
    st,fl=PAL[k]; x,y=cx-w/2,cy-h/2
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fl}" stroke="{st}" stroke-width="2.5" filter="url(#sh)"/>'
            f'<text x="{cx}" y="{cy-4}" text-anchor="middle" font-size="16" font-weight="700" fill="{st}">{t}</text>'
            f'<text x="{cx}" y="{cy+15}" text-anchor="middle" font-size="11.5" fill="#495057">{sub}</text>')
def edge(x1,y1,x2,y2,dash=False,curve=0):
    col="#868e96" if dash else "#495057"; d=' stroke-dasharray="7 5"' if dash else ""
    mk="url(#arrowd)" if dash else "url(#arrow)"
    if curve:
        mx,my=(x1+x2)/2+curve,(y1+y2)/2-abs(curve)*0.5
        return f'<path d="M{x1},{y1} Q{mx},{my} {x2},{y2}" fill="none" stroke="{col}" stroke-width="2.2"{d} marker-end="{mk}"/>'
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="2.2"{d} marker-end="{mk}"/>'

def fig_pipeline():
    W,H=1040,250; s=hdr(W,H,"Figure 1 - Data Pipeline","raw evidence is preserved separately from analytic structure")
    steps=[("Newspaper\nOCR (ALTO)","#1864ab","#d0ebff"),("OCR\ncleaning","#0b7285","#c5f6fa"),
           ("Article\nsegmentation","#5f3dc4","#e5dbff"),("Causal\nextraction","#a61e4d","#ffdeeb"),
           ("Knowledge\nGraph","#2b8a3e","#d3f9d8"),("Causal\nDAG","#364fc7","#dbe4ff"),
           ("Demo backdoor\nadjustment","#d9480f","#ffe8cc")]
    n=len(steps); bw=116; gap=(W-60-n*bw)/(n-1); y=130; h=70
    for i,(lab,st,fl) in enumerate(steps):
        x=30+i*(bw+gap)
        s.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{h}" rx="12" fill="{fl}" stroke="{st}" stroke-width="2.5" filter="url(#sh)"/>')
        for j,ln in enumerate(lab.split("\n")):
            s.append(f'<text x="{x+bw/2}" y="{y+30+j*17}" text-anchor="middle" font-size="12.5" font-weight="600" fill="{st}">{ln}</text>')
        if i<n-1:
            ax=x+bw; s.append(f'<line x1="{ax}" y1="{y+h/2}" x2="{ax+gap}" y2="{y+h/2}" stroke="#868e96" stroke-width="2.2" marker-end="url(#arrow)"/>')
    s.append(f'<text x="{W/2}" y="225" text-anchor="middle" font-size="12" fill="#868e96">raw/ = preserved evidence (90 OCR pages) &#8901; curated/ = analyst coding &#8901; every claim is traceable to a source quote</text>')
    s.append("</svg>"); (FIG/"data_pipeline.svg").write_text("\n".join(s),encoding="utf-8")

def fig_dag():
    W,H=1040,600; s=hdr(W,H,"Figure 3 - Causal DAG: Protest Framing \u2192 Improvement vs Order-Control",
                         "two pathways read from the discourse; Z (newspaper context) is analyst-added confounding")
    P={"X":(150,320),"M1":(470,210),"Y1":(840,210),"M2":(470,430),"Y2":(840,430),"Z":(520,110)}
    nw,nh=210,66
    s.append(edge(P["Z"][0]-40,P["Z"][1]+33,P["X"][0]+30,P["X"][1]-33,dash=True,curve=-90))
    s.append(edge(P["Z"][0],P["Z"][1]+33,P["M1"][0],P["M1"][1]-33,dash=True))
    s.append(edge(P["Z"][0]+90,P["Z"][1]+25,P["Y1"][0],P["Y1"][1]-33,dash=True,curve=60))
    s.append(edge(P["Z"][0]-10,P["Z"][1]+33,P["M2"][0]-30,P["M2"][1]-33,dash=True,curve=-40))
    s.append(edge(P["Z"][0]+110,P["Z"][1]+30,P["Y2"][0]+30,P["Y2"][1]-33,dash=True,curve=170))
    s.append(edge(P["X"][0]+nw/2,P["X"][1]-14,P["M1"][0]-nw/2,P["M1"][1]+10))
    s.append(edge(P["M1"][0]+nw/2,P["M1"][1],P["Y1"][0]-nw/2,P["Y1"][1]))
    s.append(edge(P["X"][0]+nw/2,P["X"][1]+14,P["M2"][0]-nw/2,P["M2"][1]-10))
    s.append(edge(P["M2"][0]+nw/2,P["M2"][1],P["Y2"][0]-nw/2,P["Y2"][1]))
    s.append(node(*P["Z"],nw+40,nh,"Z","Z - Confounders","newspaper context / locale / disorder"))
    s.append(node(*P["X"],nw,nh,"X","X - Protest pressure","strike as social pressure"))
    s.append(node(*P["M1"],nw,nh,"M1","M1 - Demand legitimacy","wage / hours / child-labor"))
    s.append(node(*P["Y1"],nw,nh,"Y1","Y1 - Improvement","hearings - investigation - wages"))
    s.append(node(*P["M2"],nw,nh,"M2","M2 - Disorder framing","riot - shots - arrests"))
    s.append(node(*P["Y2"],nw,nh,"Y2","Y2 - Order control","militia - arrests - suppression"))
    s.append('<text x="300" y="252" text-anchor="middle" font-size="12" fill="#2b8a3e" font-weight="600">progress pathway</text>')
    s.append('<text x="300" y="392" text-anchor="middle" font-size="12" fill="#c92a2a" font-weight="600">disorder pathway</text>')
    lx,ly=60,520
    s.append(f'<rect x="{lx-15}" y="{ly-22}" width="930" height="58" rx="10" fill="#fff" stroke="#dee2e6"/>')
    s.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+34}" y2="{ly}" stroke="#495057" stroke-width="2.2" marker-end="url(#arrow)"/>')
    s.append(f'<text x="{lx+44}" y="{ly+4}" font-size="12.5" fill="#495057">solid = pathway interpreted from text</text>')
    s.append(f'<line x1="{lx+330}" y1="{ly}" x2="{lx+364}" y2="{ly}" stroke="#868e96" stroke-width="2.2" stroke-dasharray="7 5" marker-end="url(#arrowd)"/>')
    s.append(f'<text x="{lx+374}" y="{ly+4}" font-size="12.5" fill="#495057">dashed = analyst-added confounding (Z)</text>')
    s.append(f'<text x="{lx}" y="{ly+26}" font-size="12" fill="#868e96">Temporal reading: X in earlier issues (Jan) \u2192 Y responses in later issues (Feb-Mar). M1/M2 are mediators, not adjusted for total-effect estimation.</text>')
    s.append("</svg>"); (FIG/"causal_dag.svg").write_text("\n".join(s),encoding="utf-8")

def fig_kg():
    W,H=1040,470; s=hdr(W,H,"Figure 2 - Knowledge Graph Schema","every causal claim is traceable from issue down to a verified source quote")
    KG={"Issue":(115,150,"#1864ab","#d0ebff"),"Article":(305,150,"#1864ab","#d0ebff"),
        "Extraction":(505,150,"#5f3dc4","#e5dbff"),"AssertedCausalClaim":(505,300,"#a61e4d","#ffdeeb"),
        "SupportingQuote":(745,225,"#2b8a3e","#d3f9d8"),"SourceURL":(935,150,"#868e96","#f1f3f5")}
    nw,nh=170,56
    def kn(name):
        cx,cy,st,fl=KG[name]; x,y=cx-nw/2,cy-nh/2
        return (f'<rect x="{x}" y="{y}" width="{nw}" height="{nh}" rx="12" fill="{fl}" stroke="{st}" stroke-width="2.5" filter="url(#sh)"/>'
                f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="13" font-weight="700" fill="{st}">{name}</text>')
    def ke(a,b,lab,curve=0):
        ax,ay=KG[a][0],KG[a][1]; bx,by=KG[b][0],KG[b][1]
        if abs(ax-bx)>=abs(ay-by):
            x1=ax+(nw/2 if bx>ax else -nw/2); y1=ay; x2=bx+(-nw/2 if bx>ax else nw/2); y2=by
        else:
            x1=ax; y1=ay+(nh/2 if by>ay else -nh/2); x2=bx; y2=by+(-nh/2 if by>ay else nh/2)
        e=edge(x1,y1,x2,y2,curve=curve)
        mx,my=((ax+bx)/2,114) if (ay==150 and by==150) else ((x1+x2)/2,(y1+y2)/2-10)
        return e+f'<text x="{mx}" y="{my}" text-anchor="middle" font-size="11" fill="#495057" font-style="italic">{lab}</text>'
    s.append(ke("Issue","Article","CONTAINS")); s.append(ke("Article","Extraction","HAS_EXTRACTION"))
    s.append(ke("Extraction","SupportingQuote","SUPPORTED_BY")); s.append(ke("AssertedCausalClaim","Extraction","REPRESENTED_AS"))
    s.append(ke("AssertedCausalClaim","SupportingQuote","EVIDENCE",curve=70)); s.append(ke("Article","SourceURL","DERIVED_FROM",curve=-150))
    for nm in KG: s.append(kn(nm))
    s.append('<text x="520" y="410" text-anchor="middle" font-size="12.5" fill="#868e96">Provenance: SourceURL \u2190 Article \u2192 Extraction \u2192 SupportingQuote; each causal claim reified and linked to its evidence.</text>')
    s.append("</svg>"); (FIG/"knowledge_graph.svg").write_text("\n".join(s),encoding="utf-8")

def fig_demo(res):
    r=[x for x in res if x["outcome"] in ("Y1_improvement_response","Y2_order_control_response")]
    W,H=940,480; s=hdr(W,H,"Figure 4 - Demo Backdoor Adjustment (naive vs adjusted)","synthetic method check, grounded in observed framing - NOT historical effects")
    ax0,ax1=120,840; zero=340; scale=900
    for v in [0.0,0.05,0.10,0.15,0.20]:
        gy=zero-v*scale
        s.append(f'<line x1="{ax0}" y1="{gy}" x2="{ax1}" y2="{gy}" stroke="#e9ecef"/>')
        s.append(f'<text x="{ax0-12}" y="{gy+4}" text-anchor="end" font-size="11" fill="#adb5bd">{v:.2f}</text>')
    s.append(f'<line x1="{ax0}" y1="{zero}" x2="{ax1}" y2="{zero}" stroke="#495057" stroke-width="1.5"/>')
    groups=[("Y1 improvement response",r[0],"#2b8a3e","#d3f9d8"),("Y2 order-control response",r[1],"#c92a2a","#ffe3e3")]
    gw=(ax1-ax0)/2; bw=92
    for gi,(name,row,st,fl) in enumerate(groups):
        gx=ax0+gi*gw+gw/2
        for j,(lab,val,fc) in enumerate([("naive",float(row["naive_difference"]),fl),("adjusted",float(row["ATE_demo_adjusted"]),st)]):
            bx=gx-bw-8+j*(bw+16); h=val*scale; by=zero-h if h>=0 else zero
            s.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{abs(h)}" rx="4" fill="{fc}" stroke="{st}" stroke-width="2"/>')
            ty=by-8 if h>=0 else by+abs(h)+18
            s.append(f'<text x="{bx+bw/2}" y="{ty}" text-anchor="middle" font-size="13" font-weight="700" fill="{st}">{val:+.3f}</text>')
            s.append(f'<text x="{bx+bw/2}" y="{zero+18}" text-anchor="middle" font-size="11.5" fill="#495057">{lab}</text>')
        s.append(f'<text x="{gx}" y="{H-58}" text-anchor="middle" font-size="14" font-weight="700" fill="{st}">{name}</text>')
    s.append(f'<text x="{W/2}" y="{H-30}" text-anchor="middle" font-size="11.5" fill="#868e96">Y1: raw association is ~0 (+0.022); only after adjusting for newspaper context does a modest +0.101 appear (one stratum is even negative).</text>')
    s.append(f'<text x="{W/2}" y="{H-14}" text-anchor="middle" font-size="11.5" fill="#868e96">Y2: raw +0.195 overstates the link; adjusting for context shrinks it to +0.121. All values are demo-only.</text>')
    s.append("</svg>"); (FIG/"demo_effect_estimation.svg").write_text("\n".join(s),encoding="utf-8")

def main():
    ex=summaries(); build_kg(ex); build_dag(); res=inference()
    # ---- sensitivity: adjusted ATE under two P(Z) weightings ----
    rows=rd(CUR/"demo_effect_data.csv")
    for r in rows:
        for k in ("X_protest_pressure","Y1_improvement_response","Y2_order_control_response"): r[k]=int(r[k])
    def wrate(o,x,z):
        f=[r for r in rows if r["X_protest_pressure"]==x and r["Z_context"]==z]
        return sum(r[o] for r in f)/len(f) if f else 0.0
    zs=["order_focused","mixed","institutional"]
    weightings={"demo_balanced":{"order_focused":0.25,"mixed":0.50,"institutional":0.25},
                "observed_issue_share":{"order_focused":0.125,"mixed":0.75,"institutional":0.125}}
    srows=[]
    for o in ("Y1_improvement_response","Y2_order_control_response"):
        within={z:round(wrate(o,1,z)-wrate(o,0,z),3) for z in zs}
        for wname,w in weightings.items():
            ate=sum(within[z]*w[z] for z in zs)
            srows.append({"outcome":o,"weighting":wname,
                          "P_Z":";".join(f"{z}={w[z]}" for z in zs),
                          "within_Z_diffs":";".join(f"{z}={within[z]}" for z in zs),
                          "adjusted_ATE_demo":round(ate,3)})
    wr(OUT/"sensitivity_weighting.csv", srows)
    # polished, presentation-quality figures in Korean (overwrite the plain built-ins)
    import importlib.util, pathlib
    spec=importlib.util.spec_from_file_location("render_figures_ko", pathlib.Path(__file__).parent/"render_figures_ko.py")
    rf=importlib.util.module_from_spec(spec); spec.loader.exec_module(rf)
    rf.render_pipeline(); rf.render_kg(); rf.render_dag(); rf.render_demo()
    y1=next(r for r in res if r["outcome"]=="Y1_improvement_response")
    y2=next(r for r in res if r["outcome"]=="Y2_order_control_response")
    print("Pipeline complete.")
    print(f"  extractions={len(ex)}  (verified quotes coded from real OCR)")
    print(f"  Y1 demo: naive {y1['naive_difference']:+} -> adjusted {y1['ATE_demo_adjusted']:+}")
    print(f"  Y2 demo: naive {y2['naive_difference']:+} -> adjusted {y2['ATE_demo_adjusted']:+}")
    print("  figures: data_pipeline, knowledge_graph, causal_dag, demo_effect_estimation")

if __name__=="__main__": main()
