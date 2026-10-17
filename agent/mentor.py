
import csv
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


def _get_project_reference(message, history=None, csv_path="data/projects.csv"):
    if not os.path.exists(csv_path):
        return None
    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            projects = list(reader)
    except Exception:
        return None

    search_corpus = message
    if history:
        for turn in reversed(history):
            search_corpus += " " + turn.get("content", "")

    search_corpus_lower = search_corpus.lower()
    for project in projects:
        title = project.get("title", "")
        if title and title.lower() in search_corpus_lower:
            return (
                f"Referenced Project from catalog: {title}\n"
                f"- Description: {project.get('description')}\n"
                f"- Department: {project.get('department')}\n"
                f"- Technologies: {project.get('technologies')}\n"
                f"- Skills: {project.get('skills')}\n"
                f"- Difficulty: {project.get('difficulty')}\n"
                f"- Estimated Hours: {project.get('estimated_hours')} hours\n"
                f"- Prerequisites: {project.get('prerequisites')}"
            )
    return None


def ask_mentor(message, student=None, history=None):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "Gemini API key is not configured."

    try:
        client = genai.Client(api_key=api_key)

        profile_parts = []
        if student:
            if "year" in student:
                profile_parts.append(f"- Year: {student.get('year')}")
            if "department" in student:
                profile_parts.append(f"- Department: {student.get('department')}")
            if "skills" in student:
                skills = student.get("skills", [])
                profile_parts.append(f"- Known Skills: {', '.join(skills) if isinstance(skills, list) else skills}")
            if "interests" in student:
                interests = student.get("interests", [])
                profile_parts.append(f"- Interests: {', '.join(interests) if isinstance(interests, list) else interests}")
            if "skill_level" in student:
                profile_parts.append(f"- Skill Level: {student.get('skill_level')}")
            if "preferred_difficulty" in student:
                profile_parts.append(f"- Preferred Difficulty: {student.get('preferred_difficulty')}")
            if "mentor_mode" in student:
                profile_parts.append(f"- Mentorship Style / Tone: {student.get('mentor_mode')}")

        student_info = "\n".join(profile_parts) if profile_parts else "Not provided"

        history_parts = []
        if history:
            for turn in history[-10:]:
                role = turn.get("role", "user")
                speaker = "Student" if role == "user" else "Mentor"
                content = turn.get("content", "").strip()
                if content:
                    history_parts.append(f"{speaker}: {content}")

        history_text = "\n\n".join(history_parts) if history_parts else "None (this is the start of the conversation)"

        project_ref = _get_project_reference(message, history)
        project_context = f"\nRelevant Project Details:\n{project_ref}\n" if project_ref else ""

        prompt = f"""
You are the AI Student Mentor inside an AI Student Ecosystem.

Your responsibilities:
- Explain technical concepts in simple, engaging language.
- Guide beginners from the fundamentals.
- When asked about a recommended project or a previously discussed topic, refer to the conversation history and project details to give a detailed, practical explanation (what the project is, why it's useful, and step-by-step guidance on how to build it).
- Never claim you don't know what was recommended if it is mentioned in the conversation history or project details.
- Create practical learning roadmaps with learning order and small milestones.
- Give advice suitable for college students.
- Never assume a student has a skill unless their profile confirms it.
- Keep answers clear, well-structured, practical, and encouraging.
- Avoid using decorative emojis to ensure clean rendering on all terminals.

Student Profile:
{student_info}
{project_context}
Conversation History:
{history_text}

Student message:
{message}
"""
        response = None
        for model_name in ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.8-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={
                        "http_options": {"timeout": 25000}
                    }
                )
                if response and response.text:
                    break
            except Exception as model_err:
                print(f"Model {model_name} unavailable: {model_err}")
                continue

        if response and response.text:
            return response.text
        return "I couldn't generate an answer. Please try again."

    except Exception as error:
        print(f"Gemini API error: {type(error).__name__}: {error}")
        return "Sorry, I couldn't get a response from the AI mentor. Please try again."