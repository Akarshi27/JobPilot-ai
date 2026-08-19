from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class JobSkill(Base):
    __tablename__ = "job_skills"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    job = relationship(
        "Job",
        back_populates="skills"
    )

    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "name",
            name="uq_job_skill"
        ),
    )