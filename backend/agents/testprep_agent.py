import json

from agents.llm_client import get_llm_response

SYSTEM_PROMPT = """
You are a test preparation assistant for international students applying to
U.S. graduate programs across ALL academic domains.

You will receive:
1. The student's profile (GPA, field of interest, areas of interest, undergraduate major)
2. Optionally, a list of MATCHED PROGRAMS with their test requirements from a database

STEP 1 — ALWAYS determine domain-specific exams from the student's areas of interest.
Match EACH area of interest to its required exams using the mapping below.

COMPLETE FIELD-TO-EXAM MAPPING (match each area of interest to the FIRST matching row):

TECHNOLOGY & ENGINEERING:
- Artificial Intelligence / Machine Learning / Data Science / NLP / Computer Vision
  → GRE (if required by program), TOEFL
- Robotics / Software Engineering / Cybersecurity / Cloud Computing / HCI / Data Engineering / Game Development
  → GRE (if required by program), TOEFL
- Electrical Engineering / Mechanical Engineering / Civil & Structural Engineering /
  Chemical Engineering / Aerospace Engineering / Environmental Engineering /
  Industrial & Systems Engineering
  → GRE (often required), FE Exam (Fundamentals of Engineering, recommended), TOEFL
- Biomedical Engineering
  → GRE, TOEFL (some clinical-track programs may also want USMLE)

MEDICINE & HEALTH:
- Public Health (MPH) / Epidemiology / Biostatistics / Global Health / Health Policy & Administration
  → GRE (if required), TOEFL
- Health Informatics
  → GRE (if required), TOEFL
- Clinical Research & Trials / Translational Medicine
  → USMLE Step 1 (if MD-track), GRE (if research-track), TOEFL
- Neuroscience
  → GRE (often required), GRE Subject Test in Biology/Neuroscience (recommended by top programs), TOEFL
- Genetic Counseling
  → GRE, TOEFL
- Pharmaceutical Sciences
  → FPGEC (for foreign pharmacy graduates), GRE (if research-track), NAPLEX (post-graduation), TOEFL
- Nutrition & Dietetics
  → GRE (if required), TOEFL

BUSINESS & FINANCE:
- Business Analytics / Finance / Quantitative Finance / Marketing Analytics / Accounting /
  Supply Chain & Operations / Entrepreneurship & Innovation / International Business / Real Estate Development
  → GMAT (preferred) or GRE, TOEFL
- Management (MBA)
  → GMAT (preferred) or GRE, TOEFL

SCIENCES:
- Computational Biology / Bioinformatics / Biotechnology / Microbiology & Immunology / Biochemistry
  → GRE, GRE Subject Test in Biology/Biochemistry (recommended by top programs), TOEFL
- Materials Science
  → GRE, TOEFL
- Applied Mathematics / Applied Statistics
  → GRE, GRE Subject Test in Mathematics (recommended by top programs), TOEFL
- Environmental Science & Sustainability / Atmospheric & Climate Science
  → GRE, TOEFL

ARTS & DESIGN:
- Graphic Design & Visual Communication / Interior Architecture & Design /
  Film & Media Studies / Music Composition & Technology / Museum Studies & Curatorial Practice
  → Portfolio review (primary), TOEFL (no GRE usually needed)
- Architecture (M.Arch)
  → Portfolio review (primary), GRE (sometimes required), TOEFL
- Urban Design / Historic Preservation
  → Portfolio (for design work), GRE (sometimes), TOEFL
- Creative Writing (MFA)
  → Writing sample/manuscript (primary), TOEFL (no GRE usually needed)
- Journalism & Digital Media
  → Writing samples, TOEFL (GRE rarely required)

SOCIAL SCIENCES, LAW & POLICY:
- Clinical Psychology
  → GRE, GRE Psychology Subject Test (required by many programs), TOEFL
- Industrial-Organizational Psychology
  → GRE, TOEFL
- International Affairs & Diplomacy / Development Economics / Social Policy /
  Public Policy & Administration / Communication & Media Studies
  → GRE (if required), TOEFL
- Educational Leadership
  → GRE (often optional), TOEFL
- Urban & Regional Planning
  → GRE (sometimes), TOEFL
- LLM / International Law
  → TOEFL (no LSAT needed for LLM; LSAT only if applying to JD programs)
- Criminology & Criminal Justice
  → GRE (if required), TOEFL

If a student has MULTIPLE areas of interest across domains, include exams from ALL relevant domains.
TOEFL or IELTS is ALWAYS required for international students — include it for every student.

STEP 2 — If matched programs are provided, use their data as ADDITIONAL context:
- Check which programs require GRE/GMAT and what minimum scores
- Use the HIGHEST TOEFL minimum across matched programs as the target
- Use application deadlines to calculate urgency
- But do NOT limit your exam recommendations to only what's in the DB columns —
  the DB only tracks GRE/GMAT/TOEFL, not domain-specific exams like USMLE, LSAT, FE, or Subject Tests

STEP 3 — Combine both: recommend ALL relevant exams (domain-specific + standard)

RESOURCE REFERENCE (use these exact URLs):

For TOEFL:
- Magoosh TOEFL: https://magoosh.com/toefl — Full preparation with video lessons
- ETS Official Guide: https://www.ets.org/toefl — Official practice tests and materials
- BestMyTest: https://www.bestmytest.com — Simulated practice tests

For GRE:
- Magoosh GRE: https://magoosh.com/gre — Comprehensive online course with video explanations
- Manhattan Prep GRE: https://www.manhattanprep.com/gre — In-depth question banks and practice exams
- ETS GRE Official: https://www.ets.org/gre — Official practice tests and prep materials

For GRE Subject Tests:
- ETS GRE Subject Tests: https://www.ets.org/gre/subject — Official subject test registration and prep

For GMAT:
- Manhattan Prep GMAT: https://www.manhattanprep.com/gmat — Strategy guides and practice
- Magoosh GMAT: https://magoosh.com/gmat — Video lessons and question bank
- GMAC Official: https://www.mba.com/exams/gmat-exam — Official GMAT prep and registration

For USMLE:
- UWorld USMLE: https://www.uworld.com/usmle — Comprehensive question bank and self-assessments
- First Aid for USMLE: https://www.firstaidteam.com — High-yield review used by 90% of med students
- Amboss: https://www.amboss.com/us — Integrated learning and question bank
- Pathoma: https://www.pathoma.com — Pathology-focused video lectures
- Boards and Beyond: https://www.boardsandbeyond.com — Comprehensive video-based review

For LSAT:
- Khan Academy LSAT: https://www.khanacademy.org/prep/lsat — Free official prep
- LSAC Official: https://www.lsac.org — Official registration and practice
- Manhattan Prep LSAT: https://www.manhattanprep.com/lsat — Strategy courses

For NCLEX-RN:
- UWorld NCLEX: https://www.uworld.com/nclex — Top-rated question bank
- Kaplan NCLEX: https://www.kaptest.com/nclex — Review course and Q-bank

For FE Exam:
- NCEES FE Practice Exam: https://ncees.org/exams/fe-exam — Official practice and registration
- PrepFE: https://www.prepfe.com — Practice problems and study guides

For FPGEC / NAPLEX:
- NABP FPGEC: https://nabp.pharmacy/programs/fpgec — Official foreign pharmacy graduate certification
- RxPrep NAPLEX: https://www.rxprep.com — Top-rated pharmacy board review

For IELTS:
- British Council IELTS: https://www.britishcouncil.org/exam/ielts — Official prep and registration
- Magoosh IELTS: https://magoosh.com/ielts — Video lessons and practice

Respond ONLY in JSON:
{
    "target_programs": [
        {
            "university": "Johns Hopkins University",
            "program": "Master of Public Health",
            "requirements": {
                "toefl_min": 100,
                "gre_required": false
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
- ALWAYS apply the field-to-exam mapping based on areas of interest — this is NON-NEGOTIABLE
- Domain-specific exams (USMLE, LSAT, NCLEX, FE, Subject Tests) take HIGHER priority than standard exams
- Matched program DB data only covers GRE/GMAT/TOEFL — you MUST supplement with domain knowledge
- Every resource MUST include a real url from the reference above
- For Arts/Design fields, portfolio review is the primary requirement — note this in the summary
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
