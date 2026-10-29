SKILL_ALIASES = {

    # =========================
    # Generative AI
    # =========================

    "rag": "retrieval-augmented generation",
    "retrieval augmented generation": "retrieval-augmented generation",
    "retrieval-augmented generation": "retrieval-augmented generation",

    "llm": "large language models",
    "llms": "large language models",
    "large language model": "large language models",
    "large language models": "large language models",
    "large language models llms": "large language models",

    "genai": "generative ai",
    "gen ai": "generative ai",
    "generative ai": "generative ai",

    # =========================
    # Embeddings
    # =========================

    "embedding": "embeddings",
    "embeddings": "embeddings",

    # =========================
    # Vector Databases
    # =========================

    "vector database": "vector databases",
    "vector databases": "vector databases",
    "vector db": "vector databases",
    "vector dbs": "vector databases",
    "vector embedding": "vector embeddings",
    "vector embeddings": "vector embeddings",

    # =========================
    # Databases
    # =========================

    "postgres": "postgresql",
    "postgresql": "postgresql",

    # =========================
    # APIs
    # =========================

    "rest api": "rest apis",
    "restful api": "rest apis",
    "restful apis": "rest apis",
    "rest apis": "rest apis",

    # =========================
    # Machine Learning
    # =========================

    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "scikit-learn": "scikit-learn",

    # =========================
    # JavaScript
    # =========================

    "javascript": "javascript",
    "js": "javascript",

    "react": "react.js",
    "reactjs": "react.js",
    "react.js": "react.js",

    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",

    # =========================
    # Python Frameworks
    # =========================

    "fast api": "fastapi",
    "fastapi": "fastapi",

    # =========================
    # Cloud
    # =========================

    "azure": "microsoft azure",
    "microsoft azure": "microsoft azure",

    "aws": "aws",

    # =========================
    # Version Control
    # =========================

    "git": "git",
    "github": "github",

    # =========================
    # Caching
    # =========================

    "api caching": "api caching",
    "redis": "redis",

    # =========================
    # DevOps
    # =========================

    "ci/cd": "ci/cd",
    "ci/cd pipelines": "ci/cd",

    "docker": "docker",
}


def normalize_skill(skill):

    skill = skill.strip().lower()

    # Remove parentheses
    skill = skill.replace("(", "")
    skill = skill.replace(")", "")

    # Normalize spaces
    skill = " ".join(skill.split())

    aliases = {

        "large language models llms":
            "large language models",

        "large language model llm":
            "large language models",

        "retrieval-augmented generation rag":
            "retrieval-augmented generation",

        "retrieval augmented generation rag":
            "retrieval-augmented generation",

    }

    if skill in aliases:

        return aliases[skill]

    return SKILL_ALIASES.get(
        skill,
        skill
    )

def collect_resume_skills(resume_analysis):
    """Collect explicitly listed technical skills from the resume."""

    categories = [
        "programming_languages",
        "frameworks_and_libraries",
        "generative_ai_skills",
        "databases_and_tools"
    ]

    skills = []

    for category in categories:
        values = resume_analysis.get(category, [])

        if isinstance(values, list):
            for value in values:
                if isinstance(value, str):
                    skills.append(value)

    return skills

def collect_resume_evidence(resume_analysis):
    """Collect text recursively from resume skills and sections."""

    evidence = []

    def extract_text(value):
        if isinstance(value, str):
            evidence.append(value)

        elif isinstance(value, dict):
            for nested_value in value.values():
                extract_text(nested_value)

        elif isinstance(value, list):
            for item in value:
                extract_text(item)

    extract_text(resume_analysis)

    return " ".join(evidence).lower()

def skill_supported_by_evidence(skill, evidence):
    """Check whether a skill is supported by resume evidence."""

    evidence_rules = {
        "generative ai": [
            "generative ai",
            "genai",
            "generative artificial intelligence"
        ],
        "vector embeddings": [
            "vector embeddings",
            "vector embedding"
        ],
        "embeddings": [
            "embedding",
            "embeddings"
        ],
        "vector databases": [
            "vector database",
            "vector databases",
            "chromadb",
            "chroma db",
            "faiss",
            "vector store"
        ],
        "rest apis": [
            "rest api",
            "restful api"
        ],
        "large language models": [
            "large language model",
            "llm",
            "llms"
        ],
        "retrieval-augmented generation": [
            "retrieval-augmented generation",
            "retrieval augmented generation",
            "rag"
        ]
    }

    patterns = evidence_rules.get(skill, [])

    return any(
        pattern in evidence
        for pattern in patterns
    )

def calculate_skill_match(
    job_analysis,
    resume_analysis
):

    # =========================
    # Job Required Skills
    # =========================

    required_skills = job_analysis.get(
        "required_skills",
        []
    )

    # =========================
    # Job Preferred Skills
    # =========================

    preferred_skills = job_analysis.get(
        "preferred_skills",
        []
    )

    # =========================
    # Fallback
    # =========================

    if not required_skills and not preferred_skills:

        required_skills = job_analysis.get(
            "technical_skills",
            []
        )

    # =========================
    # Resume Explicit Skills
    # =========================

    resume_skills = collect_resume_skills(
        resume_analysis
    )

    # =========================
    # Resume Evidence
    # =========================

    resume_evidence = collect_resume_evidence(
        resume_analysis
    )

    # =========================
    # Normalize
    # =========================

    normalized_required_skills = {

        normalize_skill(skill)

        for skill in required_skills

    }

    normalized_preferred_skills = {

        normalize_skill(skill)

        for skill in preferred_skills

    }

    normalized_resume_skills = {

        normalize_skill(skill)

        for skill in resume_skills

    }

    # =========================
    # Initial Exact Matches
    # =========================

    matched_required_skills = (

        normalized_required_skills
        &
        normalized_resume_skills

    )

    matched_preferred_skills = (

        normalized_preferred_skills
        &
        normalized_resume_skills

    )

    # =========================
    # Evidence-Based Matches
    # =========================

    evidence_matched_skills = set()

    all_job_skills = (

        normalized_required_skills
        |
        normalized_preferred_skills

    )

    for skill in all_job_skills:

        if (
            skill in matched_required_skills
            or
            skill in matched_preferred_skills
        ):

            continue

        if skill_supported_by_evidence(
            skill,
            resume_evidence
        ):

            evidence_matched_skills.add(
                skill
            )

    # =========================
    # Add Evidence Matches
    # =========================

    for skill in evidence_matched_skills:

        if skill in normalized_required_skills:

            matched_required_skills.add(
                skill
            )

        elif skill in normalized_preferred_skills:

            matched_preferred_skills.add(
                skill
            )

    # =========================
    # Missing Skills
    # =========================

    missing_required_skills = (

        normalized_required_skills
        -
        matched_required_skills

    )

    missing_preferred_skills = (

        normalized_preferred_skills
        -
        matched_preferred_skills

    )

    # =========================
    # Weighted Score
    # =========================

    if len(normalized_required_skills) > 0:

        required_score = (

            len(matched_required_skills)
            /
            len(normalized_required_skills)

        ) * 70

    else:

        required_score = 0

    if len(normalized_preferred_skills) > 0:

        preferred_score = (

            len(matched_preferred_skills)
            /
            len(normalized_preferred_skills)

        ) * 30

    else:

        preferred_score = 0

    # =========================
    # Final Score
    # =========================

    match_score = round(
        required_score
        +
        preferred_score
    )

    # =========================
    # All Matched Skills
    # =========================

    matched_skills = (

        matched_required_skills
        |
        matched_preferred_skills

    )

    # =========================
    # All Missing Skills
    # =========================

    missing_skills = (

        missing_required_skills
        |
        missing_preferred_skills

    )

    # =========================
    # Result
    # =========================

    return {

        "match_score": match_score,

        "required_skill_match": round(
            (
                len(matched_required_skills)
                /
                len(normalized_required_skills)
                * 100
            )
        ) if normalized_required_skills else 0,

        "preferred_skill_match": round(
            (
                len(matched_preferred_skills)
                /
                len(normalized_preferred_skills)
                * 100
            )
        ) if normalized_preferred_skills else 0,

        "matched_skills": sorted(
            matched_skills
        ),

        "missing_skills": sorted(
            missing_skills
        ),

        "missing_required_skills": sorted(
            missing_required_skills
        ),

        "missing_preferred_skills": sorted(
            missing_preferred_skills
        ),

        "evidence_matched_skills": sorted(
            evidence_matched_skills
        )
    }


if __name__ == "__main__":

    # =========================
    # Test Job
    # =========================

    job_analysis = {

    "required_skills": [

        "Python",
        "FastAPI",
        "REST APIs",
        "Large Language Models",
        "Generative AI",
        "Retrieval-Augmented Generation",
        "LangChain",
        "SQL",
        "PostgreSQL"

    ],

    "preferred_skills": [

        "Vector Databases",
        "Embeddings",
        "LangGraph",
        "Agentic AI",
        "Microsoft Azure",
        "AWS",
        "Docker",
        "Git",
        "GitHub",
        "Redis",
        "API Caching",
        "CI/CD Pipelines"

    ]

}
    # =========================
    # Simulated Resume Analysis
    # =========================

    resume_analysis = {

        "programming_languages": [

            "Python",
            "SQL"

        ],

        "frameworks_and_libraries": [

            "LangChain",
            "LangGraph",
            "LlamaIndex",
            "OpenAI SDK",
            "FastAPI",
            "Streamlit",
            "Scikit-learn",
            "FAISS"

        ],

        "generative_ai_skills": [

            "Prompt Engineering",
            "Large Language Models (LLMs)",
            "Retrieval-Augmented Generation (RAG)"

        ],

        "databases_and_tools": [

            "PostgreSQL",
            "OpenAI API",
            "ChromaDB",
            "Hugging Face",
            "REST APIs"

        ],

        "projects": [

            "Enterprise Knowledge Assistant using RAG: Developed an enterprise AI assistant using Retrieval-Augmented Generation (RAG), Generative AI, vector embeddings, semantic search, and ChromaDB. Designed REST APIs for integration with enterprise applications."

        ],

        "certifications": [

            "Microsoft Certified: Azure Fundamentals"

        ]

    }

    result = calculate_skill_match(
        job_analysis,
        resume_analysis
    )

    print(result)