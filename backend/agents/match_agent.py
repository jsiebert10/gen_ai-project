import json

from agents.llm_client import get_llm_response

SYSTEM_PROMPT = """
You are a university program matching assistant for international students.
Given a standardized student profile, find the best matching programs.

Consider:
- GPA requirements vs student's GPA
- Tuition costs vs student's budget
- Program reputation and rankings
- Location preferences
- Field of study alignment

Respond ONLY in JSON format like this:
{
    "matches": [
        {
            "university": "TU Munich",
            "program": "MSc Computer Science",
            "country": "Germany",
            "tuition_usd": 1500,
            "match_score": 92,
            "reason": "Strong fit based on GPA and budget"
        }
    ],
    "total_matches": 3
}
"""


def run_match_agent(profile: dict) -> dict:
    """
    Find the best university program matches for a student.

    Takes a standardized student profile (output from the Profile Agent)
    and returns a ranked list of matching university programs.

    Args:
        profile: A standardized student profile dictionary containing
                 gpa_standardized, budget_usd, risk_tolerance,
                 preferred_countries, field_of_study, education_level.

    Returns:
        A dictionary with:
        - matches (list): Ranked list of university programs with
                         university, program, country, tuition_usd,
                         match_score, and reason fields.
        - total_matches (int): Total number of matches found.
    """
    user_message = f"Find matching programs for this student profile: {profile}"
    response = get_llm_response(SYSTEM_PROMPT, user_message)
    return json.loads(response)
