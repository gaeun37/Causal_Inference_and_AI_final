#!/usr/bin/env python3
"""Korean-labeled versions of the four figures.

Reuses the geometry helpers (header/node/edge) from render_figures.py but sets
a CJK-capable font and Korean labels. Run after build_pipeline, or it is called
automatically by build_pipeline.main().
"""
import importlib.util, pathlib
_spec = importlib.util.spec_from_file_location("render_figures", pathlib.Path(__file__).parent/"render_figures.py")
rf = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(rf)
rf.FONT = "'Noto Sans CJK KR','Segoe UI',sans-serif"   # CJK-capable root font
header, node, edge, PALETTE, FIG = rf.header, rf.node, rf.edge, rf.PALETTE, rf.FIG


def render_dag():
    W, H = 1040, 600
    s = header(W, H, "인과 DAG \u2014 시위 프레이밍 \u2192 개선 vs 질서통제",
               "실제 1912년 신문 OCR에서 읽은 두 경로; Z는 연구자가 추가한 혼란변수")
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
    s.append(node(*P["Z"], nw+40, nh, "Z", "Z \u2014 혼란변수", "신문 성향 \u00b7 맥락 \u00b7 혼란"))
    s.append(node(*P["X"], nw, nh, "X", "X \u2014 시위 압력", "사회적 압력으로 프레이밍"))
    s.append(node(*P["M1"], nw, nh, "M1", "M1 \u2014 요구 정당화", "임금/시간 요구의 정당성"))
    s.append(node(*P["Y1"], nw, nh, "Y1", "Y1 \u2014 개선", "청문회 \u00b7 협상 \u00b7 임금인상"))
    s.append(node(*P["M2"], nw, nh, "M2", "M2 \u2014 혼란 프레이밍", "폭동 \u00b7 체포 \u00b7 위협"))
    s.append(node(*P["Y2"], nw, nh, "Y2", "Y2 \u2014 질서 통제", "민병대 \u00b7 체포 \u00b7 진압"))
    s.append('<text x="300" y="252" text-anchor="middle" font-size="12" fill="#2b8a3e" font-weight="600">진보 경로 (X\u2192M1\u2192Y1)</text>')
    s.append('<text x="300" y="392" text-anchor="middle" font-size="12" fill="#c92a2a" font-weight="600">혼란 경로 (X\u2192M2\u2192Y2)</text>')
    lx, ly = 60, 520
    s.append(f'<rect x="{lx-15}" y="{ly-22}" width="930" height="58" rx="10" fill="#fff" stroke="#dee2e6"/>')
    s.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+34}" y2="{ly}" stroke="#495057" stroke-width="2.2" marker-end="url(#arrow)"/>')
    s.append(f'<text x="{lx+44}" y="{ly+4}" font-size="12.5" fill="#495057">실선 = 텍스트에서 해석한 경로 (근거 인용 23건)</text>')
    s.append(f'<line x1="{lx+430}" y1="{ly}" x2="{lx+464}" y2="{ly}" stroke="#868e96" stroke-width="2.2" stroke-dasharray="7 5" marker-end="url(#arrowd)"/>')
    s.append(f'<text x="{lx+474}" y="{ly+4}" font-size="12.5" fill="#495057">점선 = 연구자 추가 혼란변수 (Z)</text>')
    s.append(f'<text x="{lx}" y="{ly+26}" font-size="12" fill="#868e96">시간 순서(호 단위): X는 1월, Y 반응은 2\u20133월. M1/M2는 매개변수 \u2014 총효과 추정 시 보정하지 않음.</text>')
    s.append("</svg>")
    (FIG/"causal_dag.svg").write_text("\n".join(s), encoding="utf-8")


def render_kg():
    W, H = 1040, 470
    s = header(W, H, "지식 그래프 스키마", "모든 인과 주장은 신문 호에서 실제 OCR 인용까지 추적된다")
    KG = {"Issue": (115,150,"#1864ab","#d0ebff"), "Article": (305,150,"#1864ab","#d0ebff"),
          "Extraction": (520,150,"#5f3dc4","#e5dbff"), "CausalAssertion": (520,300,"#a61e4d","#ffdeeb"),
          "SupportingQuote": (760,225,"#2b8a3e","#d3f9d8"), "SourceURL": (935,150,"#868e96","#f1f3f5")}
    nw, nh = 156, 56
    def kn(name):
        cx, cy, st, fl = KG[name]; x, y = cx-nw/2, cy-nh/2
        return (f'<rect x="{x}" y="{y}" width="{nw}" height="{nh}" rx="12" fill="{fl}" stroke="{st}" stroke-width="2.5" filter="url(#shadow)"/>'
                f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="13" font-weight="700" fill="{st}">{name}</text>')
    def ke(a, b, label, curve=0):
        ax, ay = KG[a][0], KG[a][1]; bx, by = KG[b][0], KG[b][1]
        if abs(ax-bx) >= abs(ay-by):
            x1 = ax + (nw/2 if bx > ax else -nw/2); y1 = ay
            x2 = bx + (-nw/2 if bx > ax else nw/2); y2 = by
        else:
            x1 = ax; y1 = ay + (nh/2 if by > ay else -nh/2)
            x2 = bx; y2 = by + (-nh/2 if by > ay else nh/2)
        e = edge(x1, y1, x2, y2, curve=curve)
        mx, my = ((ax+bx)/2, 114) if (ay == 150 and by == 150) else ((x1+x2)/2, (y1+y2)/2 - 10)
        return e + f'<text x="{mx}" y="{my}" text-anchor="middle" font-size="11" fill="#495057" font-style="italic">{label}</text>'
    s.append(ke("Issue", "Article", "CONTAINS"))
    s.append(ke("Article", "Extraction", "HAS_EXTRACTION"))
    s.append(ke("Extraction", "SupportingQuote", "SUPPORTED_BY"))
    s.append(ke("CausalAssertion", "Extraction", "REPRESENTED_AS"))
    s.append(ke("CausalAssertion", "SupportingQuote", "EVIDENCE", curve=70))
    s.append(ke("Article", "SourceURL", "DERIVED_FROM", curve=-150))
    for n in KG: s.append(kn(n))
    s.append('<text x="520" y="410" text-anchor="middle" font-size="12.5" fill="#868e96">'
             '출처 사슬: SourceURL \u2190 Article \u2192 Extraction \u2192 SupportingQuote; 각 인과 주장(CausalAssertion)은 노드화되어 근거와 연결된다.</text>')
    s.append("</svg>")
    (FIG/"knowledge_graph.svg").write_text("\n".join(s), encoding="utf-8")


def render_pipeline():
    W, H = 1040, 280
    s = header(W, H, "데이터 파이프라인", "원본 1912년 신문 OCR에서 감사 가능한 인과추론 시연까지")
    stages = [("원본 OCR", "ALTO 90쪽", "#1864ab", "#d0ebff"),
              ("정제", "정규화+로그", "#1098ad", "#c5f6fa"),
              ("기사 분리", "파업 기사", "#0ca678", "#c3fae8"),
              ("코딩", "X/M1/M2/Y1/Y2/Z", "#5f3dc4", "#e5dbff"),
              ("지식\n그래프", "출처 추적", "#a61e4d", "#ffdeeb"),
              ("인과\nDAG", "두 경로", "#e8590c", "#ffe8cc"),
              ("backdoor\ndemo", "Z 보정", "#2b8a3e", "#d3f9d8")]
    n = len(stages); bw, bh = 118, 84
    gap = (W - 60 - n*bw) / (n-1); y = 150
    for i, (name, sub, st, fl) in enumerate(stages):
        x = 30 + i*(bw+gap)
        s.append(f'<rect x="{x}" y="{y-bh/2}" width="{bw}" height="{bh}" rx="12" fill="{fl}" stroke="{st}" stroke-width="2.5" filter="url(#shadow)"/>')
        lines = name.split("\n"); ty = y - 6 - (len(lines)-1)*9
        for ln in lines:
            s.append(f'<text x="{x+bw/2}" y="{ty}" text-anchor="middle" font-size="14" font-weight="700" fill="{st}">{ln}</text>'); ty += 18
        s.append(f'<text x="{x+bw/2}" y="{y+26}" text-anchor="middle" font-size="10.5" fill="#495057">{sub}</text>')
        if i < n-1:
            ax = x+bw; s.append(f'<line x1="{ax}" y1="{y}" x2="{ax+gap}" y2="{y}" stroke="#adb5bd" stroke-width="2.4" marker-end="url(#arrow)"/>')
    s.append(f'<text x="{W/2}" y="{H-26}" text-anchor="middle" font-size="12" fill="#868e96">'
             '원본 증거(왼쪽)는 분석 구조와 분리 보존되며, 모든 단계는 기록되고 재현 가능하다.</text>')
    s.append("</svg>")
    (FIG/"data_pipeline.svg").write_text("\n".join(s), encoding="utf-8")


def render_demo():
    top, strata = rf._results()
    y1, y2 = top["Y1_improvement_response"], top["Y2_order_control_response"]
    W, H = 1040, 540
    s = header(W, H, "Demo Backdoor 보정 \u2014 정직한 결과",
               "실제 코퍼스에서 코딩한 합성 시연. 역사적 효과 아님.")
    ax0, ax1 = 90, 470; zero = 360; scale = 1150
    s.append('<text x="280" y="100" text-anchor="middle" font-size="14.5" font-weight="700" fill="#343a40">A. 단순 vs 맥락보정 ATE</text>')
    for v in [0.0, 0.05, 0.10, 0.15, 0.20]:
        gy = zero - v*scale
        s.append(f'<line x1="{ax0}" y1="{gy}" x2="{ax1}" y2="{gy}" stroke="#e9ecef"/>')
        s.append(f'<text x="{ax0-10}" y="{gy+4}" text-anchor="end" font-size="10.5" fill="#adb5bd">{v:.2f}</text>')
    s.append(f'<line x1="{ax0}" y1="{zero}" x2="{ax1}" y2="{zero}" stroke="#495057" stroke-width="1.5"/>')
    groups = [("Y1 개선", y1, "#2b8a3e", "#d3f9d8"), ("Y2 질서통제", y2, "#c92a2a", "#ffe3e3")]
    gw = (ax1-ax0)/2; bw = 78
    for gi, (name, r, st, fl) in enumerate(groups):
        gx = ax0 + gi*gw + gw/2
        for j, (lab, val, fc) in enumerate([("단순", float(r["naive_difference"]), fl),
                                            ("보정", float(r["ATE_demo_adjusted"]), st)]):
            bx = gx - bw - 6 + j*(bw+12); h = val*scale; by = zero - h if h >= 0 else zero
            s.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{abs(h)}" rx="4" fill="{fc}" stroke="{st}" stroke-width="2"/>')
            s.append(f'<text x="{bx+bw/2}" y="{by-8 if h>=0 else by+abs(h)+16}" text-anchor="middle" font-size="12.5" font-weight="700" fill="{st}">{val:+.3f}</text>')
            s.append(f'<text x="{bx+bw/2}" y="{zero+16}" text-anchor="middle" font-size="11" fill="#495057">{lab}</text>')
        s.append(f'<text x="{gx}" y="{zero+40}" text-anchor="middle" font-size="13" font-weight="700" fill="{st}">{name}</text>')
    bx0, bx1 = 600, 980; bzero = 360; bscale = 1150
    s.append('<text x="790" y="100" text-anchor="middle" font-size="14.5" font-weight="700" fill="#343a40">B. 맥락(Z)별 Y1 시위\u2013개선 연관</text>')
    for v in [-0.05, 0.0, 0.05, 0.10, 0.15]:
        gy = bzero - v*bscale
        s.append(f'<line x1="{bx0}" y1="{gy}" x2="{bx1}" y2="{gy}" stroke="#e9ecef"/>')
        s.append(f'<text x="{bx0-10}" y="{gy+4}" text-anchor="end" font-size="10.5" fill="#adb5bd">{v:+.2f}</text>')
    s.append(f'<line x1="{bx0}" y1="{bzero}" x2="{bx1}" y2="{bzero}" stroke="#495057" stroke-width="1.5"/>')
    sd = strata["Y1_improvement_response"]
    order = [("order_focused", "질서중심\n(폭동위주)"), ("mixed", "혼합\n(지역지)"), ("institutional", "제도중심\n(DC/의회)")]
    gw2 = (bx1-bx0)/3; bw2 = 70
    for gi, (zkey, zlab) in enumerate(order):
        val = sd[zkey]; gx = bx0 + gi*gw2 + gw2/2
        st = "#c92a2a" if val < 0 else "#2b8a3e"; fl = "#ffe3e3" if val < 0 else "#d3f9d8"
        h = val*bscale; by = bzero - h if h >= 0 else bzero
        s.append(f'<rect x="{gx-bw2/2}" y="{by}" width="{bw2}" height="{abs(h)}" rx="4" fill="{fl}" stroke="{st}" stroke-width="2"/>')
        s.append(f'<text x="{gx}" y="{by-8 if h>=0 else by+abs(h)+16}" text-anchor="middle" font-size="12" font-weight="700" fill="{st}">{val:+.3f}</text>')
        for k, ln in enumerate(zlab.split("\n")):
            s.append(f'<text x="{gx}" y="{bzero+30+k*14}" text-anchor="middle" font-size="10.5" fill="#495057">{ln}</text>')
    s.append('<rect x="60" y="452" width="920" height="62" rx="10" fill="#fff" stroke="#dee2e6"/>')
    s.append(f'<text x="74" y="476" font-size="12" fill="#343a40" font-weight="600">'
             f'단순 시위\u2013개선 연관은 사실상 0 (+{float(y1["naive_difference"]):.3f}); '
             f'맥락 Z 보정 후에야 약한 연관(+{float(y1["ATE_demo_adjusted"]):.3f})이 나타난다.</text>')
    s.append('<text x="74" y="498" font-size="12" fill="#495057">'
             '폭동위주 맥락에선 오히려 음수(\u20130.033) \u2014 더 많은 시위 프레이밍, 더 적은 개선 프레이밍 \u2014 단순한 \u201c시위 \u2192 진보\u201d 서사를 복잡하게 만든다.</text>')
    s.append("</svg>")
    (FIG/"demo_effect_estimation.svg").write_text("\n".join(s), encoding="utf-8")


if __name__ == "__main__":
    render_pipeline(); render_kg(); render_dag(); render_demo()
    print("Rendered 4 Korean figures into figures/")
