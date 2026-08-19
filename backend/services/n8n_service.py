import requests
import os


N8N_WEBHOOK_URL = os.getenv("N8N_RESUME_WEBHOOK_URL", "")


def trigger_resume_processing(
    resume_id: int,
    user_id: int,
    resume_text: str
):
    if not N8N_WEBHOOK_URL:
        return None

    payload = {
        "resume_id": resume_id,
        "user_id": user_id,
        "resume_text": resume_text
    }

    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        print(f"n8n webhook error: {e}")
        return None