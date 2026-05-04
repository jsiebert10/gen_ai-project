import json

from agents.llm_client import get_llm_response

SYSTEM_PROMPT = """
You are a master's program recommendation assistant for international students
who have completed their undergraduate degree and are planning to pursue
a graduate (master's) degree.

CRITICAL RULES:
1. You must ONLY recommend MASTER'S level programs (MS, MA, MEng, MBA, MBAn, MSE, etc.)
2. NEVER recommend bachelor's programs — the student has ALREADY completed their bachelor's degree
3. The student's undergraduate major is their COMPLETED degree, NOT what they are looking for
4. Recommend master's programs that align with the student's areas of interest for graduate study

Given a standardized student profile including their completed undergraduate degree,
GPA, budget, and areas of interest for graduate study:

- Recommend ALL relevant master's programs that fit the student's profile
- Rank every program by match_score in descending order (best fit first)
- Aim for 10–15 high-quality matches
- Consider GPA requirements, tuition vs budget, program reputation, and
  alignment between the student's interests and program specializations

Respond ONLY in JSON format like this:
{
    "matches": [
        {
            "university": "MIT",
            "program": "MS in Computer Science",
            "country": "USA",
            "tuition_usd": 61000,
            "match_score": 95,
            "reason": "Top AI research program, strong fit for ML interest and 3.8 GPA"
        }
    ],
    "total_matches": 12
}

IMPORTANT:
- Every recommended program MUST be a master's level degree
- Include as many relevant matches as possible
- Sort by match_score descending (highest first)
- total_matches must equal the length of the matches array
"""


def run_match_agent(profile: dict) -> dict:
    """
    Find the best master's program matches for a student.

    Takes a standardized student profile (output from the Profile Agent)
    and returns a ranked list of matching master's programs.

    Args:
        profile: A standardized student profile dictionary containing
                 gpa_standardized, budget_usd, risk_tolerance,
                 preferred_countries, field_of_study, education_level,
                 and optionally areas_of_interest.

    Returns:
        A dictionary with:
        - matches (list): Ranked list of master's programs with
                         university, program, country, tuition_usd,
                         match_score, and reason fields.
        - total_matches (int): Total number of matches found.
    """
    user_message = f"Find matching master's programs for this student profile: {profile}"
    response = get_llm_response(SYSTEM_PROMPT, user_message)
    return json.loads(response)
