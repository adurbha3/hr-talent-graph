"""A small HR knowledge graph / ontology: typed nodes (Employee, Role, Skill,
Department) and typed edges (HAS_SKILL, REQUIRES_SKILL, BELONGS_TO), built
with networkx so the structure (and the queries below) look like a real
ontology-backed semantic layer, not just a dataframe join.
"""
from __future__ import annotations

import networkx as nx

from talentgraph.synthetic_data import Employee, Role, ROLES, DEPARTMENTS


def employee_node(employee_id: str) -> str:
    return f"Employee:{employee_id}"


def role_node(role_id: str) -> str:
    return f"Role:{role_id}"


def skill_node(skill: str) -> str:
    return f"Skill:{skill}"


def department_node(department: str) -> str:
    return f"Department:{department}"


def build_graph(employees: list[Employee], roles: list[Role] = ROLES) -> nx.DiGraph:
    graph = nx.DiGraph()

    for department in DEPARTMENTS:
        graph.add_node(department_node(department), type="Department", name=department)

    for role in roles:
        graph.add_node(role_node(role.role_id), type="Role", title=role.title, department=role.department)
        graph.add_edge(role_node(role.role_id), department_node(role.department), relation="BELONGS_TO")
        for skill in role.required_skills:
            graph.add_node(skill_node(skill), type="Skill", name=skill)
            graph.add_edge(role_node(role.role_id), skill_node(skill), relation="REQUIRES_SKILL")

    for employee in employees:
        graph.add_node(employee_node(employee.employee_id), type="Employee", name=employee.name)
        graph.add_edge(employee_node(employee.employee_id), department_node(employee.department), relation="BELONGS_TO")
        for skill in employee.skills:
            graph.add_node(skill_node(skill), type="Skill", name=skill)
            graph.add_edge(employee_node(employee.employee_id), skill_node(skill), relation="HAS_SKILL")

    return graph


def employee_skills(graph: nx.DiGraph, employee_id: str) -> set[str]:
    node = employee_node(employee_id)
    return {
        graph.nodes[target]["name"]
        for _, target, data in graph.out_edges(node, data=True)
        if data["relation"] == "HAS_SKILL"
    }


def role_required_skills(graph: nx.DiGraph, role_id: str) -> set[str]:
    node = role_node(role_id)
    return {
        graph.nodes[target]["name"]
        for _, target, data in graph.out_edges(node, data=True)
        if data["relation"] == "REQUIRES_SKILL"
    }


def employees_with_skill(graph: nx.DiGraph, skill: str) -> set[str]:
    """Reverse-traverse HAS_SKILL edges to find every employee who holds a given skill."""
    node = skill_node(skill)
    if node not in graph:
        return set()
    return {
        source.split(":", 1)[1]
        for source, _, data in graph.in_edges(node, data=True)
        if data["relation"] == "HAS_SKILL"
    }
