"""A responsible-AI fairness audit for the role recommender: checks whether
the top-recommended role differs in rate across a protected attribute group
using the four-fifths (80%) rule from U.S. EEOC adverse-impact guidance, the
standard first-pass screen for selection-rate disparity.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from talentgraph.recommender import recommend_roles
from talentgraph.synthetic_data import Employee, Role, ROLES

FOUR_FIFTHS_THRESHOLD = 0.8


@dataclass
class RoleFairnessResult:
    role_id: str
    selection_rate_by_group: dict[str, float]
    disparate_impact_ratio: float
    flagged: bool


@dataclass
class FairnessReport:
    results: list[RoleFairnessResult]

    @property
    def flagged_roles(self) -> list[RoleFairnessResult]:
        return [r for r in self.results if r.flagged]


def disparate_impact_ratio(selection_rate_by_group: dict[str, float]) -> float:
    """min(group rate) / max(group rate); 1.0 is perfectly even, values below
    the four-fifths threshold are the standard flag for possible adverse impact."""
    rates = [r for r in selection_rate_by_group.values() if r is not None]
    if not rates or max(rates) == 0:
        return 1.0
    return min(rates) / max(rates)


def audit_recommender_fairness(
    employees: list[Employee], roles: list[Role] = ROLES, protected_attribute: str = "gender"
) -> FairnessReport:
    """For each protected-attribute group, compute the fraction of that
    group's members whose top recommendation is each role, then flag any
    role whose disparate impact ratio falls below the four-fifths threshold."""
    group_sizes: dict[str, int] = defaultdict(int)
    role_group_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for employee in employees:
        group = getattr(employee, protected_attribute)
        group_sizes[group] += 1
        top = recommend_roles(set(employee.skills), roles=roles, top_k=1)
        if top:
            role_group_counts[top[0].role.role_id][group] += 1

    results = []
    for role in roles:
        selection_rate_by_group = {
            group: role_group_counts[role.role_id].get(group, 0) / group_sizes[group]
            for group in group_sizes
        }
        ratio = disparate_impact_ratio(selection_rate_by_group)
        results.append(RoleFairnessResult(
            role_id=role.role_id, selection_rate_by_group=selection_rate_by_group,
            disparate_impact_ratio=ratio, flagged=ratio < FOUR_FIFTHS_THRESHOLD,
        ))

    return FairnessReport(results=results)
