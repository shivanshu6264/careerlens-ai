
from typing import Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.ai_service import (
    analyze_job_description,
    analyze_resume,
    generate_skill_recommendations,
)
from app.resume_parser import extract_text_from_pdf
from app.matching_service import calculate_skill_match


app = FastAPI(
    title="CareerLens AI",
    description="AI-powered Job Description and Resume Analysis platform.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Health",
            "description": "API health and service status.",
        },
        {
            "name": "Job Analysis",
            "description": "Analyze software engineering job descriptions.",
        },
        {
            "name": "Resume Analysis",
            "description": "Analyze candidate resumes.",
        },
        {
            "name": "Resume Matching",
            "description": "Match resumes against job requirements.",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request models

class JobRequest(BaseModel):
    job_description: str = Field(
        ...,
        min_length=20,
        max_length=20000,
        description="Job description text to analyze",
    )


class MatchRequest(BaseModel):
    job_analysis: dict[str, Any]
    resume_analysis: dict[str, Any]


# Response models

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class JobAnalysisResponse(BaseModel):
    analysis: dict[str, Any]


class ResumeAnalysisResponse(BaseModel):
    filename: str
    analysis: dict[str, Any]


class MatchResponse(BaseModel):
    match_score: int
    required_skill_match: int
    preferred_skill_match: int
    matched_skills: list[str]
    missing_skills: list[str]
    missing_required_skills: list[str]
    missing_preferred_skills: list[str]
    evidence_matched_skills: list[str]
    recommendations: dict[str, Any]


# Health endpoints

@app.get("/", tags=["Health"])
def home():
    return {"message": "CareerLens AI is running"}


@app.get(
    "/health",
    tags=["Health"],
    response_model=HealthResponse,
)
def health_check():
    return {
        "status": "healthy",
        "service": "CareerLens AI",
        "version": "1.0.0",
    }


# Job analysis

@app.post(
    "/analyze-job",
    tags=["Job Analysis"],
    response_model=JobAnalysisResponse,
)
def analyze_job(request: JobRequest):
    if not request.job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty.",
        )

    try:
        result = analyze_job_description(request.job_description)
        return {"analysis": result}

    except Exception as e:
        print("Job analysis error:", type(e).__name__, str(e))
        raise HTTPException(
            status_code=503,
            detail="AI job analysis is temporarily unavailable.",
        )


# Resume analysis

@app.post(
    "/analyze-resume",
    tags=["Resume Analysis"],
    response_model=ResumeAnalysisResponse,
)
def analyze_resume_endpoint(file: UploadFile = File(...)):
    max_file_size = 5 * 1024 * 1024  # 5 MB

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    try:
        file_content = file.file.read()

        if len(file_content) > max_file_size:
            raise HTTPException(
                status_code=413,
                detail="Resume file is too large. Maximum size is 5 MB.",
            )

        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        file.file.seek(0)
        resume_text = extract_text_from_pdf(file.file)

        if not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the PDF.",
            )

        analysis = analyze_resume(resume_text)

        return {
            "filename": file.filename,
            "analysis": analysis,
        }

    except HTTPException:
        raise

    except Exception as e:
        print("Resume analysis error:", type(e).__name__, str(e))
        raise HTTPException(
            status_code=503,
            detail="AI resume analysis is temporarily unavailable.",
        )

    finally:
        file.file.close()


# Resume matching

@app.post(
    "/match-resume",
    tags=["Resume Matching"],
    response_model=MatchResponse,
)
def match_resume(request: MatchRequest):
    try:
        result = calculate_skill_match(
            request.job_analysis,
            request.resume_analysis,
        )

        if result["missing_skills"]:
            recommendations = generate_skill_recommendations(
                result["missing_skills"],
                request.job_analysis.get("job_title", "Unknown Role"),
            )
        else:
            recommendations = {
                "recommendations": [],
                "message": "No major technical skill gaps were identified.",
            }

        result["recommendations"] = recommendations
        return result

    except Exception as e:
        print("Matching error:", type(e).__name__, str(e))
        raise HTTPException(
            status_code=500,
            detail="Resume matching failed.",
        )
