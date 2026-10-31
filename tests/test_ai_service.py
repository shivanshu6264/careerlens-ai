import json
import pytest

from app.ai_service import clean_json_response
from app.ai_service import clean_json_response, extract_soft_skills
from app.ai_service import (
    clean_json_response,
    extract_soft_skills,
    generate_json
)
from app.ai_service import (
    clean_json_response,
    extract_soft_skills,
    generate_json,
    analyze_job_description
)
from app.ai_service import (
    clean_json_response,
    extract_soft_skills,
    generate_json,
    analyze_job_description,
    analyze_resume
)
from app.ai_service import (
    clean_json_response,
    extract_soft_skills,
    generate_json,
    analyze_job_description,
    analyze_resume,
    generate_skill_recommendations
)


@pytest.mark.parametrize(
    "input_text, expected",
    [
        ('{"name": "Python"}', '{"name": "Python"}'),

        ('```json\n{"name": "Python"}\n```',
         '{"name": "Python"}'),

        ('```\n{"name": "Python"}\n```',
         '{"name": "Python"}'),

        ('  {"name": "Python"}  ',
         '{"name": "Python"}'),

        ('```json{"name": "Python"}```',
         '{"name": "Python"}')
    ]
)
def test_clean_json_response(input_text, expected):
    result = clean_json_response(input_text)

    assert result == expected

def test_extract_soft_skills():
    job_description = """
    Strong problem-solving and communication skills.
    Collaborate with product and engineering teams.
    """

    result = extract_soft_skills(job_description)

    assert result == [
        "Problem-solving",
        "Communication",
        "Collaboration"
    ]


def test_extract_soft_skills_with_no_matching_skills():
    job_description = """
    Python developer required.
    Experience with FastAPI and SQL.
    """

    result = extract_soft_skills(job_description)

    assert result == []


def test_extract_soft_skills_is_case_insensitive():
    job_description = """
    STRONG LEADERSHIP and TEAMWORK skills required.
    """

    result = extract_soft_skills(job_description)

    assert result == ["Teamwork", "Leadership"] 

def test_generate_json_success(mocker):
    mock_response = mocker.Mock()
    mock_response.text = '{"job_title": "Python Developer"}'

    mock_generate = mocker.patch(
        "app.ai_service.client.models.generate_content",
        return_value=mock_response
    )

    result = generate_json("Analyze this job description")

    assert result == {
        "job_title": "Python Developer"
    }

    mock_generate.assert_called_once_with(
        model="gemini-3.5-flash-lite",
        contents="Analyze this job description"
    )   

def test_generate_json_retries_on_empty_response(mocker):
    mock_response = mocker.Mock()
    mock_response.text = ""

    mock_generate = mocker.patch(
        "app.ai_service.client.models.generate_content",
        return_value=mock_response
    )

    mock_sleep = mocker.patch(
        "app.ai_service.time.sleep"
    )

    with pytest.raises(
        ValueError,
        match="Gemini returned an empty response."
    ):
        generate_json("Analyze this job description")

    assert mock_generate.call_count == 3

    assert mock_sleep.call_count == 2

    mock_sleep.assert_any_call(1)
    mock_sleep.assert_any_call(2)     

def test_generate_json_retries_on_invalid_json(mocker):
    mock_response = mocker.Mock()
    mock_response.text = "This is not valid JSON"

    mock_generate = mocker.patch(
        "app.ai_service.client.models.generate_content",
        return_value=mock_response
    )

    mock_sleep = mocker.patch(
        "app.ai_service.time.sleep"
    )

    with pytest.raises(json.JSONDecodeError):
        generate_json("Analyze this job description")

    assert mock_generate.call_count == 3
    assert mock_sleep.call_count == 2 

def test_generate_json_succeeds_after_retry(mocker):
    failed_response = mocker.Mock()
    failed_response.text = ""

    successful_response = mocker.Mock()
    successful_response.text = '{"job_title": "Python Developer"}'

    mock_generate = mocker.patch(
        "app.ai_service.client.models.generate_content",
        side_effect=[
            failed_response,
            successful_response
        ]
    )

    mock_sleep = mocker.patch(
        "app.ai_service.time.sleep"
    )

    result = generate_json("Analyze this job description")

    assert result == {
        "job_title": "Python Developer"
    }

    assert mock_generate.call_count == 2

    mock_sleep.assert_called_once_with(1)    

def test_generate_json_with_one_attempt(mocker):
    mock_generate = mocker.patch(
        "app.ai_service.client.models.generate_content",
        side_effect=RuntimeError("Gemini API failed")
    )

    mock_sleep = mocker.patch(
        "app.ai_service.time.sleep"
    )

    with pytest.raises(
        RuntimeError,
        match="Gemini API failed"
    ):
        generate_json(
            "Analyze this job description",
            max_attempts=1
        )

    mock_generate.assert_called_once()
    mock_sleep.assert_not_called()   

def test_analyze_job_description(mocker):
    mock_result = {
        "job_title": "Python Developer",
        "required_skills": ["Python", "FastAPI"],
        "preferred_skills": ["Docker"],
        "technical_skills": ["Python", "FastAPI", "Docker"],
        "soft_skills": [],
        "experience_requirement": "0-2 years",
        "main_responsibilities": ["Develop APIs"],
        "important_keywords": ["Backend"]
    }

    mock_generate = mocker.patch(
        "app.ai_service.generate_json",
        return_value=mock_result
    )

    job_description = """
    Python Developer required.
    Strong problem-solving and communication skills.
    """

    result = analyze_job_description(job_description)

    assert result["job_title"] == "Python Developer"

    assert result["soft_skills"] == [
        "Problem-solving",
        "Communication"
    ]

    mock_generate.assert_called_once()   

def test_analyze_resume(mocker):
    mock_result = {
        "candidate_name": "Shivanshu",
        "programming_languages": ["Python", "SQL"],
        "frameworks_and_libraries": ["FastAPI"],
        "generative_ai_skills": ["RAG"],
        "databases_and_tools": ["MySQL"],
        "soft_skills": ["Communication"],
        "projects": ["CareerLens AI"],
        "education": ["B.Tech Computer Science"],
        "certifications": ["Azure Fundamentals"],
        "coding_achievements": []
    }

    mock_generate = mocker.patch(
        "app.ai_service.generate_json",
        return_value=mock_result
    )

    resume_text = "Python developer with FastAPI and RAG experience."

    result = analyze_resume(resume_text)

    assert result["candidate_name"] == "Shivanshu"
    assert result["programming_languages"] == ["Python", "SQL"]
    assert result["frameworks_and_libraries"] == ["FastAPI"]

    mock_generate.assert_called_once()

    prompt = mock_generate.call_args[0][0]
    assert resume_text in prompt            

def test_generate_skill_recommendations(mocker):
    mock_result = {
        "recommendations": [
            {
                "skill": "Docker",
                "why_it_matters": "Useful for application deployment.",
                "what_to_learn": [
                    "Docker images",
                    "Docker containers"
                ],
                "practice_task": "Containerize a FastAPI application."
            }
        ]
    }

    mock_generate = mocker.patch(
        "app.ai_service.generate_json",
        return_value=mock_result
    )

    result = generate_skill_recommendations(
        ["Docker"],
        "Python Developer"
    )

    assert result["recommendations"][0]["skill"] == "Docker"

    assert result["message"] == (
        "Skill recommendations generated successfully."
    )

    mock_generate.assert_called_once()

    prompt = mock_generate.call_args[0][0]

    assert "Docker" in prompt
    assert "Python Developer" in prompt  

def test_generate_skill_recommendations_with_no_missing_skills(mocker):
    mock_generate = mocker.patch(
        "app.ai_service.generate_json"
    )

    result = generate_skill_recommendations(
        [],
        "Python Developer"
    )

    assert result == {
        "recommendations": [],
        "message": "No major technical skill gaps were identified."
    }

    mock_generate.assert_not_called()   

def test_analyze_job_description_without_soft_skills(mocker):
    mock_result = {
        "job_title": "Python Developer",
        "required_skills": ["Python"],
        "preferred_skills": [],
        "technical_skills": ["Python"],
        "soft_skills": ["Communication"],
        "experience_requirement": "0-2 years",
        "main_responsibilities": [],
        "important_keywords": []
    }

    mocker.patch(
        "app.ai_service.generate_json",
        return_value=mock_result
    )

    job_description = """
    Python Developer required.
    Experience with FastAPI and SQL.
    """

    result = analyze_job_description(job_description)

    assert result["soft_skills"] == []    

def test_extract_soft_skills_does_not_return_duplicates():
    job_description = """
    Strong communication and communication skills.
    Communicate effectively with the team.
    """

    result = extract_soft_skills(job_description)

    assert result == ["Communication"]
    assert len(result) == len(set(result))       