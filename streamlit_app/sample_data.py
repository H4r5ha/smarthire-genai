"""
Controlled demo data for UI-only mode.

Everything in this module is SAMPLE data. The UI must label it as such and
must never present it as the output of a real parse / AI call.
"""

SAMPLE_PROFILE = {
    "name": "Harsha",
    "initial": "H",
    "target_role": "Aspiring Data Scientist",
    "location": "Bengaluru, India",
    "email": "harsha@example.com",
    "experience_years": 3,
    "education": "B.Tech, Computer Science",
    "completeness": 85,
    "completeness_items": [
        ("Personal Info", True),
        ("Skills (12)", True),
        ("Experience (3 years)", True),
        ("Education", True),
        ("Projects (2)", False),
    ],
    "skills": [
        "Python", "Machine Learning", "Data Analysis", "SQL", "NLP",
        "Deep Learning", "Pandas", "scikit-learn", "Power BI", "Statistics",
        "Matplotlib", "Data Visualization",
    ],
    "experience": [
        {
            "title": "Data Science Intern",
            "company": "Quillworks AI",
            "period": "2023 – Present",
            "points": [
                "Built NLP pipelines for support-ticket classification.",
                "Automated weekly reporting with Python and SQL.",
            ],
        },
        {
            "title": "Analytics Associate",
            "company": "Northwind Retail",
            "period": "2021 – 2023",
            "points": [
                "Developed Power BI dashboards for regional sales teams.",
                "Ran A/B tests on promotional campaigns.",
            ],
        },
    ],
    "education_items": [
        {"degree": "B.Tech, Computer Science", "school": "PES University", "period": "2017 – 2021", "detail": "CGPA 8.6 / 10"},
    ],
    "projects": [
        {
            "name": "Resume–Job Matcher",
            "description": "Semantic retrieval system that ranks job postings against a parsed resume using dense embeddings.",
            "tech": ["Python", "FAISS", "Sentence-Transformers", "Streamlit"],
        },
        {
            "name": "Customer Churn Predictor",
            "description": "Gradient-boosted classifier with SHAP explanations deployed as a REST service.",
            "tech": ["scikit-learn", "XGBoost", "FastAPI", "Docker"],
        },
    ],
    "summary": (
        "Data professional with three years of experience across analytics and applied machine learning. "
        "Comfortable owning the full lifecycle from data preparation to model deployment, with a focus on NLP "
        "and retrieval systems."
    ),
    "certifications": [
        {"name": "TensorFlow Developer Certificate", "issuer": "Google", "year": "2023"},
    ],
    "achievements": [
        "Winner, Northwind Retail internal hackathon (2022).",
    ],
}

SUGGESTED_ROLES = [
    {"role": "Data Scientist", "jobs": 1248, "reason": "Strongest overlap with your ML and statistics skills."},
    {"role": "Machine Learning Engineer", "jobs": 856, "reason": "Matches your deployment and NLP experience."},
    {"role": "Data Analyst", "jobs": 2341, "reason": "Your SQL and Power BI background transfers directly."},
]

MATCH_SUMMARY = {"relevant_jobs": "1,248", "best_match": "92%", "avg_match": "78%", "filters": "None"}

SAMPLE_JOBS = [
    {
        "title": "Senior Machine Learning Engineer",
        "company": "Quillworks AI",
        "location": "Bengaluru",
        "mode": "Hybrid",
        "type": "Full-time",
        "posted": "2 days ago",
        "score": 92,
        "matching": ["Python", "PyTorch", "NLP", "FastAPI", "AWS"],
        "missing": ["Kubernetes"],
        "why": "Strong overlap with the candidate's retrieval and production ML experience.",
    },
    {
        "title": "Data Scientist",
        "company": "Google",
        "location": "Bengaluru",
        "mode": "On-site",
        "type": "Full-time",
        "posted": "2 days ago",
        "score": 88,
        "matching": ["Python", "Machine Learning", "SQL", "Data Analysis"],
        "missing": ["Spark", "BigQuery"],
        "why": "Work on large-scale ML systems and drive data-driven solutions.",
    },
    {
        "title": "Senior Data Analyst",
        "company": "Microsoft",
        "location": "Hyderabad",
        "mode": "Hybrid",
        "type": "Full-time",
        "posted": "3 days ago",
        "score": 81,
        "matching": ["SQL", "Power BI", "Data Visualization", "Statistics"],
        "missing": ["Azure Synapse", "DAX"],
        "why": "Analytics and dashboarding experience map well; cloud data stack is the gap.",
    },
    {
        "title": "Applied NLP Scientist",
        "company": "Sarvam Labs",
        "location": "Remote",
        "mode": "Remote",
        "type": "Full-time",
        "posted": "5 days ago",
        "score": 74,
        "matching": ["NLP", "Deep Learning", "Python"],
        "missing": ["Transformers fine-tuning", "CUDA", "Research publications"],
        "why": "NLP foundation is solid; the role expects deeper model-training experience.",
    },
    {
        "title": "Business Intelligence Analyst",
        "company": "Flipkart",
        "location": "Bengaluru",
        "mode": "On-site",
        "type": "Contract",
        "posted": "1 week ago",
        "score": 63,
        "matching": ["SQL", "Power BI", "Statistics"],
        "missing": ["Tableau", "Snowflake", "dbt"],
        "why": "Reporting skills fit; the modern BI stack is largely missing.",
    },
]

SAMPLE_TARGET_JOB = {
    "title": "Senior Machine Learning Engineer",
    "company": "Quillworks AI",
    "location": "Bengaluru · Hybrid",
}

SAMPLE_CV_RESULT = {
    "readiness": 71,
    "ats_score_before": 71,
    "ats_score_after": 88,
    "matched": 12,
    "missing_count": 5,
    "job_requirements": [
        "Python", "PyTorch", "NLP", "FastAPI", "AWS",
        "MLOps", "Docker", "System Design", "Big Data",
    ],
    "matched_skills": [
        "Python", "PyTorch", "NLP", "FastAPI", "AWS",
        "Machine Learning", "Data Analysis", "SQL", "Pandas",
        "scikit-learn", "Statistics", "Deep Learning",
    ],
    "missing_skills": [
        {"skill": "MLOps", "priority": "High"},
        {"skill": "AWS", "priority": "High"},
        {"skill": "Docker", "priority": "High"},
        {"skill": "System Design", "priority": "Medium"},
        {"skill": "Big Data", "priority": "Medium"},
    ],
    "why_skills": (
        "These skills appear in most Senior ML Engineer postings we retrieved. "
        "They are commonly required to move models from notebooks into reliable production services."
    ),
    "has_summary": True,
    "summary": (
        "Machine learning practitioner with 3+ years of experience building NLP and retrieval systems "
        "end-to-end. Proficient in Python, PyTorch and SQL, with hands-on delivery of production pipelines "
        "that improved prediction accuracy by 15%. Passionate about shipping reliable, measurable AI products."
    ),
    "bullets": [
        {
            "before": "Worked on ML models. Improved data pipelines.",
            "after": "Developed and deployed machine learning models that improved prediction accuracy by 15%. Built automated data pipelines reducing processing time by 40%.",
            "why": "Adds specific actions, quantified outcomes and production context recruiters look for.",
        },
        {
            "before": "Made dashboards for the sales team.",
            "after": "Designed Power BI dashboards used weekly by 40+ regional sales managers, cutting manual reporting effort by 6 hours per week.",
            "why": "Shows audience, scale and a concrete time saving instead of a vague task.",
        },
        {
            "before": "Used Python for NLP tasks.",
            "after": "Built an NLP classification pipeline (spaCy, scikit-learn) that auto-routed 12k support tickets per month with 91% precision.",
            "why": "Names the tools, the volume handled and a measurable quality metric.",
        },
    ],
    "experience_rewrites": [],
    "project_rewrites": [],
    "certification_rewrites": [
        {
            "certification": "TensorFlow Developer Certificate",
            "before": "TensorFlow Developer Certificate, Google, 2023",
            "after": "TensorFlow Developer Certificate — Google (2023): validated production model-building skills directly relevant to this ML Engineer role.",
            "why": "Ties the certification explicitly to the target role instead of listing it as a bare line item.",
        }
    ],
    "achievement_rewrites": [
        {
            "achievement": "Winner, Northwind Retail internal hackathon (2022).",
            "before": "Winner, Northwind Retail internal hackathon (2022).",
            "after": "1st place, Northwind Retail internal hackathon (2022) — built a working prototype under a 48-hour deadline.",
            "why": "Adds the concrete constraint (48-hour deadline) that already exists in the story to show scope without inventing new facts.",
        }
    ],
    "skills_section": {
        "recommended": [
            "Python", "Machine Learning", "Data Analysis", "SQL", "NLP",
            "Deep Learning", "Pandas", "scikit-learn", "Power BI", "Statistics",
        ],
        "missing_to_add_after_learning": ["MLOps", "AWS", "Docker", "System Design", "Big Data"],
        "why": "Keeps the skills section limited to what's already provable from experience, with target-role gaps clearly separated.",
    },
    "resume_issues": [
        {
            "issue": "Quantified outcomes are inconsistent across bullets.",
            "severity": "Medium",
            "fix": "Add a measurable result to each experience bullet where the underlying evidence supports one.",
        }
    ],
    "recommendations": [
        "Learn MLOps and Docker first — they're the highest-priority gaps against this role's postings.",
        "Add AWS hands-on experience (even a small deployed project) to close the second most-requested gap.",
        "Lead with your strongest ML project and its measurable outcome.",
        "Move certifications above education once you've added the missing skills above.",
    ],
    "soft_skills_from_jd": [
        {
            "skill": "Cross-functional collaboration",
            "why_relevant": "The posting asks for engineers who partner closely with product and data teams.",
            "how_to_add": "Your NLP pipeline bullet already shows this — mention the support/product stakeholders it served.",
        },
        {
            "skill": "Ownership",
            "why_relevant": "The role expects engineers to own a service from prototype to production.",
            "how_to_add": "Add a short 'Core Strengths' line noting end-to-end ownership, backed by your pipeline deployment bullet.",
        },
    ],
}

SUGGESTED_QUESTIONS = [
    "How do I switch to Data Analyst?",
    "What skills should I learn next?",
    "Which roles suit my profile?",
    "How should I prepare for interviews?",
    "Tell me about the Data Scientist career path.",
]

SAMPLE_MENTOR_ANSWER = (
    "Based on your profile and the retrieved career documents, a switch to a Data Analyst role is very "
    "achievable. You already have SQL, Power BI and statistics. Prioritise three things: (1) deepen SQL with "
    "window functions and query optimisation, (2) build one dashboard project with a clear business narrative, "
    "and (3) practise experimentation and A/B test analysis. Most Data Analyst postings we retrieved list exactly "
    "these requirements."
)

SAMPLE_SOURCES = [
    {"title": "Data Analyst Job Guide", "type": "Career document", "relevance": 92},
    {"title": "Career Roadmap — Data Analytics", "type": "Knowledge base", "relevance": 88},
    {"title": "Retrieved Job Description — Senior Data Analyst, Microsoft", "type": "Job posting", "relevance": 76},
]

RAG_PIPELINE = ["Guardrail", "Query Embedding", "FAISS Retrieval", "Evidence Gate", "Gemini"]

DATASET_METRICS = {"total_jobs": "5,420", "ds_jobs": "2,180", "se_jobs": "3,240", "valid": "5,390"}

INDEX_STATUS = [
    {"name": "FAISS Index", "ready": True, "detail": "Last built 3 hours ago"},
    {"name": "BM25 Index", "ready": True, "detail": "Last built 3 hours ago"},
    {"name": "Embeddings", "ready": True, "detail": "Model: text-embedding-3-small"},
    {"name": "Knowledge Base", "ready": True, "detail": "12 documents loaded"},
]

DATA_PIPELINE = [
    ("Load CSV Dataset", "Naukri job postings"),
    ("Clean & Preprocess", "Remove duplicates, standardise fields"),
    ("Generate Embeddings", "Dense local embeddings for every posting"),
    ("Build FAISS Index", "Store vectors for fast similarity search"),
    ("Load Career Notes", "Local RAG knowledge base"),
    ("Ready", "Semantic search and mentor retrieval ready"),
]

EVAL_OVERVIEW = {"top1": 72, "top5": 89, "grounding": 0.86, "helpfulness": 0.84}

EVAL_RETRIEVAL = [
    {"category": "Data Scientist", "Top-1": 74, "Top-5": 90, "Top-10": 96},
    {"category": "Software Engineer", "Top-1": 69, "Top-5": 87, "Top-10": 94},
    {"category": "Data Analyst", "Top-1": 77, "Top-5": 91, "Top-10": 97},
]

EVAL_MENTOR = [
    {"metric": "Correctness", "Original": 0.71, "Improved": 0.86},
    {"metric": "Grounding", "Original": 0.64, "Improved": 0.88},
    {"metric": "Helpfulness", "Original": 0.72, "Improved": 0.84},
]

PROMPT_COMPARISON = {
    "original_prompt": "You are a career assistant. Answer the user's question.",
    "original_result": (
        "You should learn Kubernetes, Spark, Rust and get a PhD. Most Data Analysts earn $180k in Bengaluru."
    ),
    "original_issues": ["Unsupported salary claim", "Ignores retrieved evidence", "Generic advice"],
    "improved_prompt": (
        "You are SmartHire Mentor. Answer ONLY using the retrieved evidence and the candidate profile. "
        "Cite sources. If evidence is insufficient, say so."
    ),
    "improved_result": (
        "Based on 3 retrieved Data Analyst postings, the most requested skills you are missing are advanced SQL "
        "and experimentation. Your Power BI experience is already a strength. [Sources 1, 2]"
    ),
    "improved_wins": ["Grounded in evidence", "Cites sources", "Personalised to profile"],
}

HALLUCINATION_TEST = {
    "question": "What is the exact salary Quillworks AI pays for this role?",
    "evidence": "No retrieved document mentions compensation for this posting.",
    "expected": "Refuse or say the knowledge base does not contain this information.",
    "actual": "I don't have enough evidence to answer that. None of the retrieved documents include salary details for this role.",
    "passed": True,
}