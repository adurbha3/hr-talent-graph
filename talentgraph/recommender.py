"""A content-based internal-role recommender: scores every role by how well
an employee's skill set overlaps with the role's required skills (Jaccard
similarity over skill sets), ranked highest first.
"""
from __future__ import annotations

from dataclasses import dataclass

from talentgraph.synthetic_data import Role, ROLES


@dataclass
class RoleRecommendation:
    role: Role
    score: float
    matched_skills: set[str]
    missing_skills: set[str]


def jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def recommend_roles(
    employee_skills: set[str], roles: list[Role] = ROLES, top_k: int = 3
) -> list[RoleRecommendation]:
    scored = []
    for role in roles:
        required = set(role.required_skills)
        score = jaccard_similarity(employee_skills, required)
        scored.append(RoleRecommendation(
            role=role, score=score,
            matched_skills=employee_skills & required,
            missing_skills=required - employee_skills,
        ))
    scored.sort(key=lambda r: r.score, reverse=True)
    return scored[:top_k]
