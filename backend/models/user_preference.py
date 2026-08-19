from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    application_mode: Mapped[str] = mapped_column(String(10), default="MANUAL")
    minimum_match_threshold: Mapped[int] = mapped_column(Integer, default=70)
    preferred_location: Mapped[str | None] = mapped_column(String(150))
    remote_preference: Mapped[bool] = mapped_column(Boolean, default=False)
    internship_preference: Mapped[bool] = mapped_column(Boolean, default=False)
    preferred_roles: Mapped[list] = mapped_column(JSON, default=list)
    preferred_domains: Mapped[list] = mapped_column(JSON, default=list)