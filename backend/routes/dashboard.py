"""Dashboard route — runs the full LangGraph pipeline, returns all tab data."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agents.graph import build_graph
from agents.state import GraphState
from formatters import format_dashboard

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Dashboard"])

_graph = None


def _get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


class DashboardRequest(BaseModel):
    fullName: str
    undergraduateMajor: str
    gpa: float
    dreamCareer: str = ""
    targetCountries: list[str] = Field(default_factory=list)
    annualBudget: int = 30000
    areasOfInterest: list[str] = Field(default_factory=list)


@router.post("/dashboard")
async def run_dashboard(request: DashboardRequest) -> dict:
    raw_input = {
        "fullName": request.fullName,
        "undergraduateMajor": request.undergraduateMajor,
        "gpa": request.gpa,
        "dreamCareer": request.dreamCareer,
        "targetCountries": request.targetCountries,
        "annualBudget": request.annualBudget,
        "areasOfInterest": request.areasOfInterest,
    }

    try:
        graph = _get_graph()
        final_state: GraphState = await graph.ainvoke({"raw_input": raw_input})
    except Exception as exc:
        logger.exception("Pipeline failed for %s", request.fullName)
        raise HTTPException(
            status_code=500, detail=f"Agent pipeline error: {exc}"
        ) from exc

    return format_dashboard(final_state)
