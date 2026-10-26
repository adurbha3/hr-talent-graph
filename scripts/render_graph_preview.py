#!/usr/bin/env python
"""Render a small subgraph of the knowledge graph (a handful of employees,
roles, and skills) as a PNG, so the ontology's structure is visible, not
just its query results."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from talentgraph.synthetic_data import generate_employees, ROLES
from talentgraph.ontology import build_graph


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-employees", type=int, default=2)
    parser.add_argument("--n-roles", type=int, default=3)
    parser.add_argument("--seed", type=int, default=6)
    parser.add_argument("--out", type=str, default="assets/graph_preview.png")
    args = parser.parse_args()

    employees = generate_employees(n=args.n_employees, seed=args.seed)
    graph = build_graph(employees, ROLES[: args.n_roles])

    color_by_type = {"Employee": "#2563eb", "Role": "#16a34a", "Skill": "#f59e0b", "Department": "#6b7280"}
    node_colors = [color_by_type[graph.nodes[n]["type"]] for n in graph.nodes]
    labels = {n: graph.nodes[n].get("name") or graph.nodes[n].get("title") or n.split(":", 1)[1] for n in graph.nodes}

    fig, ax = plt.subplots(figsize=(12, 9))
    pos = nx.spring_layout(graph, seed=7, k=1.3, iterations=200)
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=1400, ax=ax)
    nx.draw_networkx_edges(graph, pos, alpha=0.35, arrows=True, ax=ax, connectionstyle="arc3,rad=0.05")
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8, ax=ax)
    ax.set_title("TalentGraph: a small slice of the employee / role / skill knowledge graph")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(args.out, dpi=150)
    print(f"Saved preview to {args.out}")


if __name__ == "__main__":
    main()
