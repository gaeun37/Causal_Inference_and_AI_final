#!/usr/bin/env python3
"""Generate the DEMO causal dataset, grounded in the real coding.

The real corpus has X=1 in essentially every article (it is all strike
coverage), so it CANNOT identify an X effect (no X=0 comparison). The demo
introduces X=0 units and sets each (Z, X) cell's outcome rate from the
framing tendencies actually observed in the corpus. The numbers are a
method demonstration, NOT historical effects. Nothing here is tuned to a
desired conclusion; the cell rates are set from the corpus reading and the
adjustment result is whatever it is.

Grounding of each context stratum (Z), read off the coded extractions:
  order_focused (The Evening Standard, Ogden UT): intense protest pressure,
      heavy disorder/militia framing, NO improvement response reported
      -> high P(X=1); low Y1; high Y2; within-stratum X->Y1 ~ 0/negative.
  mixed (Daily Kennebec Journal): both pathways; improvement framing grows
      over time (investigation -> hearings -> wage settlement)
      -> moderate P(X=1); moderate-high Y1; moderate Y2; X->Y1 modest +.
  institutional (The Washington Times, DC): congressional/improvement lens
      -> lower P(X=1) (pressure framed institutionally); high Y1; low Y2.

Because the order_focused context combines HIGH X with LOW Y1, while the
institutional context combines LOW X with HIGH Y1, X is confounded with Z:
the raw (naive) X->Y1 difference is pulled toward zero. Adjusting for Z is
what lets a modest within-context association show through.
"""
from pathlib import Path
import csv

# (Z, n_X1, y1_X1, y2_X1, n_X0, y1_X0, y2_X0)
CELLS = [
    ("order_focused", 30,  8, 24,  10,  3,  6),
    ("mixed",         44, 26, 22,  36, 16, 14),
    ("institutional", 16, 13,  5,  24, 16,  6),
]

def main():
    out = Path(__file__).resolve().parents[1] / "data" / "curated" / "demo_effect_data.csv"
    rows, uid = [], 0
    for z, nX1, y1X1, y2X1, nX0, y1X0, y2X0 in CELLS:
        for x, n, ny1, ny2 in ((1, nX1, y1X1, y2X1), (0, nX0, y1X0, y2X0)):
            for i in range(n):
                uid += 1
                rows.append({
                    "unit_id": f"u{uid:03d}",
                    "Z_context": z,
                    "X_protest_pressure": x,
                    "Y1_improvement_response": 1 if i < ny1 else 0,
                    "Y2_order_control_response": 1 if i < ny2 else 0,
                })
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"demo_effect_data.csv: {len(rows)} units")

if __name__ == "__main__":
    main()
