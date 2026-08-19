from backend.services.job_sources.base import NormalizedJob


class InternshalaJobSource:
    name = "internshala"
    supported = False

    def search(self, query: str, location: str | None = None, limit: int = 25) -> list[NormalizedJob]:
        raise RuntimeError("Internshala automation is unavailable; use its official search URL manually")

    def fetch_job(self, external_id: str) -> NormalizedJob | None:
        raise RuntimeError("Internshala automation is unavailable")