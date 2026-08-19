from pydantic import BaseModel


class ProfileCreate(BaseModel):
    phone: str | None = None
    location: str | None = None
    headline: str | None = None
    summary: str | None = None
    years_of_experience: int = 0
    target_role: str | None = None


class ProfileResponse(ProfileCreate):
    id: int
    user_id: int
    education: list = []
    projects: list = []
    work_experience: list = []
    certifications: list = []

    class Config:
        from_attributes = True