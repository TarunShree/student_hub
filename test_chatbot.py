import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agent.chatbot import get_chat_response

test_queries = [
    "Hi there!",
    "What are the best study techniques?",
    "How to prepare for final exams?",
    "Can you give me an AI and ML career roadmap?",
    "Full-stack web development tips",
    "How does sleep affect my productivity and memory?",
    "How can I improve my performance prediction score?",
    "What are some good resume project ideas?",
    "What is quantum computing?"
]

print("=" * 60)
print("EduMentor AI - Student Advisor Chatbot Test Suite")
print("=" * 60)

for query in test_queries:
    print(f"\n👤 Student: {query}")
    result = get_chat_response(query)
    print(f"🤖 Mentor Reply:\n{result['reply']}")
    print(f"💡 Suggestions: {result.get('suggestions', [])}")
    print("-" * 60)
