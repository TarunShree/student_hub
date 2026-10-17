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

    # Exact 7-step architecture from student-tech-hub with rich briefs
    if is_waste_classifier:
        steps = [
            {
                "number": "01",
                "title": "Project Environment & Setup",
                "description": "Set up your development environment, repository, project structure, and required dependencies.",
                "brief": {
                    "overview": f"Establish a dedicated, reproducible development workspace for {title}. Set up Git version control, virtual environment, clean directory hierarchy (data/, models/, src/, tests/), and install core libraries including PyTorch, Ultralytics YOLOv8, and OpenCV.",
                    "milestones": [
                        "Initialize Git repository with .gitignore for Python and ML weights",
                        "Create virtual environment with Python 3.10+ (python -m venv venv)",
                        "Install ultralytics, torch, torchvision, opencv-python, pandas, and fastapi",
                        "Verify GPU/CUDA hardware acceleration or CPU fallback"
                    ],
                    "tools": ["Python 3.10+", "Git", "PyTorch", "Ultralytics YOLOv8", "OpenCV"],
                    "starter_guide": """# Verify environment and library installation
import sys
import torch
import cv2
import ultralytics

print(f"Python: {sys.version.split()[0]}")
print(f"PyTorch Version: {torch.__version__} (CUDA Available: {torch.cuda.is_available()})")
print(f"OpenCV Version: {cv2.__version__}")
print(f"YOLOv8 Version: {ultralytics.__version__}")
print("✓ Environment setup verified successfully!")""",
                    "proof_expected": "Clean terminal log confirming successful package imports and hardware acceleration status.",
                    "tips": "Always keep large weight files (*.pt, *.onnx) and raw image datasets in .gitignore to keep your Git repo lean."
                }
            },
            {
                "number": "02",
                "title": "AI / Machine Learning Resource Preparation",
                "description": f"Gather the datasets, content, or resources needed for {title}.",
                "brief": {
                    "overview": "Collect, clean, and annotate a campus waste image dataset categorized into 3 core classes: Recyclable (plastic bottles, aluminum cans, paper), Organic (food waste, fruit peels), and General/Non-recyclable (candy wrappers, styrofoam).",
                    "milestones": [
                        "Collect or download 200+ images per class from public sources (TrashNet, TACO) or campus photos",
                        "Annotate or organize images into structured train/val/test directories (70/20/10 split)",
                        "Configure dataset.yaml defining classes, paths, and metadata",
                        "Apply data augmentations (flips, random crops, brightness adjustments)"
                    ],
                    "tools": ["Roboflow", "TrashNet Dataset", "Albumentations", "dataset.yaml"],
                    "starter_guide": """# dataset.yaml - Dataset configuration for YOLOv8
path: ./data/campus_waste
train: images/train
val: images/val
test: images/test

# Classes:
names:
  0: recyclable
  1: organic
  2: general_waste""",
                    "proof_expected": "dataset.yaml file and sample batch preview displaying correctly labeled images in each class.",
                    "tips": "Balance your classes evenly to avoid bias where the model always predicts recyclable over organic."
                }
            },
            {
                "number": "03",
                "title": f"Build {title}",
                "description": f"Develop the core features of {title} using {tech1}.",
                "brief": {
                    "overview": "Train a lightweight deep neural network (YOLOv8n-cls or MobileNetV3) using transfer learning on the waste dataset. Optimize loss curves, monitor validation accuracy, and export checkpoint weights.",
                    "milestones": [
                        "Load pretrained backbone weights (yolov8n-cls.pt)",
                        "Train model for 25 epochs with Cosine Annealing learning rate schedule",
                        "Track training loss, validation top-1 accuracy, and F1-score",
                        "Save the best performing model weights to models/best_waste_classifier.pt"
                    ],
                    "tools": ["Ultralytics YOLOv8", "PyTorch", "TensorBoard"],
                    "starter_guide": """from ultralytics import YOLO

# Load lightweight pretrained model
model = YOLO('yolov8n-cls.pt')

# Train on campus waste dataset
results = model.train(
    data='./data/campus_waste',
    epochs=25,
    imgsz=224,
    batch=16,
    project='runs/waste_classifier',
    name='v1'
)
print("Model training finished! Check best.pt in runs/waste_classifier/v1/weights/")""",
                    "proof_expected": "Training log summary showing >85% validation accuracy and saved weights file.",
                    "tips": "Use batch size 16 or 32 for smooth gradient descent; if training on CPU, resize images to 224x224."
                }
            },
            {
                "number": "04",
                "title": f"{tech2} Integration & Testing",
                "description": f"Integrate {tech2}, test the project, and validate its expected results.",
                "brief": {
                    "overview": "Evaluate model inference on unseen campus test images and live camera feeds. Calculate confusion matrix, test inference latency (target < 100ms per image), and handle edge cases like crumpled packaging or mixed waste.",
                    "milestones": [
                        "Run batch evaluation on test split and generate Confusion Matrix",
                        "Calculate per-class Precision, Recall, and F1-score",
                        "Benchmark inference latency on CPU and GPU",
                        "Test real-time webcam feed with confidence score thresholds"
                    ],
                    "tools": ["Scikit-learn", "Matplotlib", "Seaborn", "OpenCV"],
                    "starter_guide": """import cv2
from ultralytics import YOLO

model = YOLO('models/best_waste_classifier.pt')

# Test single campus waste image
img_path = 'data/test_sample_bottle.jpg'
results = model(img_path)

for r in results:
    top_class = r.names[r.probs.top1]
    confidence = float(r.probs.top1conf)
    print(f"Predicted: {top_class.upper()} | Confidence: {confidence*100:.2f}%")""",
                    "proof_expected": "Confusion matrix heatmap image and test evaluation report showing robust precision across all 3 classes.",
                    "tips": "Set a confidence threshold (e.g. 60%). If confidence is low, instruct the user to reposition the item."
                }
            },
            {
                "number": "05",
                "title": "Backend / API Integration",
                "description": "Connect your frontend with APIs, services, databases, or backend functionality.",
                "brief": {
                    "overview": "Expose the waste classifier via a fast REST API using FastAPI. Create an endpoint that receives an image file, runs inference, and returns the classification, confidence score, and actionable bin guidance (Blue/Green/Black).",
                    "milestones": [
                        "Create FastAPI application with CORS support for web and mobile frontends",
                        "Implement POST /classify endpoint accepting multipart/form-data images",
                        "Map predicted classes to campus bin colors and disposal guidelines",
                        "Add request logging, error handling, and Swagger documentation"
                    ],
                    "tools": ["FastAPI", "Uvicorn", "Pydantic", "Pillow"],
                    "starter_guide": """from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
from PIL import Image
import io

app = FastAPI(title="Campus Waste Classifier API")
model = YOLO('models/best_waste_classifier.pt')

BIN_GUIDE = {
    'recyclable': {'bin': 'Blue Bin (Recyclables)', 'instruction': 'Empty liquids and place in blue bin.'},
    'organic': {'bin': 'Green Bin (Compost)', 'instruction': 'Compostable food waste. Place in green bin.'},
    'general_waste': {'bin': 'Gray/Black Bin (Landfill)', 'instruction': 'Non-recyclable. Place in general bin.'}
}

@app.post("/classify")
async def classify_waste(file: UploadFile = File(...)):
    img = Image.open(io.BytesIO(await file.read())).convert("RGB")
    res = model(img)[0]
    category = res.names[res.probs.top1]
    confidence = float(res.probs.top1conf)
    return {
        "status": "success",
        "category": category,
        "confidence": round(confidence * 100, 2),
        "guidance": BIN_GUIDE.get(category, {})
    }""",
                    "proof_expected": "Successful test request via Swagger UI (/docs) returning JSON classification output.",
                    "tips": "Always wrap image parsing in try/except blocks to gracefully handle unsupported file formats."
                }
            },
            {
                "number": "06",
                "title": "User Interface & Integration",
                "description": "Connect all components and polish the user experience across desktop and mobile devices.",
                "brief": {
                    "overview": "Build a responsive web application matching Student Tech Hub styling. Enable drag-and-drop photo upload or real-time webcam capture, show live classification predictions, confidence meters, and visual colored bin recommendations.",
                    "milestones": [
                        "Create intuitive user interface with clean typography and modern card layouts",
                        "Integrate file uploader and camera snapshot components",
                        "Display prominent visual disposal badges (Blue/Green/Black)",
                        "Connect frontend directly to backend /classify API endpoint"
                    ],
                    "tools": ["Streamlit / React", "CSS3", "JavaScript", "REST Client"],
                    "starter_guide": """import streamlit as st
import requests

st.title("♻️ Smart Campus Waste Classifier")
uploaded_file = st.file_uploader("Upload an item to classify:", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Item to classify", width=280)
    if st.button("Classify Item Now"):
        files = {"file": uploaded_file.getvalue()}
        res = requests.post("http://localhost:8000/classify", files=files).json()
        cat = res["category"].upper()
        conf = res["confidence"]
        bin_info = res["guidance"]["bin"]
        st.success(f"Classified as: **{cat}** ({conf}% confidence)")
        st.info(f"👉 Recommended Bin: **{bin_info}**")""",
                    "proof_expected": "Screenshot of the frontend displaying a waste item correctly classified with disposal bin badge.",
                    "tips": "Add clear visual icons (bottle, apple, wrapper) so users grasp the category at first glance."
                }
            },
            {
                "number": "07",
                "title": "Deployment & Portfolio Showcase",
                "description": "Deploy the project and prepare documentation so you can showcase it in your portfolio.",
                "brief": {
                    "overview": "Containerize the application with Docker, deploy live on Hugging Face Spaces or Render, create a professional GitHub repository with a detailed README and demo GIF, and add it to your Student Tech Hub portfolio.",
                    "milestones": [
                        "Write Dockerfile and requirements.txt for reproducible deployment",
                        "Deploy live interactive demo on Hugging Face Spaces or Render",
                        "Write comprehensive README with problem statement, architecture diagram, and accuracy stats",
                        "Record a 60-second video demo or GIF showcasing real-time waste sorting"
                    ],
                    "tools": ["Docker", "GitHub", "Hugging Face Spaces / Render", "Markdown"],
                    "starter_guide": """# Dockerfile for Campus Waste Classifier
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]""",
                    "proof_expected": "Live public demo URL and public GitHub repository link with formatted README.",
                    "tips": "A working live link and animated demo in your portfolio gives recruiters instant proof of skill."
                }
            }
        ]
    else:
        # Generic tailored 7-step architecture with rich briefs for catalog projects
        steps = [
            {
                "number": "01",
                "title": "Project Environment & Setup",
                "description": f"Set up your development environment, repository, project structure, and required dependencies for {title}.",
                "brief": {
                    "overview": f"Set up a professional development workspace for {title}. Initialize Git version control, configure a clean project directory hierarchy, and install required libraries ({', '.join(skills)}).",
                    "milestones": [
                        f"Initialize Git repository and configure .gitignore for {category}",
                        f"Create dedicated virtual environment and verify {tech1} runtime",
                        f"Install and pin core dependencies ({', '.join(skills)})",
                        "Create modular project folder structure (src/, tests/, docs/, data/)"
                    ],
                    "tools": ["Git", "Python / Node.js", "Virtualenv", f"{tech1}"],
                    "starter_guide": f"""# Step 01: Scaffold {title}
git init
python -m venv venv
# Activate environment and install dependencies
pip install {' '.join([s.lower().replace(' ', '-') for s in skills])}
echo "Scaffold complete for {title}!" """,
                    "proof_expected": "Clean terminal log confirming all packages installed and directory structure verified.",
                    "tips": "Keep configuration parameters in a .env file rather than hardcoding them in code."
                }
            },
            {
                "number": "02",
                "title": f"{category} Resource Preparation",
                "description": f"Gather the datasets, content, or resources needed for {title}.",
                "brief": {
                    "overview": f"Assemble and curate the raw data, schemas, API credentials, or assets necessary to power {title}.",
                    "milestones": [
                        "Source authentic datasets, API endpoints, or reference schemas",
                        "Clean and normalize incoming data formats",
                        "Perform initial exploratory validation or schema checks",
                        "Store processed data in standard structured formats"
                    ],
                    "tools": ["Pandas", "JSON / CSV", "APIs", "Data Validation"],
                    "starter_guide": f"""# Resource loader for {title}
import json, os

print("Curating resources for {title}...")
# Prepare datasets or API configs
data_schema = {{"project": "{title}", "category": "{category}", "status": "initialized"}}
print("Resource preparation verified.")""",
                    "proof_expected": "Sample dataset or validated data schema ready for implementation.",
                    "tips": "Ensure data is properly sanitized and edge cases are documented early."
                }
            },
            {
                "number": "03",
                "title": f"Build {title}",
                "description": f"Develop the core features of {title} using {tech1}.",
                "brief": {
                    "overview": f"Implement the core algorithms, state handling, and business logic of {title} using {tech1}.",
                    "milestones": [
                        f"Develop the primary processing pipeline using {tech1}",
                        "Implement key business logic and data transformations",
                        "Add error handling and defensive input checking",
                        "Ensure modular architecture with clear function boundaries"
                    ],
                    "tools": [f"{tech1}", "Core Libraries", "Debugger"],
                    "starter_guide": f"""# Core implementation of {title}
class {title.replace(' ', '')}:
    def __init__(self):
        self.name = "{title}"
        self.ready = True

    def process(self, input_data):
        # Implement core {category} logic
        return {{"status": "processed", "result": input_data}}

engine = {title.replace(' ', '')}()
print("Core engine instantiated successfully!")""",
                    "proof_expected": "Working core module executing basic test cases with clean output.",
                    "tips": "Write modular functions with single responsibilities to make testing straightforward."
                }
            },
            {
                "number": "04",
                "title": f"{tech2} Integration & Testing",
                "description": f"Integrate {tech2}, test the project, and validate its expected results.",
                "brief": {
                    "overview": f"Integrate {tech2} with your core implementation, write unit and integration test suites, and benchmark performance.",
                    "milestones": [
                        f"Connect {tech2} modules with the core engine",
                        "Write automated test cases covering normal and error scenarios",
                        "Benchmark execution speed, memory footprint, or response latency",
                        "Fix regressions and validate stability"
                    ],
                    "tools": [f"{tech2}", "Pytest / Jest", "Logging"],
                    "starter_guide": f"""# Test suite for {title}
def test_core_execution():
    assert 1 + 1 == 2
    print("Testing {title} with {tech2} integration... ALL TESTS PASSED ✓")

test_core_execution()""",
                    "proof_expected": "Test runner output showing 100% passing test cases and benchmark metrics.",
                    "tips": "Test boundary conditions like empty inputs, invalid types, and high loads."
                }
            },
            {
                "number": "05",
                "title": "Backend / API Integration",
                "description": "Connect your frontend with APIs, services, databases, or backend functionality.",
                "brief": {
                    "overview": "Design and build REST or GraphQL endpoints to serve data and functionality reliably to clients.",
                    "milestones": [
                        "Define API routing and request/response schemas",
                        "Connect persistence layer (database or storage)",
                        "Implement authentication or rate limiting if required",
                        "Document API endpoints with interactive Swagger / OpenAPI docs"
                    ],
                    "tools": ["FastAPI / Express", "SQLite / PostgreSQL", "Pydantic"],
                    "starter_guide": f"""# API endpoint for {title}
# Expose core functionality via REST API
print("API server configured for {title}.")""",
                    "proof_expected": "Functional API endpoint returning valid responses when tested via curl or HTTP client.",
                    "tips": "Always return meaningful HTTP status codes (200, 400, 404, 500) with helpful error messages."
                }
            },
            {
                "number": "06",
                "title": "User Interface & Integration",
                "description": "Connect all components and polish the user experience across desktop and mobile devices.",
                "brief": {
                    "overview": f"Develop an elegant, responsive user interface matching Student Tech Hub design standards, connecting frontend views to backend services.",
                    "milestones": [
                        "Build modern, clean user interface with consistent color palette and typography",
                        "Connect interactive elements to backend endpoints",
                        "Provide real-time loading states and user feedback",
                        "Verify responsive layout across mobile and desktop screen sizes"
                    ],
                    "tools": ["Streamlit / React", "CSS", "UI Components"],
                    "starter_guide": f"""# UI View for {title}
print("Connecting UI components with backend for {title}...")""",
                    "proof_expected": "Working UI displaying live project data and responsive controls.",
                    "tips": "Prioritize clarity and responsiveness; ensure buttons provide visual feedback when clicked."
                }
            },
            {
                "number": "07",
                "title": "Deployment & Portfolio Showcase",
                "description": "Deploy the project and prepare documentation so you can showcase it in your portfolio.",
                "brief": {
                    "overview": f"Deploy {title} to public hosting, assemble a professional GitHub repository with complete documentation, and showcase on your Student Tech Hub profile.",
                    "milestones": [
                        "Create production build or containerize with Docker",
                        "Deploy application on cloud hosting (Render, Vercel, or Hugging Face)",
                        "Write comprehensive README.md with architecture overview and setup guide",
                        "Publish to Student Tech Hub portfolio with live demo links"
                    ],
                    "tools": ["Docker", "Git", "Cloud Hosting", "Markdown"],
                    "starter_guide": f"""# Deployment checklist for {title}
# 1. Build and test container
# 2. Push to GitHub
# 3. Connect to cloud provider and deploy
echo "Deployment guide ready for {title}!" """,
                    "proof_expected": "Public URL with live application and public GitHub repository link.",
                    "tips": "A clear README with a 1-minute walkthrough video makes your project stand out to mentors and recruiters."
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
Your goal is to provide a clean, simple, practical, and easy-to-follow **Step-by-Step Roadmap** for the student to build their project.

### TARGET PROJECT:
- Project Title: {matched_title}
- Department: {dept}
- Technologies & Stack: {tech}
- Suggested Prerequisites: {prereqs}
- Difficulty: {difficulty}

### CRITICAL RULES (STRICT REQUIREMENTS):
1. **NO EXECUTIVE SUMMARY**: Do NOT include an Executive Summary, overview introduction, or abstract. Jump directly into the simple actionable guidance.
2. **NO TIME TAKEN / NO DURATIONS**: Do NOT mention or display any time taken, hours, days, weeks, durations, or completion times anywhere in the roadmap or checklist. Keep steps purely milestone-focused.
3. **SIMPLE & CHAT-FRIENDLY**: Keep the content simple, concise, and easy to read inside a chatbot window. Use short bullet points and clear formatting.

### ROADMAP STRUCTURE:
1. 🛠️ **Tools & Prerequisites**:
   - Short, simple list of tools and libraries to install.
   - 2-3 basic concepts needed.
2. 📌 **Simple Step-by-Step Phases** (No time taken or durations mentioned):
   - **Phase 1: Setup & Environment**: Simple initial steps.
   - **Phase 2: Core Implementation**: The main building blocks in simple language.
   - **Phase 3: Integration & Testing**: Simple steps to verify everything works.
   - **Phase 4: Run & Showcase**: How to test, run, and demonstrate the project.
3. 💻 **Starter Code**:
   - A clean, simple, ready-to-run boilerplate code snippet for Phase 1 with clear comments.
4. ✅ **Action Checklist**:
   - A short checklist (`- [ ]`) of clear tasks to complete (without any time estimates).

Tone: Simple, encouraging, clear, and direct. Avoid overwhelming blocks of text.
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

### INSTRUCTIONS:
- Directly answer the student's doubt about **{matched_title}** in simple, clear, and beginner-friendly terms.
- Keep the content simple and easily readable inside the chatbot (use short bullet points, avoid walls of text).
- Do NOT display or mention time taken, hours, or durations.
- If they ask for code, give clean, working, documented code specific to this project and its tools ({tech}).
- If they ask about data or datasets, provide realistic free data sources or mock data generators.
"""
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            for model_name in ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.8-flash"]:
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

