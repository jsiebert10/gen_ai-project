import json

from agents.llm_client import get_llm_response

SYSTEM_PROMPT = """
You are a visa guidance assistant for international students.
Given a student's nationality and destination country, provide
detailed visa requirements and guidance.

Consider:
- Required documents based on citizenship
- Visa type needed for student status
- Estimated processing times
- Application fees in USD
- Key tips and common mistakes to avoid

Respond ONLY in JSON format like this:
{
    "visa_type": "F-1 Student Visa",
    "destination_country": "USA",
    "required_documents": [
        "Valid passport",
        "Form I-20 from university",
        "SEVIS fee payment receipt",
        "Financial proof of funds"
    ],
    "processing_time": "3-5 weeks",
    "application_fee_usd": 185,
    "tips": [
        "Apply at least 3 months before program start",
        "Prepare to show strong ties to home country"
    ],
    "warning": "Visa interviews are mandatory for F-1 applicants"
}
"""


def run_visa_agent(visa_input: dict) -> dict:
    """
    Provide visa guidance based on student nationality and destination.

    Takes the student's citizenship and target country and returns
    detailed visa requirements, documents needed, processing times,
    and tips for a successful application.

    Args:
        visa_input: A dictionary containing:
                   - nationality (str): Student's citizenship country.
                   - destination_country (str): Target country for studies.
                   - program_start_date (str): When the program begins.

    Returns:
        A dictionary with:
        - visa_type (str): The required visa category.
        - destination_country (str): Target country.
        - required_documents (list): Documents needed for application.
        - processing_time (str): Expected processing duration.
        - application_fee_usd (int): Application fee in USD.
        - tips (list): Helpful advice for the application.
        - warning (str): Important cautionary note.
    """
    user_message = f"Provide visa guidance for this student: {visa_input}"
    response = get_llm_response(SYSTEM_PROMPT, user_message)
    return json.loads(response)
