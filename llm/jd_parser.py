
import os
import json
from docx import Document
import fitz  # PyMuPDF
from tqdm import tqdm
from app.llm_utils import call_gpt

# 📁 Folder paths
RAW_JD_FOLDER = os.path.join("data", "jobs", "raw_jd")
STRUCTURED_JD_FOLDER = os.path.join("data", "jobs", "parsed_jd")  # ✅ Corrected output path

os.makedirs(STRUCTURED_JD_FOLDER, exist_ok=True)
os.makedirs(RAW_JD_FOLDER, exist_ok=True)

# -------------------------------
# 📄 Read text from file
# -------------------------------
def extract_text_from_file(filepath):
    if filepath.endswith(".pdf"):
        text = ""
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text()
        return text
    elif filepath.endswith(".docx"):
        doc = Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        return ""  # unsupported

# -------------------------------
# 🤖 LLM: Structure the JD
# -------------------------------
def extract_jd_data_llm(text):
    system_prompt = "You are a helpful assistant that structures unformatted job descriptions."

    # 🔒 Optional: Truncate very long JDs
    if len(text) > 8000:
        text = text[:8000]

    user_prompt = f"""
Parse the following job description and return structured data as valid JSON.

Return the following keys:

{{
  "job_title": "",
  "department": "",
  "location": "",
  "employment_type": "",
  "must_have_skills": [],
  "nice_to_have_skills": [],
  "tools": [],
  "responsibilities": [],
  "requirements": [],
  "experience_level": "",
  "education_required": "",
  "keywords": []
}}

Ensure no duplicate or redundant values and output only valid JSON (no extra text).

Job Description:
\"\"\"{text}\"\"\"
    """

    response = call_gpt(system_prompt, user_prompt)

    # 🧠 Log raw GPT response
    print("\n🧠 Raw GPT Response:\n", response)

    # ✅ Strip markdown-style code blocks before parsing
    try:
        if not response.strip():
            raise ValueError("Empty response from LLM.")

        # Remove ```json or ``` from start/end
        if response.strip().startswith("```"):
            response = "\n".join(
                line for line in response.strip().splitlines()
                if not line.strip().startswith("```")
            )

        return json.loads(response)

    except Exception as e:
        print("❌ JSON parse error:", e)
        return {}

# -------------------------------
# 🔁 Process each JD
# -------------------------------

def run_job_parsing():
    for filename in tqdm(os.listdir(RAW_JD_FOLDER)):
        filepath = os.path.join(RAW_JD_FOLDER, filename)
        if not (filename.endswith(".pdf") or filename.endswith(".docx")):
            continue

        text = extract_text_from_file(filepath)
        print(f"\n📄 Preview from {filename}:\n{text[:1000]}")

        structured_data = extract_jd_data_llm(text)

        if structured_data:
            safe_name = os.path.splitext(filename)[0].replace(" ", "_")
            output_path = os.path.join(STRUCTURED_JD_FOLDER, f"{safe_name}.json")
            with open(output_path, "w", encoding="utf-8") as f_out:
                json.dump(structured_data, f_out, indent=2, ensure_ascii=False)
            print(f"✅ Parsed: {filename} → {output_path}")
        else:
            print(f"⚠️ Skipped saving empty output for {filename}")

    print("\n🎉 All job descriptions processed and structured.")

# 🔘 Optional CLI execution
if __name__ == "__main__":
    run_job_parsing()