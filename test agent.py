import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agent.assistant import run_agent

student = {
    "year": 2,
    "department": "AI & ML",
    "skills": ["Python", "SQL"],
    "interests": ["Machine Learning", "Data Science"],
    "skill_level": "Beginner",
    "available_hours": 6,
    "preferred_difficulty": "Intermediate"
}

history = [
    {
        "role": "user",
        "content": "I am a beginner. What should I learn from basics?"
    },
    {
        "role": "assistant",
        "content": (
            "Start with Python fundamentals: variables, conditions, "
            "loops, functions, lists and dictionaries."
        )
    }
]

result = run_agent(
    "What should I learn first?",
    student,
    history
)

print("\nMentor:", result["response"])