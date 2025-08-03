
import os
import json
from docx import Document
from pdfminer.high_level import extract_text

RESUME_DIR = 'data/resumes/'
OUTPUT_FILE = 'data/json/raw_data.json'

def extract_text_from_docx(path):
    try:
        doc = Document(path)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"❌ Error reading DOCX file {path}: {e}")
        return ""

def extract_text_from_pdf(path):
    try:
        return extract_text(path)
    except Exception as e:
        print(f"❌ Error reading PDF file {path}: {e}")
        return ""

def extract_raw_data(file_path):
    ext = file_path.split('.')[-1].lower()
    if ext == 'pdf':
        return extract_text_from_pdf(file_path)
    elif ext == 'docx':
        return extract_text_from_docx(file_path)
    else:
        return ""

def extract_all_resumes():
    data = []
    for file_name in os.listdir(RESUME_DIR):
        if file_name.endswith(('.pdf', '.docx')):
            full_path = os.path.join(RESUME_DIR, file_name)
            print(f"📄 Parsing {file_name}...")
            text = extract_raw_data(full_path)
            data.append({
                "filename": file_name,
                "path": full_path,
                "raw_text": text.strip()
            })
    return data

def save_to_json(data, file_name):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ✅ THIS is the function FastAPI calls now
def run_raw_parsing_debug(single_file=None):
    if single_file:
        file_path = os.path.join(RESUME_DIR, single_file)
        print(f"📄 Raw parsing single file: {single_file}")
        text = extract_raw_data(file_path)
        result = [{
            "filename": single_file,
            "path": file_path,
            "raw_text": text.strip()
        }]

    else:
        print("📄 Raw parsing all resumes...")
        result = extract_all_resumes()

    save_to_json(result, OUTPUT_FILE)
    print(f"\n✅ Saved raw data for {len(result)} resume(s) to {OUTPUT_FILE}")

# ✅ Run when executed directly (for testing only)
if __name__ == "__main__":
    run_raw_parsing_debug()


print("✅ raw_parser module loaded from:", __file__)
print("✅ run_raw_parsing_debug exists:", 'run_raw_parsing_debug' in dir())
