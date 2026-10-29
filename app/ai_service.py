import json
import time

from google import genai

from app.config import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)

MODEL_NAME = "gemini-3.5-flash-lite"


def clean_json_response(result: str):
    """
    Removes markdown code fences if Gemini returns JSON inside them.
    """

    result = result.strip()

    if result.startswith("```json"):
        result = result[7:]

    elif result.startswith("```"):
        result = result[3:]

    if result.endswith("```"):
        result = result[:-3]

    return result.strip()


def generate_json(prompt: str, max_attempts: int = 3):
    """
    Sends a prompt to Gemini and converts the response into Python JSON.
    Retries temporary failures.
    """

    for attempt in range(max_attempts):

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            if not response.text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            result = clean_json_response(
                response.text
            )

            return json.loads(result)

        except Exception as e:

            print(
                f"Gemini attempt {attempt + 1} failed:",
                type(e).__name__,
                str(e)
            )

            if attempt == max_attempts - 1:
                raise

            wait_time = 2 ** attempt

            print(
                f"Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)


def extract_soft_skills(job_description: str):
    """
    Detect common soft skills directly from the job description.

    This is deterministic and does not depend on Gemini.
    """

    text = job_description.lower()

    soft_skill_patterns = {

        "Problem-solving": [
            "problem-solving",
            "problem solving",
            "problem solver",
            "problem solving skills",
            "problem-solving skills"
        ],

        "Communication": [
            "communication",
            "communication skills",
            "communicate effectively",
            "strong communication"
        ],

        "Teamwork": [
            "teamwork",
            "team work",
            "working in a team",
            "work in a team"
        ],

        "Collaboration": [
            "collaboration",
            "collaborate",
            "collaborating",
            "cross-functional collaboration",
            "work collaboratively"
        ],

        "Leadership": [
            "leadership",
            "leadership skills",
            "lead a team",
            "leading a team"
        ],

        "Adaptability": [
            "adaptability",
            "adaptable",
            "ability to adapt"
        ],

        "Time Management": [
            "time management",
            "manage time"
        ],

        "Critical Thinking": [
            "critical thinking",
            "analytical thinking"
        ],

        "Decision Making": [
            "decision making",
            "decision-making",
            "decision making skills",
            "decision-making skills"
        ]
    }

    detected_skills = []

    for skill, patterns in soft_skill_patterns.items():

        for pattern in patterns:

            if pattern in text:

                detected_skills.append(skill)

                break

    print(
        "DETECTED SOFT SKILLS:",
        detected_skills
    )

    return detected_skills



def analyze_job_description(job_description: str):

    prompt = f"""
You are an AI career assistant specialized in analyzing
software engineering job descriptions.

Analyze the job description carefully.

Extract the following:

1. Job title
2. Required technical skills
3. Preferred technical skills
4. All technical skills
5. Soft skills
6. Experience requirement
7. Main responsibilities
8. Important keywords

REQUIRED_SKILLS:

Include ONLY technical skills that are explicitly required
for the role.

Examples:

Python
FastAPI
REST APIs
SQL
PostgreSQL
Large Language Models
Generative AI
Retrieval-Augmented Generation
LangChain

Do NOT include soft skills in required_skills.

PREFERRED_SKILLS:

Include ONLY technical skills that are explicitly described
as preferred, nice-to-have, bonus, or optional.

Examples:

Docker
AWS
Microsoft Azure
LangGraph
Agentic AI
Redis
Vector Databases

Do NOT include soft skills in preferred_skills.

IMPORTANT PREFERRED-SKILL EXTRACTION:

Carefully scan the entire job description for phrases such as:
"preferred", "nice to have", "good to have", "bonus",
"optional", "ideally", and "would be a plus".

Extract the technical skills associated with these phrases
into preferred_skills.

If the job description does not explicitly identify any
preferred or optional technical skills, return an empty list.

Do not classify a required skill as preferred unless the
description supports that classification.

TECHNICAL_SKILLS:

Include all technical skills mentioned in the job description,
including both required and preferred technical skills.

Technical skills can include:

Programming languages
Frameworks
Libraries
Databases
APIs
Cloud platforms
Developer tools
AI technologies
AI concepts
DevOps technologies
Infrastructure technologies

Examples:

Python
FastAPI
REST APIs
SQL
PostgreSQL
Docker
Git
GitHub
LangChain
LangGraph
Large Language Models
Generative AI
Retrieval-Augmented Generation
Vector Databases
Embeddings
Redis
Microsoft Azure
AWS
CI/CD Pipelines

SOFT_SKILLS:

Look specifically for human and workplace skills.

Examples:

Communication
Teamwork
Collaboration
Problem-solving
Leadership
Adaptability
Time Management
Critical Thinking
Decision Making

IMPORTANT:

If the job description explicitly mentions a soft skill,
it MUST be included in soft_skills.

For example, if the description says:

"Strong problem-solving and communication skills"

return:

[
    "Problem-solving",
    "Communication"
]

If the description says:

"Collaborate with product and engineering teams"

include:

"Collaboration"

Do not leave soft_skills empty when soft skills are
explicitly present.

CRITICAL SEPARATION RULE:

Soft skills MUST NEVER appear inside:

required_skills
preferred_skills
technical_skills

Soft skills must ONLY appear inside:

soft_skills

For example:

WRONG:

"required_skills": [
    "Python",
    "FastAPI",
    "Communication"
]

CORRECT:

"required_skills": [
    "Python",
    "FastAPI"
],

"soft_skills": [
    "Communication"
]

NORMALIZATION RULES:

Use one canonical name for the same concept.

For example:

"LLM" and "LLMs"
→ "Large Language Models"

"RAG" and "Retrieval-Augmented Generation"
→ "Retrieval-Augmented Generation"

"REST API" and "REST APIs"
→ "REST APIs"

"Postgres" and "PostgreSQL"
→ "PostgreSQL"

"React" and "React.js"
→ "React.js"

Do NOT return both the short form and long form
of the same skill.

Do not invent skills.

Keep required technical skills, preferred technical skills,
all technical skills, and soft skills clearly separated.

IMPORTANT:

Review the original job description carefully before
returning the answer.

Return ONLY valid JSON.

Do not use markdown.
Do not use ```json or ```.

Use exactly this structure:

{{
  "job_title": "...",
  "required_skills": [],
  "preferred_skills": [],
  "technical_skills": [],
  "soft_skills": [],
  "experience_requirement": "...",
  "main_responsibilities": [],
  "important_keywords": []
}}

Job Description:

{job_description}
"""

    result = generate_json(prompt)

    # Deterministic soft-skill extraction
    # This prevents Gemini from incorrectly returning [].
    detected_soft_skills = extract_soft_skills(
        job_description
    )

    print(
        "FINAL SOFT SKILLS:",
        detected_soft_skills
    )

    result["soft_skills"] = detected_soft_skills

    print(
        "FINAL JOB ANALYSIS:",
        result
    )

    return result




def analyze_resume(resume_text: str):

    print(
        "RESUME TEXT LENGTH:",
        len(resume_text)
    )

    prompt = f"""
You are an AI career assistant specialized in
resume analysis for software engineering jobs.

Analyze the resume text below carefully.

Extract:

1. Candidate name
2. Programming languages
3. Frameworks and libraries
4. Generative AI skills
5. Databases and tools
6. Soft skills
7. Projects
8. Education
9. Certifications
10. Coding achievements

IMPORTANT RULES:

- Only extract information that actually appears
  in the resume.

- Do not invent technologies, skills, projects,
  certifications or achievements.

- Keep technologies separate.

- Programming languages should include languages
  such as Python, JavaScript, SQL, C++, etc.

- Frameworks and libraries should include tools such
  as FastAPI, React, LangChain, LangGraph, LlamaIndex,
  Streamlit, Scikit-learn, etc.

- Generative AI skills should include concepts such as
  LLMs, RAG, prompt engineering, embeddings,
  vector search, agentic AI, etc., when present.

- Databases and tools should include databases,
  developer tools, APIs, cloud tools and similar
  technologies.

- Soft skills should contain human skills such as
  communication, teamwork, problem-solving,
  adaptability and collaboration.

- Projects should contain the project name and a concise
  description when available.

- Education should include degree/school information
  and relevant dates or grades when available.

- Certifications should include certification names
  and credential information when available.

- Coding achievements should include measurable
  coding accomplishments.

- Do not duplicate the same skill across categories
  unless the resume clearly presents it in different
  contexts.

Return ONLY valid JSON.

Do not use markdown.
Do not use ```json or ```.

Use exactly this structure:

{{
    "candidate_name": "string",
    "programming_languages": [],
    "frameworks_and_libraries": [],
    "generative_ai_skills": [],
    "databases_and_tools": [],
    "soft_skills": [],
    "projects": [],
    "education": [],
    "certifications": [],
    "coding_achievements": []
}}

Resume Text:

{resume_text}
"""

    return generate_json(prompt)


def generate_skill_recommendations(
    missing_skills,
    job_title
):

    if not missing_skills:

        return {
            "recommendations": [],
            "message": (
                "No major technical skill gaps were identified."
            )
        }

    skills_text = ", ".join(
        missing_skills
    )

    prompt = f"""
You are an AI career advisor helping a candidate
prepare for a software engineering role.

Job Title:

{job_title}

The candidate is missing these technical skills:

{skills_text}

For each missing skill, provide practical and
beginner-friendly recommendations.

For each skill provide:

1. Skill name
2. Why it matters for this role
3. What the candidate should learn
4. One practical project or task to practice it

IMPORTANT RULES:

- Focus only on the listed missing skills.
- Do not recommend unrelated technologies.
- Keep learning recommendations practical.
- Prefer hands-on learning over purely theoretical topics.
- Make the practice task realistic for a junior candidate.

Return ONLY valid JSON.

Do not use markdown.
Do not use ```json or ```.

Use exactly this structure:

{{
    "recommendations": [
        {{
            "skill": "string",
            "why_it_matters": "string",
            "what_to_learn": [],
            "practice_task": "string"
        }}
    ]
}}
"""

    recommendations = generate_json(
        prompt
    )

    recommendations["message"] = (
        "Skill recommendations generated successfully."
    )

    return recommendations


if __name__ == "__main__":

    test_jd = """
    Strong problem-solving and communication skills.
    Collaborate with product and engineering teams.
    """

    print(
        extract_soft_skills(test_jd)
    )