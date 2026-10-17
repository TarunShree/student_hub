
from recommender.engine import recommend_best_project

student = {
    "year": 2,
    "department": "AI & ML",
    "skills": ["Python", "SQL"],
    "interests": ["Machine Learning", "Data Science"],
    "skill_level": "Beginner",
    "available_hours": 6,
    "preferred_difficulty": "Intermediate"
}

result = recommend_best_project(student)

print(result)