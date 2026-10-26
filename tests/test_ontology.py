from talentgraph.synthetic_data import generate_employees, ROLES
from talentgraph.ontology import build_graph, employee_skills, role_required_skills, employees_with_skill


def test_build_graph_includes_every_employee_role_and_department():
    employees = generate_employees(n=5, seed=0)
    graph = build_graph(employees, ROLES)
    for employee in employees:
        assert f"Employee:{employee.employee_id}" in graph
    for role in ROLES:
        assert f"Role:{role.role_id}" in graph


def test_employee_skills_matches_source_data():
    employees = generate_employees(n=5, seed=1)
    graph = build_graph(employees, ROLES)
    for employee in employees:
        assert employee_skills(graph, employee.employee_id) == set(employee.skills)


def test_role_required_skills_matches_source_data():
    graph = build_graph(generate_employees(n=5, seed=2), ROLES)
    for role in ROLES:
        assert role_required_skills(graph, role.role_id) == set(role.required_skills)


def test_employees_with_skill_finds_every_matching_employee():
    employees = generate_employees(n=50, seed=3)
    graph = build_graph(employees, ROLES)
    expected = {e.employee_id for e in employees if "python" in e.skills}
    assert employees_with_skill(graph, "python") == expected


def test_employees_with_skill_returns_empty_set_for_unknown_skill():
    graph = build_graph(generate_employees(n=5, seed=4), ROLES)
    assert employees_with_skill(graph, "underwater basket weaving") == set()
