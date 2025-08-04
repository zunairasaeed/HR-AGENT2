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




