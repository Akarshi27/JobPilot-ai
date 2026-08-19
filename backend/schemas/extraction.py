from pydantic import BaseModel, Field, ConfigDict


class EducationEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    institution: str | None = None
    degree: str | None = None
    field: str | None = None
    dates: str | None = None


class ProjectEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)


class ExperienceEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    company: str | None = None
    title: str | None = None
    description: str | None = None
    dates: str | None = None


class ResumeExtraction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    candidate_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    summary: str | None = None
    education: list[EducationEntry] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    work_experience: list[ExperienceEntry] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)