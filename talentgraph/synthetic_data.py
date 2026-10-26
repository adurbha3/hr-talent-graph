"""Seeded synthetic HR data: skills, internal roles with requirements, and a
fictional employee roster (skills, experience, certifications, and a
synthetic demographic attribute used only for the fairness audit).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

SKILLS = [
    "python", "sql", "data analysis", "machine learning", "project management",
    "public speaking", "payroll systems", "benefits administration", "recruiting",
    "labor law compliance", "conflict resolution", "excel", "powerpoint",
    "process improvement", "customer service", "negotiation", "coaching",
    "data visualization", "cloud platforms", "api integration",
]

DEPARTMENTS = ["People Operations", "Technology", "Client Services", "Compliance", "Sales"]


@dataclass
class Role:
    role_id: str
    title: str
    department: str
    required_skills: list[str]
    min_experience_years: int
    required_certifications: list[str] = field(default_factory=list)


ROLES = [
    Role("R-HRBP", "HR Business Partner", "People Operations",
         ["recruiting", "labor law compliance", "conflict resolution", "coaching"], 3, ["PHR"]),
    Role("R-DATA", "People Analytics Associate", "Technology",
         ["python", "sql", "data analysis", "data visualization"], 1, []),
    Role("R-PAYROLL", "Payroll Specialist", "People Operations",
         ["payroll systems", "labor law compliance", "excel"], 2, ["FPC"]),
    Role("R-ML", "AI Solutions Associate", "Technology",
         ["python", "machine learning", "cloud platforms", "api integration"], 1, []),
    Role("R-CS", "Client Success Associate", "Client Services",
         ["customer service", "negotiation", "public speaking", "process improvement"], 0, []),
    Role("R-COMP", "Compliance Analyst", "Compliance",
         ["labor law compliance", "data analysis", "process improvement"], 2, ["PHR"]),
    Role("R-SALES", "Benefits Sales Associate", "Sales",
         ["benefits administration", "negotiation", "public speaking", "customer service"], 1, []),
]

ROLES_BY_ID = {r.role_id: r for r in ROLES}

CERTIFICATIONS = ["PHR", "FPC", "SHRM-CP", "PMP"]

FIRST_NAMES = ["Jordan", "Alex", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn", "Reese", "Jamie"]
LAST_NAMES = ["Nguyen", "Garcia", "Okafor", "Smith", "Patel", "Kim", "Johnson", "Rossi", "Haddad", "Novak"]


@dataclass
class Employee:
    employee_id: str
    name: str
    department: str
    skills: list[str]
    experience_years: int
    certifications: list[str]
    gender: str  # synthetic attribute, fictional employees only, used solely for the fairness audit


def generate_employees(n: int = 200, seed: int | None = None) -> list[Employee]:
    rng = np.random.default_rng(seed)
    employees = []
    for i in range(n):
        # np.random.Generator.choice returns numpy str_ scalars, not plain str;
        # cast everything back to str so Employee fields serialize and print cleanly.
        name = f"{str(rng.choice(FIRST_NAMES))} {str(rng.choice(LAST_NAMES))}"
        department = str(rng.choice(DEPARTMENTS))
        n_skills = int(rng.integers(3, 8))
        skills = [str(s) for s in rng.choice(SKILLS, size=n_skills, replace=False)]
        experience_years = int(rng.integers(0, 15))
        n_certs = int(rng.integers(0, 3))
        certifications = [str(c) for c in rng.choice(CERTIFICATIONS, size=n_certs, replace=False)] if n_certs else []
        gender = str(rng.choice(["F", "M"], p=[0.5, 0.5]))
        employees.append(Employee(
            employee_id=f"E-{i:04d}", name=name, department=department, skills=skills,
            experience_years=experience_years, certifications=certifications, gender=gender,
        ))
    return employees
