
import urllib.parse
from agent.intent import detect_intent
from agent.mentor import ask_mentor
from recommender.engine import recommend_best_project


def run_agent(message, student, history=None):
    if history is None:
        history = []
    intent = detect_intent(message)

    print(f"\nDetected intent: {intent}")


    # 1. Project recommendation: use our own recommendation engine
    if intent == "recommend_project":
        result = recommend_best_project(student)

        project = result["project"]
        matched_skills = result["matched_skills"]
        skills_to_learn = result["skills_to_learn"]
        reason = result.get("recommendation_reason", "")
        tools = result.get("tools", [])

        reason_part = f"💡 Why this project: {reason}\n\n" if reason else ""
        tools_part = f"🛠️ Recommended Tools: {', '.join(tools) if isinstance(tools, list) else tools}\n\n" if tools else ""

        encoded_proj = urllib.parse.quote_plus(project)
        roadmap_link = f"👉 [🗺️ Click Here to Open Roadmap & Clear Doubts in Chatbot 2](http://localhost:8501/?project={encoded_proj})"

        return {
            "intent": intent,
            "response": (
                f"My recommended project for you is: **{project}**\n\n"
                f"{reason_part}"
                f"{tools_part}"
                f"Skills you already have: {', '.join(matched_skills) or 'None'}\n"
                f"Skills you need to learn: {', '.join(skills_to_learn) or 'None'}\n\n"
                f"---\n"
                f"{roadmap_link}"
            ),
            "details": result,
            "roadmap_url": f"http://localhost:8501/?project={encoded_proj}"
        }

    # 2. Other questions: use Gemini
    response = ask_mentor(message, student=student, history=history)

    return {
        "intent": intent,
        "response": response,
        "details": None
    }
