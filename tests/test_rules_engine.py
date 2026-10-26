from talentgraph.rules_engine import evaluate_eligibility
from talentgraph.synthetic_data import Employee, ROLES_BY_ID


def _employee(**overrides) -> Employee:
    defaults = dict(
        employee_id="E-TEST", name="Test Employee", department="People Operations",
        skills=["recruiting", "labor law compliance", "conflict resolution", "coaching"],
        experience_years=5, certifications=["PHR"], gender="F",
    )
    defaults.update(overrides)
    return Employee(**defaults)


def test_eligible_employee_passes_all_rules():
    employee = _employee()
    result = evaluate_eligibility(employee, ROLES_BY_ID["R-HRBP"])
    assert result.eligible
    assert result.failed_rules == []


def test_insufficient_experience_fails_rule():
    employee = _employee(experience_years=1)
    result = evaluate_eligibility(employee, ROLES_BY_ID["R-HRBP"])
    assert not result.eligible
    assert any("experience" in msg for msg in result.failed_rules)


def test_missing_certification_fails_rule():
    employee = _employee(certifications=[])
    result = evaluate_eligibility(employee, ROLES_BY_ID["R-HRBP"])
    assert not result.eligible
    assert any("certification" in msg for msg in result.failed_rules)


def test_role_with_no_requirements_is_always_eligible_on_those_rules():
    employee = _employee(experience_years=0, certifications=[])
    result = evaluate_eligibility(employee, ROLES_BY_ID["R-CS"])
    assert result.eligible
