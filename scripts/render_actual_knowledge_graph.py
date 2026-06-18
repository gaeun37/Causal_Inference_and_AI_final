#!/usr/bin/env python3
"""Render only the actual Knowledge Graph figures from graph/nodes.csv and graph/edges.csv.

This is a thin wrapper around render_all_figures.py so the KG can be regenerated alone.
Usage:
    python scripts/render_actual_knowledge_graph.py
"""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
mod_path = ROOT / "scripts" / "render_all_figures.py"
spec = importlib.util.spec_from_file_location("render_all_figures", mod_path)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

figures = ROOT / "figures"
figures.mkdir(parents=True, exist_ok=True)
mod.render_actual_kg(ROOT / "graph" / "nodes.csv", ROOT / "graph" / "edges.csv", figures / "knowledge_graph_actual_full.svg", core_only=False)
mod.render_actual_kg(ROOT / "graph" / "nodes.csv", ROOT / "graph" / "edges.csv", figures / "knowledge_graph_actual_core.svg", core_only=True)
mod.render_kg_schema(figures / "kg_schema.svg")
print("Rendered actual KG figures:")
print(" -", figures / "knowledge_graph_actual_full.svg")
print(" -", figures / "knowledge_graph_actual_core.svg")
print(" -", figures / "kg_schema.svg")
