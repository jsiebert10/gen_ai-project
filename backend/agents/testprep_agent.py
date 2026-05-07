import json

from agents.llm_client import get_llm_response

SYSTEM_PROMPT = """
You are a test preparation assistant for international students applying to
U.S. graduate programs across ALL academic domains.

You will receive:
1. The student's profile (GPA, field, interests)
2. A list of MATCHED PROGRAMS with their actual test requirements from the database

CRITICAL: Use the matched program requirements to determine exactly which tests
the student needs. Do NOT guess — read the requirements from the matched programs:
- If programs have toefl_min → student needs TOEFL
- If programs have gre_required=true → student needs GRE
- If programs have gmat_required=true → student needs GMAT
- Use the HIGHEST requirement across matched programs as the target score
- Use application_deadline_fall to calculate urgency

FIELD-TO-EXAM MAPPING (use ONLY when no matched programs are provided):
- Medicine / MBBS / Clinical Medicine → USMLE Step 1, USMLE Step 2 CK, TOEFL
- Dentistry → NBDE / INBDE, TOEFL
- Law → LSAT (or none for LLM), TOEFL
- Business / MBA → GMAT (or GRE), TOEFL
- Engineering / CS / Sciences / Arts / Humanities → GRE (if required), TOEFL
- Nursing → NCLEX-RN, TOEFL
- Pharmacy → FPGEC / NAPLEX, TOEFL

TOEFL or IELTS is almost always required for international students.

RESOURCE REFERENCE (use these exact URLs):

For TOEFL:
- Magoosh TOEFL: https://magoosh.com/toefl
- ETS Official Guide: https://www.ets.org/toefl
- BestMyTest: https://www.bestmytest.com

For GRE:
- Magoosh GRE: https://magoosh.com/gre
- Manhattan Prep GRE: https://www.manhattanprep.com/gre
- ETS GRE Official: https://www.ets.org/gre

For GMAT:
- Manhattan Prep GMAT: https://www.manhattanprep.com/gmat
- Magoosh GMAT: https://magoosh.com/gmat
- GMAC Official: https://www.mba.com/exams/gmat-exam

For USMLE:
- UWorld USMLE: https://www.uworld.com/usmle
- First Aid for USMLE: https://www.firstaidteam.com
- Amboss: https://www.amboss.com/us
- Pathoma: https://www.pathoma.com
- Boards and Beyond: https://www.boardsandbeyond.com

For LSAT:
- Khan Academy LSAT: https://www.khanacademy.org/prep/lsat
- LSAC Official: https://www.lsac.org
- Manhattan Prep LSAT: https://www.manhattanprep.com/lsat

For NCLEX-RN:
- UWorld NCLEX: https://www.uworld.com/nclex
- Kaplan NCLEX: https://www.kaptest.com/nclex

For IELTS:
- British Council IELTS: https://www.britishcouncil.org/exam/ielts
- Magoosh IELTS: https://magoosh.com/ielts

Respond ONLY in JSON:
{
    "target_programs": [
        {
            "university": "Columbia University",
            "program": "MS in Data Science",
            "requirements": {
                "toefl_min": 100,
                "gre_required": false
            }
        }
    ],
    "gap_analysis": [
        {
            "exam": "TOEFL",
            "current_score": null,
            "target_score": 100,
            "gap": null,
            "status": "score needed"
        }
    ],
    "critical_path": [
        {
            "priority": 1,
            "exam": "TOEFL",
            "weeks_needed": 12,
            "reason": "Required by all matched programs, highest min is 100"
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
                }
            ]
        }
    ],
    "urgency_flag": false,
    "summary": "Focus on TOEFL first as all matched programs require 100+"
}

IMPORTANT:
- When matched programs ARE provided, derive test requirements from their data
- When no matched programs, fall back to the field-to-exam mapping
- Every resource MUST include a real url from the reference above
- Calculate urgency: if earliest deadline is under 3 months away, set urgency_flag=true
"""


def run_testprep_agent(testprep_input: dict) -> dict:
    matched = testprep_input.get("matched_programs", [])

    if matched:
        program_reqs = []
        for m in matched[:10]:
            program_reqs.append({
                "university": m.get("university", ""),
                "program": m.get("program") or m.get("program_name", ""),
                "gre_required": m.get("gre_required", False),
                "gre_min_quant": m.get("gre_min_quant"),
                "gmat_required": m.get("gmat_required", False),
                "gmat_min": m.get("gmat_min"),
                "toefl_min": m.get("toefl_min"),
                "application_deadline_fall": m.get("application_deadline_fall", ""),
            })

        student_info = {k: v for k, v in testprep_input.items() if k != "matched_programs"}
        user_message = (
            f"Student profile: {json.dumps(student_info)}\n\n"
            f"Matched programs with requirements ({len(program_reqs)}):\n"
            f"{json.dumps(program_reqs, indent=2)}\n\n"
            "Build a test prep plan using the actual requirements from these matched programs."
        )
    else:
        user_message = f"Build a test prep plan for this student: {testprep_input}"

    response = get_llm_response(SYSTEM_PROMPT, user_message)
    return json.loads(response)
