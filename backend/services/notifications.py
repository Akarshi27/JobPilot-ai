import os


class NotificationService:
    def notify_match(self, user_email: str, job_title: str, score: float) -> bool:
        # Email transport can be connected through SMTP without coupling it to scanning.
        return bool(os.getenv("SMTP_HOST"))

    def notify_application(self, user_email: str, status: str) -> bool:
        return bool(os.getenv("SMTP_HOST"))


notification_service = NotificationService()