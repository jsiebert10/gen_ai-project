"""Assembles the LangGraph multi-agent pipeline.

Flow:
    START
      └─► profile_agent
            └─► match_agent
                  ├─► visa_agent      ┐
                  ├─► career_agent    │
                  ├─► testprep_agent  ├── parallel superstep
                  └─► roadmap_agent   ┘
                        └─► END
"""

from __future__ import annotations

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
    profile_with_interests = {
        **profile,
        "areas_of_interest": raw.get("areasOfInterest", []),
        "undergraduate_major": raw.get("undergraduateMajor", ""),
    }
    return {"matches": run_match_agent(profile_with_interests)}


def _visa_node(state: GraphState) -> dict:
    profile = state["profile"]
    raw = state["raw_input"]
    countries = (
        profile.get("preferred_countries") or raw.get("targetCountries") or ["USA"]
    )
    visa_input = {
        "nationality": raw.get("nationality") or "international student",
        "destination_country": countries[0],
        "program_start_date": "Fall 2026",
        "field_of_study": profile.get("field_of_study")
        or raw.get("undergraduateMajor", ""),
    }
    return {"visa": run_visa_agent(visa_input)}


def _career_node(state: GraphState) -> dict:
    profile = state["profile"]
    raw = state["raw_input"]
    countries = (
        profile.get("preferred_countries") or raw.get("targetCountries") or ["USA"]
    )
    areas = raw.get("areasOfInterest", [])
    undergraduate = raw.get("undergraduateMajor", "")
    career_input = {
        "field_of_study": ", ".join(areas)
        if areas
        else (profile.get("field_of_study") or undergraduate),
        "destination_country": countries[0],
        "education_level": profile.get("education_level", "master"),
        "areas_of_interest": areas,
        "undergraduate_major": undergraduate,
    }
    return {"career": run_career_agent(career_input)}


def _testprep_node(state: GraphState) -> dict:
    profile = state["profile"]
    raw = state["raw_input"]
    matched_programs = state.get("matches", {}).get("matches", [])
    areas = raw.get("areasOfInterest", [])
    testprep_input = {
        "gpa": profile.get("gpa_standardized") or raw.get("gpa", 3.0),
        "undergraduate_university": "Current university",
        "field_of_interest": ", ".join(areas)
        if areas
        else (profile.get("field_of_study") or raw.get("undergraduateMajor", "")),
        "areas_of_interest": areas,
        "undergraduate_major": raw.get("undergraduateMajor", ""),
        "current_scores": {},
        "application_deadline": "December 2026",
        "matched_programs": matched_programs,
    }
    return {"testprep": run_testprep_agent(testprep_input)}


def _roadmap_node(state: GraphState) -> dict:
    profile = state["profile"]
    raw = state["raw_input"]
    matched_programs = state.get("matches", {}).get("matches", [])
    areas = raw.get("areasOfInterest", [])
    roadmap_input = {
        "gpa": profile.get("gpa_standardized") or raw.get("gpa", 3.0),
        "field_of_study": ", ".join(areas)
        if areas
        else (profile.get("field_of_study") or raw.get("undergraduateMajor", "")),
        "matched_programs": matched_programs,
        "current_scores": {},
        "requires_gre": any(p.get("requires_gre") for p in matched_programs),
        "requires_gmat": any(p.get("requires_gmat") for p in matched_programs),
    }
    return {"roadmap": run_roadmap_agent(roadmap_input)}


def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("profile_agent", _profile_node)
    builder.add_node("match_agent", _match_node)
    builder.add_node("visa_agent", _visa_node)
    builder.add_node("career_agent", _career_node)
    builder.add_node("testprep_agent", _testprep_node)
    builder.add_node("roadmap_agent", _roadmap_node)

    builder.add_edge(START, "profile_agent")
    builder.add_edge("profile_agent", "match_agent")
    builder.add_edge("match_agent", "visa_agent")
    builder.add_edge("match_agent", "career_agent")
    builder.add_edge("match_agent", "testprep_agent")
    builder.add_edge("match_agent", "roadmap_agent")
    builder.add_edge(
        ["visa_agent", "career_agent", "testprep_agent", "roadmap_agent"], END
    )

    return builder.compile()
