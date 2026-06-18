#!/usr/bin/env python3
"""
Render all project figures for the Lawrence Strike causal-framing project.

This script is designed to run inside the GitHub repository root.
It uses only Python standard-library modules and writes SVG files that GitHub can preview.

Generated figures:
- figures/kg_schema.svg
- figures/knowledge_graph_actual_full.svg
- figures/knowledge_graph_actual_core.svg
- figures/causal_dag.svg
- figures/data_pipeline.svg
- figures/demo_cell_counts.svg
- figures/demo_effect_naive_vs_adjusted.svg
- figures/real_corpus_frame_distribution.svg
- figures/sensitivity_effects.svg

Usage:
    python scripts/render_all_figures.py

Optional:
    python scripts/render_all_figures.py --repo-root .
"""
from __future__ import annotations

import argparse
import csv
import html
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


# -----------------------------------------------------------------------------
# Basic file helpers
# -----------------------------------------------------------------------------

def repo_path(root: Path, *parts: str) -> Path:
    return root.joinpath(*parts)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_csv_dicts(path: Path) -> List[Dict[str, str]]:
    """Read a CSV file as dictionaries.

    The normal repository files are standard CSVs. This helper intentionally keeps
    the parser simple and transparent so that the visualization step remains easy
    to audit. Empty rows are skipped.
    """
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            if row and any((v or "").strip() for v in row.values()):
                rows.append({(k or "").strip(): (v or "").strip() for k, v in row.items()})
        return rows


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


# -----------------------------------------------------------------------------
# SVG helpers
# -----------------------------------------------------------------------------

COLOR = {
    "Issue": "#9BD3F5",
    "Article": "#B7E4F9",
    "Extraction": "#CAB6FF",
    "FramingClaim": "#FFD1E0",
    "AssertedCausalClaim": "#FFB6C7",
    "AnalystAssumption": "#F4B183",
    "SupportingQuote": "#BFE6B8",
    "SourceURL": "#D9D9D9",
    "Person": "#FFE7A8",
    "Organization": "#FFE7A8",
    "Place": "#FFE7A8",
    "Event": "#FFE7A8",
    "confounder": "#97C47F",
    "treatment": "#8DB3E2",
    "mediator": "#C6A0F6",
    "outcome": "#F4B183",
    "default": "#E8E8E8",
}

STROKE = {
    "CONTAINS": "#555555",
    "HAS_EXTRACTION": "#777777",
    "SUPPORTED_BY": "#3B8F3B",
    "REPRESENTED_AS": "#7B61FF",
    "EVIDENCE": "#2E7D32",
    "MENTIONS": "#B8860B",
    "DERIVED_FROM": "#999999",
    "causal_path": "#222222",
    "confounding": "#7B61FF",
    "default": "#888888",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def truncate(text: str, max_len: int = 28) -> str:
    text = str(text or "")
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def svg_start(width: int, height: int) -> List[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial, Helvetica, sans-serif;} .tiny{font-size:10px;} .small{font-size:12px;} .label{font-size:13px;font-weight:600;} .title{font-size:24px;font-weight:700;} .subtitle{font-size:14px;fill:#555;} .legend{font-size:12px;fill:#333;}</style>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#777"/></marker></defs>',
    ]


def svg_end(parts: List[str]) -> str:
    parts.append("</svg>")
    return "\n".join(parts)


def rect_node(parts: List[str], x: float, y: float, w: float, h: float, label: str, fill: str, stroke: str = "#555", radius: int = 10, font_size: int = 12) -> None:
    parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>')
    parts.append(f'<text x="{x + w/2:.1f}" y="{y + h/2 + font_size/3:.1f}" text-anchor="middle" font-size="{font_size}" font-weight="600" fill="#222">{esc(label)}</text>')


def circle_node(parts: List[str], x: float, y: float, r: float, label: str, fill: str, stroke: str = "#555", font_size: int = 9) -> None:
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
    if label:
        parts.append(f'<text x="{x:.1f}" y="{y + r + 12:.1f}" text-anchor="middle" font-size="{font_size}" fill="#222">{esc(label)}</text>')


def line(parts: List[str], x1: float, y1: float, x2: float, y2: float, stroke: str = "#888", width: float = 1.0, opacity: float = 0.55, dashed: bool = False, arrow: bool = True) -> None:
    dash = ' stroke-dasharray="6,5"' if dashed else ""
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width:.1f}" opacity="{opacity:.2f}"{dash}{marker}/>' )


def title(parts: List[str], text: str, subtitle: str | None = None, x: int = 40, y: int = 44) -> None:
    parts.append(f'<text x="{x}" y="{y}" class="title" fill="#1f2937">{esc(text)}</text>')
    if subtitle:
        parts.append(f'<text x="{x}" y="{y + 24}" class="subtitle">{esc(subtitle)}</text>')


def legend(parts: List[str], items: List[Tuple[str, str]], x: int, y: int) -> None:
    for i, (name, color) in enumerate(items):
        yy = y + i * 22
        parts.append(f'<rect x="{x}" y="{yy-11}" width="14" height="14" rx="3" fill="{color}" stroke="#555"/>')
        parts.append(f'<text x="{x+22}" y="{yy}" class="legend">{esc(name)}</text>')


# -----------------------------------------------------------------------------
# Data fallbacks for deterministic reproduction
# -----------------------------------------------------------------------------

DEMO_CELLS = [
    {"Z_context": "order_focused", "X": "1", "n": "30", "Y1_count": "8", "Y1_rate": "0.267", "Y2_count": "24", "Y2_rate": "0.800"},
    {"Z_context": "order_focused", "X": "0", "n": "10", "Y1_count": "3", "Y1_rate": "0.300", "Y2_count": "6", "Y2_rate": "0.600"},
    {"Z_context": "mixed", "X": "1", "n": "44", "Y1_count": "26", "Y1_rate": "0.591", "Y2_count": "22", "Y2_rate": "0.500"},
    {"Z_context": "mixed", "X": "0", "n": "36", "Y1_count": "16", "Y1_rate": "0.444", "Y2_count": "14", "Y2_rate": "0.389"},
    {"Z_context": "institutional", "X": "1", "n": "16", "Y1_count": "13", "Y1_rate": "0.813", "Y2_count": "5", "Y2_rate": "0.313"},
    {"Z_context": "institutional", "X": "0", "n": "24", "Y1_count": "16", "Y1_rate": "0.667", "Y2_count": "6", "Y2_rate": "0.250"},
]

REAL_CORPUS = [
    {"Z_context": "order_focused", "Y1_improvement_units": "0", "Y2_order_control_units": "2", "lean": "order-control"},
    {"Z_context": "mixed", "Y1_improvement_units": "7", "Y2_order_control_units": "3", "lean": "improvement"},
    {"Z_context": "institutional", "Y1_improvement_units": "2", "Y2_order_control_units": "0", "lean": "improvement"},
]

RESULTS = [
    {"outcome": "Y1 improvement", "naive_difference": "0.022", "adjusted_effect": "0.101"},
    {"outcome": "Y2 order-control", "naive_difference": "0.195", "adjusted_effect": "0.121"},
]

SENSITIVITY = [
    {"setting": "baseline", "Y1_improvement_effect": "0.101", "Y2_order_control_effect": "0.121"},
    {"setting": "observed share", "Y1_improvement_effect": "0.124", "Y2_order_control_effect": "0.116"},
    {"setting": "Z 2-level", "Y1_improvement_effect": "0.080", "Y2_order_control_effect": "0.138"},
]


# -----------------------------------------------------------------------------
# Figure 1: data pipeline
# -----------------------------------------------------------------------------

def render_data_pipeline(out: Path) -> None:
    width, height = 1500, 420
    parts = svg_start(width, height)
    title(parts, "데이터 파이프라인", "원문 OCR에서 KG/DAG와 demo adjustment까지 이어지는 분석 흐름")
    steps = [
        ("원문 OCR", "8 issues\n90 pages"),
        ("정제", "cleaned OCR"),
        ("프레이밍 추출", "26 units"),
        ("KG", "nodes/edges"),
        ("DAG", "X, M, Y, Z"),
        ("Backdoor", "Z adjustment"),
        ("해석", "framing effect"),
    ]
    x0, y0, box_w, box_h, gap = 70, 170, 150, 82, 44
    for i, (name, sub) in enumerate(steps):
        x = x0 + i * (box_w + gap)
        fill = ["#E7F0FF", "#E8F7EE", "#FFF2CC", "#EADCF8", "#FCE4D6", "#DDEBF7", "#E2F0D9"][i]
        rect_node(parts, x, y0, box_w, box_h, name, fill, "#4B5563", 14, 14)
        parts.append(f'<text x="{x+box_w/2:.1f}" y="{y0+58:.1f}" text-anchor="middle" font-size="11" fill="#555">{esc(sub)}</text>')
        if i < len(steps)-1:
            line(parts, x+box_w, y0+box_h/2, x+box_w+gap-10, y0+box_h/2, stroke="#4B5563", width=2.0, opacity=0.85)
    parts.append('<text x="70" y="330" class="subtitle">핵심: 실제 역사 전체의 ATE가 아니라, 신문 프레이밍 안에서 Z 보정 전후 해석이 어떻게 달라지는지 확인한다.</text>')
    write_text(out, svg_end(parts))


# -----------------------------------------------------------------------------
# Figure 2: KG schema
# -----------------------------------------------------------------------------

def render_kg_schema(out: Path) -> None:
    width, height = 1200, 560
    parts = svg_start(width, height)
    title(parts, "Knowledge Graph 스키마", "원문 근거와 분석자가 붙인 프레이밍 해석을 분리해서 추적한다")
    nodes = {
        "Issue": (80, 210, 130, 52, COLOR["Issue"]),
        "Article": (280, 210, 150, 52, COLOR["Article"]),
        "Extraction": (520, 210, 150, 52, COLOR["Extraction"]),
        "SupportingQuote": (740, 270, 170, 52, COLOR["SupportingQuote"]),
        "FramingClaim": (735, 150, 170, 52, COLOR["FramingClaim"]),
        "AssertedCausalClaim": (735, 70, 210, 52, COLOR["AssertedCausalClaim"]),
        "AnalystAssumption": (735, 360, 190, 52, COLOR["AnalystAssumption"]),
        "SourceURL": (990, 210, 135, 52, COLOR["SourceURL"]),
    }
    for label, (x, y, w, h, c) in nodes.items():
        rect_node(parts, x, y, w, h, label, c)
    # edges
    def center(k):
        x, y, w, h, _ = nodes[k]
        return x + w/2, y + h/2
    for a,b,rel in [
        ("Issue","Article","CONTAINS"), ("Article","Extraction","HAS_EXTRACTION"),
        ("Extraction","SupportingQuote","SUPPORTED_BY"), ("Extraction","FramingClaim","REPRESENTED_AS"),
        ("Extraction","AssertedCausalClaim","ASSERTED"), ("Extraction","AnalystAssumption","ANALYST MODEL"),
        ("Extraction","SourceURL","DERIVED_FROM"),
    ]:
        x1,y1=center(a); x2,y2=center(b)
        line(parts, x1+55 if a in ["Issue","Article"] else x1, y1, x2-55 if b not in ["FramingClaim", "AssertedCausalClaim", "AnalystAssumption"] else x2-75, y2, STROKE.get(rel,"#777"), 1.7, .85)
        parts.append(f'<text x="{(x1+x2)/2:.1f}" y="{(y1+y2)/2-8:.1f}" text-anchor="middle" font-size="10" fill="#555">{esc(rel)}</text>')
    parts.append('<text x="80" y="480" class="subtitle">이 그림은 설계 스키마이다. 실제 nodes/edges를 렌더링한 그래프는 knowledge_graph_actual_*.svg 파일로 따로 제공한다.</text>')
    write_text(out, svg_end(parts))


# -----------------------------------------------------------------------------
# Figure 3: actual KG full/core
# -----------------------------------------------------------------------------

def normalize_node_type(t: str) -> str:
    return t if t else "Unknown"


def kg_layout(nodes: List[Dict[str,str]], core_only: bool = False) -> Tuple[Dict[str, Tuple[float,float]], int, int, List[Dict[str,str]]]:
    if core_only:
        keep_types = {"Issue", "Article", "Extraction", "FramingClaim", "AssertedCausalClaim", "AnalystAssumption", "SupportingQuote"}
        nodes = [n for n in nodes if normalize_node_type(n.get("type","")) in keep_types]
    type_order = ["Issue", "Article", "Extraction", "FramingClaim", "AssertedCausalClaim", "AnalystAssumption", "SupportingQuote", "Person", "Organization", "Place", "Event", "SourceURL", "Unknown"]
    groups: Dict[str, List[Dict[str,str]]] = defaultdict(list)
    for n in nodes:
        groups[normalize_node_type(n.get("type",""))].append(n)
    present = [t for t in type_order if groups.get(t)]
    width = max(1300, 220 * len(present) + 120)
    max_count = max((len(groups[t]) for t in present), default=1)
    height = max(900, 70 + max_count * 54)
    pos: Dict[str, Tuple[float,float]] = {}
    for ci, t in enumerate(present):
        x = 80 + ci * 215
        items = groups[t]
        n = len(items)
        if n == 1:
            ys = [height/2]
        else:
            top, bottom = 140, height - 120
            step = (bottom - top) / max(n-1, 1)
            ys = [top + i*step for i in range(n)]
        for item, y in zip(items, ys):
            pos[item.get("id","")] = (x, y)
    return pos, width, height, nodes


def render_actual_kg(nodes_path: Path, edges_path: Path, out: Path, core_only: bool = False) -> None:
    nodes = read_csv_dicts(nodes_path)
    edges = read_csv_dicts(edges_path)
    if not nodes or not edges:
        # Draw a warning placeholder rather than failing silently.
        parts = svg_start(1000, 400)
        title(parts, "Actual Knowledge Graph", "graph/nodes.csv 또는 graph/edges.csv를 읽을 수 없습니다")
        parts.append('<text x="60" y="160" font-size="16" fill="#555">Run this script from the repository root after confirming graph/nodes.csv and graph/edges.csv exist.</text>')
        write_text(out, svg_end(parts))
        return
    pos, width, height, shown_nodes = kg_layout(nodes, core_only=core_only)
    shown_ids = set(pos)
    parts = svg_start(width, height)
    subtitle = "실제 graph/nodes.csv와 graph/edges.csv에서 렌더링한 core evidence graph" if core_only else "실제 graph/nodes.csv와 graph/edges.csv에서 렌더링한 full evidence graph"
    title(parts, "실제 Knowledge Graph 시각화", subtitle)
    # type column labels
    type_counts = Counter(normalize_node_type(n.get("type","")) for n in shown_nodes)
    # group x positions by type from pos
    type_x = {}
    for n in shown_nodes:
        nid, t = n.get("id",""), normalize_node_type(n.get("type",""))
        if nid in pos and t not in type_x:
            type_x[t] = pos[nid][0]
    for t, x in type_x.items():
        parts.append(f'<text x="{x:.1f}" y="110" text-anchor="middle" font-size="13" font-weight="700" fill="#333">{esc(t)} ({type_counts[t]})</text>')
    # edges first
    for e in edges:
        s, tgt = e.get("source", ""), e.get("target", "")
        if s in pos and tgt in pos:
            x1, y1 = pos[s]; x2, y2 = pos[tgt]
            rel = e.get("relationship") or e.get("edge_type") or "default"
            stroke = STROKE.get(rel, STROKE["default"])
            opacity = 0.30 if not core_only else 0.42
            line(parts, x1, y1, x2, y2, stroke=stroke, width=1.0, opacity=opacity, dashed=(rel == "DERIVED_FROM"), arrow=True)
    # nodes
    for n in shown_nodes:
        nid = n.get("id", "")
        if nid not in pos:
            continue
        x, y = pos[nid]
        t = normalize_node_type(n.get("type", ""))
        fill = COLOR.get(t, COLOR["default"])
        label = nid if t in {"Extraction", "SupportingQuote", "FramingClaim", "AssertedCausalClaim", "AnalystAssumption"} else truncate(n.get("label", nid), 19)
        if t in {"Issue", "Article"}:
            rect_node(parts, x-62, y-18, 124, 36, label, fill, font_size=10)
        else:
            circle_node(parts, x, y, 12, label, fill, font_size=8)
    # legend and footer
    items = [("Issue", COLOR["Issue"]), ("Article", COLOR["Article"]), ("Extraction", COLOR["Extraction"]), ("Claim", COLOR["FramingClaim"]), ("Quote", COLOR["SupportingQuote"]), ("Entity", COLOR["Organization"])]
    legend(parts, items, width-210, 50)
    parts.append(f'<text x="40" y="{height-45}" class="subtitle">Rendered from: {esc(str(nodes_path))} and {esc(str(edges_path))}. Nodes shown: {len(shown_nodes)} / edges file rows: {len(edges)}.</text>')
    write_text(out, svg_end(parts))


# -----------------------------------------------------------------------------
# Figure 4: DAG
# -----------------------------------------------------------------------------

def render_dag(dag_nodes_path: Path, dag_edges_path: Path, out: Path) -> None:
    nodes = read_csv_dicts(dag_nodes_path)
    edges = read_csv_dicts(dag_edges_path)
    labels = {n.get("id",""): n.get("label", n.get("id","")) for n in nodes}
    types = {n.get("id",""): n.get("type", "default") for n in nodes}
    if not labels:
        labels = {"Z":"Contextual confounders", "X":"Protest pressure framing", "M1":"Demand-legitimacy framing", "Y1":"Improvement response", "M2":"Disorder/conflict framing", "Y2":"Order-control response"}
        types = {"Z":"confounder", "X":"treatment", "M1":"mediator", "Y1":"outcome", "M2":"mediator", "Y2":"outcome"}
        edges = [
            {"source":"Z","target":"X","edge_type":"confounding"}, {"source":"Z","target":"M1","edge_type":"confounding"}, {"source":"Z","target":"Y1","edge_type":"confounding"}, {"source":"Z","target":"M2","edge_type":"confounding"}, {"source":"Z","target":"Y2","edge_type":"confounding"},
            {"source":"X","target":"M1","edge_type":"causal_path"}, {"source":"M1","target":"Y1","edge_type":"causal_path"}, {"source":"X","target":"M2","edge_type":"causal_path"}, {"source":"M2","target":"Y2","edge_type":"causal_path"},
        ]
    width, height = 1200, 720
    parts = svg_start(width, height)
    title(parts, "Causal DAG", "개선 경로와 질서 통제 경로, 그리고 신문 맥락 Z의 보정 역할")
    pos = {"Z": (590, 145), "X": (170, 360), "M1": (470, 265), "Y1": (840, 265), "M2": (470, 465), "Y2": (840, 465)}
    # edges behind
    for e in edges:
        s, t = e.get("source",""), e.get("target","")
        if s in pos and t in pos:
            rel = e.get("edge_type") or e.get("relationship") or "default"
            x1,y1=pos[s]; x2,y2=pos[t]
            line(parts, x1, y1, x2, y2, stroke=STROKE.get(rel, "#777"), width=2.0 if rel=="causal_path" else 1.6, opacity=.85 if rel=="causal_path" else .55, dashed=(rel=="confounding"), arrow=True)
    # nodes
    for nid, (x,y) in pos.items():
        fill = COLOR.get(types.get(nid,"default"), COLOR["default"])
        rect_node(parts, x-95, y-30, 190, 60, f"{nid} · {truncate(labels.get(nid,nid), 22)}", fill, "#4B5563", 16, 12)
    parts.append('<text x="70" y="635" class="subtitle">실선: X에서 outcome으로 이어지는 해석 경로 / 점선: Z가 X·M·Y에 영향을 줄 수 있는 confounding path</text>')
    write_text(out, svg_end(parts))


# -----------------------------------------------------------------------------
# Bar chart helpers
# -----------------------------------------------------------------------------

def bar_chart_svg(out: Path, title_text: str, subtitle_text: str, data: List[Dict[str, str]], x_key: str, series: List[Tuple[str, str]], width: int = 1100, height: int = 620, y_label: str = "value") -> None:
    parts = svg_start(width, height)
    title(parts, title_text, subtitle_text)
    margin = dict(left=90, right=60, top=120, bottom=110)
    plot_w = width - margin["left"] - margin["right"]
    plot_h = height - margin["top"] - margin["bottom"]
    values = []
    for row in data:
        for key, _ in series:
            try:
                values.append(float(row.get(key, 0)))
            except ValueError:
                pass
    max_v = max(values + [1])
    min_v = min(values + [0])
    y_min = min(0, min_v)
    y_max = max_v * 1.15 if max_v > 0 else 1
    if y_min < 0:
        y_min *= 1.15
    def sx(i: int, inner: int, nser: int) -> float:
        group_w = plot_w / max(len(data),1)
        return margin["left"] + i * group_w + group_w * 0.18 + inner * (group_w * 0.64 / max(nser,1))
    def sy(v: float) -> float:
        return margin["top"] + (y_max - v) / (y_max - y_min) * plot_h
    def sh(v: float) -> float:
        return abs(sy(v) - sy(0))
    # grid and zero line
    parts.append(f'<line x1="{margin["left"]}" y1="{sy(0):.1f}" x2="{width-margin["right"]}" y2="{sy(0):.1f}" stroke="#555" stroke-width="1.2"/>')
    for k in range(5):
        v = y_min + k*(y_max-y_min)/4
        yy = sy(v)
        parts.append(f'<line x1="{margin["left"]}" y1="{yy:.1f}" x2="{width-margin["right"]}" y2="{yy:.1f}" stroke="#eee" stroke-width="1"/>')
        parts.append(f'<text x="{margin["left"]-12}" y="{yy+4:.1f}" text-anchor="end" font-size="11" fill="#555">{v:.2f}</text>')
    colors = ["#79A7D3", "#F4A261", "#8BCB88", "#E76F51"]
    nser = len(series)
    for i,row in enumerate(data):
        group_w = plot_w / max(len(data),1)
        bar_w = (group_w * 0.64 / max(nser,1)) * 0.82
        for j,(key,label) in enumerate(series):
            try: v=float(row.get(key,0))
            except ValueError: v=0.0
            x = sx(i,j,nser)
            y = sy(max(v,0)) if v >= 0 else sy(0)
            h = sh(v)
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" rx="4" fill="{colors[j%len(colors)]}" opacity="0.90"/>')
            parts.append(f'<text x="{x+bar_w/2:.1f}" y="{y-7 if v>=0 else y+h+15:.1f}" text-anchor="middle" font-size="10" fill="#333">{v:+.3f}</text>' if abs(v)<1 else f'<text x="{x+bar_w/2:.1f}" y="{y-7:.1f}" text-anchor="middle" font-size="10" fill="#333">{int(v)}</text>')
        parts.append(f'<text x="{margin["left"] + i*group_w + group_w/2:.1f}" y="{height-72}" text-anchor="middle" font-size="12" fill="#333">{esc(row.get(x_key,""))}</text>')
    # legend
    for j,(_,label) in enumerate(series):
        x = margin["left"] + j*180
        y = height - 35
        parts.append(f'<rect x="{x}" y="{y-12}" width="14" height="14" rx="3" fill="{colors[j%len(colors)]}"/>')
        parts.append(f'<text x="{x+21}" y="{y}" class="legend">{esc(label)}</text>')
    parts.append(f'<text x="{margin["left"]}" y="{height-18}" font-size="11" fill="#666">Y-axis: {esc(y_label)}</text>')
    write_text(out, svg_end(parts))


def render_demo_cell_counts(rows: List[Dict[str,str]], out: Path) -> None:
    data = []
    for r in rows:
        data.append({"cell": f'{r["Z_context"]}\nX={r["X"]}', "n": r["n"], "Y1_count": r["Y1_count"], "Y2_count": r["Y2_count"]})
    bar_chart_svg(out, "Demo-coded data cell counts", "Z 맥락별 X=1/X=0 비교 단위와 Y1/Y2 count", data, "cell", [("n", "n units"), ("Y1_count", "Y1 count"), ("Y2_count", "Y2 count")], width=1300, height=650, y_label="count")


def render_real_corpus(rows: List[Dict[str,str]], out: Path) -> None:
    data = [{"context": r["Z_context"], "Y1": r.get("Y1_improvement_units", r.get("Y1", "0")), "Y2": r.get("Y2_order_control_units", r.get("Y2", "0"))} for r in rows]
    bar_chart_svg(out, "Real-corpus framing distribution", "실제 26개 extraction에서 관찰한 Y1/Y2 분포", data, "context", [("Y1", "Y1 improvement"), ("Y2", "Y2 order-control")], width=1050, height=620, y_label="units")


def render_demo_effect(rows: List[Dict[str,str]], out: Path) -> None:
    data = []
    for r in rows:
        data.append({"outcome": r.get("outcome", ""), "naive": r.get("naive_difference", "0"), "adjusted": r.get("adjusted_effect", "0")})
    bar_chart_svg(out, "Naive vs adjusted demo effect", "신문 맥락 Z를 보정하기 전과 후의 framing effect 비교", data, "outcome", [("naive", "Naive"), ("adjusted", "Adjusted")], width=1050, height=620, y_label="effect size")


def render_sensitivity(rows: List[Dict[str,str]], out: Path) -> None:
    data = [{"setting": r["setting"], "Y1": r["Y1_improvement_effect"], "Y2": r["Y2_order_control_effect"]} for r in rows]
    bar_chart_svg(out, "Sensitivity checks", "Z 가중치와 Z 범주 설정을 바꿔도 방향이 유지되는지 확인", data, "setting", [("Y1", "Y1 improvement"), ("Y2", "Y2 order-control")], width=1100, height=620, y_label="effect size")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".", help="Repository root. Default: current directory")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    figures = repo_path(root, "figures")
    ensure_dir(figures)

    # input paths
    nodes_path = repo_path(root, "graph", "nodes.csv")
    edges_path = repo_path(root, "graph", "edges.csv")
    dag_nodes_path = repo_path(root, "graph", "dag_nodes.csv")
    dag_edges_path = repo_path(root, "graph", "dag_edges.csv")

    # fallback-aware rows
    demo_rows = read_csv_dicts(repo_path(root, "data", "curated", "demo_cell_counts.csv")) or DEMO_CELLS
    real_rows = read_csv_dicts(repo_path(root, "outputs", "real_corpus_frame_distribution_polished.csv")) or read_csv_dicts(repo_path(root, "outputs", "real_corpus_cooccurrence.csv")) or REAL_CORPUS
    result_rows = read_csv_dicts(repo_path(root, "outputs", "results_summary_polished.csv")) or read_csv_dicts(repo_path(root, "outputs", "demo_backdoor_adjustment_results.csv")) or RESULTS
    sens_rows = read_csv_dicts(repo_path(root, "outputs", "sensitivity_effects_polished.csv")) or SENSITIVITY

    # render all figures
    render_data_pipeline(repo_path(root, "figures", "data_pipeline.svg"))
    render_kg_schema(repo_path(root, "figures", "kg_schema.svg"))
    render_actual_kg(nodes_path, edges_path, repo_path(root, "figures", "knowledge_graph_actual_full.svg"), core_only=False)
    render_actual_kg(nodes_path, edges_path, repo_path(root, "figures", "knowledge_graph_actual_core.svg"), core_only=True)
    render_dag(dag_nodes_path, dag_edges_path, repo_path(root, "figures", "causal_dag.svg"))
    render_demo_cell_counts(demo_rows, repo_path(root, "figures", "demo_cell_counts.svg"))
    render_real_corpus(real_rows, repo_path(root, "figures", "real_corpus_frame_distribution.svg"))
    render_demo_effect(result_rows, repo_path(root, "figures", "demo_effect_naive_vs_adjusted.svg"))
    render_sensitivity(sens_rows, repo_path(root, "figures", "sensitivity_effects.svg"))

    print("Rendered figures to:", figures)
    for name in [
        "data_pipeline.svg", "kg_schema.svg", "knowledge_graph_actual_full.svg", "knowledge_graph_actual_core.svg",
        "causal_dag.svg", "demo_cell_counts.svg", "real_corpus_frame_distribution.svg",
        "demo_effect_naive_vs_adjusted.svg", "sensitivity_effects.svg",
    ]:
        print(" -", figures / name)


if __name__ == "__main__":
    main()
