from talentgraph.fairness import disparate_impact_ratio, audit_recommender_fairness, FOUR_FIFTHS_THRESHOLD
from talentgraph.synthetic_data import generate_employees


def test_disparate_impact_ratio_equal_rates_is_one():
    assert disparate_impact_ratio({"F": 0.3, "M": 0.3}) == 1.0


def test_disparate_impact_ratio_unequal_rates():
    ratio = disparate_impact_ratio({"F": 0.2, "M": 0.4})
    assert abs(ratio - 0.5) < 1e-9


def test_disparate_impact_ratio_handles_all_zero_rates():
    assert disparate_impact_ratio({"F": 0.0, "M": 0.0}) == 1.0


def test_audit_runs_over_synthetic_population_and_flags_consistently():
    employees = generate_employees(n=300, seed=0)
    report = audit_recommender_fairness(employees)
    assert len(report.results) > 0
    for result in report.results:
        assert result.flagged == (result.disparate_impact_ratio < FOUR_FIFTHS_THRESHOLD)
        assert set(result.selection_rate_by_group.keys()) == {"F", "M"}
