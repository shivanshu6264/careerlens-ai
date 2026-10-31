import pytest

from app.matching_service import normalize_skill
from app.matching_service import collect_resume_evidence
from app.matching_service import skill_supported_by_evidence
from app.matching_service import calculate_skill_match


@pytest.mark.parametrize(
    "input_skill, expected",
    [
        ("Python", "python"),
        ("RAG", "retrieval-augmented generation"),
        ("LLM", "large language models"),
        ("GenAI", "generative ai"),
        ("Postgres", "postgresql"),
        ("Fast API", "fastapi"),
        ("ReactJS", "react.js"),
        ("NodeJS", "node.js"),
        ("Sklearn", "scikit-learn"),
        ("  Python  ", "python"),
        ("Large Language Models (LLMs)", "large language models"),
        ("Unknown Skill", "unknown skill"),
    ]
)
def test_normalize_skill(input_skill, expected):
    assert normalize_skill(input_skill) == expected

from app.matching_service import collect_resume_skills


def test_collect_resume_skills():
    resume_analysis = {
        "programming_languages": ["Python", "SQL"],
        "frameworks_and_libraries": ["FastAPI", "React"],
        "generative_ai_skills": ["RAG", "LangChain"],
        "databases_and_tools": ["PostgreSQL", "Docker"],
        "projects": ["CareerLens AI"]
    }

    result = collect_resume_skills(resume_analysis)

    assert result == [
        "Python",
        "SQL",
        "FastAPI",
        "React",
        "RAG",
        "LangChain",
        "PostgreSQL",
        "Docker"
    ]    

def test_collect_resume_skills_handles_invalid_categories():
    resume_analysis = {
        "programming_languages": ["Python"],
        "frameworks_and_libraries": "FastAPI",
        "generative_ai_skills": None,
        "databases_and_tools": ["MySQL", 123, None]
    }

    result = collect_resume_skills(resume_analysis)

    assert result == ["Python", "MySQL"] 


def test_collect_resume_evidence():
    resume_analysis = {
        "skills": ["Python", "FastAPI"],
        "projects": [
            {
                "name": "CareerLens AI",
                "description": "Built a RAG-based application"
            }
        ],
        "certifications": {
            "name": "Azure Fundamentals"
        }
    }

    result = collect_resume_evidence(resume_analysis)

    assert "python" in result
    assert "fastapi" in result
    assert "careerlens ai" in result
    assert "rag-based application" in result
    assert "azure fundamentals" in result

@pytest.mark.parametrize(
    "skill, evidence, expected",
    [
        (
            "generative ai",
            "developed a generative ai assistant",
            True
        ),
        (
            "vector databases",
            "used chromadb and faiss",
            True
        ),
        (
            "rest apis",
            "designed restful api endpoints",
            True
        ),
        (
            "large language models",
            "worked with llms",
            True
        ),
        (
            "retrieval-augmented generation",
            "implemented rag pipeline",
            True
        ),
        (
            "python",
            "developed a python application",
            False
        ),
        (
            "unknown skill",
            "some project description",
            False
        )
    ]
)
def test_skill_supported_by_evidence(skill, evidence, expected):
    assert skill_supported_by_evidence(skill, evidence) is expected  

def test_calculate_skill_match_basic():
    job_analysis = {
        "required_skills": ["Python", "FastAPI", "Docker"],
        "preferred_skills": ["PostgreSQL", "AWS"]
    }

    resume_analysis = {
        "programming_languages": ["Python"],
        "frameworks_and_libraries": ["FastAPI"],
        "databases_and_tools": ["PostgreSQL"]
    }

    result = calculate_skill_match(
        job_analysis,
        resume_analysis
    )

    assert result["match_score"] == 62
    assert result["required_skill_match"] == 67
    assert result["preferred_skill_match"] == 50

    assert result["matched_skills"] == [
        "fastapi",
        "postgresql",
        "python"
    ]

    assert result["missing_skills"] == [
        "aws",
        "docker"
    ]     

def test_calculate_skill_match_uses_resume_evidence():
    job_analysis = {
        "required_skills": [
            "RAG",
            "Vector Databases"
        ],
        "preferred_skills": []
    }

    resume_analysis = {
        "programming_languages": ["Python"],
        "projects": [
            "Built a Retrieval-Augmented Generation application using FAISS."
        ]
    }

    result = calculate_skill_match(
        job_analysis,
        resume_analysis
    )

    assert result["matched_skills"] == [
    "retrieval-augmented generation",
    "vector databases"
    ]

    assert result["missing_skills"] == []

    assert result["evidence_matched_skills"] == [
    "retrieval-augmented generation",
    "vector databases"
    ]

    assert result["match_score"] == 70     

def test_calculate_skill_match_uses_technical_skills_fallback():
    job_analysis = {
        "required_skills": [],
        "preferred_skills": [],
        "technical_skills": ["Python", "FastAPI"]
    }

    resume_analysis = {
        "programming_languages": ["Python"],
        "frameworks_and_libraries": []
    }

    result = calculate_skill_match(
        job_analysis,
        resume_analysis
    )

    assert result["required_skill_match"] == 50
    assert result["preferred_skill_match"] == 0
    assert result["match_score"] == 35

    assert result["matched_skills"] == ["python"]
    assert result["missing_skills"] == ["fastapi"]

def test_calculate_skill_match_with_empty_job_requirements():
    job_analysis = {
        "required_skills": [],
        "preferred_skills": []
    }

    resume_analysis = {
        "programming_languages": ["Python", "SQL"]
    }

    result = calculate_skill_match(
        job_analysis,
        resume_analysis
    )

    assert result["match_score"] == 0
    assert result["required_skill_match"] == 0
    assert result["preferred_skill_match"] == 0

    assert result["matched_skills"] == []
    assert result["missing_skills"] == []   

def test_calculate_skill_match_with_all_skills_matched():
    job_analysis = {
        "required_skills": ["Python", "FastAPI"],
        "preferred_skills": ["PostgreSQL"]
    }

    resume_analysis = {
        "programming_languages": ["Python"],
        "frameworks_and_libraries": ["FastAPI"],
        "databases_and_tools": ["PostgreSQL"]
    }

    result = calculate_skill_match(
        job_analysis,
        resume_analysis
    )

    assert result["required_skill_match"] == 100
    assert result["preferred_skill_match"] == 100
    assert result["match_score"] == 100

    assert result["missing_skills"] == []
    assert result["matched_skills"] == [
        "fastapi",
        "postgresql",
        "python"
    ]         