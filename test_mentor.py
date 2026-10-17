import os
from dotenv import load_dotenv
from agent.mentor import ask_mentor

load_dotenv()

print("Testing Mentor:")
response = ask_mentor("I am a complete beginner. What should I learn first to get into AI?")
print("\nMentor's Response:\n")
print(response)
