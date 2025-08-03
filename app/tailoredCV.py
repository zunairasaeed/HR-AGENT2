import os
import json

# === CONFIG ===
MATCHED_DIR = "data/json/results"
TAILORED_DIR = "data/json/tailored"
os.makedirs(TAILORED_DIR, exist_ok=True)

def tailor_best_job_cv():
    for file_name in os.listdir(MATCHED_DIR):
        if not file_name.endswith("__matches.jsoan"):
            continue

        file_path = os.path.join(MATCHED_DIR, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        matched_jobs = data.get("matched_jobs", [])
        if not matched_jobs:
            continue

        # Sort jobs by final_percentage (descending)
        sorted_jobs = sorted(matched_jobs, key=lambda x: x.get("final_percentage", 0), reverse=True)
        best_job = sorted_jobs[0]
        other_jobs = sorted_jobs[1:]

        tailored_data = {
            "candidate_name": data.get("candidate_name", "Unknown"),
            "email": data.get("email", ""),
            "phone": data.get("phone", ""),
            "linkedin": data.get("linkedin", ""),
            "target_job": best_job.get("job_role"),
            "final_match_percentage": best_job.get("final_percentage"),
            "qualified": best_job.get("qualified"),
            "matched": best_job.get("matched", {}),
            "total_score": best_job.get("total_score"),
            "bonus_score": best_job.get("bonus_score"),
            "max_score_among_candidates": best_job.get("max_score_among_candidates"),
            "other_job_scores": [
                {
                    "job_role": j["job_role"],
                    "score": j["total_score"],
                    "match_percentage": j["final_percentage"],
                    "qualified": j["qualified"]
                }
                for j in other_jobs
            ]
        }

        # Save tailored CV JSON
        candidate_safe = file_name.replace("__matches.json", "__tailored.json")
        out_path = os.path.join(TAILORED_DIR, candidate_safe)

        with open(out_path, "w", encoding="utf-8") as out:
            json.dump(tailored_data, out, indent=4)

        print(f"✅ Tailored CV created for: {tailored_data['candidate_name']} → {out_path}")

if __name__ == "__main__":
    tailor_best_job_cv()
