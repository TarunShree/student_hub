
def detect_intent(message):
    message = message.lower().strip()

    project_keywords = [
    "recommend a project",
    "recommend me a project",
    "suggest a project",
    "suggest me a project",
    "project for me",
    "project to develop myself",
    "project to build",
    "best project",
    "which project",
    "project recommendation",
    "help me choose a project",
    "give me a project"
]

    roadmap_keywords = [
        "learning roadmap",
    "roadmap",
    "road map",
    "roadmap of the project",
    "roadmap for the project",
    "roadmap for this project",
    "roadmap of this project",
    "i want the roadmap",
    "give me a roadmap",
    "project roadmap",
    "learning path",
    "learn from basics",
    "start from basics",
    "where should i start",
    "what should i learn",
    "how do i learn",
    "how to build this project",
    "steps to build this project"
    ]

    if any(keyword in message for keyword in project_keywords):
        return "recommend_project"

    if any(keyword in message for keyword in roadmap_keywords):
        return "learning_roadmap"

    if message.endswith("?") or any(
        word in message.split()
        for word in ["explain", "what", "why", "how", "teach"]
    ):
        return "explain_concept"

    return "general_chat"
