import os
import json

# === CONFIG ===
RESULTS_DIR = "data/json/results"
OUTPUT_FILE = "data/json/job_rankings.json"

# Collect ranking data per job
job_rankings = {}

# Step 1: Load each candidate's result file
for filename in os.listdir(RESULTS_DIR):
    if not filename.endswith("__matches.json"):
        continue

    with open(os.path.join(RESULTS_DIR, filename), "r", encoding="utf-8") as f:
        data = json.load(f)

    candidate_name = data.get("candidate_name", data.get("resume_file"))
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
            "qualified": qualified
        }

        if job_role not in job_rankings:
            job_rankings[job_role] = []

        job_rankings[job_role].append(entry)

# Step 2: Sort each job list by percentage (descending)
for job, candidates in job_rankings.items():
    candidates.sort(key=lambda x: x["final_percentage"], reverse=True)
    # Add rank field
    for i, c in enumerate(candidates, start=1):
        c["rank"] = i

# Step 3: Write result
with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    json.dump(job_rankings, out, indent=4)

print(f"Ranking file generated: {OUTPUT_FILE}")
