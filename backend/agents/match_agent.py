import json

from agents.llm_client import get_llm_response
from services.program_data import get_candidate_programs

SYSTEM_PROMPT = """
You are a master's program recommendation assistant for international students
who have completed their undergraduate degree and are planning to pursue
a graduate (master's) degree in the UNITED STATES.

You will receive:
1. A student profile (GPA, budget, areas of interest, undergraduate major)
2. A list of REAL programs from the U.S. College Scorecard database

CRITICAL RULES:
1. You must ONLY return programs from the provided database list — do NOT invent programs
2. For each program, assign a match_score (0–100) and a reason
3. Consider: GPA vs min_gpa, tuition vs budget, field alignment with interests, program reputation
4. A program above the student's budget can still be recommended but with a lower score
5. Return ALL programs that score >= 40
6. Sort by match_score descending (highest first)
7. Preserve tuition_usd_total, duration_months, gre_required, application_deadline_fall
   exactly as they appear in the database — do NOT change these values
8. Use the program_name from the database as the "program" field

Respond ONLY in JSON:
{
    "matches": [
        {
            "university": "MIT",
            "program": "Master of Science in Computer Science",
            "country": "USA",
            "tuition_usd": 118000,
            "duration_months": 18,
            "gre_required": false,
            "toefl_min": 100,
            "application_deadline_fall": "December 15, 2026",
            "match_score": 95,
            "reason": "Top AI research program, strong fit for ML interest and 3.8 GPA"
        }
    ],
    "total_matches": 12
}
"""

FALLBACK_PROMPT = """
You are a master's program recommendation assistant for international students.
No programs were found in the database for this student's interests.
Based on your knowledge of real U.S. master's programs, recommend 10–15 programs.

CRITICAL: Only recommend real, existing U.S. master's programs.
Sort by match_score descending.

Respond ONLY in JSON:
{
    "matches": [
        {
            "university": "MIT",
            "program": "Master of Science in Computer Science",
            "country": "USA",
            "tuition_usd": 61000,
            "duration_months": 18,
            "gre_required": false,
            "toefl_min": 100,
            "application_deadline_fall": "December 15, 2026",
            "match_score": 95,
            "reason": "Top AI research program, strong fit for ML interest"
        }
    ],
    "total_matches": 12
}
"""


def run_match_agent(profile: dict) -> dict:
    """Match programs from the Scorecard DB, then use LLM to score and rank."""
    candidates = get_candidate_programs(
        field_of_study=profile.get("field_of_study") or profile.get("undergraduate_major", ""),
        areas_of_interest=profile.get("areas_of_interest", []),
        budget_usd=profile.get("budget_usd"),
        gpa=profile.get("gpa_standardized"),
    )

    if not candidates:
        user_message = f"Student profile: {json.dumps(profile)}"
        response = get_llm_response(FALLBACK_PROMPT, user_message)
        return json.loads(response)

    candidate_summary = []
    for c in candidates:
        candidate_summary.append({
            "university": c["university"],
            "program_name": c["program_name"],
            "field": c["field"],
            "country": c["country"],
            "tuition_usd_total": c["tuition_usd_total"],
            "duration_months": c["duration_months"],
            "description": c.get("description", ""),
            "toefl_min": c.get("toefl_min"),
            "ielts_min": c.get("ielts_min"),
            "gre_required": c.get("gre_required", False),
            "gre_min_quant": c.get("gre_min_quant"),
            "gmat_required": c.get("gmat_required", False),
            "gmat_min": c.get("gmat_min"),
            "min_gpa": c.get("min_gpa"),
            "application_deadline_fall": c.get("application_deadline_fall", ""),
            "application_deadline_spring": c.get("application_deadline_spring", ""),
        })

    user_message = (
        f"Student profile:\n{json.dumps(profile, indent=2)}\n\n"
        f"Database programs ({len(candidate_summary)} candidates):\n"
        f"{json.dumps(candidate_summary, indent=2)}\n\n"
        "Score and rank these programs for this student. "
        "Return all with match_score >= 40, sorted descending."
    )

    response = get_llm_response(SYSTEM_PROMPT, user_message)
    return json.loads(response)
