"""Service layer for querying the U.S. College Scorecard SQLite database."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "programs.db"


def get_candidate_programs(
    field_of_study: str = "",
    areas_of_interest: list[str] | None = None,
    budget_usd: int | None = None,
    gpa: float | None = None,
) -> list[dict[str, Any]]:
    """Query programs.db for programs matching the student's profile."""
    if not DB_PATH.exists():
        return []

    areas = areas_of_interest or []
    search_terms = ([field_of_study] + areas) if field_of_study else areas

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    try:
        if not search_terms:
            rows = conn.execute("""
                SELECT p.program_id, p.university, p.program_name, p.field, p.country,
                       p.tuition_usd_total, p.duration_months, p.description, p.url,
                       r.toefl_min, r.ielts_min, r.gre_required, r.gre_min_quant,
                       r.gmat_required, r.gmat_min, r.min_gpa,
                       r.letters_of_recommendation,
                       r.application_deadline_fall, r.application_deadline_spring
                FROM masters_programs p
                JOIN program_requirements r USING (program_id)
                ORDER BY p.tuition_usd_total ASC
            """).fetchall()
        else:
            clauses = []
            params = []
            for term in search_terms:
                for col in ("p.program_name", "p.field", "p.description"):
                    clauses.append(f"{col} LIKE ?")
                    params.append(f"%{term}%")
            where = " OR ".join(clauses)
            rows = conn.execute(f"""
                SELECT p.program_id, p.university, p.program_name, p.field, p.country,
                       p.tuition_usd_total, p.duration_months, p.description, p.url,
                       r.toefl_min, r.ielts_min, r.gre_required, r.gre_min_quant,
                       r.gmat_required, r.gmat_min, r.min_gpa,
                       r.letters_of_recommendation,
                       r.application_deadline_fall, r.application_deadline_spring
                FROM masters_programs p
                JOIN program_requirements r USING (program_id)
                WHERE {where}
                ORDER BY p.tuition_usd_total ASC
            """, params).fetchall()
    finally:
        conn.close()

    programs = []
    for row in rows:
        prog = _row_to_dict(row)
        prog["application_deadline_fall"] = _add_year(
            prog.get("application_deadline_fall"), 2026
        )
        prog["application_deadline_spring"] = _add_year(
            prog.get("application_deadline_spring"), 2027
        )
        programs.append(prog)

    return programs


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    for key in ("gre_required", "gmat_required"):
        if key in d and d[key] is not None:
            d[key] = bool(d[key])
    return d


def _add_year(deadline: str | None, year: int) -> str:
    if not deadline or deadline.strip().lower() in ("", "rolling", "no spring admission"):
        return deadline or ""
    if any(str(y) in deadline for y in range(2024, 2030)):
        return deadline
    return f"{deadline.strip()}, {year}"
