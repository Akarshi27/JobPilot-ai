from dotenv import load_dotenv

load_dotenv()

from backend.routes.resume_analysis import router as resume_analysis_router
from backend.routes.auth import router as auth_router
from fastapi import FastAPI
from database.database import create_database
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.matching import router as matching_router
from backend.routes.users import router as users_router
from backend.routes.profiles import router as profiles_router
from backend.routes.resumes import router as resumes_router
from backend.routes.analysis import router as analysis_router
from backend.routes.jobs import router as jobs_router
from backend.routes.job_analysis import router as job_analysis_router
from backend.routes.applications import router as applications_router
from backend.routes.preferences import router as preferences_router
app = FastAPI(
    title="JobPilot AI",
    description="Autonomous job discovery and skill-gap assistant",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://jobpilot-ai-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(matching_router)
app.include_router(job_analysis_router)
app.include_router(users_router)
app.include_router(profiles_router)
app.include_router(resumes_router)
app.include_router(analysis_router)
app.include_router(jobs_router)
app.include_router(resume_analysis_router)
app.include_router(auth_router)
app.include_router(applications_router)
app.include_router(preferences_router)


@app.on_event("startup")
def initialize_database():
    create_database()


@app.get("/")
def root():
    return {
        "message": "JobPilot AI is running",
        "status": "ok"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/health/ai")
def ai_health():
    from backend.services.ai_providers import get_ai_provider
    provider = get_ai_provider()
    return {
        "provider": provider.provider_name,
        "available": provider.is_available()
    }
