from pathlib import Path
from dotenv import load_dotenv
import os

# 🔥 Load env before anything else
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")
print("✅ ENV LOADED:", os.getenv("AZURE_OPENAI_API_KEY")[:8])



from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import os

# ✅ Load .env from the absolute path (so it always works)
from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)

app = FastAPI()

# === Setup Upload Directory ===
UPLOAD_DIR = PROJECT_ROOT / "data" / "resumes"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload")
async def upload_and_process(file: UploadFile = File(...)):
    filename = file.filename
    ext = filename.split(".")[-1].lower()

    if ext not in ["pdf", "docx"]:
        return JSONResponse(status_code=400, content={"error": "❌ Only PDF or DOCX allowed."})

    # ✅ Save uploaded file
    file_path = UPLOAD_DIR / filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # ✅ STEP-BY-STEP PIPELINE CALLS
        from app.raw_parser import run_raw_parsing_debug
        from llm.parser import run_llm_parsing
        from llm.jd_parser import run_job_parsing
        from llm.matcher import run_matching
        from llm.jobs_ranking import run_job_ranking_by_candidate
        from llm.rank_candidates_by_job import run_candidate_ranking_by_job
        from llm.parsered_template import run_template_extractor
        from llm.tailoredcv import tailor_all

        print(f"\n📄 STEP 1: Raw parsing for {filename}")
        run_raw_parsing_debug()

        print(f"🧠 STEP 2: LLM resume parsing for {filename}")
        run_llm_parsing()

        print("📃 STEP 3: Job description parsing")
        run_job_parsing()
 
        print(f"🔍 STEP 4: Matching for {filename}")
        run_matching()

        print(f"📊 STEP 5: Ranking jobs for candidate {filename}")
        run_job_ranking_by_candidate()

        print("📊 STEP 6: Ranking candidates by job")
        run_candidate_ranking_by_job()

        print(f"📝 STEP 7: Generating template context for {filename}")
        run_template_extractor()

        print(f"🎯 STEP 8: Tailoring final CV for {filename}")
        tailor_all()

        base_name = filename.rsplit(".", 1)[0]
        tailored_output = f"data/json/llm_tailored_cv/{base_name}__<job>__tailored.docx"

        return JSONResponse(
            status_code=200,
            content={
                "message": "✅ Full pipeline executed successfully.",
                "tailored_cv_path": tailored_output
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"❌ Pipeline error: {str(e)}"})
