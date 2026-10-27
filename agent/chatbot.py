"""
Chatbot module for the AI-Student-Ecosystem.
Provides intelligent academic advising, project doubt clarification, career roadmaps,
and study guidance for students in simple, crystal-clear layman's language.
"""

import os
import re
from typing import Dict, Any, List
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Active working Gemini models in order of priority (gemini-2.5-flash is retired/404 for new users)
GEMINI_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest"),
    "gemini-flash-lite-latest",
    "gemini-2.5-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash"
]

class StudentAdvisorChatbot:
    """
    Intelligent student advisory & doubt-clearing chatbot.
    Answers any manual technical, project, or academic question using Google Gemini
    in simple layman's language with real-world analogies, while supporting full offline fallback.
    """

    def __init__(self):
        self.bot_name = "EduMentor AI"
        self.knowledge_base = self._initialize_knowledge()

    def _initialize_knowledge(self) -> List[Dict[str, Any]]:
        """Structured offline knowledge base for instant offline answers."""
        return [
            {
                "intent": "study_techniques",
                "keywords": ["study technique", "study method", "feynman", "pomodoro", "active recall", "spaced repetition", "how to study"],
                "response": (
                    "### 🎯 Top Study Methods for Beginners\n\n"
                    "1. **The Feynman Technique (Teach Like You're Talking to a 10-Year-Old)**:\n"
                    "   - Take a concept you just learned and explain it out loud in the simplest everyday words you can.\n"
                    "   - Whenever you get stuck or use a complicated word, go back to your notes and simplify it until anyone can understand you!\n\n"
                    "2. **Active Recall (Self-Testing with Flashcards)**:\n"
                    "   - Passive re-reading tricks your brain into thinking you know the material.\n"
                    "   - Instead, close the book and quiz yourself, or use flashcard apps (like Anki). Test yourself again after 1 day, 3 days, and 1 week.\n\n"
                    "3. **Pomodoro (25-Min Focus + 5-Min Walk)**:\n"
                    "   - Set a timer for 25 minutes and work on just ONE single task.\n"
                    "   - When the timer rings, take a 5-minute break away from screens to let your brain recharge."
                ),
                "suggestions": [
                    "How to prepare for final exams?",
                    "How to balance study and sleep?",
                    "Suggest a daily study schedule"
                ]
            },
            {
                "intent": "exam_prep",
                "keywords": ["exam prep", "prepare for exam", "final exam", "cramming", "exam stress", "exam timetable"],
                "response": (
                    "### 📝 Stress-Free Exam Preparation Blueprint\n\n"
                    "- **2 Weeks Before**: Practice solving old exam papers with a timer like a fun rehearsal match.\n"
                    "- **1 Week Before**: Find high-weightage topics and summarize them onto a 1-page cheat sheet.\n"
                    "- **2 Days Before**: Don't try to learn brand-new chapters now. Reinforce what you already know so you feel confident.\n"
                    "- **Night Before**: Get 7 to 8 hours of solid sleep. Your brain organizes and locks in your memories while you rest!"
                ),
                "suggestions": [
                    "Help me handle exam stress",
                    "How many hours should I study daily?",
                    "Tips for active recall"
                ]
            },
            {
                "intent": "career_ai_ml",
                "keywords": ["ai roadmap", "machine learning roadmap", "ml career", "how to learn ai", "data science roadmap"],
                "response": (
                    "### 🤖 AI & Machine Learning Explained Simply\n\n"
                    "Think of Machine Learning like teaching a computer by showing it lots of photo examples, the same way a child learns what a dog looks like!\n\n"
                    "Here is your beginner roadmap:\n"
                    "1. **Learn Python**: The friendliest coding language in the world.\n"
                    "2. **Work with Data (Pandas)**: Pandas is like Excel inside Python—you use it to open tables and inspect numbers.\n"
                    "3. **Build Simple Models (Scikit-Learn)**: Use ready-made toolkits to predict numbers or sort things into categories.\n"
                    "4. **Build Cool Projects**: Create a working app (like our Smart Campus Waste Classifier or Academic Predictor) to showcase on your resume!"
                ),
                "suggestions": [
                    "Web development roadmap",
                    "Best portfolio project ideas",
                    "How to get tech internships"
                ]
            },
            {
                "intent": "career_web_dev",
                "keywords": ["web dev roadmap", "web development roadmap", "frontend roadmap", "backend roadmap", "fullstack roadmap"],
                "response": (
                    "### 🌐 Web Development Roadmap in Plain English\n\n"
                    "Building websites is just like building a house:\n"
                    "1. **HTML (The Brick Walls)**: Creates the structure—headings, text, buttons, and images.\n"
                    "2. **CSS (The Paint & Interior Design)**: Makes everything look modern, clean, colorful, and styled.\n"
                    "3. **JavaScript (The Electricity & Plumbing)**: Makes things interactive—like buttons that open popups or submit forms.\n"
                    "4. **Backend & Databases (The Storage Room)**: Stores user accounts and handles logic behind the scenes using Python (FastAPI/Flask) or Node.js."
                ),
                "suggestions": [
                    "AI & Machine Learning roadmap",
                    "Resume tips for software engineering",
                    "How to start contributing to open source"
                ]
            },
            {
                "intent": "ide_terminal_commands",
                "keywords": ["check version", "git version", "python version", "node version", "npm version", "terminal command", "install package"],
                "response": (
                    "### 🛠️ Easy Guide: Checking Tools & Versions in Your Code Editor\n\n"
                    "Think of your terminal (command prompt) like a text chat where you give your computer direct instructions.\n\n"
                    "Here are the simple commands to check your tools:\n"
                    "1. **Check Python** (Your coding language):\n"
                    "   ```bash\n"
                    "   python --version\n"
                    "   ```\n\n"
                    "2. **Check Git** (Tracks changes like save checkpoints):\n"
                    "   ```bash\n"
                    "   git --version\n"
                    "   ```\n\n"
                    "3. **Check Node & npm** (Runs modern web screens):\n"
                    "   ```bash\n"
                    "   node --version\n"
                    "   npm --version\n"
                    "   ```\n\n"
                    "4. **Installing a Python Package**:\n"
                    "   ```bash\n"
                    "   pip install <package_name>\n"
                    "   ```\n\n"
                    "💡 *Remember: You don't need complicated Git commands to build your project roadmap—just focus on building your project step by step!*"
                ),
                "suggestions": [
                    "How to open terminal in VS Code",
                    "AI & Machine Learning roadmap",
                    "Fun project ideas for beginners"
                ]
            }
        ]

    def _ask_gemini_in_laymans_terms(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """
        Query Gemini LLM with strict instructions to answer ANY student doubt or manual question
        in simple layman's language with relatable real-world analogies.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None

        # Build context about active project or student
        project_context_str = ""
        if context:
            proj_name = context.get("project") or context.get("title") or context.get("project_name")
            if proj_name:
                project_context_str += f"\n- Active Project: {proj_name}"
            skills = context.get("skills")
            if skills:
                skills_val = ", ".join(skills) if isinstance(skills, list) else str(skills)
                project_context_str += f"\n- Student's Skills: {skills_val}"
            interest = context.get("interest")
            if interest:
                project_context_str += f"\n- Student's Interest: {interest}"

        prompt = f"""
You are EduMentor AI, a warm, patient, and brilliant academic advisor and project mentor for college students.
Your core mission is to answer the student's exact question or technical doubt in **EXTREMELY CLEAR, LAYMAN'S LANGUAGE** that complete beginners with ZERO prior technical knowledge can immediately understand.

### STUDENT CONTEXT:
{project_context_str if project_context_str else "- General student / beginner"}

### STUDENT'S MANUAL QUESTION / DOUBT:
"{user_message}"

### STRICT RULES FOR YOUR RESPONSE:
1. **Directly Answer Their Question**: Do NOT give generic canned advice. Answer the exact question or problem the student asked about.
2. **Use Relatable Real-World Analogies**: Always explain technical concepts using familiar daily life analogies (like cooking recipes, ordering pizza, a restaurant waiter, cars, filing cabinets, or LEGO blocks).
3. **Working Beginner-Friendly Code**: If they ask for code or how to build something, provide clean, minimal, working code with simple plain-English comments above each line explaining what it does.
4. **No Unexplained Jargon**: If you mention any technical term (like API, database, framework, model, server, loop), explain what it is in one simple everyday sentence.
5. **Short & Clean Formatting**: Use markdown headings (`###`), bullet points, bold key terms, and generous spacing. Avoid dense walls of text.
6. **Encouraging Tone**: End with a warm, encouraging 1-sentence next step the student can do right now.
"""
        try:
            client = genai.Client(api_key=api_key)
            seen_models = set()
            for model_name in GEMINI_MODELS:
                if not model_name or model_name in seen_models:
                    continue
                seen_models.add(model_name)
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config={"http_options": {"timeout": 25000}}
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception as model_err:
                    print(f"Gemini model {model_name} attempt failed: {model_err}")
                    continue
        except Exception as err:
            print(f"Gemini client error in chatbot: {err}")
        return None

    def _generate_smart_suggestions(self, user_message: str, context: Dict[str, Any] = None) -> List[str]:
        """Generate dynamic, relevant follow-up suggestion chips based on the question."""
        q_low = user_message.lower()
        proj = (context.get("project") if context else "") or ""

        if "sqlite" in q_low or "database" in q_low or "sql" in q_low:
            return [
                "How do I add and read data in SQLite?",
                "How do I connect my database to a web page?",
                "What is SQL injection and how to avoid it?"
            ]
        elif "api" in q_low or "fastapi" in q_low or "flask" in q_low:
            return [
                "Show me a simple FastAPI hello world example",
                "How do I test my API in the browser?",
                "How does my frontend talk to this API?"
            ]
        elif "git" in q_low or "version" in q_low or "terminal" in q_low or "command" in q_low:
            return [
                "How to open the terminal in VS Code",
                "What to do if python command is not recognized",
                "How to install packages using pip"
            ]
        elif "study" in q_low or "exam" in q_low or "feynman" in q_low:
            return [
                "Feynman technique example",
                "25-minute Pomodoro study routine",
                "How to study without getting distracted"
            ]
        elif proj:
            return [
                f"How do I build Step 1 for {proj}?",
                f"Show starter code for {proj}",
                "Where can I get free sample data for this?"
            ]
        else:
            return [
                "Can you explain that with another analogy?",
                "Show me a simple code example",
                "What are the next beginner steps?"
            ]

    def _offline_knowledge_fallback(self, user_message: str, clean_text: str) -> Dict[str, Any]:
        """Provides graceful structured offline responses when internet or API is unavailable."""
        # Check offline knowledge base using multi-word matching or key phrases
        best_match = None
        highest_score = 0

        for item in self.knowledge_base:
            match_count = 0
            for kw in item["keywords"]:
                if kw in clean_text:
                    match_count += 2
            if match_count > highest_score:
                highest_score = match_count
                best_match = item

        if best_match and highest_score >= 2:
            return {
                "reply": best_match["response"],
                "suggestions": best_match["suggestions"]
            }

        # Friendly general fallback that directly acknowledges their question
        fallback_reply = (
            f"### 💡 Friendly Mentor Guidance\n\n"
            f"You asked: *\"{user_message}\"*\n\n"
            f"Here are 3 simple ways to approach this right now:\n"
            f"- **Break It Down**: Break this task into tiny, bite-sized 15-minute steps. Building small pieces first prevents getting overwhelmed!\n"
            f"- **Try a Tiny Test**: Before building the whole thing, write a 5-line test script to see the basics working.\n"
            f"- **Keep It Simple**: Start with the simplest version that works (a basic script), then polish it step by step.\n\n"
            f"Feel free to ask for starter code, study methods, or project tips anytime!"
        )

        return {
            "reply": fallback_reply,
            "suggestions": [
                "Explain study techniques",
                "AI & Machine Learning roadmap",
                "Web development roadmap",
                "How to check tool versions in terminal"
            ]
        }

    def generate_response(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user message and return structured response.
        PRIORITIZES dynamic Gemini LLM for all manual questions so students get
        accurate, personalized, layman-friendly explanations with real-world analogies.
        Falls back to offline knowledge base only when offline or API is unavailable.
        """
        clean_text = user_message.lower().strip()

        if not clean_text:
            return {
                "reply": "Hello! I am **EduMentor AI**. How can I help you in your studies, career goals, or project doubts today? I explain everything in simple, everyday words!",
                "suggestions": ["Study techniques", "AI/ML roadmap", "Explain my project roadmap", "How to install tools"]
            }

        # Check for simple greetings
        if re.match(r"^(hi|hello|hey|greetings|hola|sup|good\s+(morning|afternoon|evening))\b", clean_text) and len(clean_text.split()) <= 4:
            return {
                "reply": (
                    "👋 **Hello there!** I'm **EduMentor AI**, your Academic Advisor & Project Doubt Clarifier.\n\n"
                    "I explain everything in **simple, beginner-friendly words** without confusing jargon:\n"
                    "- 🚀 **Clear Project Doubts**: Ask any coding, architecture, or tool questions\n"
                    "- 📚 **Easy Study Habits**: Feynman Technique, Active Recall, 25-Min Pomodoro\n"
                    "- 🛠️ **Tool & Version Help**: Python, Git, Node, and terminal commands\n"
                    "- 💡 **Fun Resume Project Ideas**\n\n"
                    "What would you like to ask or explore today?"
                ),
                "suggestions": [
                    "How do I start building my project?",
                    "Top evidence-based study techniques",
                    "How to check tool versions in terminal",
                    "AI & Machine Learning roadmap"
                ]
            }

        # 1. PRIMARY ENGINE: Query Gemini LLM for all student questions & doubts
        llm_reply = self._ask_gemini_in_laymans_terms(user_message, context)
        if llm_reply:
            suggestions = self._generate_smart_suggestions(user_message, context)
            return {
                "reply": llm_reply,
                "suggestions": suggestions
            }

        # 2. OFFLINE FALLBACK: If offline or API fails, use structured offline knowledge
        return self._offline_knowledge_fallback(user_message, clean_text)


# Global chatbot singleton
chatbot_instance = StudentAdvisorChatbot()

def get_chat_response(message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    return chatbot_instance.generate_response(message, context)
