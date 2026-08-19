from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, Boolean, Float, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    company: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    location: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    job_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    external_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    remote: Mapped[bool] = mapped_column(Boolean, default=False)
    requirements: Mapped[list] = mapped_column(JSON, default=list)
    preferred_skills: Mapped[list] = mapped_column(JSON, default=list)
    salary_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    experience_required: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    skills = relationship(
        "JobSkill",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    @property
    def url(self) -> str | None:
        return self.job_url

    @property
    def source_url(self) -> str | None:
        return self.job_url

    __table_args__ = (
        Index("ix_jobs_source_external_id", "source", "external_id", unique=True),
    )