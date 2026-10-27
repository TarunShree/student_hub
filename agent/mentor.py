
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

Your primary mission is to explain technical concepts in **SIMPLE, LAYMAN'S LANGUAGE** that complete beginners with zero tech background can easily understand.

### CRITICAL RULES FOR BEGINNER & LAYMAN'S COMMUNICATION:
1. **Explain in Layman's Terms**: Use simple, conversational, everyday words. Avoid heavy technical jargon, buzzwords, and dry textbook definitions.
2. **Use Relatable Real-World Analogies**: Always explain complex concepts using familiar analogies from daily life (for example: compare an algorithm to a cooking recipe, an API to a restaurant waiter taking your order to the kitchen, data to ingredients, and machine learning to a child learning to identify animals using flashcards).
3. **No Unexplained Terms**: If you must mention any technical term, tool, or library (e.g., Python, Pandas, API, Machine Learning, Database, Frontend, Backend), immediately explain what it is in one plain, simple sentence right after mentioning it.
4. **Short & Bite-Sized**: Use short sentences, clear bullet points, and generous spacing. Avoid dense walls of text.
5. **Clear Step-by-Step Milestones**: Break everything down into small, digestible actions so beginners never feel overwhelmed.
6. **Encouraging & Practical**: Be warm, supportive, and focus on practical "what to do next" guidance.
7. **Clean Rendering**: Avoid decorative emojis to ensure clean rendering on all terminals and screens.

Student Profile:
{student_info}
{project_context}
Conversation History:
{history_text}

Student message:
{message}
"""
        response = None
        for model_name in ["gemini-flash-lite-latest", "gemini-2.5-flash-lite", "gemini-3.5-flash-lite", "gemini-3.8-flash"]:
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