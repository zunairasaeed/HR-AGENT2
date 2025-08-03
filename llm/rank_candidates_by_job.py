


import os
import json
from app.llm_utils import call_gpt

RESULTS_DIR = "data/json/llm_results"
OUTPUT_FILE = "data/json/rank_candidates_by_job/job_rankings.json"

job_rankings = {}

def generate_llm_summary(candidate_name, job_role, percent, qualified):
    system_prompt = "You are an assistant evaluating job candidates."
    user_prompt = f"""
Candidate: {candidate_name}
Job Role: {job_role}
Score %: {percent}
Qualified: {"Yes" if qualified else "No"}

Summarize why this candidate is ranked as such for the job. Use 2-3 lines, mention if they met the criteria well or lacked some important skills.
"""
    return call_gpt(system_prompt, user_prompt) or "Summary unavailable."



def run_candidate_ranking_by_job():
    job_rankings = {}

    for filename in os.listdir(RESULTS_DIR):
        if not filename.endswith("__matches.json"):
            continue

        with open(os.path.join(RESULTS_DIR, filename), "r", encoding="utf-8") as f:
            data = json.load(f)

        candidate_name = data.get("candidate_name")
        email = data.get("email", "")
        phone = data.get("phone", "")
        linkedin = data.get("linkedin", "")

        for job in data.get("matched_jobs", []):
            job_role = job["job_role"]
            score = job["total_score"]
            bonus = job["bonus_score"]
            percent = job["final_percentage"]
            qualified = job["qualified"]

            entry = {
                "candidate_name": candidate_name,
                "email": email,
                "phone": phone,
                "linkedin": linkedin,
                "total_score": score,
                "bonus_score": bonus,
                "final_percentage": percent,
                "qualified": qualified,
                "llm_ranking_summary": generate_llm_summary(candidate_name, job_role, percent, qualified)
            }

            job_rankings.setdefault(job_role, []).append(entry)

    # Sort and rank
    for job, candidates in job_rankings.items():
        candidates.sort(key=lambda x: x["final_percentage"], reverse=True)
        for i, c in enumerate(candidates, start=1):
            c["rank"] = i

    # Save output
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(job_rankings, out, indent=4)

    print(f"🎯 Job rankings saved to {OUTPUT_FILE}")


# 🔥 Optional CLI
if __name__ == "__main__":
    run_candidate_ranking_by_job()