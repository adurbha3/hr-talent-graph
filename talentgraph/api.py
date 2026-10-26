"""A small FastAPI deployment of the recommender, skill extractor, and
fairness audit -- the "cloud & API integration for deploying AI models"
half of this project, not just notebooks."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from talentgraph.fairness import audit_recommender_fairness
from talentgraph.recommender import recommend_roles
from talentgraph.rules_engine import evaluate_eligibility
from talentgraph.skill_extraction import extract_skills
from talentgraph.synthetic_data import generate_employees, ROLES_BY_ID

app = FastAPI(title="TalentGraph API")
_employees = {e.employee_id: e for e in generate_employees(n=200, seed=0)}


class SkillExtractionRequest(BaseModel):
    text: str


class SkillExtractionResponse(BaseModel):
    skills: list[str]


class RoleRecommendationResponse(BaseModel):
    role_id: str
    title: str
    score: float
    matched_skills: list[str]
    missing_skills: list[str]
    eligible: bool
    failed_rules: list[str]


@app.post("/skills/extract", response_model=SkillExtractionResponse)
def extract(request: SkillExtractionRequest) -> SkillExtractionResponse:
    return SkillExtractionResponse(skills=extract_skills(request.text))


@app.get("/employees/{employee_id}/recommendations", response_model=list[RoleRecommendationResponse])
def recommendations(employee_id: str, top_k: int = 3) -> list[RoleRecommendationResponse]:
    employee = _employees.get(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail=f"unknown employee_id {employee_id!r}")

    recs = recommend_roles(set(employee.skills), top_k=top_k)
    response = []
    for rec in recs:
        eligibility = evaluate_eligibility(employee, rec.role)
        response.append(RoleRecommendationResponse(
            role_id=rec.role.role_id, title=rec.role.title, score=rec.score,
            matched_skills=sorted(rec.matched_skills), missing_skills=sorted(rec.missing_skills),
            eligible=eligibility.eligible, failed_rules=eligibility.failed_rules,
        ))
    return response


@app.get("/fairness/report")
def fairness_report() -> dict:
    report = audit_recommender_fairness(list(_employees.values()))
    return {
        "roles": [
            {
                "role_id": r.role_id,
                "selection_rate_by_group": r.selection_rate_by_group,
                "disparate_impact_ratio": r.disparate_impact_ratio,
                "flagged": r.flagged,
            }
            for r in report.results
        ],
        "flagged_role_ids": [r.role_id for r in report.flagged_roles],
    }
