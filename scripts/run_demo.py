#!/usr/bin/env python
"""End-to-end demo: build the knowledge graph, extract skills from free text,
recommend internal roles for an employee, check eligibility against the
rules engine, and run the fairness audit."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from talentgraph.synthetic_data import generate_employees, ROLES
from talentgraph.ontology import build_graph, employee_skills, employees_with_skill
from talentgraph.skill_extraction import extract_skills
from talentgraph.recommender import recommend_roles
from talentgraph.rules_engine import evaluate_eligibility
from talentgraph.fairness import audit_recommender_fairness


def main() -> None:
    employees = generate_employees(n=200, seed=0)
    graph = build_graph(employees, ROLES)
    print(f"Knowledge graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

    sample = employees[0]
    print(f"\n{sample.name} ({sample.employee_id}) skills via graph query: {sorted(employee_skills(graph, sample.employee_id))}")
    print(f"Employees across the org who know 'python': {len(employees_with_skill(graph, 'python'))}")

    self_assessment = (
        "I have strong Python and SQL skills, some ML experience, and I am comfortable with PPT "
        "and public speaking for stakeholder updates."
    )
    extracted = extract_skills(self_assessment)
    print(f"\nSkills extracted from free text: {extracted}")

    print(f"\nTop role recommendations for {sample.name} (skills: {sorted(sample.skills)}):")
    for rec in recommend_roles(set(sample.skills), top_k=3):
        eligibility = evaluate_eligibility(sample, rec.role)
        status = "ELIGIBLE" if eligibility.eligible else "NOT ELIGIBLE"
        print(f"  {rec.role.title} (score={rec.score:.2f}) [{status}]")
        print(f"    matched: {sorted(rec.matched_skills)}  missing: {sorted(rec.missing_skills)}")
        if not eligibility.eligible:
            for reason in eligibility.failed_rules:
                print(f"    blocked: {reason}")

    print("\nResponsible-AI fairness audit (top recommendation by gender, four-fifths rule):")
    report = audit_recommender_fairness(employees)
    for result in report.results:
        flag = " <-- FLAGGED" if result.flagged else ""
        rates = {g: f"{rate:.2f}" for g, rate in result.selection_rate_by_group.items()}
        print(f"  {result.role_id}: rates={rates} ratio={result.disparate_impact_ratio:.2f}{flag}")


if __name__ == "__main__":
    main()
