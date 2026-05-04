"""Assembles the LangGraph multi-agent pipeline.

Flow:
    START
      └─► profile_agent           # normalize student profile
            └─► match_agent       # find best-fit programs
                  ├─► visa_agent      ┐
                  ├─► career_agent    ├── parallel superstep
                  └─► testprep_agent  ┘
                        └─► END
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.career_agent import run_career_agent
from agents.match_agent import run_match_agent
from agents.profile_agent import run_profile_agent
from agents.state import GraphState
from agents.testprep_agent import run_testprep_agent
from agents.visa_agent import run_visa_agent


# ---------------------------------------------------------------------------
# Node functions — wrap each existing agent, mapping state fields between stages
# ---------------------------------------------------------------------------

def _profile_node(state: GraphState) -> dict:
    """Map frontend UserProfile fields → profile agent input, run agent."""
    raw = state["raw_input"]
    profile_input = {
        "gpa": str(raw.get("gpa", "")),
        "budget": str(raw.get("annualBudget", "")),
        "risk_tolerance": "medium",
        "preferred_countries": raw.get("targetCountries", []),
        "field_of_study": raw.get("undergraduateMajor", ""),
        "education_level": "bachelor",
    }
    return {"profile": run_profile_agent(profile_input)}


def _match_node(state: GraphState) -> dict:
    """Pass normalized profile directly to match agent."""
    return {"matches": run_match_agent(state["profile"])}


def _visa_node(state: GraphState) -> dict:
    """Build visa agent input from normalized profile."""
    profile = state["profile"]
    raw = state["raw_input"]
    countries = profile.get("preferred_countries") or raw.get("targetCountries") or ["USA"]
    visa_input = {
        "nationality": "international student",
        "destination_country": countries[0],
        "program_start_date": "Fall 2026",
    }
    return {"visa": run_visa_agent(visa_input)}


def _career_node(state: GraphState) -> dict:
    """Build career agent input from normalized profile."""
    profile = state["profile"]
    raw = state["raw_input"]
    countries = profile.get("preferred_countries") or raw.get("targetCountries") or ["USA"]
    career_input = {
        "field_of_study": profile.get("field_of_study") or raw.get("undergraduateMajor", ""),
        "destination_country": countries[0],
        "education_level": profile.get("education_level", "bachelor"),
    }
    return {"career": run_career_agent(career_input)}


def _testprep_node(state: GraphState) -> dict:
    """Build testprep agent input from normalized profile."""
    profile = state["profile"]
    raw = state["raw_input"]
    testprep_input = {
        "gpa": profile.get("gpa_standardized") or raw.get("gpa", 3.0),
        "undergraduate_university": "Current university",
        "field_of_interest": profile.get("field_of_study") or raw.get("undergraduateMajor", ""),
        "current_scores": {},
        "application_deadline": "December 2026",
    }
    return {"testprep": run_testprep_agent(testprep_input)}


# ---------------------------------------------------------------------------
# Graph factory
# ---------------------------------------------------------------------------

def build_graph():
    """Build and compile the consultation StateGraph.

    Node functions are synchronous (they call get_llm_response directly).
    LangGraph's ainvoke() executes them in a thread pool, so visa_agent,
    career_agent, and testprep_agent run concurrently.
    """
    builder = StateGraph(GraphState)

    builder.add_node("profile_agent", _profile_node)
    builder.add_node("match_agent", _match_node)
    builder.add_node("visa_agent", _visa_node)
    builder.add_node("career_agent", _career_node)
    builder.add_node("testprep_agent", _testprep_node)

    # Sequential: START → profile → match
    builder.add_edge(START, "profile_agent")
    builder.add_edge("profile_agent", "match_agent")

    # Fan-out: match feeds three parallel agents
    builder.add_edge("match_agent", "visa_agent")
    builder.add_edge("match_agent", "career_agent")
    builder.add_edge("match_agent", "testprep_agent")

    # Fan-in: END only fires after all three parallel agents complete
    builder.add_edge(["visa_agent", "career_agent", "testprep_agent"], END)

    return builder.compile()
