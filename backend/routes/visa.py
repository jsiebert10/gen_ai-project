from agents.visa_agent import run_visa_agent
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["Agents"])


class VisaInput(BaseModel):
    """
    Student visa inquiry input.

    Attributes:
        nationality: Student's citizenship country (e.g. 'Chile', 'India').
        destination_country: Country where the student plans to study.
        program_start_date: When the program begins (e.g. 'September 2026').
    """

    nationality: str
    destination_country: str
    program_start_date: str


@router.post("/visa")
def visa_endpoint(input: VisaInput):
    """
    Provide visa guidance based on student nationality and destination.

    Receives nationality and destination country, passes it to the
    Visa Agent which uses an LLM to return detailed visa requirements,
    documents, processing times and tips.

    Args:
        input: Student visa inquiry data.

    Returns:
        A dictionary with visa type, required documents,
        processing time, fees and tips.

    Raises:
        HTTPException 500: If the agent fails to process the input.
    """
    try:
        result = run_visa_agent(input.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
