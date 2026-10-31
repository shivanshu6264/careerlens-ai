from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "CareerLens AI is running"
    }


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "CareerLens AI",
        "version": "1.0.0",
    }

def test_analyze_job_rejects_short_description():
    response = client.post(
        "/analyze-job",
        json={"job_description": "Python developer"},
    )

    assert response.status_code == 422

def test_analyze_job_success(mocker):
    mock_result = {
        "job_title": "Python Developer",
        "required_skills": ["Python", "FastAPI"],
        "preferred_skills": ["Docker"],
    }

    mocker.patch(
        "app.main.analyze_job_description",
        return_value=mock_result,
    )

    response = client.post(
        "/analyze-job",
        json={
            "job_description": (
                "We are looking for a Python Developer "
                "with experience in FastAPI and REST APIs."
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["analysis"] == mock_result 

def test_analyze_resume_rejects_non_pdf():
    response = client.post(
        "/analyze-resume",
        files={
            "file": (
                "resume.txt",
                b"This is a text file.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are supported."  

def test_analyze_resume_rejects_empty_file():
    response = client.post(
        "/analyze-resume",
        files={
            "file": (
                "resume.pdf",
                b"",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded file is empty." 

def test_analyze_resume_rejects_large_file():
    large_file = b"a" * (5 * 1024 * 1024 + 1)

    response = client.post(
        "/analyze-resume",
        files={
            "file": (
                "large_resume.pdf",
                large_file,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 413
    assert response.json()["detail"] == (
        "Resume file is too large. Maximum size is 5 MB."
    )    

def test_analyze_resume_success(mocker):
    mocker.patch(
        "app.main.extract_text_from_pdf",
        return_value="Python developer with FastAPI experience.",
    )

    mock_result = {
        "technical_skills": ["Python", "FastAPI"],
        "projects": ["CareerLens AI"],
    }

    mocker.patch(
        "app.main.analyze_resume",
        return_value=mock_result,
    )

    response = client.post(
        "/analyze-resume",
        files={
            "file": (
                "resume.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "resume.pdf"
    assert response.json()["analysis"] == mock_result

def test_match_resume_success(mocker):
    mock_result = {
        "match_score": 85,
        "required_skill_match": 90,
        "preferred_skill_match": 70,
        "matched_skills": ["Python", "FastAPI"],
        "missing_skills": ["Docker"],
        "missing_required_skills": [],
        "missing_preferred_skills": ["Docker"],
        "evidence_matched_skills": ["Python", "FastAPI"],
    }

    mocker.patch(
        "app.main.calculate_skill_match",
        return_value=mock_result,
    )

    mock_recommendations = {
        "recommendations": [
            "Learn Docker fundamentals."
        ]
    }

    mocker.patch(
        "app.main.generate_skill_recommendations",
        return_value=mock_recommendations,
    )

    response = client.post(
        "/match-resume",
        json={
            "job_analysis": {
                "job_title": "Python Developer"
            },
            "resume_analysis": {
                "technical_skills": ["Python", "FastAPI"]
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["match_score"] == 85
    assert response.json()["matched_skills"] == [
        "Python",
        "FastAPI",
    ]
    assert response.json()["recommendations"] == mock_recommendations  

def test_match_resume_without_missing_skills(mocker):
    mock_result = {
        "match_score": 100,
        "required_skill_match": 100,
        "preferred_skill_match": 100,
        "matched_skills": ["Python", "FastAPI"],
        "missing_skills": [],
        "missing_required_skills": [],
        "missing_preferred_skills": [],
        "evidence_matched_skills": ["Python", "FastAPI"],
    }

    mocker.patch(
        "app.main.calculate_skill_match",
        return_value=mock_result,
    )

    mock_recommendations = mocker.patch(
        "app.main.generate_skill_recommendations"
    )

    response = client.post(
        "/match-resume",
        json={
            "job_analysis": {
                "job_title": "Python Developer"
            },
            "resume_analysis": {
                "technical_skills": ["Python", "FastAPI"]
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["match_score"] == 100
    assert response.json()["missing_skills"] == []

    mock_recommendations.assert_not_called()

    assert response.json()["recommendations"] == {
        "recommendations": [],
        "message": "No major technical skill gaps were identified.",
    }      

def test_match_resume_handles_internal_error(mocker):
    mocker.patch(
        "app.main.calculate_skill_match",
        side_effect=Exception("Matching service failed"),
    )

    response = client.post(
        "/match-resume",
        json={
            "job_analysis": {
                "job_title": "Python Developer"
            },
            "resume_analysis": {
                "technical_skills": ["Python"]
            },
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Resume matching failed."  

def test_analyze_job_handles_ai_service_error(mocker):
    mocker.patch(
        "app.main.analyze_job_description",
        side_effect=Exception("Gemini service unavailable"),
    )

    response = client.post(
        "/analyze-job",
        json={
            "job_description": (
                "We are looking for a Python Developer "
                "with experience in FastAPI and REST APIs."
            )
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "AI job analysis is temporarily unavailable."
    )      

def test_analyze_resume_handles_ai_service_error(mocker):
    mocker.patch(
        "app.main.extract_text_from_pdf",
        return_value="Python developer with FastAPI experience.",
    )

    mocker.patch(
        "app.main.analyze_resume",
        side_effect=Exception("Gemini service unavailable"),
    )

    response = client.post(
        "/analyze-resume",
        files={
            "file": (
                "resume.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "AI resume analysis is temporarily unavailable."
    )    

def test_analyze_resume_rejects_unreadable_pdf(mocker):
    mocker.patch(
        "app.main.extract_text_from_pdf",
        return_value="   "
    )

    response = client.post(
        "/analyze-resume",
        files={
            "file": (
                "resume.pdf",
                b"fake pdf content",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Could not extract text from the PDF."

def test_analyze_job_rejects_whitespace_description():
    response = client.post(
        "/analyze-job",
        json={"job_description": " " * 25}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Job description cannot be empty."    