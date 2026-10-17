
from recommender.skill_gap import find_skill_gaps

student_skills = ["Python", "SQL"]

project_skills = [
    "Python",
    "Pandas",
    "SQL",
    "Machine Learning",
    "Scikit-learn"
]

result = find_skill_gaps(student_skills, project_skills)

print(result)