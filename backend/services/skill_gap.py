def generate_skill_gap(
    matched_skills: list[str],
    missing_skills: list[str]
) -> dict:

    priority = []

    for skill in missing_skills:
        priority.append({
            "skill": skill,
            "priority": "high"
        })

    if not missing_skills:
        summary = "No required skills are missing."
    else:
        summary = (
            f"You are missing {len(missing_skills)} "
            f"required skill(s) for this job."
        )

    return {
        "summary": summary,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "priority": priority
    }