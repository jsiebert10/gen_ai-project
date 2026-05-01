import json

from agents.llm_client import get_llm_response

SYSTEM_PROMPT = """
You are a test preparation assistant for international students applying to graduate programs.

Given a student's profile, you will:
1. Identify the best matching programs based on their GPA, undergraduate university and field of interest
2. Find the test requirements for those programs (TOEFL, IELTS, GRE, GMAT)
3. Analyze gaps between current scores and requirements
4. Build a prioritized critical path based on application deadline
5. Recommend the best resources for each exam needed

For resources, consider:
- TOEFL/IELTS: Magoosh, ETS Official Guide, BestMyTest
- GRE: Magoosh, Manhattan Prep, ETS Official Guide, Kaplan
- GMAT: Manhattan Prep, Magoosh, Official GMAT Guide

For the critical path, consider:
- More than 6 months left: can prepare for all exams comfortably
- 3-6 months left: prioritize the most required exam first
- Less than 3 months left: focus only on the most critical exam, flag urgency

Respond ONLY in JSON format like this:
{
    "target_programs": [
        {
            "university": "Columbia University",
            "program": "MS in Data Science",
            "requirements": {
                "toefl_min": 100,
                "ielts_min": 7.0,
                "gre_required": false,
                "gmat_required": false
            }
        }
    ],
    "gap_analysis": [
        {
            "exam": "TOEFL",
            "current_score": 95,
            "target_score": 100,
            "gap": 5,
            "status": "needs improvement"
        }
    ],
    "critical_path": [
        {
            "priority": 1,
            "exam": "TOEFL",
            "weeks_needed": 4,
            "reason": "5 point gap, most programs require it"
        }
    ],
    "resources": [
        {
            "exam": "TOEFL",
            "recommendations": [
                {
                    "name": "Magoosh TOEFL",
                    "url": "https://magoosh.com/toefl",
                    "type": "paid",
                    "best_for": "Full preparation with video lessons"
                },
                {
                    "name": "ETS Official Guide",
                    "url": "https://www.ets.org/toefl",
                    "type": "official",
                    "best_for": "Official practice tests"
                }
            ]
        }
    ],
    "urgency_flag": false,
    "summary": "Focus on improving TOEFL by 5 points before tackling GRE prep"
}
"""


def run_testprep_agent(testprep_input: dict) -> dict:
    """
    Build a personalized test preparation plan for a student.

    Identifies target programs based on the student's profile,
    analyzes score gaps, and builds a critical path with
    resource recommendations for each required exam.

    Args:
        testprep_input: A dictionary containing:
                       - gpa (float): Student's GPA on 4.0 scale.
                       - undergraduate_university (str): Student's current/past university.
                       - field_of_interest (str): Intended field of graduate study.
                       - current_scores (dict): Existing test scores, e.g.
                         {"toefl": 95, "gre_v": 155, "gre_q": 160}.
                       - application_deadline (str): Target application date
                         e.g. "December 2026".

    Returns:
        A dictionary with:
        - target_programs (list): Matched programs with their requirements.
        - gap_analysis (list): Score gaps per exam.
        - critical_path (list): Prioritized study plan.
        - resources (list): Recommended study resources per exam.
        - urgency_flag (bool): True if deadline is under 3 months.
        - summary (str): High level recommendation for the student.
    """
    user_message = f"Build a test prep plan for this student: {testprep_input}"
    response = get_llm_response(SYSTEM_PROMPT, user_message)
    return json.loads(response)
