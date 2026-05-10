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
   (these have ALREADY been filtered to be within the student's budget)

CRITICAL RULES:
1. You must ONLY return programs from the provided database list — do NOT invent programs
2. For each program, assign a match_score (0–100) based on this weighted rubric:
   - Field alignment with areas of interest: 40 points
   - GPA fit (student GPA vs program min_gpa): 25 points
   - Affordability (how far under budget): 20 points
   - Program reputation and career outcomes: 15 points
3. NEVER recommend a program that is not in the provided list
4. Return ALL programs that score >= 40
5. Sort by match_score descending (highest first)
6. Use tuition_usd_annual (annual tuition) as the "tuition_usd" field in your output
7. Preserve duration_months, gre_required, application_deadline_fall
   exactly as they appear in the database — do NOT change these values
8. Use the program_name from the database as the "program" field

Respond ONLY in JSON:
{
    "matches": [
        {
            "university": "University of Florida",
            "program": "Master of Science in Data Science",
            "country": "USA",
            "tuition_usd": 28000,
            "duration_months": 24,
            "gre_required": false,
            "toefl_min": 80,
            "application_deadline_fall": "December 15, 2026",
            "match_score": 92,
            "reason": "Strong data science curriculum, well within $30K budget, GPA exceeds minimum"
        }
    ],
    "total_matches": 5
}
"""

FALLBACK_PROMPT = """
You are a master's program recommendation assistant for international students.
No programs were found in the database for this student's interests and budget.
Based on your knowledge of real U.S. master's programs, recommend 5–10 programs
that fit WITHIN the student's annual budget.

CRITICAL:
- Only recommend real, existing U.S. master's programs
- The tuition_usd MUST be the annual tuition and MUST be within the student's budget
- Sort by match_score descending
- Use the same scoring rubric: field alignment (40), GPA fit (25), affordability (20), reputation (15)

Respond ONLY in JSON:
{
    "matches": [
        {
            "university": "Georgia Tech",
            "program": "Master of Science in Computer Science",
            "country": "USA",
            "tuition_usd": 29000,
            "duration_months": 24,
            "gre_required": false,
            "toefl_min": 90,
            "application_deadline_fall": "February 1, 2026",
            "match_score": 90,
            "reason": "Top-ranked CS program with affordable tuition for out-of-state students"
        }
    ],
    "total_matches": 5
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
            "tuition_usd_annual": c["tuition_usd_annual"],
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
        f"Database programs ({len(candidate_summary)} candidates, all within budget):\n"
        f"{json.dumps(candidate_summary, indent=2)}\n\n"
        "Score and rank these programs for this student. "
        "Return all with match_score >= 40, sorted descending."
    )

    response = get_llm_response(SYSTEM_PROMPT, user_message)
    return json.loads(response)
