"""Maps the final GraphState to the frontend dashboard JSON payload.

Tab mapping (from src/pages/Dashboard.tsx):
  overview   ← stats derived from all agents + activity log
  programs   ← matches list from match_agent
  visa       ← documents, tips, fees from visa_agent
  career     ← job market outlook from career_agent
  test_prep  ← gap analysis and critical path from testprep_agent
"""
from __future__ import annotations

from typing import Any

from agents.state import GraphState


def format_dashboard(state: GraphState) -> dict[str, Any]:
    """Convert final graph state into the frontend dashboard payload."""
    profile  = state.get("profile") or {}
    matches  = state.get("matches") or {}
    visa     = state.get("visa") or {}
    career   = state.get("career") or {}
    testprep = state.get("testprep") or {}
    raw      = state.get("raw_input") or {}

    program_list: list = matches.get("matches") or []
    docs: list = visa.get("required_documents") or []
    strong = sum(1 for p in program_list if p.get("match_score", 0) >= 80)

    return {
        # ── Overview tab ──────────────────────────────────────────────
        "overview": {
            "stats": {
                # → StatCard "Recommended Programs"
                "programs_matched": matches.get("total_matches", len(program_list)),
                "strong_matches": strong,
                # → StatCard "Course Strategy"
                "course_plan_semesters": 4,
                # → StatCard "Visa Roadmap"
                "visa_steps_total": len(docs),
                "visa_steps_completed": 0,
                # → StatCard "Career Outlook"
                "career_employment_rate": _sponsorship_to_pct(
                    career.get("sponsorship_likelihood") or ""
                ),
            },
            "activity": [
                {"label": "Profile standardized", "time": "Just now"},
                {
                    "label": f"{matches.get('total_matches', len(program_list))} programs matched",
                    "time": "1 sec ago",
                },
                {"label": "Visa requirements retrieved", "time": "2 sec ago"},
                {"label": "Career report ready", "time": "3 sec ago"},
            ],
        },

        # ── Programs tab ──────────────────────────────────────────────
        "programs": {
            "query_summary": (
                f"{profile.get('field_of_study') or raw.get('undergraduateMajor', '')} "
                f"programs in "
                f"{', '.join(profile.get('preferred_countries') or raw.get('targetCountries') or [])}"
            ),
            "items": program_list,
        },

        # ── Visa tab ──────────────────────────────────────────────────
        "visa": {
            "visa_type": visa.get("visa_type", ""),
            "destination_country": visa.get("destination_country", ""),
            "required_documents": docs,
            "processing_time": visa.get("processing_time", ""),
            "application_fee_usd": visa.get("application_fee_usd", 0),
            "tips": visa.get("tips") or [],
            "warning": visa.get("warning", ""),
        },

        # ── Career tab ────────────────────────────────────────────────
        "career": {
            "field": career.get("field", profile.get("field_of_study", "")),
            "country": career.get("country", ""),
            "job_market_outlook": career.get("job_market_outlook", ""),
            "average_salary_usd": career.get("average_salary_usd", 0),
            "top_roles": career.get("top_roles") or [],
            "top_companies": career.get("top_companies") or [],
            "sponsorship_likelihood": career.get("sponsorship_likelihood", ""),
            "in_demand_skills": career.get("in_demand_skills") or [],
            "timeline_to_employment": career.get("timeline_to_employment", ""),
            "insight": career.get("insight", ""),
        },

        # ── Test Prep tab ─────────────────────────────────────────────
        "test_prep": {
            "target_programs": testprep.get("target_programs") or [],
            "gap_analysis": testprep.get("gap_analysis") or [],
            "critical_path": testprep.get("critical_path") or [],
            "resources": testprep.get("resources") or [],
            "urgency_flag": testprep.get("urgency_flag", False),
            "summary": testprep.get("summary", ""),
        },
    }


def _sponsorship_to_pct(likelihood: str) -> int:
    """Convert sponsorship_likelihood string to integer % for the Career stat card."""
    mapping = {"very high": 95, "high": 80, "moderate": 60, "low": 35, "very low": 15}
    return mapping.get(likelihood.lower().strip(), 0)
