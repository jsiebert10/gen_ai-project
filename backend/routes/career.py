from agents.career_agent import run_career_agent
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["Agents"])


class CareerInput(BaseModel):
    """
    Student career outlook inquiry input.

    Attributes:
        field_of_study: Student's intended field (e.g. 'Computer Science').
        destination_country: Country where the student plans to work.
        education_level: Degree level being pursued (bachelor, master, phd).
    """

    field_of_study: str
    destination_country: str
    education_level: str


@router.post("/career")
def career_endpoint(input: CareerInput):
    """
    Provide career outlook based on field of study and target country.

    Receives field of study and destination country, passes it to the
    Career Agent which uses an LLM to return a full job market analysis
    including salaries, top roles, companies and sponsorship trends.

    Args:
        input: Student career inquiry data.

    Returns:
        A dictionary with job market outlook, salaries, top roles,
        companies, sponsorship likelihood and career insights.

    Raises:
        HTTPException 500: If the agent fails to process the input.
    """
    try:
        result = run_career_agent(input.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
