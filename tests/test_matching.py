from backend.services.matching import semantic_match


def test_paraphrased_backend_project_is_eligible(monkeypatch):
    monkeypatch.setattr(
        "backend.services.matching.embed_text",
        lambda text: (
            [1.0, 0.0]
            if "backend" in text.lower() or "api" in text.lower()
            else [0.8, 0.6]
        ),
    )

    result = semantic_match(
        "Built a REST API backend using FastAPI.",
        "Backend engineering intern responsible for building APIs using Python web frameworks.",
        ["FastAPI", "Python"],
        ["Python web frameworks"],
    )

    assert result["match_percentage"] >= 70
    assert result["eligible_for_application"] is True


def test_unrelated_senior_role_is_not_eligible(monkeypatch):
    # Keep this unit test completely offline.
    # The test is about matching logic, not Gemini/OpenAI/Ollama.
    monkeypatch.setattr(
        "backend.services.matching.embed_text",
        lambda text: (
            [1.0, 0.0]
            if any(
                keyword in text.lower()
                for keyword in ["python", "pandas"]
            )
            else [0.0, 1.0]
        ),
    )

    result = semantic_match(
        "Python data analysis and Pandas coursework.",
        "Senior Java Spring Boot engineer leading enterprise services with five years experience.",
        ["Python", "Pandas"],
        ["Java", "Spring Boot"],
    )

    assert result["match_percentage"] < 70
    assert result["eligible_for_application"] is False