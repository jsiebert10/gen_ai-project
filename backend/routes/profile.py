from agents.profile_agent import run_profile_agent
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["Agents"])


class ProfileInput(BaseModel):
    """
    Raw student profile input received from the frontend.

    Attributes:
        gpa: Student's GPA as a string (e.g. '3.8/4.0' or '85/100').
        budget: Annual budget as a string (e.g. '30k USD' or '25000').
        risk_tolerance: Student's risk appetite ('low', 'medium', 'high').
        preferred_countries: List of countries the student is interested in.
        field_of_study: Student's intended field (e.g. 'Computer Science').
        education_level: Current level ('bachelor', 'master', 'phd').
    """

    gpa: str
    budget: str
    risk_tolerance: str
    preferred_countries: list[str]
    field_of_study: str
    education_level: str


@router.post("/profile")
def profile_endpoint(input: ProfileInput):
    """
    Standardize a student's raw profile using the Profile Agent.

    Receives raw student data from the frontend, passes it to the
    Profile Agent which uses an LLM to normalize and structure it.

    Args:
        input: Raw student profile data.

    Returns:
        A standardized student profile dictionary.

    Raises:
        HTTPException 500: If the agent fails to process the input.
    """
    try:
        result = run_profile_agent(input.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
