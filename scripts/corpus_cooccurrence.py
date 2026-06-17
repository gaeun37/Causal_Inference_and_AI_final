#!/usr/bin/env python3
"""Rung-1 (association) read of the REAL corpus -- no synthetic data.

The demo backdoor adjustment in build_pipeline.py runs on synthetic units and is
explicitly a *method demonstration*, not a finding. To avoid resting any claim on
data we designed, this script reports what can actually be observed in the 26
verified extractions / 8 strike articles themselves:

  (a) extraction-level: how many X / M1 / M2 / Y1 / Y2 framing units appear in
      each newspaper-context Z;
  (b) article-level: in how many strike articles each framing role is present,
      and the within-context lean toward improvement (Y1) vs order-control (Y2);
  (c) a 2-level Z collapse (order_focused vs reform_leaning = mixed+institutional),
      which is what the data-driven proximal measure in issue_context.py actually
      supports.

These are small-n DESCRIPTIVE associations (rung 1). They are not adjusted, not
causal, and not historical. They exist so the report can show a genuine observed
pattern next to the synthetic adjustment demo.

Writes: outputs/real_corpus_cooccurrence.csv
"""
from pathlib import Path
import csv
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[1]
CUR  = ROOT / "data" / "curated"
OUT  = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

# data-driven 2-level collapse (see issue_context.py honest note)
COLLAPSE = {"order_focused": "order_focused",
            "mixed": "reform_leaning",
            "institutional": "reform_leaning"}
FRAMES = ["X", "M1", "Y1", "M2", "Y2"]


def read(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    ex = [e for e in read(CUR / "real_extractions.csv")
          if e["role_in_dag"] in FRAMES]          # textual framing units only
    arts = [a for a in read(CUR / "articles.csv")
            if a.get("strike_related") == "1"]     # strike articles only

    rows = []

    # ---- (a) extraction-level frame counts, by 3-level and 2-level Z ----
    for scheme, keyfn in (("Z_3level", lambda z: z),
                          ("Z_2level", lambda z: COLLAPSE[z])):
        by_ctx = defaultdict(Counter)
        for e in ex:
            by_ctx[keyfn(e["context_Z"])][e["role_in_dag"]] += 1
        for ctx in sorted(by_ctx):
            c = by_ctx[ctx]
            y1, y2 = c.get("Y1", 0), c.get("Y2", 0)
            denom = y1 + y2
            rows.append({
                "view": "extraction_counts",
                "scheme": scheme,
                "context_Z": ctx,
                "n_X": c.get("X", 0), "n_M1": c.get("M1", 0),
                "n_M2": c.get("M2", 0), "n_Y1": y1, "n_Y2": y2,
                "Y1_share_of_responses": round(y1 / denom, 3) if denom else "",
                "lean": ("order-control (Y2)" if y2 > y1
                         else "improvement (Y1)" if y1 > y2
                         else "balanced/none"),
            })

    # ---- (b) article-level presence of each role, by 3-level Z ----
    art_roles = {a["article_id"]: set(a.get("main_role", "").replace(" ", "").split("/"))
                 for a in arts}
    art_ctx = {a["article_id"]: a["context_Z"] for a in arts}
    by_ctx_art = defaultdict(list)
    for aid in art_roles:
        by_ctx_art[art_ctx[aid]].append(aid)
    for ctx in sorted(by_ctx_art):
        aids = by_ctx_art[ctx]
        n = len(aids)
        present = {f: sum(1 for a in aids if f in art_roles[a]) for f in FRAMES}
        rows.append({
            "view": "article_presence",
            "scheme": "Z_3level",
            "context_Z": ctx,
            "n_X": f"{present['X']}/{n}", "n_M1": f"{present['M1']}/{n}",
            "n_M2": f"{present['M2']}/{n}", "n_Y1": f"{present['Y1']}/{n}",
            "n_Y2": f"{present['Y2']}/{n}",
            "Y1_share_of_responses": "",
            "lean": ("order-control (Y2)" if present["Y2"] > present["Y1"]
                     else "improvement (Y1)" if present["Y1"] > present["Y2"]
                     else "balanced/none"),
        })

    fields = ["view", "scheme", "context_Z", "n_X", "n_M1", "n_M2",
              "n_Y1", "n_Y2", "Y1_share_of_responses", "lean"]
    with open(OUT / "real_corpus_cooccurrence.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    # console summary
    print("Rung-1 (real corpus, NOT synthetic) -- extraction-level frame counts:")
    print(f"  {'scheme':10}{'context':16}{'Y1':>4}{'Y2':>4}   lean")
    for r in rows:
        if r["view"] == "extraction_counts":
            print(f"  {r['scheme']:10}{r['context_Z']:16}{r['n_Y1']:>4}{r['n_Y2']:>4}   {r['lean']}")
    print("\nObserved pattern (descriptive, rung 1, not adjusted, not historical):")
    print("  order_focused (Evening Standard, Jan) -> order-control only, no improvement frame;")
    print("  institutional/mixed (later issues)    -> improvement frames present and growing.")
    print("CAVEAT: order_focused = one paper / one issue / earliest date, so the")
    print("'early control -> later improvement' reading is confounded with newspaper and time.")


if __name__ == "__main__":
    main()
