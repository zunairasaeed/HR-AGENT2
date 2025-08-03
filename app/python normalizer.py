
import os
import json
import re

RAW_FILE = os.path.join( 'data', 'json', 'raw_data.json')  # ✅ fixed path

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

def extract_all_possible_links(text):
    matches = re.findall(r'(https?://[^\s\)]+|www\.[^\s\)]+|linkedin\.com/\S+|github\.com/\S+)', text)
    cleaned_links = []

    for link in matches:
        link = link.strip('.,);')
        if not link.startswith("http"):
            link = "https://" + link
        cleaned_links.append(link)
    
    return list(set(cleaned_links))

def extract_link_from_links(links, keyword):
    for link in links:
        if keyword in link:
            return link
    return ""

def extract_certificates(links):
    cert_sources = [
        "coursera.org", "udemy.com", "edx.org", "futurelearn.com",
        "kaggle.com/certificates", "certificates.mooc.fi", "freecodecamp.org/certification",
        "nptel.ac.in", "skillshare.com", "linkedin.com/learning"
    ]
    cert_links = []
    for link in links:
        for src in cert_sources:
            if src in link:
                cert_links.append(link)
                break
    return list(set(cert_links))

def load_skill_keywords():
    return [
        "python", "java", "c++", "react", "javascript", "html", "css",
        "sql", "postgresql", "mysql", "flask", "django", "node.js"
    ]

def load_tool_keywords():
    return [
        "git", "github", "aws", "azure", "docker", "kubernetes", "linux",
        "firebase", "pandas", "numpy", "tensorflow", "keras", "fastapi", "postman",
        "jupyter", "powerbi", "tableau", "excel", "matplotlib", "seaborn"
    ]

def extract_keywords(text, keyword_list):
    found = []
    for word in keyword_list:
        if word in text:
            found.append(word)
    return list(set(found))

def process_resume(entry):
    text = normalize_text(entry.get("raw_text", ""))
    name = extract_name(entry.get("raw_text", ""))
    links = extract_all_possible_links(text)
    skills = extract_keywords(text, load_skill_keywords())
    tools = extract_keywords(text, load_tool_keywords())
    keywords_only = [kw for kw in tools if kw not in skills]
    name = extract_name(entry.get("raw_text", ""))

    return {
        
        "filename": entry.get("filename", "unknown"),
        "name": name,
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_link_from_links(links, "linkedin.com"),
        "github": extract_link_from_links(links, "github.com"),
        "certificates": extract_certificates(links),
        "skills": skills,
        "keywords": keywords_only,
        "raw_text": text
    }

def extract_name(text):
    lines = text.strip().split('\n')
    
    # Loop through first 10 lines to find a name-like line
    for line in lines[:10]:
        clean_line = line.strip()

        # Skip empty or contact info lines
        if not clean_line:
            continue
        if re.search(r'@|http|linkedin|github|[\\d\\+\\-]', clean_line.lower()):
            break  # stop early if contact info starts

        # Assume it's a name if it's 2–4 words and no digits
        if 1 <= len(clean_line.split()) <= 4 and not re.search(r'\\d', clean_line):
            return clean_line.title()

    return "Unknown"

def normalize_all():
    if not os.path.exists(RAW_FILE):
        print(f"❌ File not found: {RAW_FILE}")
        return

    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    output_dir = os.path.join('data', 'json', 'normalized')
    os.makedirs(output_dir, exist_ok=True)

    for entry in raw_data:
        result = process_resume(entry)
        filename = entry.get("filename", "unknown")
        base_name = os.path.splitext(filename)[0]
        safe_name = re.sub(r'[^\w\-_ ]', '_', base_name).strip()
        output_path = os.path.join(output_dir, f"{safe_name}.json")

        with open(output_path, 'w', encoding='utf-8') as f_out:
            json.dump(result, f_out, indent=4, ensure_ascii=False)

        print(f"✅ Normalized: {filename} → {output_path}")

    print(f"\n🎉 Done! Saved {len(raw_data)} individual JSON files in {output_dir}")

def save_individual_raw_jsons():
    if not os.path.exists(RAW_FILE):
        print(f"❌ File not found: {RAW_FILE}")
        return

    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    output_dir = os.path.join("data", "json", "normalized")  # ✅ fixed output path
    os.makedirs(output_dir, exist_ok=True)

    for entry in raw_data:
        filename = entry.get("filename", "unknown")
        base_name = os.path.splitext(filename)[0]
        safe_name = re.sub(r'[^\w\-_ ]', '_', base_name).strip()  # ✅ sanitize name
        output_path = os.path.join(output_dir, f"{safe_name}.json")

        with open(output_path, 'w', encoding='utf-8') as f_out:
            json.dump(entry, f_out, indent=4, ensure_ascii=False)

        print(f"📄 Saved raw JSON: {output_path}")

    print(f"\n✅ Done! Created {len(raw_data)} raw JSON files in {output_dir}")

if __name__ == "__main__":
    save_individual_raw_jsons()
    normalize_all()
