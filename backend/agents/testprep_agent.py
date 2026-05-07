import json

from agents.llm_client import get_llm_response

SYSTEM_PROMPT = """
You are a test preparation assistant for international students applying to
U.S. graduate programs across ALL academic domains.

You will receive:
1. The student's profile (GPA, field of interest, areas of interest, undergraduate major)
2. Optionally, a list of MATCHED PROGRAMS with their test requirements from a database

STEP 1 — ALWAYS determine domain-specific exams from the student's field/areas of interest:

FIELD-TO-EXAM MAPPING (ALWAYS apply this based on the student's areas of interest):
- Medicine / MBBS / Clinical Medicine / Translational Medicine → USMLE Step 1, USMLE Step 2 CK, TOEFL
- Public Health / Epidemiology / Biostatistics / Global Health → GRE (if required), TOEFL
- Dentistry → NBDE / INBDE, TOEFL
- Law / LLM / Intellectual Property Law → LSAT (for JD) or none (for LLM), TOEFL
- Business / MBA / Finance / Marketing Analytics / Accounting → GMAT (or GRE), TOEFL
- Engineering / CS / Data Science / AI / Cybersecurity → GRE (if required), TOEFL
- Nursing → NCLEX-RN, TOEFL
- Pharmacy / Pharmaceutical Sciences → FPGEC / NAPLEX, TOEFL
- Psychology (clinical/counseling) → GRE Psychology Subject Test, TOEFL
- Architecture → GRE (sometimes), portfolio review, TOEFL
- Fine Arts / MFA / Creative Writing → portfolio/writing sample, TOEFL
- Sciences (Biology, Chemistry, Biochemistry, Microbiology, etc.) → GRE (if required), TOEFL
- Education → GRE (sometimes optional), TOEFL

TOEFL or IELTS is almost always required for international students.

STEP 2 — If matched programs are provided, use their data as ADDITIONAL context:
- Check which programs require GRE/GMAT and what minimum scores
- Use the HIGHEST TOEFL minimum across matched programs as the target
- Use application deadlines to calculate urgency
- But do NOT limit your exam recommendations to only what's in the DB columns —
  the DB only tracks GRE/GMAT/TOEFL, not domain-specific exams like USMLE or LSAT

STEP 3 — Combine both: recommend ALL relevant exams (domain-specific + standard)

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
            "university": "Johns Hopkins University",
            "program": "Master of Public Health",
            "requirements": {
                "toefl_min": 100,
                "gre_required": false,
                "usmle_step1_required": true
            }
        }
    ],
    "gap_analysis": [
        {
            "exam": "USMLE Step 1",
            "current_score": null,
            "target_score": 230,
            "gap": null,
            "status": "score needed"
        },
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
            "exam": "USMLE Step 1",
            "weeks_needed": 24,
            "reason": "Required for medical residency and clinical master's programs"
        },
        {
            "priority": 2,
            "exam": "TOEFL",
            "weeks_needed": 8,
            "reason": "Required by all matched programs, highest min is 100"
        }
    ],
    "resources": [
        {
            "exam": "USMLE Step 1",
            "recommendations": [
                {
                    "name": "UWorld USMLE",
                    "url": "https://www.uworld.com/usmle",
                    "type": "paid",
                    "best_for": "Comprehensive question bank and self-assessments"
                },
                {
                    "name": "First Aid for USMLE",
                    "url": "https://www.firstaidteam.com",
                    "type": "paid",
                    "best_for": "High-yield review book used by 90% of medical students"
                }
            ]
        },
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
    "summary": "As a medical student, prioritize USMLE Step 1 preparation first, then TOEFL"
}

IMPORTANT:
- ALWAYS apply the field-to-exam mapping based on areas of interest
- Domain-specific exams (USMLE, LSAT, NCLEX, etc.) take HIGHER priority than standard exams
- Matched program DB data only covers GRE/GMAT/TOEFL — supplement with domain knowledge
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
            "Build a test prep plan. Use the field-to-exam mapping for domain-specific "
            "exams AND the matched program data for GRE/GMAT/TOEFL requirements."
        )
    else:
        user_message = f"Build a test prep plan for this student: {testprep_input}"

    response = get_llm_response(SYSTEM_PROMPT, user_message)
    return json.loads(response)
