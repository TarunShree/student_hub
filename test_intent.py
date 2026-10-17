
from agent.intent import detect_intent


messages = [
    "Recommend a project for me",
    "I'm a beginner. What should I learn from basics?",
    "What is machine learning?",
    "Hello, I need some guidance"
]

for message in messages:
    print(message, "->", detect_intent(message))
