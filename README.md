# 🤖 AI HR Agent

## 📌 Project Overview

AI HR Agent is an intelligent system designed to automate and optimize the resume screening and job matching process. It leverages **LLMs (Large Language Models)** to extract, normalize, and analyze candidate resumes and job descriptions. The system provides intelligent ranking, scoring, and even CV tailoring based on job-specific requirements.

---

## 🚀 Features

- Upload resumes manually (supports `.docx` and `.pdf`)
- Resume parsing and raw data extraction using LLM
- Normalization and transformation of data into structured JSON
- Extraction of key fields (e.g., personal info, skills, education, etc.)
- Parsing job descriptions (JDs) from `.pdf`, `.docx`, or text blocks
- Matching candidate skills with job requirements
- Ranking candidates:
  - Candidate-by-job
  - Job-by-candidate
- CV tailoring using LLM and optional company Word templates
- FastAPI backend for API endpoints

---

## 🛠️ Technologies Used

- Python
- FastAPI
- Uvicorn
- LLMs (e.g., OpenAI GPT-based models)
- PyMuPDF / docx2txt / pdfminer / python-docx (for file parsing)
- JSON for normalized data storage

---

## 🛠️ Project Flow
##  System Flow Diagram
https://github.com/zunairasaeed/HR-AGENT2/blob/main/data/SYSTEM-FLOW-DIAGRAM.png
##  Archtecture  Flow Diagram
https://github.com/zunairasaeed/HR-AGENT2/blob/main/data/ARCH-DIA.png


## 📂 Folder Structure 
HR-AGENT2/
│
├── app/ # Main backend app
│ ├── init.py
│ ├── main.py # FastAPI entry point
│ ├── automation_agent.py # Agent automation logic
│ ├── calendar_utils.py # Calendar helper (if any)
│ ├── database.py # DB logic (if integrated)
│ ├── emailer.py # Email service logic
│ ├── gmail_fetcher.py # Gmail integration logic
│ ├── jobs_ranking.py # JD ranking logic
│ ├── llm_utils.py # Utility functions for LLM calls
│ ├── matcher.py # Matching logic
│ ├── python_normalizer.py # Data normalization logic
│ ├── raw_parser.py # Raw parsing from resumes
│ ├── tailoredCV.py # Tailored CV generator
│ ├── test_gpt.py # LLM test script
│ └── utils.py # General helper functions
│
├── data/
│ ├── jobs/ # Folder for Job Description files (auto-fetch)
│ └── json/ # Normalized JSON data output
│
├── resumes/ # Uploaded resume files (.docx, .pdf)
│
├── llm/ # LLM-related resume processing
│ ├── jd_parser.py
│ ├── jobs_ranking.py
│ ├── matcher.py
│ ├── parser.py
│ ├── parsed_template.py
│ ├── rank_candidates_by_job.py
│ ├── tailoredcv.py
│ └── test_tailoring_single.py
│
├── templates/
│ ├── Word Template.docx # Sample company-provided Word CV template
│ └── json_extracted_template/
│ └── Word Template__extracted_template.json
│
├── static/ # (Optional) Static files for web if any
├── .env # Environment variables
├── .gitignore
└── README.md


