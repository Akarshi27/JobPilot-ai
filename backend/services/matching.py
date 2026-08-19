from backend.services.embedding_service import embed_text, similarity


def calculate_match(candidate_skills: list[str], required_skills: list[str]) -> dict:

    candidate_map = {
        skill.lower(): skill
        for skill in candidate_skills
    }

    required_map = {
        skill.lower(): skill
        for skill in required_skills
    }

    matched_keys = (
        candidate_map.keys()
        & required_map.keys()
    )

    missing_keys = (
        required_map.keys()
        - candidate_map.keys()
    )

    matched = sorted(
        required_map[key]
        for key in matched_keys
    )

    missing = sorted(
        required_map[key]
        for key in missing_keys
    )

    # Keep this legacy endpoint deterministic, but do not use overlap as the
    # production score. The recommendation path below compares meaning.
    score = similarity(embed_text("; ".join(candidate_skills)), embed_text("; ".join(required_skills))) * 100

    return {
        "match_score": round(score, 2),
        "matched_skills": matched,
        "missing_skills": missing,
        "total_required_skills": len(required_map),
        "total_matched_skills": len(matched)
    }


def semantic_match(
    candidate_text: str,
    job_text: str,
    candidate_skills: list[str] | None = None,
    required_skills: list[str] | None = None,
    candidate_experience: str = "",
    candidate_education: str = "",
) -> dict:
    candidate_skills = candidate_skills or []
    required_skills = required_skills or []
    semantic_score = similarity(embed_text(candidate_text), embed_text(job_text))
    candidate_context_embedding = embed_text(candidate_text)
    skill_scores = [similarity(embed_text(skill), embed_text(job_text)) for skill in candidate_skills]
    requirement_scores = [max([similarity(embed_text(skill), embed_text(requirement)) for skill in candidate_skills] + [similarity(candidate_context_embedding, embed_text(requirement))]) for requirement in required_skills]
    skill_fit = sum(requirement_scores) / max(1, len(requirement_scores))
    project_fit = similarity(embed_text(candidate_text), embed_text(job_text))
    experience_fit = 0.8 if any(term in job_text.lower() for term in ("intern", "entry level", "junior")) else (0.45 if not candidate_experience else 0.75)
    education_fit = similarity(embed_text(candidate_education or candidate_text), embed_text(job_text))
    score = round(100 * (semantic_score * 0.55 + skill_fit * 0.15 + experience_fit * 0.15 + project_fit * 0.10 + education_fit * 0.05), 2)
    matched = [skill for skill, fit in zip(candidate_skills, skill_scores) if fit >= 0.35]
    missing = [skill for skill, fit in zip(required_skills, requirement_scores) if fit < 0.35]
    if semantic_score >= 0.62 and not missing and experience_fit >= 0.7:
        score = max(score, 70.0)
    return {
        "match_percentage": score,
        "eligible_for_application": score >= 70,
        "confidence": round(min(0.99, 0.45 + semantic_score * 0.5), 2),
        "semantic_score": round(semantic_score * 100, 2),
        "skill_score": round(skill_fit * 100, 2),
        "project_score": round(project_fit * 100, 2),
        "experience_score": round(experience_fit * 100, 2),
        "education_score": round(education_fit * 100, 2),
        "matched_skills": matched,
        "missing_skills": missing,
        "semantic_similarity": round(semantic_score, 4),
        "experience_assessment": "Compatible with the candidate context" if experience_fit >= 0.7 else "Experience alignment needs review",
        "education_assessment": "Education appears relevant" if education_fit >= 0.35 else "Education relevance is limited",
        "why_match": "The resume and job responsibilities are semantically aligned, including project and capability context.",
        "why_not_perfect": f"Review missing or weak requirements: {', '.join(missing) or 'none identified'}.",
        "recommendation": "Eligible to apply" if score >= 70 else "Do not apply automatically; use the gaps to improve your profile",
    }