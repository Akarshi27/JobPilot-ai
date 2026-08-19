from dataclasses import dataclass
from typing import Protocol


@dataclass
class ApplicationResult:
    status: str
    reason: str
    external_application_id: str | None = None


class ApplicationProvider(Protocol):
    name: str
    def can_handle(self, url: str | None) -> bool: ...
    def prepare_application(self, application_data: dict) -> dict: ...
    def fill_application(self, application_data: dict) -> dict: ...
    def submit_application(self, application_data: dict) -> ApplicationResult: ...
    def get_status(self, external_id: str) -> str: ...


class ManualApplicationProvider:
    name = "manual"

    def can_handle(self, url: str | None) -> bool:
        return bool(url)

    def prepare_application(self, application_data: dict) -> dict:
        return application_data

    def fill_application(self, application_data: dict) -> dict:
        return application_data

    def submit_application(self, application_data: dict) -> ApplicationResult:
        return ApplicationResult(status="manual_required", reason="No supported application provider")

    def get_status(self, external_id: str) -> str:
        return "REVIEW_REQUIRED"


def provider_for(url: str | None) -> ApplicationProvider:
    return ManualApplicationProvider()