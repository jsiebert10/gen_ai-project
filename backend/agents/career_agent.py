import json

from agents.llm_client import get_llm_response

SYSTEM_PROMPT = """
You are a career outlook assistant for international students.
Given a student's field of study and target country, provide
a realistic job market analysis and career pathway guidance.

Consider:
- Job market demand for the field
- Average salaries in the target country
- Top hiring companies
- H1B or work visa sponsorship trends (if USA)
- In-demand specializations within the field
- Realistic timeline from graduation to employment

Respond ONLY in JSON format like this:
{
    "field": "Computer Science",
    "country": "USA",
    "job_market_outlook": "Very Strong",
    "average_salary_usd": 110000,
    "top_roles": [
        "Software Engineer",
        "Data Scientist",
        "ML Engineer"
    ],
    "top_companies": [
        "Google",
        "Microsoft",
        "Amazon"
    ],
    "sponsorship_likelihood": "High",
    "in_demand_skills": [
        "Python",
        "Machine Learning",
        "Cloud Computing"
    ],
    "timeline_to_employment": "3-6 months after graduation",
    "insight": "CS graduates in the USA have strong job prospects with many companies actively sponsoring H1B visas"
}
"""


def run_career_agent(career_input: dict) -> dict:
    """
    Provide career outlook based on field of study and target country.

    Takes the student's intended field and destination country and
    returns a realistic job market analysis including salaries,
    top roles, hiring companies and sponsorship trends.

    Args:
        career_input: A dictionary containing:
                     - field_of_study (str): Student's intended field.
                     - destination_country (str): Target country for career.
                     - education_level (str): Degree level being pursued.

    Returns:
        A dictionary with:
        - field (str): Field of study.
        - country (str): Target country.
        - job_market_outlook (str): Overall market strength.
        - average_salary_usd (int): Expected average salary.
        - top_roles (list): Most common job titles.
        - top_companies (list): Top hiring companies.
        - sponsorship_likelihood (str): Visa sponsorship chances.
        - in_demand_skills (list): Skills to prioritize.
        - timeline_to_employment (str): Expected job search duration.
        - insight (str): Key takeaway for the student.
    """
    user_message = f"Provide career outlook for this student: {career_input}"
    response = get_llm_response(SYSTEM_PROMPT, user_message)
    return json.loads(response)
