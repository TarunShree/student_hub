import re


def clean_text(text):
    """
    Convert text into a clean lowercase format.
    """

    if not text:
        return ""

    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def convert_to_list(value):
    """
    Convert comma-separated text into a clean list.
    """

    if not value:
        return []

    if isinstance(value, list):
        return [clean_text(item) for item in value]

    return [
        clean_text(item)
        for item in str(value).split(",")
        if item.strip()
    ]


def normalize_skill(skill):
    """
    Convert equivalent skill names into one standard name.
    """

    skill = clean_text(skill)

    skill_mapping = {
        "python programming": "python",
        "python language": "python",
        "ml": "machine learning",
        "machinelearning": "machine learning",
        "dataanalytics": "data analytics"
    }

    return skill_mapping.get(skill, skill)


def normalize_skills(skills):
    """
    Clean and normalize a list of skills.
    """

    skills = convert_to_list(skills)

    return list(set(
        normalize_skill(skill)
        for skill in skills
        if skill
    ))



def prepare_student(student):
    """
    Prepare student information for recommendation.
    """

    return {
        "year": student.get("year"),
        "department": clean_text(student.get("department")),
        "skills": normalize_skills(student.get("skills")),
        "interests": normalize_skills(student.get("interests")),
        "skill_level": clean_text(student.get("skill_level")),
        "available_hours": student.get("available_hours"),
        "preferred_difficulty": clean_text(
            student.get("preferred_difficulty")
        )
    }

def prepare_project(project):
    """
    Prepare one project for recommendation.
    """

    raw_title = str(project.get("title", ""))
    title = clean_text(raw_title)
    description = clean_text(project.get("description", ""))
    dept = clean_text(project.get("department", ""))

    skills = normalize_skills(project.get("skills"))
    interests = normalize_skills(project.get("interests"))
    technologies = normalize_skills(project.get("technologies"))

    recommendation_text = " ".join([
        title,
        description,
        dept,
        " ".join(skills),
        " ".join(interests)
    ])

    return {
        "id": project.get("id"),
        "title": title,
        "raw_title": raw_title,
        "description": description,
        "department": dept,
        "skills": skills,
        "interests": interests,
        "technologies": technologies,
        "difficulty": clean_text(project.get("difficulty")),
        "estimated_hours": project.get("estimated_hours"),
        "prerequisites": normalize_skills(
            project.get("prerequisites")
        ),
        "recommendation_reason": project.get("recommendation_reason") or description,
        "source_url": project.get("source_url"),
        "recommendation_text": recommendation_text
    }


    