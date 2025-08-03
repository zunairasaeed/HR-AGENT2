import os
import json
import re
from tqdm import tqdm
from app.llm_utils import call_gpt  # ✅ Your GPT wrapper

# 📁 File paths
RAW_FILE = os.path.join('data', 'json', 'raw_data.json')
OUTPUT_DIR = os.path.join('data', 'json', 'llm_normalized')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------
# ✅ Regex-based extractors
# -------------------------------
def normalize_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else ""

def extract_phone(text):
    match = re.search(r'\b(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}\b', text)
    return match.group(0) if match else ""

def extract_links(text):
    matches = re.findall(r'(https?://[^\s\)]+|www\.[^\s\)]+|linkedin\.com/\S+|github\.com/\S+)', text)
    cleaned = []
    for link in matches:
        link = link.strip('.,);')
        if not link.startswith("http"):
            link = "https://" + link
        cleaned.append(link)
    return list(set(cleaned))

def extract_link_from_links(links, keyword):
    for link in links:
        if keyword in link:
            return link
    return ""

def extract_certificates(links):
    cert_sources = [
        "coursera.org", "udemy.com", "edx.org", "futurelearn.com",
        "kaggle.com/certificates", "certificates.mooc.fi",
        "freecodecamp.org/certification", "nptel.ac.in",
        "skillshare.com", "linkedin.com/learning"
    ]
    return [link for link in links if any(src in link for src in cert_sources)]

# -------------------------------
# 🔥 GPT-based structured extractor
# -------------------------------

def extract_resume_data_llm(text):
    system_prompt = "You are a smart resume parser. Extract structured information from a resume."

    user_prompt = f"""
Extract the following JSON structure from this resume:

{{
  "name": "",
  "skills": [],
  "tools": [],
  "technologies": [],
  "certifications": [],
  "projects": [{{"title": "", "description": ""}}],
  "education": [{{"degree": "", "field": "", "institute": "", "years": ""}}],
  "experience": [{{"company": "", "role": "", "years": "", "description": ""}}]
}}

⚠️ Return **valid JSON only**, no markdown, no comments.
⚠️ Ensure no duplicate or reworded items (e.g., "python" and "Python").
⚠️ Deduplicate and clean all list entries: "skills", "tools", "technologies", etc.

Resume:
\"\"\"{text}\"\"\"
"""

    try:
        response = call_gpt(system_prompt, user_prompt)

        if not response:
            raise ValueError("Empty response from GPT")

        return json.loads(response)

    except Exception as e:
        print("❌ JSON decode failed:", e)
        return {
            "name": "",
            "skills": [],
            "tools": [],
            "technologies": [],
            "certifications": [],
            "projects": [],
            "education": [],
            "experience": []
        }


# -------------------------------
# 🔁 Process each resume
# -------------------------------
def process_resume(filename, raw_text):
    text = normalize_text(raw_text)
    
    # Rule-based fields
    email = extract_email(text)
    phone = extract_phone(text)
    links = extract_links(text)
    linkedin = extract_link_from_links(links, "linkedin.com")
    github = extract_link_from_links(links, "github.com")
    cert_links = extract_certificates(links)

    try:
        structured = extract_resume_data_llm(raw_text)
    except Exception as e:
        print(f"❌ GPT extraction failed for {filename}: {e}")
        structured = {}

    return {
        "filename": filename,
        "name": structured.get("name", "Unknown"),
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "certificates": cert_links,
        "skills": structured.get("skills", []),
        "tools": structured.get("tools", []),
        "technologies": structured.get("technologies", []),
        "certifications": structured.get("certifications", []),
        "projects": structured.get("projects", []),
        "education": structured.get("education", []),
        "experience": structured.get("experience", []),
        "raw_text": text
    }




def run_llm_parsing():
    if not os.path.exists(RAW_FILE):
        print(f"❌ File not found: {RAW_FILE}")
        return

    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        resumes = json.load(f)  # ✅ This is a list

    for entry in tqdm(resumes):  # ✅ Loop through the list
        filename = entry.get("filename", "unknown")
        raw_text = entry.get("raw_text", "")
        result = process_resume(filename, raw_text)

        # ✅ Use candidate name for output file
        candidate_name = result.get("name", "unknown_candidate")
        safe_name = re.sub(r'[^\w\-_ ]', '_', candidate_name).strip().lower()
        output_path = os.path.join(OUTPUT_DIR, f"{safe_name}.json")

        # ✅ Update if file exists, otherwise create new
        if os.path.exists(output_path):
            # 🔄 Load existing content
            with open(output_path, 'r', encoding='utf-8') as existing_file:
                try:
                    existing_data = json.load(existing_file)
                except json.JSONDecodeError:
                    existing_data = {}

            # 🔁 Update existing data with new info
            existing_data.update(result)

            # 💾 Save updated content
            with open(output_path, 'w', encoding='utf-8') as out_file:
                json.dump(existing_data, out_file, indent=2, ensure_ascii=False)

            print(f"🔄 Updated: {candidate_name} → {output_path}")

        else:
            # 🆕 Save new file
            with open(output_path, 'w', encoding='utf-8') as out_file:
                json.dump(result, out_file, indent=2, ensure_ascii=False)

            print(f"✅ Saved: {candidate_name} → {output_path}")

    print("\n🎉 All resumes processed with LLM parsing.")

# 🔥 Optional for standalone runs
if __name__ == "__main__":
    run_llm_parsing()
