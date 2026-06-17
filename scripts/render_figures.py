#!/usr/bin/env python3
"""Render presentation-quality SVG figures from the REAL-data outputs.

Reads the honest numbers computed by build_pipeline.py
(outputs/demo_backdoor_adjustment_results.csv) and the DAG/extraction tables,
then emits four figures:
  figures/data_pipeline.svg
  figures/knowledge_graph.svg
  figures/causal_dag.svg
  figures/demo_effect_estimation.svg
Deterministic; no network, no randomness.
"""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)
OUT = ROOT / "outputs"

FONT = "'Segoe UI','Helvetica Neue',Arial,sans-serif"
PALETTE = {
    "X":  ("#364fc7", "#dbe4ff"), "M1": ("#0b7285", "#c5f6fa"),
    "Y1": ("#2b8a3e", "#d3f9d8"), "M2": ("#d9480f", "#ffe8cc"),
    "Y2": ("#c92a2a", "#ffe3e3"), "Z":  ("#5f3dc4", "#e5dbff"),
}


def header(w, h, title, sub=""):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
         f'viewBox="0 0 {w} {h}" font-family="{FONT}">',
         '<defs>'
         '<marker id="arrow" markerWidth="12" markerHeight="12" refX="9" refY="4" '
         'orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L0,8 L10,4 z" fill="#495057"/></marker>'
         '<marker id="arrowd" markerWidth="12" markerHeight="12" refX="9" refY="4" '
         'orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L0,8 L10,4 z" fill="#868e96"/></marker>'
         '<marker id="arroww" markerWidth="13" markerHeight="13" refX="9" refY="4" '
         'orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L0,8 L10,4 z" fill="#ffffff"/></marker>'
         '<filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">'
         '<feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.14"/></filter>'
         '</defs>',
         f'<rect width="{w}" height="{h}" fill="#fbfcfe"/>',
         f'<text x="{w/2}" y="40" text-anchor="middle" font-size="23" font-weight="700" '
         f'fill="#212529" letter-spacing="0.3">{title}</text>']
    if sub:
        s.append(f'<text x="{w/2}" y="64" text-anchor="middle" font-size="13.5" fill="#868e96">{sub}</text>')
    return s


def node(cx, cy, w, h, key, title, subtitle):
    stroke, fill = PALETTE[key]; x, y = cx - w/2, cy - h/2
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="2.5" filter="url(#shadow)"/>'
            f'<text x="{cx}" y="{cy-4}" text-anchor="middle" font-size="16" font-weight="700" '
            f'fill="{stroke}">{title}</text>'
            f'<text x="{cx}" y="{cy+15}" text-anchor="middle" font-size="11.5" fill="#495057">{subtitle}</text>')


def edge(x1, y1, x2, y2, dashed=False, curve=0):
    color = "#868e96" if dashed else "#495057"
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    marker = "url(#arrowd)" if dashed else "url(#arrow)"
    if curve:
        mx, my = (x1+x2)/2 + curve, (y1+y2)/2 - abs(curve)*0.5
        return (f'<path d="M{x1},{y1} Q{mx},{my} {x2},{y2}" fill="none" stroke="{color}" '
                f'stroke-width="2.2"{dash} marker-end="{marker}"/>')
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="2.2"{dash} marker-end="{marker}"/>')


# ---------------------------------------------------------------- DAG
def render_dag():
    W, H = 1040, 600
    s = header(W, H, "Causal DAG \u2014 Protest Framing \u2192 Improvement vs Order-Control",
               "Two pathways read from real 1912 newspaper OCR; Z is analyst-added confounding")
    P = {"X": (150, 320), "M1": (470, 210), "Y1": (840, 210),
         "M2": (470, 430), "Y2": (840, 430), "Z": (520, 110)}
    nw, nh = 210, 66
    s.append(edge(P["Z"][0]-40, P["Z"][1]+33, P["X"][0]+30, P["X"][1]-33, True, -90))
    s.append(edge(P["Z"][0], P["Z"][1]+33, P["M1"][0], P["M1"][1]-33, True))
    s.append(edge(P["Z"][0]+90, P["Z"][1]+25, P["Y1"][0], P["Y1"][1]-33, True, 60))
    s.append(edge(P["Z"][0]-10, P["Z"][1]+33, P["M2"][0]-30, P["M2"][1]-33, True, -40))
    s.append(edge(P["Z"][0]+110, P["Z"][1]+30, P["Y2"][0]+30, P["Y2"][1]-33, True, 170))
    s.append(edge(P["X"][0]+nw/2, P["X"][1]-14, P["M1"][0]-nw/2, P["M1"][1]+10))
    s.append(edge(P["M1"][0]+nw/2, P["M1"][1], P["Y1"][0]-nw/2, P["Y1"][1]))
    s.append(edge(P["X"][0]+nw/2, P["X"][1]+14, P["M2"][0]-nw/2, P["M2"][1]-10))
    s.append(edge(P["M2"][0]+nw/2, P["M2"][1], P["Y2"][0]-nw/2, P["Y2"][1]))
    s.append(node(*P["Z"], nw+40, nh, "Z", "Z \u2014 Confounders", "orientation \u00b7 context \u00b7 disorder"))
    s.append(node(*P["X"], nw, nh, "X", "X \u2014 Protest pressure", "strike framed as social pressure"))
    s.append(node(*P["M1"], nw, nh, "M1", "M1 \u2014 Demand legitimacy", "wage/hours claims as legitimate"))
    s.append(node(*P["Y1"], nw, nh, "Y1", "Y1 \u2014 Improvement", "hearings \u00b7 negotiation \u00b7 wage rise"))
    s.append(node(*P["M2"], nw, nh, "M2", "M2 \u2014 Disorder framing", "riot \u00b7 arrests \u00b7 public danger"))
    s.append(node(*P["Y2"], nw, nh, "Y2", "Y2 \u2014 Order control", "militia \u00b7 arrests \u00b7 suppression"))
    s.append('<text x="300" y="252" text-anchor="middle" font-size="12" fill="#2b8a3e" font-weight="600">progress pathway (X\u2192M1\u2192Y1)</text>')
    s.append('<text x="300" y="392" text-anchor="middle" font-size="12" fill="#c92a2a" font-weight="600">disorder pathway (X\u2192M2\u2192Y2)</text>')
    lx, ly = 60, 520
    s.append(f'<rect x="{lx-15}" y="{ly-22}" width="930" height="58" rx="10" fill="#fff" stroke="#dee2e6"/>')
    s.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+34}" y2="{ly}" stroke="#495057" stroke-width="2.2" marker-end="url(#arrow)"/>')
    s.append(f'<text x="{lx+44}" y="{ly+4}" font-size="12.5" fill="#495057">solid = pathway interpreted from text (23 supporting quotes)</text>')
    s.append(f'<line x1="{lx+470}" y1="{ly}" x2="{lx+504}" y2="{ly}" stroke="#868e96" stroke-width="2.2" stroke-dasharray="7 5" marker-end="url(#arrowd)"/>')
    s.append(f'<text x="{lx+514}" y="{ly+4}" font-size="12.5" fill="#495057">dashed = analyst-added confounding (Z)</text>')
    s.append(f'<text x="{lx}" y="{ly+26}" font-size="12" fill="#868e96">Temporal reading across issues: X in January, Y responses in Feb\u2013Mar. M1/M2 are mediators \u2014 not adjusted for total-effect estimation.</text>')
    s.append("</svg>")
    (FIG/"causal_dag.svg").write_text("\n".join(s), encoding="utf-8")


# ---------------------------------------------------------------- KG
def render_kg():
    W, H = 1040, 470
    s = header(W, H, "Knowledge Graph Schema",
               "Every causal claim is traceable from newspaper issue down to a real OCR quote")
    KG = {"Issue": (115,150,"#1864ab","#d0ebff"), "Article": (305,150,"#1864ab","#d0ebff"),
          "Extraction": (520,150,"#5f3dc4","#e5dbff"), "CausalAssertion": (520,300,"#a61e4d","#ffdeeb"),
          "SupportingQuote": (760,225,"#2b8a3e","#d3f9d8"), "SourceURL": (935,150,"#868e96","#f1f3f5")}
    nw, nh = 156, 56

    def kn(name):
        cx, cy, st, fl = KG[name]; x, y = cx-nw/2, cy-nh/2
        return (f'<rect x="{x}" y="{y}" width="{nw}" height="{nh}" rx="12" fill="{fl}" '
                f'stroke="{st}" stroke-width="2.5" filter="url(#shadow)"/>'
                f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="13.5" font-weight="700" fill="{st}">{name}</text>')

    def ke(a, b, label, curve=0):
        ax, ay = KG[a][0], KG[a][1]; bx, by = KG[b][0], KG[b][1]
        if abs(ax-bx) >= abs(ay-by):
            x1 = ax + (nw/2 if bx > ax else -nw/2); y1 = ay
            x2 = bx + (-nw/2 if bx > ax else nw/2); y2 = by
        else:
            x1 = ax; y1 = ay + (nh/2 if by > ay else -nh/2)
            x2 = bx; y2 = by + (-nh/2 if by > ay else nh/2)
        e = edge(x1, y1, x2, y2, curve=curve)
        if ay == 150 and by == 150:
            mx, my = (ax+bx)/2, 114
        else:
            mx, my = (x1+x2)/2, (y1+y2)/2 - 10
        return e + (f'<text x="{mx}" y="{my}" text-anchor="middle" font-size="11" '
                    f'fill="#495057" font-style="italic">{label}</text>')

    s.append(ke("Issue", "Article", "CONTAINS"))
    s.append(ke("Article", "Extraction", "HAS_EXTRACTION"))
    s.append(ke("Extraction", "SupportingQuote", "SUPPORTED_BY"))
    s.append(ke("CausalAssertion", "Extraction", "REPRESENTED_AS"))
    s.append(ke("CausalAssertion", "SupportingQuote", "EVIDENCE", curve=70))
    s.append(ke("Article", "SourceURL", "DERIVED_FROM", curve=-150))
    for n in KG:
        s.append(kn(n))
    s.append('<text x="520" y="410" text-anchor="middle" font-size="12.5" fill="#868e96">'
             'Provenance chain: SourceURL \u2190 Article \u2192 Extraction \u2192 SupportingQuote; '
             'each CausalAssertion is reified and linked to its evidence.</text>')
    s.append("</svg>")
    (FIG/"knowledge_graph.svg").write_text("\n".join(s), encoding="utf-8")


# ---------------------------------------------------------------- pipeline
def render_pipeline():
    W, H = 1040, 280
    s = header(W, H, "Data Pipeline", "From raw 1912 newspaper OCR to an auditable causal-inference demo")
    stages = [("Raw OCR", "90 ALTO pages", "#1864ab", "#d0ebff"),
              ("Clean", "normalize + log", "#1098ad", "#c5f6fa"),
              ("Segment", "strike articles", "#0ca678", "#c3fae8"),
              ("Code", "X/M1/M2/Y1/Y2/Z", "#5f3dc4", "#e5dbff"),
              ("Knowledge\nGraph", "provenance", "#a61e4d", "#ffdeeb"),
              ("Causal\nDAG", "two pathways", "#e8590c", "#ffe8cc"),
              ("Backdoor\ndemo", "adjust for Z", "#2b8a3e", "#d3f9d8")]
    n = len(stages); bw, bh = 118, 84
    gap = (W - 60 - n*bw) / (n-1)
    y = 150
    for i, (name, sub, st, fl) in enumerate(stages):
        x = 30 + i*(bw+gap)
        s.append(f'<rect x="{x}" y="{y-bh/2}" width="{bw}" height="{bh}" rx="12" fill="{fl}" '
                 f'stroke="{st}" stroke-width="2.5" filter="url(#shadow)"/>')
        lines = name.split("\n")
        ty = y - 6 - (len(lines)-1)*9
        for ln in lines:
            s.append(f'<text x="{x+bw/2}" y="{ty}" text-anchor="middle" font-size="14.5" '
                     f'font-weight="700" fill="{st}">{ln}</text>'); ty += 18
        s.append(f'<text x="{x+bw/2}" y="{y+26}" text-anchor="middle" font-size="10.5" fill="#495057">{sub}</text>')
        if i < n-1:
            ax = x+bw; s.append(f'<line x1="{ax}" y1="{y}" x2="{ax+gap}" y2="{y}" stroke="#adb5bd" '
                                f'stroke-width="2.4" marker-end="url(#arrow)"/>')
    s.append(f'<text x="{W/2}" y="{H-26}" text-anchor="middle" font-size="12" fill="#868e96">'
             'Raw evidence (left) is preserved separately from analytic structure; every step is logged and reproducible.</text>')
    s.append("</svg>")
    (FIG/"data_pipeline.svg").write_text("\n".join(s), encoding="utf-8")


# ---------------------------------------------------------------- demo effect
def _results():
    rows = list(csv.DictReader(open(OUT/"demo_backdoor_adjustment_results.csv", encoding="utf-8")))
    top = {r["outcome"]: r for r in rows if r["naive_difference"]}
    strata = {}
    for r in rows:
        if " by " in r["outcome"] and r["naive_difference"]:
            base, z = r["outcome"].split(" by ")
            strata.setdefault(base, {})[z] = float(r["naive_difference"])
    return top, strata


def render_demo():
    top, strata = _results()
    y1, y2 = top["Y1_improvement_response"], top["Y2_order_control_response"]
    W, H = 1040, 540
    s = header(W, H, "Demo Backdoor Adjustment \u2014 the Honest Result",
               "Synthetic method check coded from the real corpus. NOT a historical effect.")
    # ---- Panel A: naive vs adjusted ----
    ax0, ax1 = 90, 470; zero = 360; scale = 1150
    s.append('<text x="280" y="100" text-anchor="middle" font-size="14.5" font-weight="700" fill="#343a40">A. Naive vs context-adjusted ATE</text>')
    for v in [0.0, 0.05, 0.10, 0.15, 0.20]:
        gy = zero - v*scale
        s.append(f'<line x1="{ax0}" y1="{gy}" x2="{ax1}" y2="{gy}" stroke="#e9ecef"/>')
        s.append(f'<text x="{ax0-10}" y="{gy+4}" text-anchor="end" font-size="10.5" fill="#adb5bd">{v:.2f}</text>')
    s.append(f'<line x1="{ax0}" y1="{zero}" x2="{ax1}" y2="{zero}" stroke="#495057" stroke-width="1.5"/>')
    groups = [("Y1 improvement", y1, "#2b8a3e", "#d3f9d8"),
              ("Y2 order-control", y2, "#c92a2a", "#ffe3e3")]
    gw = (ax1-ax0)/2; bw = 78
    for gi, (name, r, st, fl) in enumerate(groups):
        gx = ax0 + gi*gw + gw/2
        for j, (lab, val, fc) in enumerate([("naive", float(r["naive_difference"]), fl),
                                            ("adjusted", float(r["ATE_demo_adjusted"]), st)]):
            bx = gx - bw - 6 + j*(bw+12); h = val*scale
            by = zero - h if h >= 0 else zero
            s.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{abs(h)}" rx="4" fill="{fc}" stroke="{st}" stroke-width="2"/>')
            s.append(f'<text x="{bx+bw/2}" y="{by-8 if h>=0 else by+abs(h)+16}" text-anchor="middle" '
                     f'font-size="12.5" font-weight="700" fill="{st}">{val:+.3f}</text>')
            s.append(f'<text x="{bx+bw/2}" y="{zero+16}" text-anchor="middle" font-size="10.5" fill="#495057">{lab}</text>')
        s.append(f'<text x="{gx}" y="{zero+40}" text-anchor="middle" font-size="13" font-weight="700" fill="{st}">{name}</text>')
    # ---- Panel B: Y1 by stratum (shows one negative stratum) ----
    bx0, bx1 = 600, 980; bzero = 360; bscale = 1150
    s.append('<text x="790" y="100" text-anchor="middle" font-size="14.5" font-weight="700" fill="#343a40">B. Y1 protest\u2013improvement link by context (Z)</text>')
    for v in [-0.05, 0.0, 0.05, 0.10, 0.15]:
        gy = bzero - v*bscale
        s.append(f'<line x1="{bx0}" y1="{gy}" x2="{bx1}" y2="{gy}" stroke="#e9ecef"/>')
        s.append(f'<text x="{bx0-10}" y="{gy+4}" text-anchor="end" font-size="10.5" fill="#adb5bd">{v:+.2f}</text>')
    s.append(f'<line x1="{bx0}" y1="{bzero}" x2="{bx1}" y2="{bzero}" stroke="#495057" stroke-width="1.5"/>')
    sd = strata["Y1_improvement_response"]
    order = [("order_focused", "order-focused\n(riot-only paper)"),
             ("mixed", "mixed\n(regional)"),
             ("institutional", "institutional\n(DC/Congress)")]
    gw2 = (bx1-bx0)/3; bw2 = 70
    for gi, (zkey, zlab) in enumerate(order):
        val = sd[zkey]; gx = bx0 + gi*gw2 + gw2/2
        st = "#c92a2a" if val < 0 else "#2b8a3e"
        fl = "#ffe3e3" if val < 0 else "#d3f9d8"
        h = val*bscale; by = bzero - h if h >= 0 else bzero
        s.append(f'<rect x="{gx-bw2/2}" y="{by}" width="{bw2}" height="{abs(h)}" rx="4" fill="{fl}" stroke="{st}" stroke-width="2"/>')
        s.append(f'<text x="{gx}" y="{by-8 if h>=0 else by+abs(h)+16}" text-anchor="middle" font-size="12" font-weight="700" fill="{st}">{val:+.3f}</text>')
        for k, ln in enumerate(zlab.split("\n")):
            s.append(f'<text x="{gx}" y="{bzero+30+k*14}" text-anchor="middle" font-size="10.5" fill="#495057">{ln}</text>')
    # caption
    s.append('<rect x="60" y="452" width="920" height="62" rx="10" fill="#fff" stroke="#dee2e6"/>')
    s.append(f'<text x="74" y="476" font-size="12" fill="#343a40" font-weight="600">'
             f'Naive protest\u2013improvement association \u2248 0 (+{float(y1["naive_difference"]):.3f}); '
             f'a modest link (+{float(y1["ATE_demo_adjusted"]):.3f}) emerges only after adjusting for context Z.</text>')
    s.append('<text x="74" y="498" font-size="12" fill="#495057">'
             'In the riot-only context it even turns negative (\u20130.033) \u2014 '
             'complicating a simple \u201cprotest \u2192 progress\u201d story.</text>')
    s.append("</svg>")
    (FIG/"demo_effect_estimation.svg").write_text("\n".join(s), encoding="utf-8")


if __name__ == "__main__":
    render_pipeline(); render_kg(); render_dag(); render_demo()
    print("Rendered 4 polished figures into figures/")
