from backend.services.job_sources.base import NormalizedJob


class CompanyCareerSource:
    name = "company_career"
    supported = False

    def search(self, query: str, location: str | None = None, limit: int = 25) -> list[NormalizedJob]:
        raise RuntimeError("Company career pages require an explicitly configured permitted integration")

    def fetch_job(self, external_id: str) -> NormalizedJob | None:
        raise RuntimeError("Company career integration is not configured")