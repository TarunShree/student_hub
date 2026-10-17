
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key is missing from environment (.env).")
else:
    try:
        client = genai.Client(api_key=api_key)
        print("API key is loaded into the client.")
        print("Now checking Gemini connectivity...")

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents="Reply OK",
            config={"http_options": {"timeout": 20000}}
        )

        print("SUCCESS: API request worked.")
        print("Gemini response:", response.text)

    except Exception as error:
        print("API TEST FAILED:")
        print(type(error).__name__, str(error))
