![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC)
![Deployment](https://img.shields.io/badge/deployed-Render-46E3B7)

[![Live Demo](https://img.shields.io/badge/Live-Demo-success)](https://jobpilot-ai-frontend.onrender.com)
[![API Docs](https://img.shields.io/badge/API-Swagger-orange)](https://jobpilot-ai-fqi4.onrender.com/docs)
 # 🚀 JobPilot AI

> AI-powered job discovery and career intelligence platform that helps candidates discover relevant jobs, understand their fit, identify skill gaps, and manage their job-search workflow from a single platform.

## 🌐 Live Demo

| Service | Link |
|---|---|
| 🖥️ Frontend | https://jobpilot-ai-frontend.onrender.com |
| ⚡ Backend API | https://jobpilot-ai-fqi4.onrender.com |
| 📚 Swagger Docs | https://jobpilot-ai-fqi4.onrender.com/docs |
| 📖 ReDoc | https://jobpilot-ai-fqi4.onrender.com/redoc |

JobPilot AI is a full-stack career intelligence platform designed to reduce the manual effort involved in finding and applying for jobs.

Instead of simply displaying job listings, JobPilot AI focuses on **candidate-job intelligence** by combining job discovery, resume analysis, skill extraction, job matching, skill-gap identification, and application workflow management.

---

## ✨ Key Features

### 🔎 Intelligent Job Discovery

* Collect and organize relevant job opportunities.
* Store job information in a structured format.
* Avoid duplicate job listings.
* Filter jobs according to candidate preferences.
* Track job sources and metadata.
* Prepare jobs for automated matching.

### 📄 Resume Analysis

Upload a resume and extract useful career information such as:

* Name and contact information
* Education
* Technical skills
* Programming languages
* Frameworks and libraries
* Projects
* Certifications
* Work experience
* Relevant keywords

The extracted information can then be used by the matching engine.

### 🤖 AI-Powered Job Matching

JobPilot AI analyzes the relationship between a candidate's profile and a job description.

The matching system can consider:

* Technical skills
* Required skills
* Preferred skills
* Experience
* Education
* Projects
* Keywords
* Job requirements

The objective is to answer:

> **"How suitable is this job for me?"**

### 🧠 Skill-Gap Analysis

JobPilot AI compares the candidate's existing skills with the requirements of a target job.

Example:

```text
Job Requirements
├── Python          ✓
├── FastAPI         ✓
├── Docker          ✓
├── AWS             ✓
├── Kubernetes      ✗
└── PostgreSQL      ✗
```

This allows candidates to identify what they should learn next.

### 📊 Career Intelligence

The platform can provide insights such as:

* Job compatibility
* Missing skills
* Matching skills
* Job requirements
* Candidate strengths
* Recommended learning areas
* Application status
* Job-search progress

### 📌 Application Tracking

Track the progress of applications through stages such as:

```text
Discovered
    ↓
Saved
    ↓
Applied
    ↓
Assessment
    ↓
Interview
    ↓
Offer / Rejected
```

### ⚙️ Background Processing

The `worker/` component is designed for tasks that should run independently from normal API requests.

Possible workloads include:

* Job ingestion
* Job processing
* Duplicate detection
* Resume processing
* Matching
* Scheduled jobs
* Notifications

### 📁 Resume/File Uploads

Uploaded files are handled through the application's upload system and stored separately from source code.

---

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │      JobPilot AI     │
                    │      Frontend        │
                    │   React + Vite       │
                    └──────────┬───────────┘
                               │
                               │ HTTP / REST
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │      Backend         │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
      │   Routes    │   │  Services   │   │   Schemas   │
      └─────────────┘   └──────┬──────┘   └─────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
          ┌──────────┐   ┌───────────┐   ┌───────────┐
          │ Database │   │ AI / NLP  │   │   Worker  │
          └──────────┘   └───────────┘   └───────────┘
                │
                ▼
          ┌──────────┐
          │ Job Data │
          └──────────┘
```

---

# 🛠️ Tech Stack

## Frontend

* React
* Vite
* JavaScript / TypeScript ecosystem
* React Router
* Lucide React
* Modern CSS/UI tooling

## Backend

* Python
* FastAPI
* Uvicorn
* Pydantic
* REST APIs

## Database

* SQLite / relational database layer
* Database models and persistence layer

## AI / NLP

The AI layer is designed to support:

* Resume parsing
* Skill extraction
* Job-description analysis
* Semantic matching
* Skill-gap analysis
* Career recommendations

AI providers/models can be integrated independently from the core API.

## Development

* Git
* GitHub
* Python virtual environment
* npm
* pytest

---

# 📂 Project Structure

```text
jobpilot-ai/
│
├── backend/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   └── utils/
│
├── database/
│
├── data/
│
├── scripts/
│
├── src/
│
├── tests/
│
├── uploads/
│
├── worker/
│
├── .gitignore
├── requirements.txt
├── package.json
├── README.md
└── ...
```

### Backend

```text
backend/
├── models/
├── routes/
├── schemas/
├── services/
└── utils/
```

| Directory   | Responsibility              |
| ----------- | --------------------------- |
| `models/`   | Database models             |
| `routes/`   | API endpoints               |
| `schemas/`  | Request/response validation |
| `services/` | Business logic              |
| `utils/`    | Shared utilities            |

### Frontend

```text
src/
```

Contains the React/Vite application and its UI components, pages, routing, and frontend logic.

### Database

```text
database/
```

Responsible for database initialization, configuration, and persistence-related code.

### Worker

```text
worker/
```

Contains background-processing logic that can execute tasks independently of the API server.

### Data

```text
data/
```

Used for application data and locally processed datasets.

### Scripts

```text
scripts/
```

Contains helper scripts used during development, setup, processing, or maintenance.

### Tests

```text
tests/
```

Contains automated tests for the application.

### Uploads

```text
uploads/
```

Used for uploaded user files such as resumes.

> **Important:** User uploads, credentials, virtual environments, caches, and generated files should not be committed to Git.

---

# ⚡ Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/jobpilot-ai.git
cd jobpilot-ai
```

---

# 🐍 Backend Setup

## 2. Create a Python Virtual Environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

# 📦 Install Python Dependencies

```bash
pip install -r requirements.txt
```

Verify the installation:

```bash
pip list
```

---

# 🌐 Start the Backend

Run the FastAPI application with Uvicorn.

```bash
uvicorn backend.main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation will be available at:

```text
http://127.0.0.1:8000/docs
```

Alternative documentation:

```text
http://127.0.0.1:8000/redoc
```

---

# 💻 Frontend Setup

Open another terminal and navigate to the project directory.

Install JavaScript dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The terminal will display the local frontend URL.

Typically:

```text
http://localhost:5173
```

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

Example:

```env
APP_ENV=development

DATABASE_URL=sqlite:///./database/jobpilot.db

SECRET_KEY=your_secret_key

# AI provider
AI_API_KEY=your_api_key

# Optional external job APIs
JOB_API_KEY=your_api_key
```

The exact environment variables depend on the services enabled in the current implementation.

### Never commit secrets

Make sure `.env` is included in `.gitignore`:

```gitignore
.env
.env.*
!.env.example
```

For GitHub, provide:

```text
.env.example
```

containing placeholder values instead of real credentials.

---

# 🔄 JobPilot AI Workflow

The platform follows a pipeline similar to:

```text
                ┌───────────────┐
                │ Job Discovery │
                └───────┬───────┘
                        ↓
                ┌───────────────┐
                │ Job Extraction│
                └───────┬───────┘
                        ↓
                ┌───────────────┐
                │ Normalization │
                └───────┬───────┘
                        ↓
                ┌───────────────┐
                │ Deduplication │
                └───────┬───────┘
                        ↓
                ┌───────────────┐
                │ Job Database  │
                └───────┬───────┘
                        ↓
              ┌─────────────────────┐
              │ Candidate Profile  │
              │ + Resume Analysis  │
              └──────────┬──────────┘
                         ↓
                ┌────────────────┐
                │ Job Matching   │
                └───────┬────────┘
                        ↓
                ┌────────────────┐
                │ Skill Analysis │
                └───────┬────────┘
                        ↓
                ┌────────────────┐
                │ Recommendations│
                └───────┬────────┘
                        ↓
                ┌────────────────┐
                │ Application    │
                │ Tracking       │
                └────────────────┘
```

---

# 📄 Resume Processing Pipeline

```text
Resume Upload
     │
     ▼
File Validation
     │
     ▼
Text Extraction
     │
     ▼
Resume Parsing
     │
     ▼
Skill Extraction
     │
     ▼
Candidate Profile
     │
     ▼
Job Matching
```

The system can be extended to support multiple resume formats such as:

* PDF
* DOCX
* TXT

---

# 🧠 Job Matching

A job can be represented using structured information:

```text
Job
├── Title
├── Company
├── Location
├── Description
├── Required Skills
├── Preferred Skills
├── Experience
├── Education
└── Employment Type
```

The candidate profile can similarly contain:

```text
Candidate
├── Skills
├── Education
├── Experience
├── Projects
├── Certifications
└── Resume Content
```

The matching layer compares these two representations.

A conceptual score can be represented as:

```text
Match Score =
    Skill Compatibility
  + Experience Compatibility
  + Education Compatibility
  + Semantic Similarity
  + Preference Compatibility
```

The final implementation can use deterministic scoring, embeddings, an LLM, or a hybrid approach.

---

# 🎯 Skill-Gap Analysis

Skill-gap analysis identifies the difference between:

```text
Candidate Skills
        +
        ↓
Target Job Requirements
        =
Missing Skills
```

Example:

```text
Candidate:
Python
FastAPI
Git
SQL

Target Job:
Python
FastAPI
Docker
AWS
PostgreSQL
Kubernetes
```

Output:

```text
Strong:
✓ Python
✓ FastAPI

Needs Development:
○ Docker
○ AWS
○ PostgreSQL
○ Kubernetes
```

This information can then be used to generate personalized learning recommendations.

---

# 📡 API

JobPilot AI uses FastAPI to expose backend functionality through REST APIs.

The API is organized around separate route modules inside:

```text
backend/routes/
```

Typical API domains include:

```text
Resume
Jobs
Matching
Skills
Applications
Users
```

The exact endpoints should be verified from the current route implementation.

Interactive API documentation is available through FastAPI:

```text
/docs
```

---

# 🧪 Testing

Run the test suite with:

```bash
pytest
```

For more detailed output:

```bash
pytest -v
```

Run a specific test:

```bash
pytest tests/<test_file>.py
```

---

# 🧹 Code Quality

Before committing changes:

```bash
pytest
```

Check that:

* Backend starts correctly.
* Frontend builds successfully.
* API endpoints respond correctly.
* Database operations work.
* Resume uploads work.
* No secrets are committed.
* Tests pass.

---

# 🏭 Production Build

## Frontend

Create a production build:

```bash
npm run build
```

The generated production files are placed in:

```text
dist/
```

Preview the production build:

```bash
npm run preview
```

## Backend

For production, run FastAPI without development reload:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Production deployment should additionally use:

* Environment variables
* HTTPS
* Secure secrets
* Production database
* Proper logging
* Process management
* CORS configuration
* File-upload limits
* Authentication and authorization

---

# 🐳 Docker

Docker support can be added to provide a reproducible deployment environment.

A typical architecture would be:

```text
                Docker / Cloud
                      │
          ┌───────────┴───────────┐
          │                       │
     Frontend                 Backend
      Container               Container
                                  │
                           ┌──────┴──────┐
                           │             │
                       Database       Worker
```

Recommended production services:

```text
Frontend
Backend API
Worker
Database
```

---

# 🔒 Security Considerations

JobPilot AI processes potentially sensitive career information.

Important security practices include:

* Never commit API keys.
* Never commit `.env`.
* Validate uploaded files.
* Restrict upload size.
* Sanitize uploaded filenames.
* Validate API input.
* Use authentication for protected endpoints.
* Hash passwords rather than storing plaintext passwords.
* Use HTTPS in production.
* Configure CORS correctly.
* Restrict database access.
* Avoid exposing internal errors to clients.
* Keep dependencies updated.

---

# 📈 Future Roadmap

## Phase 1 — Core Platform

* [x] FastAPI backend
* [x] React frontend
* [x] Database layer
* [x] Job data layer
* [x] Resume upload infrastructure
* [x] Testing structure

## Phase 2 — Intelligence

* [ ] Advanced resume parsing
* [ ] Automatic skill extraction
* [ ] Semantic job matching
* [ ] Match scoring
* [ ] Skill-gap analysis
* [ ] Personalized recommendations

## Phase 3 — Job Intelligence

* [ ] Automated job discovery
* [ ] Multi-source job ingestion
* [ ] Duplicate detection
* [ ] Job freshness detection
* [ ] Personalized job ranking
* [ ] Job alerts

## Phase 4 — Application Management

* [ ] Application tracker
* [ ] Application status management
* [ ] Interview tracking
* [ ] Application analytics
* [ ] Follow-up reminders
* [ ] Resume version management

## Phase 5 — Advanced AI

* [ ] AI career assistant
* [ ] Resume optimization
* [ ] Job-specific resume recommendations
* [ ] Cover-letter generation
* [ ] Interview preparation
* [ ] Personalized learning paths
* [ ] Career trend analysis

---

# 🗺️ Long-Term Vision

JobPilot AI aims to become a complete **AI career operating system**.

Instead of:

```text
Search Jobs
     ↓
Read Job Description
     ↓
Compare Resume
     ↓
Find Missing Skills
     ↓
Apply
     ↓
Track Application
```

the goal is:

```text
                    ┌───────────────────┐
                    │   Candidate      │
                    │     Profile      │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   JobPilot AI    │
                    └─────────┬─────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    Job Discovery       Job Matching        Skill Analysis
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                    ┌───────────────────┐
                    │ Recommendations  │
                    └─────────┬─────────┘
                              ▼
                    ┌───────────────────┐
                    │ Application Mgmt │
                    └─────────┬─────────┘
                              ▼
                    ┌───────────────────┐
                    │ Career Insights  │
                    └───────────────────┘
```

The long-term objective is to make JobPilot AI an intelligent system that continuously understands:

**who the candidate is → what they know → what jobs fit them → what they are missing → what they should learn → which opportunities they should pursue.**

---

# 🤝 Contributing

Contributions are welcome.

### 1. Fork the repository

```bash
git fork
```

### 2. Create a branch

```bash
git checkout -b feature/your-feature
```

### 3. Make your changes

Follow the existing project structure and coding conventions.

### 4. Run tests

```bash
pytest
```

### 5. Commit

```bash
git add .
git commit -m "feat: add your feature"
```

### 6. Push

```bash
git push origin feature/your-feature
```

### 7. Open a Pull Request

Describe:

* What changed
* Why it changed
* How it was tested
* Any limitations

---

# 📝 Development Guidelines

Recommended commit prefixes:

```text
feat:     new functionality
fix:      bug fix
docs:     documentation
refactor: code restructuring
test:     tests
chore:    maintenance
```

Example:

```bash
git commit -m "feat: add resume skill extraction"
```

---

# 📊 Project Goals

JobPilot AI is designed around five major goals:

| Goal          | Description                            |
| ------------- | -------------------------------------- |
| 🔎 Discover   | Find relevant opportunities            |
| 🧠 Understand | Analyze jobs and candidate profiles    |
| 🎯 Match      | Determine candidate-job compatibility  |
| 📚 Improve    | Identify and close skill gaps          |
| 📌 Manage     | Track applications and career progress |

---

# ⚠️ Disclaimer

JobPilot AI is a career-assistance platform.

Job recommendations, match scores, AI-generated insights, and skill-gap analyses should be treated as **decision-support information**, not guaranteed predictions of hiring outcomes.

Users should independently verify job descriptions, company information, eligibility requirements, deadlines, and application details before applying.

---

# 📄 License

This project is currently under development.

Add the appropriate license before distributing the project publicly.

Example:

```text
MIT License
```

---

# 👩‍💻 Author

**Akarshi Srivastava**

Engineering Student
Computer Science & Artificial Intelligence / Machine Learning

Areas of interest:

* Artificial Intelligence
* Machine Learning
* Robotics
* Data Structures & Algorithms
* Backend Development
* Computer Vision

---

# ⭐ JobPilot AI

> **Find better opportunities. Understand your fit. Close your skill gaps. Build your career.**

If you find this project useful, consider giving the repository a ⭐ on GitHub.
