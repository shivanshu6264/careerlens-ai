# CareerLens AI

AI-powered Job Description and Resume Analysis platform built with FastAPI and Google Gemini.

## Features

- Job Description analysis
- Resume PDF parsing
- AI-powered resume analysis
- Technical skill extraction
- Soft skill extraction
- Required vs preferred skill classification
- Resume-to-job skill matching
- Evidence-based skill matching
- Match score calculation
- Missing skill identification
- AI-generated learning recommendations

## Tech Stack

- Python
- FastAPI
- Google Gemini
- Pydantic
- PyPDF
- REST APIs
- PostgreSQL
- Git

## Project Structure

```text
careerlens-ai/
│
├── app/
│   ├── ai_service.py
│   ├── config.py
│   ├── main.py
│   ├── matching_service.py
│   ├── resume_parser.py
│   └── __init__.py
│
├── .gitignore
├── requirements.txt
└── README.md