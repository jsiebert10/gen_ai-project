"""Assembles the LangGraph multi-agent pipeline.

Flow:
    START
      └─► profile_agent
            └─► match_agent
                  ├─► visa_agent      ┐
                  ├─► career_agent    ├── parallel superstep
                  └─► testprep_agent  ┘
                        └─► END
"""

from __future__ import annotations

from datetime import date, datetime

from langgraph.graph import END, START, StateGraph

from agents.career_agent import run_career_agent
from agents.match_agent import run_match_agent
from agents.profile_agent import run_profile_agent
from agents.roadmap_agent import run_roadmap_agent
from agents.state import GraphState
from agents.testprep_agent import run_testprep_agent
from agents.visa_agent import run_visa_agent


def _profile_node(state: GraphState) -> dict:
    raw = state["raw_input"]
    profile_input = {
        "gpa": str(raw.get("gpa", "")),
        "budget": str(raw.get("annualBudget", "")),
        "risk_tolerance": "medium",
        "preferred_countries": raw.get("targetCountries", []),
        "field_of_study": raw.get("undergraduateMajor", ""),
        "areas_of_interest": raw.get("areasOfInterest", []),
        "education_level": "bachelor",
    }
    return {"profile": run_profile_agent(profile_input)}


def _match_node(state: GraphState) -> dict:
    profile = state["profile"]
    raw = state["raw_input"]
    match_input = {
        "gpa_standardized": profile.get("gpa_standardized"),
        "budget_usd": profile.get("budget_usd"),
        "risk_tolerance": profile.get("risk_tolerance"),
        "preferred_countries": profile.get("preferred_countries"),
        "education_level": profile.get("education_level"),
        "areas_of_interest": raw.get("areasOfInterest", []),
        "undergraduate_major": raw.get("undergraduateMajor", ""),
        "dream_career": raw.get("dreamCareer", ""),
    }
    return {"matches": run_match_agent(match_input)}


def _visa_node(state: GraphState) -> dict:
    profile = state["profile"]
    raw = state["raw_input"]
    countries = (
        profile.get("preferred_countries") or raw.get("targetCountries") or ["USA"]
    )
    visa_input = {
        "nationality": "international student",
        "destination_country": countries[0],
        "program_start_date": "Fall 2026",
    }
    return {"visa": run_visa_agent(visa_input)}


def _career_node(state: GraphState) -> dict:
    profile = state["profile"]
    raw = state["raw_input"]
    countries = (
        profile.get("preferred_countries") or raw.get("targetCountries") or ["USA"]
    )
    career_input = {
        "field_of_study": profile.get("field_of_study")
        or raw.get("undergraduateMajor", ""),
        "destination_country": countries[0],
        "education_level": profile.get("education_level", "master"),
        "areas_of_interest": raw.get("areasOfInterest", []),
    }
    return {"career": run_career_agent(career_input)}


def _testprep_node(state: GraphState) -> dict:
    profile = state["profile"]
    raw = state["raw_input"]
    testprep_input = {
        "gpa": profile.get("gpa_standardized") or raw.get("gpa", 3.0),
        "undergraduate_university": "Current university",
        "field_of_interest": profile.get("field_of_study")
        or raw.get("undergraduateMajor", ""),
        "areas_of_interest": raw.get("areasOfInterest", []),
        "current_scores": {},
        "application_deadline": "December 2026",
    }
    return {"testprep": run_testprep_agent(testprep_input)}


def _roadmap_node(state: GraphState) -> dict:
    profile = state["profile"]
    matches = state["matches"]
    raw = state["raw_input"]

    matched_programs = matches.get("matches", [])

    # Calculate urgency in Python — no LLM needed
    urgency = calculate_urgency(matched_programs)

    requires_gre = any(
        m.get("requirements", {}).get("gre_required", False) for m in matched_programs
    )
    requires_gmat = any(
        m.get("requirements", {}).get("gmat_required", False) for m in matched_programs
    )

    roadmap_input = {
        "gpa": profile.get("gpa_standardized", 0),
        "field_of_study": profile.get("field_of_study", ""),
        "matched_programs": matched_programs,
        "current_scores": raw.get("current_scores", {}),
        "requires_gre": requires_gre,
        "requires_gmat": requires_gmat,
        # Pass pre-calculated urgency so LLM focuses on roadmap only
        "days_remaining": urgency["days_remaining"],
        "urgency_level": urgency["urgency_level"],
        "earliest_deadline": urgency["earliest_deadline"],
    }
    return {"roadmap": run_roadmap_agent(roadmap_input)}


def calculate_urgency(matched_programs: list) -> dict:
    """Calculate urgency level based on days remaining to earliest deadline."""
    deadlines = []
    for m in matched_programs:
        deadline = m.get("application_deadline")
        if deadline:
            try:
                parsed = datetime.strptime(deadline, "%B %d, %Y")
                deadlines.append(parsed)
            except ValueError:
                continue

    if not deadlines:
        return {
            "days_remaining": 240,
            "urgency_level": "moderate",
            "earliest_deadline": "Unknown",
        }

    earliest = min(deadlines)
    days_remaining = (earliest.date() - date.today()).days

    if days_remaining > 240:
        level = "low"
    elif days_remaining > 180:
        level = "moderate"
    elif days_remaining > 120:
        level = "high"
    elif days_remaining > 60:
        level = "critical"
    else:
        level = "emergency"

    return {
        "days_remaining": days_remaining,
        "urgency_level": level,
        "earliest_deadline": earliest.strftime("%B %d, %Y"),
    }


def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("profile_agent", _profile_node)
    builder.add_node("match_agent", _match_node)
    builder.add_node("visa_agent", _visa_node)
    builder.add_node("career_agent", _career_node)
    builder.add_node("testprep_agent", _testprep_node)

    builder.add_edge(START, "profile_agent")
    builder.add_edge("profile_agent", "match_agent")
    builder.add_edge("match_agent", "visa_agent")
    builder.add_edge("match_agent", "career_agent")
    builder.add_edge("match_agent", "testprep_agent")
    builder.add_node("roadmap_agent", _roadmap_node)
    builder.add_edge(["visa_agent", "career_agent", "testprep_agent"], "roadmap_agent")
    builder.add_edge("roadmap_agent", END)

    return builder.compile()
