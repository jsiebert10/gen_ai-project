import json

from agents.llm_client import get_llm_response

SYSTEM_PROMPT = """
You are a profile standardization assistant for international students.
Your job is to take raw student input and return a clean, structured profile.

Given the student's information, extract and standardize:
- GPA on a 4.0 scale
- Budget in USD per year
- Risk tolerance (low, medium, high)
- Preferred countries (list)
- Field of study
- Current education level (bachelor, master, phd)

Respond ONLY in JSON format like this:
{
    "gpa_standardized": 3.5,
    "budget_usd": 30000,
    "risk_tolerance": "medium",
    "preferred_countries": ["USA", "Germany"],
    "field_of_study": "Computer Science",
    "education_level": "bachelor"
}
"""


def run_profile_agent(raw_input: dict) -> dict:
    """
    Standardize a student's raw profile using an LLM.

    Takes unstructured student input (GPA, budget, preferences)
    and returns a clean, normalized profile ready for downstream
    agents like matching and visa guidance.

    Args:
        raw_input: A dictionary with the student's raw data.
                   Example: {"gpa": "3.8/4.0", "budget": "30k USD",
                             "country": "USA or Germany"}

    Returns:
        A dictionary with standardized fields:
        - gpa_standardized (float)
        - budget_usd (int)
        - risk_tolerance (str)
        - preferred_countries (list)
        - field_of_study (str)
        - education_level (str)
    """
    user_message = f"Here is the student's raw profile: {raw_input}"
    response = get_llm_response(SYSTEM_PROMPT, user_message)
    return json.loads(response)
