from preprocessing import prepare_student


student = {
    "year": 2,
    "department": "AI & ML",
    "skills": ["Python Programming", "SQL"],
    "interests": ["ML", "Data Science"],
    "skill_level": "Beginner",
    "available_hours": 6,
    "preferred_difficulty": "Intermediate"
}


result = prepare_student(student)

print(result)