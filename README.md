# ✨ Student Tech Hub // Project Roadmap & AI Mentor

An interactive student project roadmap and AI-powered mentorship application built with **Streamlit**, **FastAPI**, and **Google Gemini**, designed with the [Student Tech Hub](https://vixhnu90.github.io/student-tech-hub/) design system.

---

## 🚀 Key Features

* **Interactive 7-Step Project Roadmap**: Milestone-driven architecture designed to guide students from environment setup, dataset preparation, core implementation, testing, API development, to portfolio showcase.
* **Detailed Step Execution Briefs**: Click any step in the roadmap to view a focused execution brief with actionable checklists, tool dependencies, copyable starter code snippets, and verification criteria.
* **Floating IRCTC-Style AI Mentor**: A floating widget pinned to the bottom-left of the screen (`✨ Ask AI Mentor`) that opens a focused doubt-clearing chat interface to answer questions about any project or step.
* **Project Catalog & Recommender**: Built-in catalog of 50+ curated student projects across AI/ML, Web, Mobile, IoT, Biotechnology, and Engineering with TF-IDF cosine similarity recommendations.
* **FastAPI Backend Services**: Endpoints for chat (`/chat`), roadmaps (`/roadmap`), doubt clearing (`/doubt`), and catalog lookups (`/hub-roadmap/{project_name}`).

---

## 🛠️ Tech Stack

* **Frontend**: Streamlit, Custom Vanilla CSS & Plus Jakarta Sans typography
* **AI & LLM**: Google Gemini API (`google-genai`)
* **Recommendation Engine**: Scikit-Learn (TF-IDF & Cosine Similarity), Pandas
* **Backend API**: FastAPI, Uvicorn, Pydantic

---

## 📦 Local Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<YOUR_USERNAME>/<YOUR_REPOSITORY_NAME>.git
cd <YOUR_REPOSITORY_NAME>
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and set your Google Gemini API key:
```bash
cp .env.example .env
```
In `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Run the Application
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🌐 Deploying to Streamlit Community Cloud (Free)

1. Push this repository to your **GitHub** account.
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
3. Click **"New app"**.
4. Select your repository, branch (`main`), and set **Main file path** to `app.py`.
5. Under **Advanced settings** -> **Secrets**, add your Gemini API key:
   ```toml
   GEMINI_API_KEY = "your_actual_gemini_api_key"
   ```
6. Click **Deploy!** Your app will be live with a public URL.
