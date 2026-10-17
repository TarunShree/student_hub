
from recommender.skill_gap import find_skill_gaps
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from recommender.preprocessing import (
    prepare_student,
    prepare_project
)


_PROJECTS_CACHE = None

def get_cached_projects(csv_path="data/projects.csv"):
    global _PROJECTS_CACHE
    if _PROJECTS_CACHE is None:
        projects_df = pd.read_csv(csv_path)
        _PROJECTS_CACHE = [
            prepare_project(row)
            for row in projects_df.to_dict(orient="records")
        ]
    return _PROJECTS_CACHE

def recommend_best_project(student, csv_path="data/projects.csv"):
    # 1. Prepare the student information
    student = prepare_student(student)

    # 2. Load and prepare all projects (cached for zero latency)
    projects = get_cached_projects(csv_path)

    # 3. Create text describing the student's department, skills, and interests
    dept_text = student.get("department", "")
    student_text = f"{dept_text} {' '.join(student['skills'])} {' '.join(student['interests'])}".strip()

    # 4. Compare the student with every project
    project_texts = [
        project["recommendation_text"]
        for project in projects
    ]

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(
        [student_text] + project_texts
    )

    similarities = cosine_similarity(
        vectors[0:1],
        vectors[1:]
    )[0]

    # 5. Find the most similar project
    best_index = similarities.argmax()
    best_project = projects[best_index]

    # 6. Find skills the student needs to learn
    skill_gaps = find_skill_gaps(
        student["skills"],
        best_project["skills"]
    )

    # 7. Return the project and skill gaps
    return {
        "project": best_project.get("raw_title") or best_project["title"].title(),
        "similarity_score": round(
            float(similarities[best_index]) * 100, 2
        ),
        "department": best_project.get("department", ""),
        "tools": best_project.get("technologies", []),
        "recommendation_reason": best_project.get("recommendation_reason", best_project.get("description", "")),
        "estimated_hours": best_project.get("estimated_hours", 6),
        "difficulty": best_project.get("difficulty", "Intermediate"),
        "matched_skills": skill_gaps["matched_skills"],
        "skills_to_learn": skill_gaps["skills_to_learn"]
    }
