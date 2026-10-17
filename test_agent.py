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

history = []

print("\n===== AI STUDENT MENTOR =====")
print("Ask questions about projects, roadmaps, or concepts.")
print("Type 'exit' to stop.\n")

while True:
    message = input("You: ").strip()

    if message.lower() in ["exit", "quit"]:
        print("Mentor: Goodbye! Keep learning.")
        break

    if not message:
        continue

    try:
        result = run_agent(
            message=message,
            student=student,
            history=history
        )

        response = result["response"]
        print(f"\nMentor: {response}\n")

        history.append({
            "role": "user",
            "content": message
        })
        history.append({
            "role": "assistant",
            "content": response
        })

        history = history[-10:]

    except Exception as error:
        print(f"\nError: {error}\n")
