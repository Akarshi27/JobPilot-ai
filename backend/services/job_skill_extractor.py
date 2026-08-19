from backend.services.skill_extractor import extract_skills


def extract_job_skills(job_description: str) -> list[str]:
    """
    Extract normalized skills from a job description.
    Uses the same canonical skill dictionary as resume analysis.
    """

    return extract_skills(job_description)