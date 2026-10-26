"""A small declarative eligibility rules engine: each rule is a named,
independently testable predicate over an (employee, role) pair, run as a
batch to decide whether a recommended role is one the employee can actually
move into today -- the kind of hard business-rule layer that sits beside,
not instead of, a similarity-based recommender.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from talentgraph.synthetic_data import Employee, Role


@dataclass
class Rule:
    name: str
    predicate: Callable[[Employee, Role], bool]
    failure_message: Callable[[Employee, Role], str]


def _check_experience(employee: Employee, role: Role) -> bool:
    return employee.experience_years >= role.min_experience_years


def _check_certifications(employee: Employee, role: Role) -> bool:
    return set(role.required_certifications).issubset(set(employee.certifications))


RULES: list[Rule] = [
    Rule(
        name="minimum_experience",
        predicate=_check_experience,
        failure_message=lambda e, r: (
            f"requires {r.min_experience_years}+ years of experience, "
            f"employee has {e.experience_years}"
        ),
    ),
    Rule(
        name="required_certifications",
        predicate=_check_certifications,
        failure_message=lambda e, r: (
            f"requires certification(s) {sorted(r.required_certifications)}, "
            f"employee holds {sorted(e.certifications)}"
        ),
    ),
]


@dataclass
class EligibilityResult:
    eligible: bool
    failed_rules: list[str]


def evaluate_eligibility(employee: Employee, role: Role, rules: list[Rule] = RULES) -> EligibilityResult:
    failures = [rule.failure_message(employee, role) for rule in rules if not rule.predicate(employee, role)]
    return EligibilityResult(eligible=not failures, failed_rules=failures)
