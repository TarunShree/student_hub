
from recommender.preprocessing import normalize_skills


def find_skill_gaps(student_skills, project_skills):
    # Clean and standardize both skill lists
    student_skills = set(normalize_skills(student_skills))
    project_skills = set(normalize_skills(project_skills))

    # Skills the student already knows
    matched_skills = sorted(student_skills & project_skills)

    # Skills required by the project that the student lacks
    missing_skills = sorted(project_skills - student_skills)

    return {
        "matched_skills": matched_skills,
        "skills_to_learn": missing_skills
    }