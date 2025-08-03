# import os
# import json
# import re

# # === CONFIGURATION ===
# RESUMES_DIR = "data/json/normalized"
# JOBS_FILE = "data/jobs/jobs.json"
# RESULTS_DIR = "data/json/results"
# os.makedirs(RESULTS_DIR, exist_ok=True)

# # === SCORING WEIGHTS ===
# CATEGORY_WEIGHTS = {
#     "must_have": 5,
#     "nice_to_have": 3,
#     "bonus": 2
# }

# def normalize_text(text):
#     """Lowercase and clean spacing"""
#     return re.sub(r'\s+', ' ', text.lower().strip())

# def get_match_context(resume_data):
#     """Build context for matching: structured + raw_text"""
#     context = []
#     context += resume_data.get("skills", [])
#     context += resume_data.get("keywords", [])
#     context += resume_data.get("certificates", [])
    
#     raw_text = resume_data.get("raw_text", "")
#     context += re.findall(r'\b\w+\b', raw_text.lower())

#     return list(set([normalize_text(word) for word in context if len(word) > 1]))

# def match_keywords(context_words, keywords):
#     """Return matched keywords from context"""
#     matched = []
#     for kw in keywords:
#         kw_norm = normalize_text(kw)
#         if kw_norm in context_words:
#             matched.append(kw)
#     return list(set(matched))

# def process_resume(file_name, jobs_data):
#     with open(os.path.join(RESUMES_DIR, file_name), 'r', encoding='utf-8') as f:
#         resume_data = json.load(f)

#     context_words = get_match_context(resume_data)
#     matched_jobs = []

#     for role, job in jobs_data.items():
#         total_score = 0
#         matched_summary = {}

#         # Match must_have, nice_to_have, bonus
#         for category in ["must_have", "nice_to_have", "bonus"]:
#             items = job.get(category, [])
#             matched = match_keywords(context_words, items)
#             score = len(matched) * CATEGORY_WEIGHTS[category]
#             total_score += score

#             matched_summary[category] = {
#                 "matched": matched,
#                 "score": score
#             }

#         matched_jobs.append({
#             "job_role": role,
#             "matched": matched_summary,
#             "total_score": total_score,
#             "qualified": total_score >= 75
#         })

#     # Final result per resume, with all job matches
#     result = {
#         "resume_file": file_name,
#         "candidate_name": resume_data.get("name", "Unknown"),
#         "email": resume_data.get("email", ""),
#         "phone": resume_data.get("phone", ""),
#         "linkedin": resume_data.get("linkedin", ""),
#         "matched_jobs": matched_jobs
#     }

#     out_name = file_name.replace(".json", "__matches.json")
#     with open(os.path.join(RESULTS_DIR, out_name), "w", encoding="utf-8") as out:
#         json.dump(result, out, indent=4)

# def main():
#     with open(JOBS_FILE, "r", encoding="utf-8") as f:
#         jobs_data = json.load(f)

#     for resume_file in os.listdir(RESUMES_DIR):
#         if resume_file.endswith(".json"):
#             process_resume(resume_file, jobs_data)

# if __name__ == "__main__":
#     main()












import os
import json
import re

# === CONFIGURATION ===
RESUMES_DIR = "data/json/normalized"
JOBS_FILE = "data/jobs/jobs.json"
RESULTS_DIR = "data/json/results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# === SCORING WEIGHTS ===
CATEGORY_WEIGHTS = {
    "must_have": 5,
    "nice_to_have": 3,
    "bonus": 2
}

# Qualification cutoff percentage based on relative scoring later
QUALIFICATION_PERCENTAGE = 60


def normalize_text(text):
    return re.sub(r'\s+', ' ', text.lower().strip())

def get_match_context(resume_data):
    context = []
    context += resume_data.get("skills", [])
    context += resume_data.get("keywords", [])
    context += resume_data.get("certificates", [])

    raw_text = resume_data.get("raw_text", "")
    context += re.findall(r'\b\w+\b', raw_text.lower())

    return list(set([normalize_text(word) for word in context if len(word) > 1]))

def match_keywords(context_words, keywords):
    matched = []
    for kw in keywords:
        if normalize_text(kw) in context_words:
            matched.append(kw)
    return list(set(matched))

def collect_max_scores(jobs_data):
    """Pass 1: Get the max total score per job across all resumes."""
    max_scores = {role: 0 for role in jobs_data.keys()}
    for resume_file in os.listdir(RESUMES_DIR):
        if not resume_file.endswith(".json"):
            continue
        with open(os.path.join(RESUMES_DIR, resume_file), 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
        context_words = get_match_context(resume_data)

        for role, job in jobs_data.items():
            score = 0
            for category in ["must_have", "nice_to_have"]:
                matched = match_keywords(context_words, job.get(category, []))
                weight = CATEGORY_WEIGHTS[category]
                score += len(matched) * weight
            if score > max_scores[role]:
                max_scores[role] = score
    return max_scores

def process_resume(file_name, jobs_data, job_max_scores):
    with open(os.path.join(RESUMES_DIR, file_name), 'r', encoding='utf-8') as f:
        resume_data = json.load(f)

    context_words = get_match_context(resume_data)
    matched_jobs = []

    for role, job in jobs_data.items():
        total_score = 0
        bonus_score = 0
        matched_summary = {}

        for category in ["must_have", "nice_to_have", "bonus"]:
            items = job.get(category, [])
            matched = match_keywords(context_words, items)

            weight = CATEGORY_WEIGHTS[category]
            score = len(matched) * weight

            if category in ["must_have", "nice_to_have"]:
                total_score += score
            elif category == "bonus":
                bonus_score = score

            matched_summary[category] = {
                "matched": matched,
                "score": score
            }

        max_score = job_max_scores.get(role, 1)
        match_percentage = (total_score / max_score * 100) if max_score > 0 else 0
        match_percentage += bonus_score  # ADD bonus on top
        qualified = match_percentage >= QUALIFICATION_PERCENTAGE

        matched_jobs.append({
            "job_role": role,
            "matched": matched_summary,
            "total_score": total_score,
            "bonus_score": bonus_score,
            "max_score_among_candidates": max_score,
            "final_percentage": round(match_percentage, 2),
            "qualified": qualified
        })

    result = {
        "resume_file": file_name,
        "candidate_name": resume_data.get("name", "Unknown"),
        "email": resume_data.get("email", ""),
        "phone": resume_data.get("phone", ""),
        "linkedin": resume_data.get("linkedin", ""),
        "matched_jobs": matched_jobs
    }

    out_name = file_name.replace(".json", "__matches.json")
    with open(os.path.join(RESULTS_DIR, out_name), "w", encoding="utf-8") as out:
        json.dump(result, out, indent=4)

def main():
    with open(JOBS_FILE, "r", encoding="utf-8") as f:
        jobs_data = json.load(f)

    job_max_scores = collect_max_scores(jobs_data)

    for resume_file in os.listdir(RESUMES_DIR):
        if resume_file.endswith(".json"):
            process_resume(resume_file, jobs_data, job_max_scores)

if __name__ == "__main__":
    main()
