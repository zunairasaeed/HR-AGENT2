

import os
import json
from app.llm_utils import call_gpt

RESULTS_DIR = "data/json/llm_results"
OUTPUT_DIR = "data/json/llm_ranking_by_candidates/by_candidate"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_llm_summary(candidate_name, job_title, score, qualified):
    system_prompt = "You are an expert assistant helping HR rank candidates."
    user_prompt = f"""
Candidate: {candidate_name}
Job Role: {job_title}
Score: {score}
Qualified: {"Yes" if qualified else "No"}

Explain in 3-4 lines why this candidate ranked where they did for this job. Mention if their score was high or low, and any specific strength or gap if known.
"""
    return call_gpt(system_prompt, user_prompt) or "No summary available."

for filename in os.listdir(RESULTS_DIR):
    if not filename.endswith("__matches.json"):
        continue

    with open(os.path.join(RESULTS_DIR, filename), "r", encoding="utf-8") as f:
        data = json.load(f)

    candidate = {
        "name": data.get("candidate_name"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "linkedin": data.get("linkedin"),
    }

    ranked_jobs = data.get("matched_jobs", [])
    ranked_jobs.sort(key=lambda x: x["final_percentage"], reverse=True)

    for i, job in enumerate(ranked_jobs, start=1):
        job["rank"] = i
        job["llm_ranking_summary"] = generate_llm_summary(candidate["name"], job["job_role"], job["final_percentage"], job["qualified"])

    result = {
        "candidate": candidate,
        "ranked_jobs": ranked_jobs
    }

    out_path = os.path.join(OUTPUT_DIR, filename.replace("__matches.json", "__ranked_jobs.json"))
    with open(out_path, "w", encoding="utf-8") as out:
        json.dump(result, out, indent=4)

    print(f"✅ Ranked: {filename}")


def run_job_ranking_by_candidate():
    for filename in os.listdir(RESULTS_DIR):
        if not filename.endswith("__matches.json"):
            continue

        with open(os.path.join(RESULTS_DIR, filename), "r", encoding="utf-8") as f:
            data = json.load(f)

        candidate = {
            "name": data.get("candidate_name"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "linkedin": data.get("linkedin"),
        }

        ranked_jobs = data.get("matched_jobs", [])
        ranked_jobs.sort(key=lambda x: x["final_percentage"], reverse=True)

        for i, job in enumerate(ranked_jobs, start=1):
            job["rank"] = i
            job["llm_ranking_summary"] = generate_llm_summary(
                candidate["name"], job["job_role"], job["final_percentage"], job["qualified"]
            )

        result = {
            "candidate": candidate,
            "ranked_jobs": ranked_jobs
        }

        out_path = os.path.join(OUTPUT_DIR, filename.replace("__matches.json", "__ranked_jobs.json"))
        with open(out_path, "w", encoding="utf-8") as out:
            json.dump(result, out, indent=4)

        print(f"✅ Ranked: {filename}")

# 🔥 Optional for standalone CLI use
if __name__ == "__main__":
    run_job_ranking_by_candidate()
