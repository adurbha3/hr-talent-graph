from talentgraph.recommender import jaccard_similarity, recommend_roles
from talentgraph.synthetic_data import ROLES_BY_ID


def test_jaccard_similarity_identical_sets_is_one():
    s = {"python", "sql"}
    assert jaccard_similarity(s, s) == 1.0


def test_jaccard_similarity_disjoint_sets_is_zero():
    assert jaccard_similarity({"python"}, {"excel"}) == 0.0


def test_jaccard_similarity_empty_sets_is_zero():
    assert jaccard_similarity(set(), set()) == 0.0


def test_recommend_roles_ranks_best_match_first():
    hrbp = ROLES_BY_ID["R-HRBP"]
    employee_skills = set(hrbp.required_skills)  # a perfect match for this role
    recs = recommend_roles(employee_skills, top_k=1)
    assert recs[0].role.role_id == "R-HRBP"
    assert recs[0].score == 1.0


def test_recommend_roles_reports_matched_and_missing_skills():
    recs = recommend_roles({"python", "sql"}, top_k=len(ROLES_BY_ID))
    data_role = next(r for r in recs if r.role.role_id == "R-DATA")
    assert "python" in data_role.matched_skills
    assert "sql" in data_role.matched_skills
    assert "data visualization" in data_role.missing_skills


def test_recommend_roles_respects_top_k():
    recs = recommend_roles({"python"}, top_k=2)
    assert len(recs) == 2
