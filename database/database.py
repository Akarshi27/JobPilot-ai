from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from database.base import Base


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database directory
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# SQLite database location
DATABASE_URL = f"sqlite:///{DATA_DIR / 'jobpilot.db'}"


# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
)


@event.listens_for(engine, "connect")
def _configure_sqlite(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.close()


# Create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def create_database():
    # Import models here so SQLAlchemy knows about all tables.
    from backend.models import User, Profile, Resume, Skill, Job, JobSkill, JobMatch, Application, UserPreference

    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        columns = {row[1] for row in connection.exec_driver_sql("PRAGMA table_info(users)")}
        if "password_hash" not in columns:
            connection.exec_driver_sql("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)")
        migrations = {
            "jobs": {
                "external_id": "VARCHAR(200)",
                "remote": "BOOLEAN DEFAULT 0",
                "requirements": "JSON",
                "preferred_skills": "JSON",
                "salary_min": "FLOAT",
                "salary_max": "FLOAT",
                "employment_type": "VARCHAR(50)",
                "experience_required": "VARCHAR(100)",
                "is_active": "BOOLEAN DEFAULT 1",
                "is_demo": "BOOLEAN DEFAULT 0",
            },
            "resumes": {
                "extraction_data": "JSON",
                "analysis_status": "VARCHAR(30) DEFAULT 'PENDING'",
                "analysis_error": "TEXT",
                "is_current": "BOOLEAN DEFAULT 1",
            },
            "profiles": {
                "education": "JSON",
                "projects": "JSON",
                "work_experience": "JSON",
                "certifications": "JSON",
            },
        }
        for table, table_columns in migrations.items():
            existing = {row[1] for row in connection.exec_driver_sql(f"PRAGMA table_info({table})")}
            for column, definition in table_columns.items():
                if column not in existing:
                    connection.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        connection.exec_driver_sql("UPDATE jobs SET remote = 0 WHERE remote IS NULL")
        connection.exec_driver_sql("UPDATE jobs SET requirements = '[]' WHERE requirements IS NULL")
        connection.exec_driver_sql("UPDATE jobs SET preferred_skills = '[]' WHERE preferred_skills IS NULL")
        connection.exec_driver_sql("UPDATE jobs SET is_active = 0 WHERE is_active IS NULL")
        connection.exec_driver_sql("UPDATE jobs SET is_active = 0 WHERE lower(job_url) LIKE '%example.com%' OR lower(job_url) LIKE '%localhost%' OR job_url IS NULL OR trim(job_url) = ''")
        connection.exec_driver_sql("UPDATE jobs SET is_demo = 0 WHERE is_demo IS NULL")
        connection.exec_driver_sql("UPDATE resumes SET is_current = 0 WHERE is_current IS NULL")
        connection.exec_driver_sql("UPDATE resumes SET is_current = 1 WHERE id IN (SELECT MAX(id) FROM resumes GROUP BY user_id)")


if __name__ == "__main__":
    create_database()
    print("Database initialized successfully.")