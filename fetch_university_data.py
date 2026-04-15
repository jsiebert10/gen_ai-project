"""
fetch_university_data.py
========================
Pulls master's program data from the College Scorecard API (two endpoints:
institution-level and field-of-study-level) and saves everything into a
SQLite database ready for your FastAPI backend.

HOW TO RUN
----------
1. Get a free API key at: https://api.data.gov/signup/
2. Install dependencies:
       pip install requests pandas sqlalchemy tqdm
3. Set your API key:
       export SCORECARD_API_KEY="your_key_here"   (Mac/Linux)
       set SCORECARD_API_KEY=your_key_here         (Windows)
4. Run:
       python fetch_university_data.py

OUTPUT
------
  data/university_data.db   <-- SQLite file with 3 tables:
    - institutions           (school-level info)
    - masters_programs       (one row per school x field-of-study)
    - program_requirements   (static lookup: what each type of program typically requires)
"""

import os
import time
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from tqdm import tqdm


# ── CONFIG ────────────────────────────────────────────────────────────────────

API_KEY   = "mvMwAfqV2BKNgYOf89syHn3UNNBZh9fE6pnyVdiv"
BASE_URL  = "https://api.data.gov/ed/collegescorecard/v1/schools"
PER_PAGE  = 100          # max allowed by the API
DB_PATH   = "data/university_data.db"
SLEEP_SEC = 0.3          # be polite to the API between pages


# ── STEP 1: FETCH INSTITUTION-LEVEL DATA ──────────────────────────────────────
#
# We filter to schools that:
#   - Are currently operating  (school.operating=1)
#   - Award graduate degrees   (school.degrees_awarded.highest=4  means grad degrees)
#   - Are in the US            (implicitly true for this API)
#
# Fields pulled and what they mean:
#   id                                    → IPEDS unit ID (unique school identifier)
#   school.name                           → University name
#   school.state                          → 2-letter state code
#   school.city                           → City
#   school.school_url                     → Official website
#   school.ownership                      → 1=Public, 2=Private nonprofit, 3=Private for-profit
#   school.locale                         → Urban/suburban/rural code
#   latest.student.size                   → Total enrolled students
#   latest.cost.tuition.in_state          → Annual in-state tuition (undergrad proxy)
#   latest.cost.tuition.out_of_state      → Annual out-of-state tuition
#   latest.cost.avg_net_price.public      → Avg net price after aid (public schools)
#   latest.cost.avg_net_price.private     → Avg net price after aid (private schools)
#   latest.admissions.admission_rate.overall → Acceptance rate (0.0 – 1.0)
#   latest.admissions.sat_scores.average.overall → Avg SAT score
#   latest.completion.completion_rate_4yr_150nt  → 4-yr grad rate (150% time)
#   latest.earnings.10_yrs_after_entry.median    → Median earnings 10 yrs after enrollment
#   latest.student.grad_students         → Number of graduate students enrolled
#   latest.academics.program_percentage.graduate → % of programs that are graduate-level

INSTITUTION_FIELDS = ",".join([
    "id",
    "school.name",
    "school.state",
    "school.city",
    "school.school_url",
    "school.ownership",
    "school.locale",
    "latest.student.size",
    "latest.student.grad_students",
    "latest.cost.tuition.in_state",
    "latest.cost.tuition.out_of_state",
    "latest.cost.avg_net_price.public",
    "latest.cost.avg_net_price.private",
    "latest.admissions.admission_rate.overall",
    "latest.admissions.sat_scores.average.overall",
    "latest.completion.completion_rate_4yr_150nt",
    "latest.earnings.10_yrs_after_entry.median",
])

INSTITUTION_FILTERS = {
    "school.operating": 1,
    "school.degrees_awarded.highest": 4,   # 4 = graduate degree
}


def fetch_all_pages(fields: str, filters: dict, label: str) -> list[dict]:
    """Fetches every page from the Scorecard API for a given query."""
    params = {
        "api_key": API_KEY,
        "fields":  fields,
        "per_page": PER_PAGE,
        "page": 0,
        **filters,
    }
    all_results = []

    # First call to find total number of pages
    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    total    = data["metadata"]["total"]
    n_pages  = (total // PER_PAGE) + 1
    all_results.extend(data["results"])

    print(f"\n{label}: {total} records across {n_pages} pages")

    for page in tqdm(range(1, n_pages), desc=label):
        params["page"] = page
        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        all_results.extend(resp.json()["results"])
        time.sleep(SLEEP_SEC)

    return all_results


def build_institutions_df(raw: list[dict]) -> pd.DataFrame:
    """Flattens raw API dicts into a clean DataFrame."""
    rename = {
        "id":                                            "school_id",
        "school.name":                                   "school_name",
        "school.state":                                  "state",
        "school.city":                                   "city",
        "school.school_url":                             "website",
        "school.ownership":                              "ownership_code",
        "school.locale":                                 "locale_code",
        "latest.student.size":                           "total_students",
        "latest.student.grad_students":                  "grad_students",
        "latest.cost.tuition.in_state":                  "tuition_in_state",
        "latest.cost.tuition.out_of_state":              "tuition_out_of_state",
        "latest.cost.avg_net_price.public":              "net_price_public",
        "latest.cost.avg_net_price.private":             "net_price_private",
        "latest.admissions.admission_rate.overall":      "acceptance_rate",
        "latest.admissions.sat_scores.average.overall":  "avg_sat",
        "latest.completion.completion_rate_4yr_150nt":   "graduation_rate",
        "latest.earnings.10_yrs_after_entry.median":     "median_earnings_10yr",
    }
    df = pd.DataFrame(raw)

    # Only rename columns that actually came back from the API.
    # Some fields are sparsely populated and may be absent for all schools.
    actual_rename = {k: v for k, v in rename.items() if k in df.columns}
    missing = [k for k in rename if k not in df.columns]
    if missing:
        print(f"\n  ℹ️  These API fields were absent and will be NULL: {missing}")
    df = df.rename(columns=actual_rename)

    # Decode ownership so the frontend can show "Public" / "Private nonprofit"
    ownership_map = {1: "Public", 2: "Private nonprofit", 3: "Private for-profit"}
    df["ownership"] = df["ownership_code"].map(ownership_map) if "ownership_code" in df.columns else None

    # Decode locale: 11-13 = City, 21-23 = Suburb, 31-33 = Town, 41-43 = Rural
    def locale_label(code):
        if pd.isna(code): return None
        code = int(code)
        if code < 20:  return "City"
        if code < 30:  return "Suburb"
        if code < 40:  return "Town"
        return "Rural"
    df["locale"] = df["locale_code"].apply(locale_label) if "locale_code" in df.columns else None

    # Round acceptance rate to a readable percentage
    if "acceptance_rate" in df.columns:
        df["acceptance_rate_pct"] = (df["acceptance_rate"] * 100).round(1)
    else:
        df["acceptance_rate_pct"] = None

    # Desired columns — add as None if the API didn't return them
    keep = [
        "school_id", "school_name", "state", "city", "website",
        "ownership", "locale", "total_students", "grad_students",
        "tuition_in_state", "tuition_out_of_state",
        "net_price_public", "net_price_private",
        "acceptance_rate_pct", "avg_sat",
        "graduation_rate", "median_earnings_10yr",
    ]
    for col in keep:
        if col not in df.columns:
            df[col] = None

    return df[keep].drop_duplicates(subset="school_id")


# ── STEP 2: FETCH FIELD-OF-STUDY (PROGRAM) DATA ───────────────────────────────
#
# The Scorecard has a separate endpoint for field-of-study data.
# We filter to credential_level=3 which means Master's degrees.
#
# Fields pulled:
#   latest.programs.cip_4_digit.school.id         → links back to institution
#   latest.programs.cip_4_digit.title             → field of study name (e.g. "Computer Science")
#   latest.programs.cip_4_digit.code              → 4-digit CIP code (standard classification)
#   latest.programs.cip_4_digit.credential.level  → 3 = Master's
#   latest.programs.cip_4_digit.credential.title  → "Master's Degree"
#   latest.programs.cip_4_digit.earnings.median_earnings       → median earnings after completion
#   latest.programs.cip_4_digit.debt.median_debt               → median federal debt at graduation
#   latest.programs.cip_4_digit.counts.ipeds_awards2           → number of awards conferred

PROGRAM_FIELDS = ",".join([
    "id",
    "school.name",
    "school.state",
    "latest.programs.cip_4_digit.school.id",
    "latest.programs.cip_4_digit.title",
    "latest.programs.cip_4_digit.code",
    "latest.programs.cip_4_digit.credential.level",
    "latest.programs.cip_4_digit.credential.title",
    "latest.programs.cip_4_digit.earnings.median_earnings",
    "latest.programs.cip_4_digit.debt.median_debt",
    "latest.programs.cip_4_digit.counts.ipeds_awards2",
])

PROGRAM_FILTERS = {
    "school.operating": 1,
    "school.degrees_awarded.highest": 4,
    "latest.programs.cip_4_digit.credential.level": 3,   # 3 = Master's degree
}


def build_programs_df(raw: list[dict]) -> pd.DataFrame:
    """
    The program data comes back as nested arrays under each school.
    This function explodes them into one row per school+program.
    """
    rows = []
    for school in raw:
        school_id   = school.get("id")
        school_name = school.get("school.name")
        state       = school.get("school.state")
        programs    = school.get("latest.programs.cip_4_digit") or []

        for prog in programs:
            # Only keep Master's (credential level 3) — filter should handle this
            # but double-check since nested arrays sometimes include other levels
            if prog.get("credential.level") != 3:
                continue
            rows.append({
                "school_id":           school_id,
                "school_name":         school_name,
                "state":               state,
                "cip_code":            prog.get("code"),
                "field_of_study":      prog.get("title"),
                "credential_level":    prog.get("credential.level"),
                "credential_title":    prog.get("credential.title"),
                "median_earnings":     prog.get("earnings.median_earnings"),
                "median_debt":         prog.get("debt.median_debt"),
                "awards_conferred":    prog.get("counts.ipeds_awards2"),
            })

    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["school_id", "cip_code"])
    df["program_id"] = range(1, len(df) + 1)
    return df


# ── STEP 3: BUILD PROGRAM REQUIREMENTS LOOKUP TABLE ───────────────────────────
#
# The Scorecard API does NOT have specific admission requirements
# (GRE scores, letters of rec, etc.) — that data lives on each school's own website.
#
# What we CAN do is build a lookup table keyed by CIP code (field of study)
# that lists the *typical* requirements for that type of program.
# Your AI agents can use this table to generate a "to-do list" for each applicant.
#
# CIP code reference (4-digit): https://nces.ed.gov/ipeds/cipcode/
# The entries below cover the most common master's fields for international students.

def build_requirements_table() -> pd.DataFrame:
    """
    Static lookup table: CIP code → typical admission requirements.
    Each field is a comma-separated list so it's easy to split in Python.
    Add more rows as your demo expands.
    """
    requirements = [
        # CIP   Field                    GRE?   GMAT?  Min GPA  TOEFL  IELTS  Work exp?  Portfolio?  Typical documents
        ("1101", "Computer Science",
         True,  False, 3.0, 90,  6.5, False, False,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV, GRE Scores"),

        ("1104", "Information Science",
         True,  False, 3.0, 90,  6.5, False, False,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV"),

        ("5202", "Business Administration (MBA)",
         False, True,  3.0, 100, 7.0, True,  False,
         "Transcripts, 2 Letters of Recommendation, Statement of Purpose, Resume/CV, GMAT Scores, Work Experience Letter"),

        ("5203", "Finance",
         False, True,  3.2, 100, 7.0, True,  False,
         "Transcripts, 2 Letters of Recommendation, Statement of Purpose, Resume/CV, GMAT or GRE Scores"),

        ("1401", "Engineering (General)",
         True,  False, 3.2, 90,  6.5, False, False,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV, GRE Scores"),

        ("1408", "Electrical Engineering",
         True,  False, 3.2, 90,  6.5, False, False,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV, GRE Scores"),

        ("1419", "Mechanical Engineering",
         True,  False, 3.2, 90,  6.5, False, False,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV, GRE Scores"),

        ("2701", "Mathematics",
         True,  False, 3.3, 90,  6.5, False, False,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV, GRE Scores (Math Subject Test recommended)"),

        ("2799", "Statistics / Data Science",
         True,  False, 3.2, 90,  6.5, False, False,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV, GRE Scores"),

        ("4501", "Economics",
         True,  False, 3.3, 95,  7.0, False, False,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV, GRE Scores"),

        ("4511", "International Relations",
         False, False, 3.0, 100, 7.0, True,  False,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV, Writing Sample"),

        ("4202", "Psychology",
         True,  False, 3.0, 90,  6.5, False, False,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV, GRE Scores, Research Statement"),

        ("5109", "Public Health (MPH)",
         False, False, 3.0, 90,  6.5, True,  False,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV, Work Experience in Health Field"),

        ("4403", "Urban Planning",
         False, False, 3.0, 90,  6.5, False, False,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV, Portfolio (optional)"),

        ("0401", "Architecture",
         False, False, 3.0, 90,  6.5, False, True,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV, Portfolio of Design Work"),

        ("5007", "Fine Arts (MFA)",
         False, False, 3.0, 79,  6.5, False, True,
         "Transcripts, 2 Letters of Recommendation, Statement of Purpose, Portfolio of Creative Work"),

        ("0901", "Communication",
         False, False, 3.0, 90,  6.5, False, False,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV, Writing Sample"),

        ("1310", "Education / Teaching",
         False, False, 2.8, 79,  6.5, True,  False,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV, Teaching License (if applicable)"),

        ("2604", "Linguistics",
         True,  False, 3.0, 90,  6.5, False, False,
         "Transcripts, 3 Letters of Recommendation, Statement of Purpose, Resume/CV, Writing Sample"),

        ("3099", "Interdisciplinary Studies",
         False, False, 3.0, 90,  6.5, False, False,
         "Transcripts, 2 Letters of Recommendation, Statement of Purpose, Resume/CV"),
    ]

    rows = []
    for r in requirements:
        (cip, field, gre, gmat, min_gpa, toefl, ielts,
         work_exp, portfolio, documents) = r

        # Build a human-readable checklist string for the app's to-do list
        checklist_items = []
        checklist_items.append("Request official transcripts from all universities attended")
        checklist_items.append("Write Statement of Purpose (1-2 pages)")
        checklist_items.append("Update your Resume / CV")
        if gre:
            checklist_items.append(f"Register for and take the GRE (target: score competitive for your program)")
        if gmat:
            checklist_items.append(f"Register for and take the GMAT")
        checklist_items.append(f"Take English test: TOEFL (min {toefl}) or IELTS (min {ielts})")
        if work_exp:
            checklist_items.append("Gather proof of work experience (employment letters, resume highlights)")
        if portfolio:
            checklist_items.append("Prepare a portfolio of your work (digital PDF preferred)")
        checklist_items.append("Secure letters of recommendation (contact professors/supervisors early)")
        checklist_items.append("Prepare financial documents (bank statements, sponsor letter) for visa application")
        checklist_items.append("Research application deadlines for each program (typically Nov–Feb for Fall admission)")

        rows.append({
            "cip_code":              cip,
            "field_of_study":        field,
            "gre_required":          gre,
            "gmat_required":         gmat,
            "min_gpa_recommended":   min_gpa,
            "min_toefl":             toefl,
            "min_ielts":             ielts,
            "work_exp_expected":     work_exp,
            "portfolio_required":    portfolio,
            "required_documents":    documents,
            "applicant_checklist":   " | ".join(checklist_items),
            "notes": (
                "Requirements vary by school. Always verify on the program's official admissions page. "
                "International students should apply 6-12 months before the deadline."
            ),
        })

    return pd.DataFrame(rows)


# ── STEP 4: SAVE TO SQLITE ────────────────────────────────────────────────────

def save_to_sqlite(df_institutions, df_programs, df_requirements):
    os.makedirs("data", exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}")

    with engine.begin() as conn:
        # institutions table
        df_institutions.to_sql(
            "institutions", conn,
            if_exists="replace", index=False
        )
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_inst_id ON institutions(school_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_inst_state ON institutions(state)"))

        # masters_programs table
        df_programs.to_sql(
            "masters_programs", conn,
            if_exists="replace", index=False
        )
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_prog_school ON masters_programs(school_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_prog_cip ON masters_programs(cip_code)"))

        # program_requirements lookup table
        df_requirements.to_sql(
            "program_requirements", conn,
            if_exists="replace", index=False
        )
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_req_cip ON program_requirements(cip_code)"))

    print(f"\n✅  Saved to {DB_PATH}")
    print(f"   institutions:        {len(df_institutions):,} rows")
    print(f"   masters_programs:    {len(df_programs):,} rows")
    print(f"   program_requirements:{len(df_requirements):,} rows")


# ── STEP 5: QUICK SANITY-CHECK QUERY ─────────────────────────────────────────

def preview_db():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.connect() as conn:
        print("\n── Sample: top 5 programs by median earnings ──")
        q = """
            SELECT p.school_name, p.field_of_study, p.state,
                   p.median_earnings, i.acceptance_rate_pct
            FROM   masters_programs p
            JOIN   institutions i USING (school_id)
            WHERE  p.median_earnings IS NOT NULL
            ORDER  BY p.median_earnings DESC
            LIMIT  5
        """
        result = pd.read_sql(q, conn)
        print(result.to_string(index=False))

        print("\n── Sample: checklist for Computer Science ──")
        q2 = """
            SELECT applicant_checklist
            FROM   program_requirements
            WHERE  cip_code = '1101'
        """
        row = pd.read_sql(q2, conn)
        if not row.empty:
            for item in row.iloc[0]["applicant_checklist"].split(" | "):
                print(f"  • {item}")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    if API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️  No API key found.")
        print("   Get one free at: https://api.data.gov/signup/")
        print("   Then run:  export SCORECARD_API_KEY='your_key'")
        return

    print("=" * 60)
    print("  College Scorecard Data Fetcher")
    print("  International Student AI Consultant — Demo Data")
    print("=" * 60)

    # 1. Institutions
    raw_inst = fetch_all_pages(INSTITUTION_FIELDS, INSTITUTION_FILTERS,
                               "Fetching institutions")
    df_inst  = build_institutions_df(raw_inst)

    # 2. Master's programs
    raw_prog = fetch_all_pages(PROGRAM_FIELDS, PROGRAM_FILTERS,
                               "Fetching master's programs")
    df_prog  = build_programs_df(raw_prog)

    # 3. Requirements lookup (static — no API call needed)
    df_req   = build_requirements_table()

    # 4. Save everything
    save_to_sqlite(df_inst, df_prog, df_req)

    # 5. Quick preview
    preview_db()


if __name__ == "__main__":
    main()
