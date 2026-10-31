# CareerLens AI 🚀

**AI-Powered Job Description Analysis and Resume Matching Platform**

CareerLens AI is a FastAPI-based application that uses Google Gemini to analyze job descriptions and resumes, identify technical skill gaps, calculate job-match scores, and generate personalized learning recommendations.

The goal is to help candidates understand job requirements and identify the skills they should focus on to improve their career opportunities.

## ✨ Features

- **Job Description Analysis** — Extract job titles, technical skills, responsibilities, keywords, and experience requirements.
- **Resume Parsing** — Extract text from PDF resumes.
- **AI-Powered Resume Analysis** — Identify programming languages, frameworks, Generative AI skills, projects, education, and certifications.
- **Skill Classification** — Separate required technical skills, preferred technical skills, and soft skills.
- **Resume-to-Job Matching** — Compare extracted resume skills with job requirements.
- **Evidence-Based Matching** — Use resume content and project evidence to support skill matching.
- **Match Score Calculation** — Calculate an overall match score using required and preferred skill matches.
- **Skill Gap Identification** — Highlight missing required and preferred skills.
- **Personalized Learning Recommendations** — Generate practical learning suggestions for identified skill gaps.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| FastAPI | REST API development |
| Google Gemini | AI-powered text analysis and recommendations |
| Pydantic | Request validation and data models |
| PyPDF | PDF text extraction |
| python-dotenv | Environment variable management |
| Uvicorn | ASGI application server |
| Git & GitHub | Version control and source code hosting |

## 🏗️ Project Structure

```text
careerlens-ai/
├── app/
│   ├── __init__.py
│   ├── ai_service.py
│   ├── config.py
│   ├── main.py
│   ├── matching_service.py
│   └── resume_parser.py
├── .gitignore
├── README.md
└── requirements.txt
```

## ⚙️ Getting Started

### Prerequisites

- Python 3.10 or a compatible newer version
- Git
- A Google Gemini API key

### 1. Clone the repository

```bash
git clone https://github.com/shivanshu6264/careerlens-ai.git
cd careerlens-ai
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the placeholder with your own API key.

**Security:** Never commit your `.env` file or expose your API key in source code, screenshots, or public logs.

### 5. Start the application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- Base URL: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`
- Alternative API documentation: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Root endpoint |
| GET | `/health` | Check application health |
| POST | `/analyze-job` | Analyze a job description |
| POST | `/analyze-resume` | Analyze an uploaded resume |
| POST | `/match-resume` | Match resume analysis against job analysis |

Use the interactive Swagger documentation at `/docs` to inspect request schemas and test the endpoints.

## 🧠 How It Works

1. Submit a job description for analysis.
2. Upload a resume in PDF format for text extraction and analysis.
3. Extract and normalize relevant technical skills.
4. Compare resume skills against required and preferred job skills.
5. Calculate the match score and identify missing skills.
6. Generate practical learning recommendations for the identified gaps.

## 🔒 Security and Limitations

- API credentials are loaded through environment variables.
- Resume files and local configuration files are excluded through `.gitignore`.
- Skill extraction and matching results depend on the quality of the input data.
- AI-generated analysis and recommendations may require manual verification.
- A match score is an estimate of skill alignment, not a guarantee of selection or interview shortlisting.

## 🚀 Future Improvements

- Automated unit and integration tests
- More robust API error handling and file validation
- Database-backed storage for job and resume analyses
- Match-score evaluation against a curated test dataset
- Logging, monitoring, and AI response quality evaluation
- Frontend dashboard and live deployment

## 👨‍💻 Author

**Shivanshu Tiwari**

- GitHub: [shivanshu6264](https://github.com/shivanshu6264)
- LinkedIn: [shivanshu6264](https://www.linkedin.com/in/shivanshu6264/)
- Portfolio: [shivanshu-seven.vercel.app](https://shivanshu-seven.vercel.app/)

---

*Built with Python, FastAPI, and Google Gemini.*

## 🧪 Running Tests

Install project dependencies:

```bash
python -m pip install -r requirements.txt