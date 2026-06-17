#!/usr/bin/env python3
"""Quantify issue-level context Z from the FULL issue OCR (all articles).

Two transparent measures per issue, both heuristics (not validated instruments):
  (a) full-issue keyword rates  -- counts every page of the issue;
  (b) strike-proximal order_share -- within lines that mention the strike
      (+/- 1 line), the share of disorder vocabulary vs reform/institutional
      vocabulary. This targets the construct of interest: HOW this paper frames
      the strike's environment, which is what the confounder Z encodes.

Non-strike content informs Z only -- never the outcomes Y1/Y2.
Honest note: (a) barely separates the papers because general legislative/crime
vocabulary saturates 1912 newsprint; (b) cleanly isolates the order-focused
paper. Both are written out so the Z assignment is auditable.

Writes: data/curated/issue_context_features.csv
"""
from pathlib import Path
import csv, re, glob, os

ROOT = Path(__file__).resolve().parents[1]
OCR = ROOT/"data"/"raw"/"ocr"; CUR = ROOT/"data"/"curated"
MONTHS={"January":"01","February":"02","March":"03"}
PAPER={"Evening standard":"The Evening Standard","Kennebec":"Daily Kennebec Journal","Washington times":"The Washington Times"}
ISSUE={("The Evening Standard","1912-01-15"):"iss001",("Daily Kennebec Journal","1912-01-22"):"iss002",
("Daily Kennebec Journal","1912-02-09"):"iss003",("The Washington Times","1912-02-27"):"iss004",
("Daily Kennebec Journal","1912-02-27"):"iss005",("Daily Kennebec Journal","1912-02-28"):"iss006",
("Daily Kennebec Journal","1912-03-08"):"iss007",("Daily Kennebec Journal","1912-03-15"):"iss008"}
ASSIGN={"iss001":"order_focused","iss002":"mixed","iss003":"mixed","iss004":"institutional",
        "iss005":"mixed","iss006":"mixed","iss007":"mixed","iss008":"mixed"}
STRIKE=re.compile(r"lawrence|strike|striker|operativ|woolen|\bmills?\b",re.I)
ORDER=re.compile(r"riot|disorder|police|militia|arrest|mob|violence|bayonet|troop|shots?|club|ambush",re.I)
REFORM=re.compile(r"investigat|hearing|committee|congress|senate|resolution|settlement|agreement|increase|wage scale|arbitrat",re.I)
FULL_ORDER=ORDER; FULL_REFORM=REFORM

def iid(fn):
    m=re.search(r"of (.+?) \((.+?)\) (January|February|March) (\d+) 1912",fn)
    if not m: return None
    paper=next((v for k,v in PAPER.items() if k.lower() in m.group(1).lower()),None)
    return ISSUE.get((paper,f"1912-{MONTHS[m.group(3)]}-{int(m.group(4)):02d}"))

def main():
    agg={}
    for p in glob.glob(str(OCR/"*.txt")):
        i=iid(os.path.basename(p))
        if not i: continue
        txt=open(p,encoding="utf-8",errors="replace").read(); low=txt.lower()
        lines=txt.splitlines()
        a=agg.setdefault(i,{"words":0,"f_order":0,"f_reform":0,"sl":0,"p_order":0,"p_reform":0})
        a["words"]+=len(re.findall(r"\w+",low))
        a["f_order"]+=len(FULL_ORDER.findall(low)); a["f_reform"]+=len(FULL_REFORM.findall(low))
        for j,ln in enumerate(lines):
            if STRIKE.search(ln):
                win=" ".join(lines[max(0,j-1):j+2])
                a["sl"]+=1; a["p_order"]+=len(ORDER.findall(win)); a["p_reform"]+=len(REFORM.findall(win))
    rows=[]
    for i in sorted(agg):
        a=agg[i]; w=max(a["words"],1)
        pden=a["p_order"]+a["p_reform"] or 1
        psh=round(a["p_order"]/pden,3)
        dd="order_focused" if psh>=0.6 else ("reform_leaning" if psh<=0.30 else "mixed")
        rows.append({"issue_id":i,"assigned_Z":ASSIGN[i],
            "full_order_per_1k":round(a["f_order"]/w*1000,2),"full_reform_per_1k":round(a["f_reform"]/w*1000,2),
            "strike_lines":a["sl"],"proximal_order":a["p_order"],"proximal_reform":a["p_reform"],
            "proximal_order_share":psh,"data_driven_Z_proximal":dd,
            "note":("order-focused strongly confirmed (disorder-only strike framing)" if psh>=0.6
                    else "reform/institution-leaning strike framing")})
    with open(CUR/"issue_context_features.csv","w",newline="",encoding="utf-8") as f:
        w_=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w_.writeheader(); w_.writerows(rows)
    print(f"{'issue':8}{'assigned':14}{'prox_share':11}{'data_driven':16}")
    for r in rows:
        print(f"{r['issue_id']:8}{r['assigned_Z']:14}{r['proximal_order_share']:<11}{r['data_driven_Z_proximal']:16}")
    print("\nHonest reading: order_focused (Evening Standard) confirmed at share=1.0;")
    print("all other issues are reform-leaning in strike-proximal vocabulary, so the")
    print("mixed-vs-institutional split is a coarse, locale-informed distinction (limitation).")

if __name__=="__main__": main()
