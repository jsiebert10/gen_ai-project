"""
generate_programs_data.py
=========================
Uses the Anthropic API to generate a realistic seed dataset of ~200 master's
programs across top US universities, then saves everything to SQLite.

HOW TO RUN
----------
1. Install dependencies:
       pip install anthropic sqlalchemy pandas tqdm

2. Set your Anthropic API key:
       export ANTHROPIC_API_KEY=""

3. Run:
       python generate_programs_data.py

OUTPUT
------
  data/programs.db  with two tables:
    - masters_programs       (~200 rows, one per program)
    - program_requirements   (~200 rows, matched to programs)
"""

import os
import json
import time
import re
import sqlite3
import pandas as pd
from tqdm import tqdm


# ── CONFIG ────────────────────────────────────────────────────────────────────


DB_PATH           = "data/programs.db"
MODEL             = "claude-sonnet-4-6"

# We generate data in batches by field. Each batch asks for 10 programs.
# This keeps each API call small and reliable.
FIELDS_TO_GENERATE = [
    ("Computer Science",              "CS / Software Engineering / AI"),
    ("Data Science",                  "Data Science / Analytics / Machine Learning"),
    ("Electrical Engineering",        "Electrical & Computer Engineering"),
    ("Mechanical Engineering",        "Mechanical & Aerospace Engineering"),
    ("Business Administration (MBA)", "MBA / Management / Strategy"),
    ("Finance",                       "Finance / Financial Engineering / Fintech"),
    ("Public Health (MPH)",           "Public Health / Epidemiology / Health Policy"),
    ("International Relations",       "International Affairs / Global Policy"),
    ("Architecture",                  "Architecture / Urban Design"),
    ("Psychology",                    "Psychology / Cognitive Science"),
    ("Economics",                     "Economics / Applied Economics"),
    ("Education",                     "Education / Learning Sciences / Curriculum"),
    ("Communication",                 "Communication / Media Studies / Journalism"),
    ("Environmental Science",         "Environmental Science / Sustainability"),
    ("Biomedical Engineering",        "Biomedical Engineering / Biotechnology"),
    ("Statistics",                    "Statistics / Biostatistics / Quantitative Methods"),
    ("Urban Planning",                "Urban Planning / Public Policy"),
    ("Fine Arts (MFA)",               "Fine Arts / Creative Writing / Design"),
    ("Law (LLM)",                     "Law / Legal Studies (LLM)"),
    ("Social Work (MSW)",             "Social Work / Counseling"),
]

# Mix of university tiers to get realistic variety
UNIVERSITIES = [
    # Elite research universities
    "MIT", "Stanford University", "Harvard University", "Caltech",
    "University of Chicago", "Princeton University", "Columbia University",
    "Yale University", "University of Pennsylvania", "Northwestern University",
    # Strong research universities
    "UC Berkeley", "UCLA", "University of Michigan", "Carnegie Mellon University",
    "Cornell University", "Duke University", "Johns Hopkins University",
    "Vanderbilt University", "Georgetown University", "NYU",
    # Very good regional/specialized
    "University of Southern California", "Boston University", "Tufts University",
    "George Washington University", "American University", "Northeastern University",
    "Purdue University", "University of Texas at Austin", "University of Washington",
    "Georgia Tech", "University of Illinois Urbana-Champaign", "Ohio State University",
    "Penn State University", "University of Wisconsin-Madison", "University of Minnesota",
    "University of Florida", "University of North Carolina Chapel Hill",
    "Arizona State University", "University of Colorado Boulder",
]


# ── PROMPT BUILDER ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a higher education data expert. You generate realistic, 
accurate JSON datasets about US master's degree programs. All data must be plausible 
and consistent with real-world programs. Return ONLY valid JSON, no markdown, no 
preamble, no explanation."""

def build_prompt(field_name: str, field_description: str, universities: list[str]) -> str:
    unis_str = ", ".join(universities)
    return f"""Generate exactly 10 realistic US master's programs in the field of {field_description}.

Choose universities from this list (pick the most realistic fits for this field): {unis_str}

Return a JSON array of exactly 10 objects. Each object must have ALL of these fields:

{{
  "university": "Full university name",
  "program_name": "Exact program name (e.g. 'Master of Science in Computer Science')",
  "field": "{field_name}",
  "country": "USA",
  "tuition_usd_total": <integer, realistic total program tuition in USD for international/out-of-state students>,
  "duration_months": <integer, typical full-time duration in months, usually 12, 18, 21, or 24>,
  "description": "2-3 sentence description of what makes this specific program distinctive. Mention focus areas, research strengths, or industry connections.",
  "url": "https://realistic-looking-url-for-the-program-page",
  "toefl_min": <integer or null, minimum TOEFL score required, typically 80-105>,
  "ielts_min": <number or null, minimum IELTS score, typically 6.5-7.5>,
  "gre_required": <true or false>,
  "gre_min_quant": <integer or null, minimum GRE Quant score if GRE required, typically 155-170>,
  "gmat_required": <true or false>,
  "gmat_min": <integer or null, minimum GMAT score if required, typically 550-720>,
  "letters_of_recommendation": <integer, typically 2 or 3>,
  "personal_statement_required": <true or false, almost always true>,
  "writing_sample_required": <true or false, true for humanities/social sciences>,
  "portfolio_required": <true or false, true for design/arts programs>,
  "min_gpa": <number or null, minimum undergraduate GPA if exist>,
  "application_deadline_fall": "Typical fall admission deadline for international students as a string, e.g. 'December 15' or 'January 15' or 'Rolling'",
  "application_deadline_spring": "Typical spring admission deadline or 'No spring admission'"
}}

Rules:
- Each program must be from a DIFFERENT university
- Tuition must be realistic for that university type (public vs private)
- Public universities: $20,000-$45,000 total; Private: $45,000-$120,000 total
- Duration: most STEM programs 18-21 months; MBA 18-24; MFA/Architecture 24; LLM 12
- GRE is increasingly optional — mix required and optional realistically
- GMAT only for business programs; GRE for all others
- Writing samples only for humanities, social sciences, policy, law
- Portfolios only for architecture, fine arts, design
- Make URLs realistic (like https://www.cs.mit.edu/academics/graduate or similar)
- Deadlines: most programs Dec 1 - Feb 15 for fall; Oct 1 - Nov 15 for spring

Return ONLY the JSON array, starting with [ and ending with ]"""


# ── API CALL ──────────────────────────────────────────────────────────────────

def call_claude(prompt: str, retries: int = 3) -> list[dict]:
    """Calls the Anthropic API and returns parsed JSON list."""
    import urllib.request

    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
    }
    body = json.dumps({
        "model": MODEL,
        "max_tokens": 4000,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()

    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=body,
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())

            text = data["content"][0]["text"].strip()

            # Strip markdown fences if Claude wrapped the JSON anyway
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

            return json.loads(text)

        except Exception as e:
            print(f"    Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(3 * (attempt + 1))
            else:
                raise
    return []


# ── MAIN GENERATION LOOP ──────────────────────────────────────────────────────

def generate_all_programs() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Iterates over every field, calls the API, collects all programs,
    then splits into two DataFrames: one for program info, one for requirements.
    """
    import random
    all_rows = []
    used_universities = set()

    print(f"\nGenerating programs across {len(FIELDS_TO_GENERATE)} fields...")
    print("(Each field = 1 API call = 10 programs)\n")

    for field_name, field_description in tqdm(FIELDS_TO_GENERATE, desc="Fields"):
        # Rotate universities so we don't repeat too much
        available = [u for u in UNIVERSITIES if u not in used_universities]
        if len(available) < 15:
            used_universities.clear()
            available = UNIVERSITIES.copy()

        sample_unis = random.sample(available, min(20, len(available)))

        try:
            prompt = build_prompt(field_name, field_description, sample_unis)
            programs = call_claude(prompt)

            for prog in programs:
                if isinstance(prog, dict) and "university" in prog:
                    all_rows.append(prog)
                    used_universities.add(prog.get("university", ""))

            time.sleep(1.0)  # Rate limit buffer

        except Exception as e:
            print(f"\n  ⚠️  Failed for field '{field_name}': {e}")
            continue

    print(f"\n✅  Generated {len(all_rows)} total programs")

    # ── Split into two tables ─────────────────────────────────────────────────

    program_cols = [
        "university", "program_name", "field", "country",
        "tuition_usd_total", "duration_months",
        "description", "url",
    ]
    requirement_cols = [
        "program_id",
        "toefl_min", "ielts_min",
        "gre_required", "gre_min_quant",
        "gmat_required", "gmat_min",
        "letters_of_recommendation",
        "personal_statement_required",
        "writing_sample_required",
        "portfolio_required",
        "min_gpa",
        "application_deadline_fall",
        "application_deadline_spring",
    ]

    df_all = pd.DataFrame(all_rows)

    # Add auto-increment program_id
    df_all.insert(0, "program_id", range(1, len(df_all) + 1))

    # Programs table: core info
    prog_cols_present = ["program_id"] + [c for c in program_cols if c in df_all.columns]
    df_programs = df_all[prog_cols_present].copy()

    # Requirements table: admission criteria, linked by program_id
    req_cols_present = ["program_id"] + [c for c in requirement_cols if c in df_all.columns]
    df_requirements = df_all[req_cols_present].copy()

    return df_programs, df_requirements


# ── SAVE TO SQLITE ────────────────────────────────────────────────────────────

def save_to_sqlite(df_programs: pd.DataFrame, df_requirements: pd.DataFrame):
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop and recreate tables for a clean run
    cursor.execute("DROP TABLE IF EXISTS masters_programs")
    cursor.execute("DROP TABLE IF EXISTS program_requirements")

    cursor.execute("""
        CREATE TABLE masters_programs (
            program_id            INTEGER PRIMARY KEY,
            university            TEXT NOT NULL,
            program_name          TEXT NOT NULL,
            field                 TEXT,
            country               TEXT DEFAULT 'USA',
            tuition_usd_total     INTEGER,
            duration_months       INTEGER,
            description           TEXT,
            url                   TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE program_requirements (
            req_id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            program_id                INTEGER REFERENCES masters_programs(program_id),
            toefl_min                 INTEGER,
            ielts_min                 REAL,
            gre_required              INTEGER,   -- 0/1 boolean
            gre_min_quant             INTEGER,
            gmat_required             INTEGER,   -- 0/1 boolean
            gmat_min                  INTEGER,
            letters_of_recommendation INTEGER,
            personal_statement_required INTEGER,
            writing_sample_required   INTEGER,
            portfolio_required        INTEGER,
            min_gpa                   REAL,
            application_deadline_fall  TEXT,
            application_deadline_spring TEXT
        )
    """)

    # Indexes
    cursor.execute("CREATE INDEX idx_prog_field ON masters_programs(field)")
    cursor.execute("CREATE INDEX idx_prog_uni ON masters_programs(university)")
    cursor.execute("CREATE INDEX idx_prog_tuition ON masters_programs(tuition_usd_total)")
    cursor.execute("CREATE INDEX idx_req_prog ON program_requirements(program_id)")

    conn.commit()

    # Insert programs
    df_programs.to_sql("masters_programs", conn, if_exists="append", index=False)

    # Insert requirements — convert bool columns to int for SQLite
    bool_cols = [
        "gre_required", "gmat_required",
        "personal_statement_required", "writing_sample_required", "portfolio_required",
    ]
    df_req = df_requirements.copy()
    for col in bool_cols:
        if col in df_req.columns:
            df_req[col] = df_req[col].apply(
                lambda x: 1 if x in [True, "true", "True", 1] else 0
            )
    df_req.to_sql("program_requirements", conn, if_exists="append", index=False)

    conn.close()

    print(f"\n✅  Saved to {DB_PATH}")
    print(f"   masters_programs:     {len(df_programs):,} rows")
    print(f"   program_requirements: {len(df_requirements):,} rows")


# ── PREVIEW ───────────────────────────────────────────────────────────────────

def preview_db():
    conn = sqlite3.connect(DB_PATH)

    print("\n── Sample: 5 programs with tuition + requirements ──")
    q = """
        SELECT p.university, p.program_name, p.tuition_usd_total,
               p.duration_months, r.toefl_min, r.gre_required,
               r.letters_of_recommendation, r.application_deadline_fall
        FROM   masters_programs p
        JOIN   program_requirements r USING (program_id)
        ORDER  BY p.tuition_usd_total DESC
        LIMIT  5
    """
    df = pd.read_sql(q, conn)
    print(df.to_string(index=False))

    print("\n── Programs by field ──")
    q2 = """
        SELECT field, COUNT(*) as programs,
               ROUND(AVG(tuition_usd_total)) as avg_tuition,
               ROUND(AVG(duration_months), 1) as avg_duration_months
        FROM   masters_programs
        GROUP  BY field
        ORDER  BY programs DESC
    """
    df2 = pd.read_sql(q2, conn)
    print(df2.to_string(index=False))

    conn.close()


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    if ANTHROPIC_API_KEY == "YOUR_KEY_HERE":
        print("⚠️  No Anthropic API key found.")
        print("   Get one at: https://console.anthropic.com/")
        print("   Then run:  export ANTHROPIC_API_KEY='sk-ant-...'")
        return

    print("=" * 60)
    print("  Master's Program Seed Data Generator")
    print("  Using Claude API — International Student AI Consultant")
    print("=" * 60)
    print(f"  Fields:    {len(FIELDS_TO_GENERATE)} disciplines")
    print(f"  Target:    ~{len(FIELDS_TO_GENERATE) * 10} programs total")
    print(f"  Output:    {DB_PATH}")
    print(f"  API calls: {len(FIELDS_TO_GENERATE)} (one per field)")
    print()

    df_programs, df_requirements = generate_all_programs()

    if df_programs.empty:
        print("\n⚠️  No data was generated. Check your API key and network.")
        return

    save_to_sqlite(df_programs, df_requirements)
    preview_db()

    print("\n── Next steps ──────────────────────────────────────────")
    print("  • Query with: sqlite3 data/programs.db")
    print("  • In Python:  conn = sqlite3.connect('data/programs.db')")
    print("  • Join tables ON program_id to get full program + requirements")
    print("  Example query:")
    print("""
    SELECT p.university, p.program_name, p.tuition_usd_total,
           r.toefl_min, r.gre_required, r.application_deadline_fall
    FROM   masters_programs p
    JOIN   program_requirements r USING (program_id)
    WHERE  p.field = 'Computer Science'
    ORDER  BY p.tuition_usd_total ASC;
    """)


if __name__ == "__main__":
    main()
