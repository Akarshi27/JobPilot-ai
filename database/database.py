import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from database.base import Base

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/jobpilot.db",
)

# SQLite is retained only as a local fallback.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 30,
        },
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def create_database():
    # Import models so SQLAlchemy knows about all tables.
    from backend.models import (
        User,
        Profile,
        Resume,
        Skill,
        Job,
        JobSkill,
        JobMatch,
        Application,
        UserPreference,
    )

    Base.metadata.create_all(bind=engine)

    # PostgreSQL-compatible schema migration.
    inspector = inspect(engine)

    migrations = {
        "users": {
            "password_hash": "VARCHAR(255)",
        },
        "jobs": {
            "external_id": "VARCHAR(200)",
            "remote": "BOOLEAN DEFAULT FALSE",
            "requirements": "JSON",
            "preferred_skills": "JSON",
            "salary_min": "FLOAT",
            "salary_max": "FLOAT",
            "employment_type": "VARCHAR(50)",
            "experience_required": "VARCHAR(100)",
            "is_active": "BOOLEAN DEFAULT TRUE",
            "is_demo": "BOOLEAN DEFAULT FALSE",
        },
        "resumes": {
            "extraction_data": "JSON",
            "analysis_status": "VARCHAR(30) DEFAULT 'PENDING'",
            "analysis_error": "TEXT",
            "is_current": "BOOLEAN DEFAULT TRUE",
        },
        "profiles": {
            "education": "JSON",
            "projects": "JSON",
            "work_experience": "JSON",
            "certifications": "JSON",
        },
    }

    with engine.begin() as connection:
        for table, columns in migrations.items():
            existing_columns = {
                column["name"]
                for column in inspect(connection).get_columns(table)
            }

            for column, definition in columns.items():
                if column not in existing_columns:
                    connection.execute(
                        text(
                            f'ALTER TABLE "{table}" '
                            f'ADD COLUMN "{column}" {definition}'
                        )
                    )

        # Safe PostgreSQL-compatible data cleanup.
        connection.execute(
            text(
                "UPDATE jobs SET remote = FALSE "
                "WHERE remote IS NULL"
            )
        )

        connection.execute(
            text(
                "UPDATE jobs SET is_active = FALSE "
                "WHERE is_active IS NULL"
            )
        )

        connection.execute(
            text(
                "UPDATE jobs SET is_demo = FALSE "
                "WHERE is_demo IS NULL"
            )
        )

        connection.execute(
            text(
                "UPDATE resumes SET is_current = FALSE "
                "WHERE is_current IS NULL"
            )
        )


if __name__ == "__main__":
    create_database()
    print("Database initialized successfully.")