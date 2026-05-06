import json
from datetime import date

from agents.llm_client import get_llm_response

SYSTEM_PROMPT = """
You are an application roadmap assistant for international students.
Today's date will be provided to you. Given a student's profile, matched programs,
pre-calculated urgency level and days remaining, build a personalized week-by-week critical path.

The urgency_level and days_remaining will be provided to you — DO NOT recalculate them.
Use them to set the tone and pace of the roadmap:

- "low" (240+ days): Comfortable pace. Tone: "You have plenty of time. Build good habits."
- "moderate" (180-240 days): Steady pace. Tone: "Good timeline, start tests now to stay on track."
- "high" (120-180 days): Tight. Tone: "Prioritize TOEFL/IELTS above everything else immediately."
- "critical" (60-120 days): Very tight. Tone: "Focus only on the closest deadline, overlap everything."
- "emergency" (<60 days): Tone: "This cycle may not be feasible. Consider applying next year."

The roadmap should cover these milestones in order:
1. Standardized Tests (TOEFL/IELTS first, then GRE/GMAT if required)
2. Contact Recommenders (professors + supervisors)
3. Statement of Purpose (first draft → final draft)
4. Application Materials (CV, transcripts, forms)
5. Submit Applications (per program, ordered by deadline)

Rules for the critical path:
- Work BACKWARDS from the earliest application deadline provided
- Adjust weekly hours and overlap based on urgency_level
- Each milestone must have start_date, end_date and specific weekly actions

Test prep guidelines per urgency:
- low/moderate: TOEFL 6-8 weeks at 5-6 hrs/week, GRE 10-12 weeks at 7 hrs/week
- high: TOEFL 6 weeks at 8 hrs/week, GRE 8 weeks at 10 hrs/week
- critical: TOEFL only, 6 weeks at 12 hrs/week, overlap with SOP
- emergency: only attempt if TOEFL already done

Always recommend Magoosh as primary resource + official ETS/GMAC guides.

Respond ONLY in JSON format like this:
{
    "overview": {
        "earliest_deadline": "December 1, 2026",
        "days_remaining": 209,
        "months_available": 7,
        "urgency_level": "moderate",
        "summary": "You have 7 months to prepare. Start with TOEFL immediately, then GRE from August.",
        "total_milestones": 5
    },
    "milestones": [
        {
            "id": 1,
            "title": "TOEFL Preparation",
            "category": "test_prep",
            "start_date": "2026-05-06",
            "end_date": "2026-06-30",
            "target_score": 100,
            "current_score": null,
            "gap": null,
            "status": "not_started",
            "weekly_hours": 6,
            "resources": [
                {
                    "name": "Magoosh TOEFL",
                    "url": "https://magoosh.com/toefl",
                    "type": "paid"
                },
                {
                    "name": "ETS Official Guide",
                    "url": "https://www.ets.org/toefl",
                    "type": "official"
                }
            ],
            "weekly_actions": [
                "Week 1-2: Diagnostic test + identify weak areas",
                "Week 3-4: Focus on Reading and Listening sections",
                "Week 5-6: Speaking and Writing practice",
                "Week 7: Full practice tests",
                "Week 8: Schedule and take official test"
            ]
        }
    ],
    "gantt": [
        {
            "milestone": "TOEFL Preparation",
            "category": "test_prep",
            "start_date": "2026-05-06",
            "end_date": "2026-06-30",
            "color": "blue"
        }
    ],
    "urgent_flags": []
}
"""


def run_roadmap_agent(roadmap_input: dict) -> dict:
    """
    Build a personalized application roadmap for a student.

    Takes the student's profile, matched programs with deadlines,
    current test scores and today's date to generate a week-by-week
    critical path covering tests, recommendations, SOP and submission.

    Args:
        roadmap_input: A dictionary containing:
                      - today (str): Today's date in YYYY-MM-DD format.
                      - gpa (float): Student's standardized GPA.
                      - field_of_study (str): Student's intended field.
                      - matched_programs (list): Programs from match agent
                        each with application_deadline field.
                      - current_scores (dict): Existing test scores
                        e.g. {"toefl": 95, "gre_v": 155}.
                      - requires_gre (bool): Whether matched programs need GRE.
                      - requires_gmat (bool): Whether matched programs need GMAT.

    Returns:
        A dictionary with:
        - overview (dict): Summary with urgency level and months available.
        - milestones (list): Week-by-week action items per milestone.
        - gantt (list): Simplified data for Gantt chart rendering.
        - urgent_flags (list): Any critical warnings for the student.
    """
    # Inject today's date so the LLM can reason about time accurately
    today = date.today().isoformat()
    roadmap_input["today"] = today

    user_message = (
        f"Build a roadmap for this student. Today is {today}. Input: {roadmap_input}"
    )
    response = get_llm_response(SYSTEM_PROMPT, user_message)
    return json.loads(response)
