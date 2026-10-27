import csv
import os
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()

_CATALOG_CACHE = None

def get_project_catalog(csv_path="data/projects.csv"):
    """
    Load and cache projects from catalog for instant lookup.
    """
    global _CATALOG_CACHE
    if _CATALOG_CACHE is not None:
        return _CATALOG_CACHE

    if not os.path.exists(csv_path):
        return []

    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            _CATALOG_CACHE = list(reader)
            return _CATALOG_CACHE
    except Exception as e:
        print(f"Error loading project catalog: {e}")
        return []


def find_project_by_name(project_name, csv_path="data/projects.csv"):
    """
    Fuzzy match a project name against catalog titles.
    """
    projects = get_project_catalog(csv_path)
    if not project_name or not projects:
        return None

    clean_query = re.sub(r"[^a-z0-9]", "", project_name.lower())

    # Exact match first
    for p in projects:
        clean_title = re.sub(r"[^a-z0-9]", "", p.get("title", "").lower())
        if clean_query == clean_title:
            return p

    # Substring match
    for p in projects:
        clean_title = re.sub(r"[^a-z0-9]", "", p.get("title", "").lower())
        if clean_query in clean_title or clean_title in clean_query:
            return p

    # Partial word overlap match
    query_words = set(re.findall(r"\w+", project_name.lower()))
    best_match = None
    max_overlap = 0
    for p in projects:
        title_words = set(re.findall(r"\w+", p.get("title", "").lower()))
        overlap = len(query_words.intersection(title_words))
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = p

    return best_match if max_overlap > 0 else None


def get_student_tech_hub_roadmap(project_name):
    """
    Returns the exact 7-step interactive roadmap schema matching Student Tech Hub:
    https://vixhnu90.github.io/student-tech-hub/
    """
    proj = find_project_by_name(project_name)
    if proj:
        title = proj.get("title", project_name)
        desc = proj.get("description", proj.get("recommendation_reason", f"Build a practical {title} project."))
        dept_raw = proj.get("department", "AI / Machine Learning")
        if "AI" in dept_raw or "ML" in dept_raw:
            category = "AI / Machine Learning"
        elif "Web" in dept_raw or "BCA" in dept_raw:
            category = "Web Development"
        elif "Mobile" in dept_raw or "App" in dept_raw:
            category = "Mobile Development"
        elif "ECE" in dept_raw or "EEE" in dept_raw or "Embedded" in dept_raw:
            category = "IoT & Embedded Systems"
        elif "Civil" in dept_raw or "Mechanical" in dept_raw or "CAD" in dept_raw:
            category = "Engineering Design"
        elif "Bio" in dept_raw:
            category = "Biotechnology"
        else:
            category = dept_raw.split(",")[0].strip()

        raw_skills = proj.get("skills", proj.get("technologies", "Python, Machine Learning, Computer Vision"))
        skills = [s.strip() for s in re.split(r"[,;]+", raw_skills) if s.strip()][:3]
        if not skills:
            skills = ["Python", "Machine Learning", "Computer Vision"]
        difficulty = proj.get("difficulty", "Intermediate")
    else:
        title = project_name
        desc = f"Build an innovative project: {project_name}."
        category = "AI / Machine Learning"
        skills = ["Python", "Machine Learning", "Computer Vision"]
        difficulty = "Intermediate"

    tech1 = skills[0] if len(skills) > 0 else "Python"
    tech2 = skills[1] if len(skills) > 1 else category
    tech3 = skills[2] if len(skills) > 2 else "Framework"

    is_waste_classifier = "waste" in title.lower() and "classifier" in title.lower()

    # 7-Step architecture focused 100% on the project building process in simple layman's terms
    if is_waste_classifier:
        steps = [
            {
                "number": "01",
                "title": "Project Workspace & Planning",
                "description": "Create your project folder and choose your 3 waste categories.",
                "brief": {
                    "overview": f"Before writing any code, set up a clean folder on your computer for {title}. Decide on the 3 waste categories you want your project to recognize: Recyclables (plastic bottles, soda cans, paper), Organics (food scraps, fruit peels), and General Trash. Think of this like setting up a clean kitchen counter before cooking.",
                    "milestones": [
                        "Create a main folder called 'campus_waste_classifier' on your computer",
                        "Create simple subfolders: 'photos', 'code', and 'models'",
                        "Decide on your 3 categories: Recyclable, Organic, and General Trash",
                        "💡 Need help installing tools or checking versions (Python, Git, npm) in your code editor? Ask our AI Chatbot anytime!"
                    ],
                    "tools": ["Project Folder", "Code Editor", "AI Mentor Chatbot"],
                    "starter_guide": """# Step 1: Project Plan & Goal
print("Welcome to Smart Campus Waste Classifier!")
print("Goal: Look at any photo and tell which bin it goes in.")
print("Categories: 1. Recyclables | 2. Organics | 3. General Trash")""",
                    "proof_expected": "Project folder created with subfolders ready to hold your photos and code.",
                    "tips": "Keeping your photos and code in separate folders makes everything much easier to build!"
                }
            },
            {
                "number": "02",
                "title": "Gathering Sample Photos (The Ingredients)",
                "description": "Collect sample pictures of waste items to teach the computer.",
                "brief": {
                    "overview": "Computers learn from examples just like people do. To teach the computer how to recognize waste, collect 30 to 50 sample photos for each category (clear photos of water bottles, fruit peels, snack wrappers, etc.).",
                    "milestones": [
                        "Collect 30+ photos of recyclable items (plastic bottles, cans, clean paper)",
                        "Collect 30+ photos of organic waste (apple cores, banana peels, food scraps)",
                        "Collect 30+ photos of general trash (candy wrappers, styrofoam, tissues)",
                        "Place the photos into their matching category subfolders"
                    ],
                    "tools": ["Phone Camera or Free Web Photos", "Photo Folders"],
                    "starter_guide": """# Step 2: Check your photos
import os

categories = ['recyclable', 'organic', 'general_trash']
print("Categories ready:", categories)
print("Place your sample photos inside photos/<category>/ folders.")""",
                    "proof_expected": "Photos organized into category folders ready for teaching the computer.",
                    "tips": "Taking photos in good lighting with clear backgrounds helps the computer learn much faster!"
                }
            },
            {
                "number": "03",
                "title": f"Teaching the Computer (Building the Model)",
                "description": "Train the computer vision model to spot the patterns in your photos.",
                "brief": {
                    "overview": "Now you feed your photos into a friendly computer vision helper (YOLO). The computer studies the colors and shapes of each item, learns the differences, and saves its new 'brain' so it can recognize waste on its own.",
                    "milestones": [
                        "Feed your sample photos into the learning program",
                        "Let the computer study the pictures and practice recognizing the items",
                        "Save the trained model brain file so you can use it anytime",
                        "Check the score to make sure it guesses correctly on most photos"
                    ],
                    "tools": ["Vision Helper (YOLO)", "Python Code"],
                    "starter_guide": """# Step 3: Teaching the computer
from ultralytics import YOLO

# Load a friendly starter vision model
model = YOLO('yolov8n-cls.pt')

# Teach it using your sample photos
# model.train(data='./photos', epochs=10)
print("Training complete! The computer has learned your waste categories.")""",
                    "proof_expected": "A saved model file that successfully learned the 3 waste categories.",
                    "tips": "If the computer mixes up two items, just show it a few more clear photos of each."
                }
            },
            {
                "number": "04",
                "title": "Testing with Real Waste Items",
                "description": "Test your trained model on brand-new photos to see if it guesses correctly.",
                "brief": {
                    "overview": "Time to see how smart your computer model is! Show it 5 new mystery photos it has never seen before, and watch it tell you which bin each item belongs in and how confident it feels.",
                    "milestones": [
                        "Take 5 new mystery test photos from around your room or campus",
                        "Run the model on each photo to see its guess",
                        "Check the confidence percentage (how sure the computer is)",
                        "Verify that bottles go to recyclable, food to organic, and wrappers to trash"
                    ],
                    "tools": ["Mystery Test Photos", "Testing Script"],
                    "starter_guide": """# Step 4: Testing on a new photo
from ultralytics import YOLO

model = YOLO('models/best_waste_classifier.pt')
# Test on a new mystery photo
results = model('photos/test_bottle.jpg')

for r in results:
    best_guess = r.names[r.probs.top1]
    sureness = float(r.probs.top1conf) * 100
    print(f"Guess: {best_guess.upper()} ({sureness:.1f}% sure)")""",
                    "proof_expected": "Output showing the computer correctly identifying your test photos.",
                    "tips": "Aim for 80% or higher confidence on clear photos before moving to the next step."
                }
            },
            {
                "number": "05",
                "title": "Connecting the Engine (The Helper Bridge)",
                "description": "Create a simple bridge that takes in a photo and returns the right colored bin.",
                "brief": {
                    "overview": "Think of this step like hiring a friendly restaurant waiter (an API). Whenever someone sends a photo, this bridge takes it to your model brain, asks for the guess, and brings back clear instructions: 'Throw this in the Blue Bin!'",
                    "milestones": [
                        "Build the simple photo receiver (API)",
                        "Connect the receiver directly to your trained model",
                        "Attach easy bin color rules: Blue (Recycle), Green (Compost), Gray (Trash)",
                        "Test sending a photo and receiving the bin recommendation"
                    ],
                    "tools": ["FastAPI Bridge", "Bin Color Rules"],
                    "starter_guide": """# Step 5: The Helper Bridge
from fastapi import FastAPI, UploadFile, File

app = FastAPI(title="Waste Bin Assistant")

@app.post("/sort-waste")
async def sort_waste(file: UploadFile = File(...)):
    # Receives a photo and tells the user where to throw it
    return {
        "result": "Plastic Bottle",
        "bin": "Blue Bin (Recyclables)",
        "advice": "Please empty liquids before throwing!"
    }""",
                    "proof_expected": "A working bridge that receives a photo and responds with the right bin advice.",
                    "tips": "Clear bin colors make it foolproof for anyone on campus to throw trash in the right place."
                }
            },
            {
                "number": "06",
                "title": "Building the Friendly Screen",
                "description": "Make a colorful, easy-to-use webpage with a photo upload button.",
                "brief": {
                    "overview": "Now build the visual screen that everyday students and teachers will see on their phones or laptops. Add an upload button, a photo preview, and big friendly badges showing the right bin.",
                    "milestones": [
                        "Create an easy web page with an upload button",
                        "Display the uploaded photo on the screen",
                        "Show a bright, colorful badge showing which bin to use (Blue, Green, or Gray)",
                        "Add a helpful recycling tip below the result"
                    ],
                    "tools": ["Streamlit Web Page", "Visual Badges"],
                    "starter_guide": """# Step 6: Simple Web Screen
import streamlit as st

st.title("♻️ Campus Waste Sorting Helper")
photo = st.file_uploader("Upload a photo of your waste item:")

if photo:
    st.image(photo, caption="Your Item", width=250)
    st.success("✅ Throw in the BLUE BIN (Recyclable)")
    st.info("💡 Tip: Empty and rinse any liquid before discarding.")""",
                    "proof_expected": "Screenshot of your working web screen with photo upload and bin badge.",
                    "tips": "Keep the buttons large and simple so anyone on campus can use it quickly on mobile."
                }
            },
            {
                "number": "07",
                "title": "Live Showcase & Demo",
                "description": "Run the completed project, test it with friends, and show it off.",
                "brief": {
                    "overview": f"You did it! Your smart waste classifier is completely built. In this final step, you test it out live with 5 real items, show it to friends or classmates, and prepare a 1-minute walk-through to showcase what you built.",
                    "milestones": [
                        "Start the finished app and test it with 5 different everyday items",
                        "Invite a friend or classmate to try it and give feedback",
                        "Take 2-3 screenshots showing successful waste classifications",
                        "Write a 2-sentence summary explaining how your app helps keep campus clean"
                    ],
                    "tools": ["Completed App", "Demo Screenshots", "Project Showcase"],
                    "starter_guide": """# Step 7: Final Project Showcase
print("🎉 Congratulations! Your Waste Classifier is fully built.")
print("Test your app live, take screenshots, and show off your work!")""",
                    "proof_expected": "Screenshots showing your completed app correctly sorting real trash items.",
                    "tips": "When showcasing your project, explain the practical value: helping everyone recycle correctly with zero confusion!"
                }
            }
        ]
    else:
        # Generic tailored 7-step architecture for catalog projects (100% project-building, no Git)
        steps = [
            {
                "number": "01",
                "title": "Project Workspace & Blueprint",
                "description": f"Create your project folder and map out the goal for {title}.",
                "brief": {
                    "overview": f"Before writing code, create a dedicated project folder on your computer for {title}. Write down the main goal: what input will your project receive, and what helpful result will it give the user? Think of this like planning the blueprint before building with LEGO blocks.",
                    "milestones": [
                        f"Create a main folder named '{title.lower().replace(' ', '_')}' on your computer",
                        "Create organized subfolders: 'data', 'code', and 'results'",
                        "Write down a 1-sentence goal for what your project solves",
                        "💡 Need help installing tools or checking versions (Python, Git, npm) in your code editor? Ask our AI Chatbot anytime!"
                    ],
                    "tools": ["Project Folder", "Code Editor", "AI Mentor Chatbot"],
                    "starter_guide": f"""# Step 01: Blueprint for {title}
print("Starting {title}!")
print("Goal: Solve everyday student and campus challenges.")""",
                    "proof_expected": "Clean project folder created with organized subfolders ready to build.",
                    "tips": "Starting with a clear 1-sentence goal prevents getting confused later."
                }
            },
            {
                "number": "02",
                "title": f"Gathering Ingredients (Data & Content)",
                "description": f"Collect the sample data, text, or examples needed for {title}.",
                "brief": {
                    "overview": f"Gather the sample information, tables, or text needed to power {title}. Think of this step like collecting all your ingredients before baking.",
                    "milestones": [
                        "Find 20 to 50 sample examples or data records to test with",
                        "Save the examples in a clean table or text file inside your 'data' folder",
                        "Check that there are no empty or corrupted items",
                        "Review 3 examples to make sure they match your project goal"
                    ],
                    "tools": ["Sample Data / Table", "Data Folder"],
                    "starter_guide": f"""# Step 02: Resource Loader for {title}
print("Loading sample ingredients for {title}...")
print("Found clean sample records ready to use.")""",
                    "proof_expected": "Sample dataset or table ready in your project data folder.",
                    "tips": "A small, clean set of examples is much easier for beginners than a huge messy dataset."
                }
            },
            {
                "number": "03",
                "title": f"Building the Core Logic",
                "description": f"Write the main function that processes the input for {title}.",
                "brief": {
                    "overview": f"Write the main recipe for {title}. This is the central function that takes the user's input, runs your logic, and figures out the result.",
                    "milestones": [
                        f"Write the primary function that processes incoming inputs",
                        "Add simple rules or model checks to produce the output",
                        "Print friendly status messages so you can watch your code work",
                        "Ensure the function handles simple inputs without crashing"
                    ],
                    "tools": [f"{tech1}", "Code Editor"],
                    "starter_guide": f"""# Step 03: Core Logic for {title}
def run_core_logic(user_input):
    print("Processing:", user_input)
    # Core logic produces friendly result
    return f"Success! Result computed for: {{user_input}}"

result = run_core_logic("Sample Test Input")
print(result)""",
                    "proof_expected": "Working function executing a test input and printing the expected result.",
                    "tips": "Test one small line at a time so you can catch mistakes immediately."
                }
            },
            {
                "number": "04",
                "title": "Testing & Trying It Out",
                "description": f"Test {title} with 3 to 4 real-world examples to verify it works.",
                "brief": {
                    "overview": "Take your project for a test drive! Try out 3 or 4 different sample inputs to see if the computer gives the right answer every time.",
                    "milestones": [
                        "Create 3 different test inputs (one easy, one medium, one tricky)",
                        "Run each test input through your core function",
                        "Verify that all test outputs are correct and make sense",
                        "Fix any minor errors that pop up during testing"
                    ],
                    "tools": ["Test Cases", "Python Console"],
                    "starter_guide": f"""# Step 04: Testing {title}
test_samples = ["Sample 1", "Sample 2", "Sample 3"]
for sample in test_samples:
    print(f"Testing {{sample}}... PASSED ✓")""",
                    "proof_expected": "Output showing successful test runs across all your sample inputs.",
                    "tips": "Always test what happens if an empty or weird input is given."
                }
            },
            {
                "number": "05",
                "title": "Connecting the Engine (The Helper Bridge)",
                "description": "Create a simple bridge that lets other apps send requests and get answers.",
                "brief": {
                    "overview": "Think of this step like hiring a friendly waiter (an API). Whenever a user or screen asks a question, this bridge passes it to your core logic and returns the answer.",
                    "milestones": [
                        "Create a simple receiver function for incoming requests",
                        "Connect the receiver directly to your core logic function",
                        "Format the output in a clean, friendly text format",
                        "Test sending a question and receiving the instant reply"
                    ],
                    "tools": ["FastAPI Bridge", "Data Formatter"],
                    "starter_guide": f"""# Step 05: The Helper Bridge
print("Setting up helper bridge for {title}...")
print("Ready to receive requests and return instant results!")""",
                    "proof_expected": "Working bridge that receives requests and returns clean answers.",
                    "tips": "Keep the output format simple so any screen or website can display it easily."
                }
            },
            {
                "number": "06",
                "title": "Building the Friendly Screen",
                "description": f"Build a clean visual screen with buttons and inputs for {title}.",
                "brief": {
                    "overview": f"Make the visual webpage that everyday people will use! Add a simple title, an input box for the user, a friendly action button, and a clean result card.",
                    "milestones": [
                        "Create a clean web page with an input box",
                        "Add a prominent 'Run / Submit' button",
                        "Show the calculated result in a clear, colorful card",
                        "Add friendly instructions explaining what to type"
                    ],
                    "tools": ["Streamlit Screen", "Clean Visual Cards"],
                    "starter_guide": f"""# Step 06: Visual Screen for {title}
import streamlit as st

st.title("✨ {title}")
user_input = st.text_input("Enter your input:")
if st.button("Generate Result"):
    st.success(f"Result ready for: {{user_input}}")""",
                    "proof_expected": "Screenshot of your visual webpage showing an input box, button, and result.",
                    "tips": "Keep the page clean with plenty of white space so beginners feel comfortable."
                }
            },
            {
                "number": "07",
                "title": "Live Showcase & Demo",
                "description": "Run the completed project, try it out, and show it off to friends.",
                "brief": {
                    "overview": f"Congratulations! {title} is fully built. In this final milestone, run your finished application, test it with friends or classmates, and prepare a 1-minute walk-through demo.",
                    "milestones": [
                        "Start your completed application and test it from start to finish",
                        "Show it to a friend or classmate and watch them use it",
                        "Take 2-3 screenshots of the working app in action",
                        "Write a short 2-sentence summary explaining how your app helps people"
                    ],
                    "tools": ["Completed App", "Demo Screenshots", "Project Showcase"],
                    "starter_guide": f"""# Step 07: Project Showcase for {title}
print("🎉 Congratulations! {title} is completely built.")
print("Take screenshots of your working app and showcase your work!")""",
                    "proof_expected": "Screenshots showing your completed app running with real inputs.",
                    "tips": "Focus on the problem your project solves when explaining it to others!"
                }
            }
        ]

    return {
        "title": title,
        "description": desc,
        "category": category,
        "difficulty": difficulty,
        "skills": skills,
        "steps": steps,
        "why_matters": f"Every verified step brings {title} closer to your portfolio."
    }


def generate_roadmap(project_name, student=None, history=None):
    """
    Specialized Roadmap Architect Agent:
    Retrieves project specifications from catalog and synthesizes an actionable,
    step-by-step roadmap tailored to the student's background and available hours.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "project": project_name,
            "roadmap": "Gemini API key is not configured.",
            "project_details": None
        }

    proj = find_project_by_name(project_name)

    if proj:
        matched_title = proj.get("title", project_name)
        dept = proj.get("department", "Engineering")
        tech = proj.get("technologies", "Standard Tools")
        prereqs = proj.get("prerequisites", "Basic Programming")
        hours = proj.get("estimated_hours", 8)
        reason = proj.get("recommendation_reason", proj.get("description", ""))
        difficulty = proj.get("difficulty", "Intermediate")
    else:
        matched_title = project_name
        dept = student.get("department", "General") if student else "General"
        tech = "Standard Industry Tools"
        prereqs = "Basic foundations"
        hours = student.get("available_hours", 6) if student else 6
        reason = "Hands-on implementation experience"
        difficulty = "Intermediate"

    student_skills = student.get("skills", []) if student else []
    student_year = student.get("year", "Undergraduate") if student else "Undergraduate"

    # Context history for multi-turn roadmap chat
    history_lines = []
    if history:
        for turn in history[-6:]:
            role = turn.get("role", "user")
            speaker = "Student" if role == "user" else "Roadmap Architect"
            content = turn.get("content", "").strip()
            if content:
                history_lines.append(f"{speaker}: {content}")
    history_text = "\n".join(history_lines) if history_lines else "None (Starting new roadmap)"

    prompt = f"""
You are the **Project Roadmap Mentor** inside an Academic AI Ecosystem.
Your goal is to provide a clean, simple, practical **Step-by-Step Roadmap** written in **PURE LAYMAN'S LANGUAGE** for a complete beginner who has ZERO knowledge of technology.

### TARGET PROJECT:
- Project Title: {matched_title}
- Department: {dept}
- Technologies & Stack: {tech}
- Suggested Prerequisites: {prereqs}
- Difficulty: {difficulty}

### STRICT CRITICAL RULES:
1. **FOCUS ONLY ON BUILDING THE PROJECT (NO GIT PROCESS)**:
   - Do NOT include any Git processes, git init, git clone, git commits, or GitHub repository steps in the roadmap phases.
   - Do NOT include complex npm/git/IDE version installation commands in the roadmap.
   - Instead, explicitly tell the student: "💡 *Need help installing tools, checking versions (Git, Python, npm), or running terminal commands in your code editor? Just ask our AI Chatbot on the bottom-left!*"
2. **EXPLAIN IN LAYMAN'S LANGUAGE (ASSUME ZERO TECH BACKGROUND)**:
   - The person reading this knows NOTHING about programming, coding jargon, or developer tools.
   - Use simple everyday words. Explain concepts using real-life analogies (e.g. comparing software to a cooking recipe, building with LEGO blocks, or ordering food at a restaurant).
   - If any tool name is mentioned, explain what it does in 1 plain everyday sentence right away.
3. **NO TIME TAKEN / NO DURATIONS**:
   - Do NOT mention or display any time taken, hours, days, weeks, durations, or completion times anywhere in the roadmap.
4. **NO EXECUTIVE SUMMARY**:
   - Skip introductory essays, abstracts, and executive summaries. Jump directly into the simple actionable guidance.

### ROADMAP STRUCTURE:
1. 💡 **Quick Beginner Note**:
   - Remind the student: "This roadmap focuses 100% on building your project! If you need terminal commands to install tools or check versions (Git, Python, npm), ask our AI Chatbot anytime."
2. 🛠️ **What You Need (In Plain Words)**:
   - 2-3 simple tools explained in plain English (e.g. "A code editor is like a clean notepad where you write instructions for your computer").
3. 📌 **Simple Step-by-Step Project Creation**:
   - **Phase 1: Project Plan & Folder**: Creating your project workspace and writing down what the project will do.
   - **Phase 2: Gathering Ingredients (Data/Examples)**: Collecting sample examples or data records.
   - **Phase 3: Teaching the Computer / Building the Core Logic**: Writing the main function that creates the result.
   - **Phase 4: Testing & Trying It Out**: Running 3-4 real examples to verify it gives the right answer.
   - **Phase 5: Building the Friendly Screen**: Making a clean visual page with buttons so anyone can use it.
   - **Phase 6: Live Showcase & Demo**: Running the finished project and showing it off!
4. 💻 **Simple Starter Code**:
   - A friendly, working boilerplate code snippet with simple plain-English comments above each line.
5. ✅ **Action Checklist**:
   - A short checklist (`- [ ]`) of clear tasks to complete.

Tone: Warm, welcoming, encouraging, and crystal clear.
"""

    try:
        client = genai.Client(api_key=api_key)
        response = None
        for model_name in ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.8-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"http_options": {"timeout": 25000}}
                )
                if response and response.text:
                    break
            except Exception as e:
                continue

        roadmap_text = response.text if (response and response.text) else "Unable to generate roadmap at this time. Please retry."

        return {
            "project": matched_title,
            "roadmap": roadmap_text,
            "project_details": {
                "department": dept,
                "technologies": tech,
                "prerequisites": prereqs,
                "difficulty": difficulty,
                "reason": reason
            }
        }
    except Exception as err:
        return {
            "project": matched_title,
            "roadmap": f"Error synthesizing roadmap: {err}",
            "project_details": None
        }


def answer_project_doubt(question, project_name, student=None, history=None, current_step=None):
    """
    Chatbot 2 Doubt-Clearing Mentor:
    Answers specific technical, architectural, or code-level questions about
    the active project while remembering all project specifications and previous dialog.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    proj = find_project_by_name(project_name)
    matched_title = proj.get("title", project_name) if proj else project_name
    dept = proj.get("department", "Engineering") if proj else "Engineering"
    tech = proj.get("technologies", "") if proj else ""
    prereqs = proj.get("prerequisites", "") if proj else ""
    reason = proj.get("recommendation_reason", proj.get("description", "")) if proj else ""

    step_context = ""
    if current_step:
        step_num = current_step.get("number", "")
        step_title = current_step.get("title", "")
        step_desc = current_step.get("description", "")
        step_context = f"\n### CURRENT ROADMAP STEP IN FOCUS:\n- Step {step_num}: {step_title}\n- Step Goal: {step_desc}\n"

    history_lines = []
    if history:
        for turn in history[-8:]:
            role = turn.get("role", "user")
            speaker = "Student" if role == "user" else "Roadmap Mentor"
            content = turn.get("content", "").strip()
            if content:
                history_lines.append(f"{speaker}: {content}")
    history_text = "\n".join(history_lines) if history_lines else "None"

    prompt = f"""
You are **Chatbot 2: The Dedicated Project Roadmap Architect & Mentor**.
Your sole mission is to guide the student through building their project: **{matched_title}** and clear any doubts they have along the way.

Your responses MUST be written in **SIMPLE, LAYMAN'S LANGUAGE** that complete beginners can easily understand.

### PROJECT SPECIFICATIONS:
- Project Title: {matched_title}
- Department: {dept}
- Technologies & Tools: {tech}
- Prerequisites: {prereqs}
- Purpose & Focus: {reason}
{step_context}
### STUDENT PROFILE:
- Current Year: {student.get('year', 'College') if student else 'College'}
- Department: {student.get('department', dept) if student else dept}
- Verified Known Skills: {', '.join(student.get('skills', [])) if student and student.get('skills') else 'Beginner'}
- Mentorship Style: {student.get('mentor_mode', 'Encouraging & Practical') if student else 'Encouraging & Practical'}

### PREVIOUS PROJECT ROADMAP DIALOG:
{history_text}

### STUDENT'S SPECIFIC QUESTION / DOUBT ABOUT THIS PROJECT:
"{question}"

### CRITICAL RULES (LAYMAN'S TERMS & BEGINNER-FRIENDLY):
1. **Explain in Layman's Terms**: Directly answer the student's doubt about **{matched_title}** in simple, everyday words. Avoid textbook jargon and complex buzzwords.
2. **Use Real-World Analogies**: Always explain technical ideas using simple real-world comparisons (e.g., comparing an API to a restaurant waiter, a machine learning model to a smart guessing game, or a database to an organized filing cabinet).
3. **No Unexplained Terms**: If you mention any tool or technical library, explain what it is in 1 plain English sentence right next to it.
4. **Plain-English Code**: If they ask for code, give clean, minimal, working code with simple line-by-line comments in everyday English explaining what each part does.
5. **Chat-Friendly & Bite-Sized**: Use short bullet points and clean formatting. Avoid long walls of text.
6. **No Time Estimates**: Do NOT display or mention time taken, hours, or durations.
7. **Free Resources in Plain Words**: If they ask about datasets or resources, describe where to get free beginner-friendly samples in simple terms.
"""
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            for model_name in ["gemini-flash-lite-latest", "gemini-2.5-flash-lite", "gemini-3.5-flash-lite", "gemini-3.8-flash"]:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config={"http_options": {"timeout": 25000}}
                    )
                    if response and response.text:
                        return response.text
                except Exception:
                    continue
        except Exception as err:
            print(f"Gemini API call failed: {err}")

    # Fallback response generator if Gemini is offline or fails
    q_low = question.lower()
    if "starter code" in q_low or "code" in q_low:
        return f"""Here is the recommended starter code for **{matched_title}**:

```python
# {matched_title} - Starter Implementation
import os
import sys

def initialize_project():
    print("🚀 Initializing {matched_title}...")
    # Verify core environment
    print(f"Python Runtime: {{sys.version.split()[0]}}")
    print("Status: Core dependencies loaded successfully.")
    return True

if __name__ == '__main__':
    initialize_project()
```

**Next Steps:**
- Run this in your terminal: `python main.py`
- Verify dependencies in your virtual environment
- Ask me if you need help with training or API routing!"""
    elif "dataset" in q_low or "data" in q_low:
        return f"""Here are the top free resources & datasets for **{matched_title}**:

- **Kaggle Datasets**: Search for open datasets matching `{matched_title}`.
- **Roboflow Universe**: Public annotated computer vision datasets ready to export in YOLO/COCO format.
- **Hugging Face Hub**: Free community datasets and pretrained model weights.
- **UCI Machine Learning Repository**: Benchmark academic datasets for ML classification.

*Tip: For testing, start with 150-200 sample items to validate your pipeline before scaling up!*"""
    elif "version" in q_low or "npm" in q_low or "git" in q_low or "terminal" in q_low or "command" in q_low:
        return f"""### 🛠️ Quick Tool Version Checks in Your Code Editor (VS Code)

To check what tools you have installed, open your terminal (press `Ctrl + ~` in VS Code) and run these simple commands:

- **Check Python Version**: `python --version` (or `python3 --version`)
- **Check Git Version**: `git --version`
- **Check Node.js Version**: `node --version`
- **Check npm Version**: `npm --version`

**Helpful Commands:**
- Install Python libraries: `pip install <package_name>`
- Install Node packages: `npm install <package_name>`
- Run a Python file: `python filename.py`

*Note: You do NOT need any Git or complex version control knowledge to build this project! Our roadmap walks you purely through building the project step by step in plain everyday words.*"""
    elif "explain" in q_low or "simple" in q_low or "analogy" in q_low:
        return f"""**{matched_title} Explained Simply:**

Think of this project like building a smart automated assistant for campus operations. Instead of manually inspecting every item or record, our system takes the incoming input (like an image or data feed), extracts key patterns using machine learning, and instantly recommends the right action or disposal bin!

**Key milestones:**
1. Collect example samples
2. Train the model to recognize patterns
3. Connect it to an API so any student or camera can use it!"""
    else:
        return f"""Great question about **{matched_title}**!

To succeed in this project:
- Make sure your dependencies ({tech or 'Python, ML tools'}) are cleanly installed in an isolated virtual environment.
- Follow the 7-step roadmap from environment setup through dataset preparation, model training, and API integration.
- Break each step into the action checklist and test each part with sample data before moving on.

Feel free to ask for specific code snippets, bug fixes, or architecture advice!"""

