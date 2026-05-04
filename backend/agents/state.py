"""Shared LangGraph state for the multi-agent pipeline."""
from __future__ import annotations

from typing import Any, TypedDict


class GraphState(TypedDict):
    # ── Input ──────────────────────────────────────────────────────────
    raw_input: dict[str, Any]      # UserProfile from frontend (camelCase)

    # ── Stage 1: profile_agent ─────────────────────────────────────────
    profile: dict[str, Any]
    # keys: gpa_standardized, budget_usd, risk_tolerance,
    #       preferred_countries, field_of_study, education_level

    # ── Stage 2: match_agent ───────────────────────────────────────────
    matches: dict[str, Any]
    # keys: matches (list), total_matches (int)

    # ── Stage 3: parallel ─────────────────────────────────────────────
    visa: dict[str, Any]
    # keys: visa_type, destination_country, required_documents,
    #       processing_time, application_fee_usd, tips, warning

    career: dict[str, Any]
    # keys: field, country, job_market_outlook, average_salary_usd,
    #       top_roles, top_companies, sponsorship_likelihood,
    #       in_demand_skills, timeline_to_employment, insight

    testprep: dict[str, Any]
    # keys: target_programs, gap_analysis, critical_path,
    #       resources, urgency_flag, summary
