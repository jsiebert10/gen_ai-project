from agents.match_agent import run_match_agent
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["Agents"])


class MatchInput(BaseModel):
    """
    Standardized student profile used to find university matches.
    This is typically the output from the Profile Agent.

    Attributes:
        gpa_standardized: GPA on a 4.0 scale.
        budget_usd: Annual budget in USD.
        risk_tolerance: Student's risk appetite (low, medium, high).
        preferred_countries: List of countries the student is interested in.
        field_of_study: Student's intended field of study.
        education_level: Current level (bachelor, master, phd).
    """

    gpa_standardized: float
    budget_usd: int
    risk_tolerance: str
    preferred_countries: list[str]
    field_of_study: str
    education_level: str


@router.post("/match")
def match_endpoint(input: MatchInput):
    """
    Find university program matches based on a standardized student profile.

    Receives a standardized profile and passes it to the Match Agent
    which uses an LLM to find and rank the best fitting programs.

    Args:
        input: Standardized student profile data.

    Returns:
        A dictionary with ranked university matches and total count.

    Raises:
        HTTPException 500: If the agent fails to process the input.
    """
    try:
        result = run_match_agent(input.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
