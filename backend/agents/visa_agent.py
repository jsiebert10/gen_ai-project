import json

from agents.llm_client import get_llm_response
from services.rag_service import retrieve_visa_context

RAG_SYSTEM_PROMPT = """
You are a visa guidance assistant for international students.
You will receive REAL visa documentation excerpts retrieved from official
USCIS and government sources, along with the student's details.

Use the provided documentation to give accurate, fact-based visa guidance.
Where the documents provide specific details (fees, documents, timelines),
use those exact figures. Only supplement with your general knowledge where
the retrieved documents do not cover a topic.

Respond ONLY in JSON format:
{
    "visa_type": "F-1 Student Visa",
    "destination_country": "USA",
    "required_documents": [
        "Valid passport",
        "Form I-20 from university",
        "SEVIS fee payment receipt",
        "Financial proof of funds",
        "Completed Form DS-160",
        "Visa interview appointment confirmation",
        "Passport-sized photograph"
    ],
    "processing_time": "3-5 weeks",
    "application_fee_usd": 185,
    "tips": [
        "Apply at least 3 months before program start",
        "Schedule your visa interview as early as possible",
        "Prepare to show strong ties to your home country",
        "Have financial documents readily available for the interview"
    ],
    "warning": "Visa interviews are mandatory for F-1 applicants"
}
"""

FALLBACK_SYSTEM_PROMPT = """
You are a visa guidance assistant for international students.
Given a student's nationality and destination country, provide
detailed visa requirements and guidance based on your knowledge.

Respond ONLY in JSON format:
{
    "visa_type": "F-1 Student Visa",
    "destination_country": "USA",
    "required_documents": [
        "Valid passport",
        "Form I-20 from university",
        "SEVIS fee payment receipt",
        "Financial proof of funds",
        "Completed Form DS-160",
        "Visa interview appointment confirmation",
        "Passport-sized photograph"
    ],
    "processing_time": "3-5 weeks",
    "application_fee_usd": 185,
    "tips": [
        "Apply at least 3 months before program start",
        "Schedule your visa interview as early as possible",
        "Prepare to show strong ties to your home country"
    ],
    "warning": "Visa interviews are mandatory for F-1 applicants"
}
"""


def run_visa_agent(visa_input: dict) -> dict:
    """Provide visa guidance using RAG-retrieved documents + LLM reasoning."""
    destination = visa_input.get("destination_country", "USA")
    field = visa_input.get("field_of_study", "")
    query = (
        f"{destination} F-1 student visa requirements application process "
        f"documents fees SEVIS I-20 {field}"
    )

    rag_context = retrieve_visa_context(query)

    if rag_context:
        user_message = (
            f"Student details: {json.dumps(visa_input)}\n\n"
            f"--- Retrieved official visa documentation ---\n\n"
            f"{rag_context}\n\n"
            f"--- End of retrieved documents ---\n\n"
            "Based on the above official documentation and the student's details, "
            "provide comprehensive visa guidance. Prefer facts from the documents "
            "over general knowledge."
        )
        response = get_llm_response(RAG_SYSTEM_PROMPT, user_message)
    else:
        user_message = f"Provide visa guidance for this student: {visa_input}"
        response = get_llm_response(FALLBACK_SYSTEM_PROMPT, user_message)

    return json.loads(response)
