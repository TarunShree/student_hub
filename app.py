import os
import json
import urllib.parse
import streamlit as st

from agent.roadmap import (
    get_student_tech_hub_roadmap,
    get_project_catalog,
    find_project_by_name,
    answer_project_doubt
)

# Page Configuration matching Student Tech Hub
st.set_page_config(
    page_title="Student Tech Hub // Project Roadmap",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- STATE MANAGEMENT ----------------
# Check for incoming project parameter via URL (e.g. ?project=Smart+Campus+Waste+Classifier)
query_project = st.query_params.get("project", "").strip()

if "active_project" not in st.session_state:
    st.session_state.active_project = query_project if query_project else "Smart Campus Waste Classifier"

if query_project and query_project != st.session_state.get("last_query_param", ""):
    st.session_state.active_project = query_project
    st.session_state.last_query_param = query_project
    st.session_state.step_progress = 0
    st.session_state.doubt_messages = [
        {"role": "assistant", "content": f"Hello! I am your AI Mentor for **{query_project}**. Ask me any questions, starter code, or doubt clearance as you work through each step!"}
    ]

# Completed step index (0 means step 1 is current, 0 completed)
if "step_progress" not in st.session_state:
    st.session_state.step_progress = 0

if "show_project_picker" not in st.session_state:
    st.session_state.show_project_picker = False

if "doubt_messages" not in st.session_state:
    st.session_state.doubt_messages = [
        {
            "role": "assistant",
            "content": f"👋 Welcome! I am your **AI Project Mentor** for **{st.session_state.active_project}**.\n\nYou can ask me for starter code, dataset sources, architecture design, or interview preparation for any step in your roadmap!"
        }
    ]


# ---------------- STUDENT TECH HUB CLEAN DESIGN SYSTEM CSS ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    /* Global typography and palette reset */
    html, body, [class*="css"], .stMarkdown, p, div, label, span {
        font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
        color: #17233D;
        -webkit-font-smoothing: antialiased;
    }

    /* Clean luminous background matching Student Tech Hub */
    .stApp {
        background-color: #F4F7FC !important;
        background-image: radial-gradient(at 0% 0%, rgba(88, 101, 242, 0.04) 0px, transparent 50%),
                          radial-gradient(at 100% 100%, rgba(99, 102, 241, 0.03) 0px, transparent 50%) !important;
    }

    /* Completely hide Streamlit sidebar and controls */
    section[data-testid="stSidebar"], 
    [data-testid="collapsedControl"],
    button[kind="header"],
    [data-testid="stSidebarCollapseButton"],
    header[data-testid="stHeader"] button,
    div[data-testid="stSidebarContent"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* Spacious Center container layout */
    .main .block-container {
        max-width: 1040px !important;
        margin: 0 auto !important;
        padding-top: 1.5rem !important;
        padding-bottom: 6rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* Top Floating Navigation Bar */
    .hub-navbar {
        background: #FFFFFF;
        border: 1px solid #E1E8F4;
        border-radius: 18px;
        box-shadow: 0 4px 20px rgba(50, 70, 110, 0.04);
        padding: 12px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 32px;
    }

    .brand-wrap {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-icon {
        width: 36px;
        height: 36px;
        background: #EFF0FF;
        border: 1px solid #DFE3FF;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #5865F2;
        font-size: 18px;
    }

    .brand-title {
        font-size: 16px;
        font-weight: 800;
        color: #17233D;
        line-height: 1.1;
    }

    .brand-subtitle {
        font-size: 11px;
        font-weight: 600;
        color: #8C98A9;
    }

    .nav-links {
        display: flex;
        align-items: center;
        gap: 24px;
    }

    .nav-item {
        color: #5C6A82;
        font-size: 14px;
        font-weight: 600;
        text-decoration: none;
    }

    .nav-item.active {
        background: #5865F2;
        color: #FFFFFF !important;
        padding: 6px 18px;
        border-radius: 999px;
        font-weight: 700;
        box-shadow: 0 2px 10px rgba(88, 101, 242, 0.35);
    }

    .nav-actions {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .nav-btn-icon {
        width: 36px;
        height: 36px;
        border: 1px solid #E2E8F0;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #FFFFFF;
        color: #5C6A82;
        font-size: 15px;
    }

    /* Project Header */
    .roadmap-eyebrow {
        color: #5865F2;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 8px;
    }

    .roadmap-title {
        font-size: 32px;
        font-weight: 800;
        color: #17233D;
        margin: 0 0 8px 0;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }

    .roadmap-desc {
        font-size: 15px;
        font-weight: 500;
        color: #5C6A82;
        margin: 0;
        line-height: 1.6;
        max-width: 800px;
    }

    /* Progress Summary Card */
    .roadmap-summary-card {
        background: #FFFFFF;
        border: 1px solid #E1E8F4;
        border-radius: 18px;
        box-shadow: 0 4px 20px rgba(50, 70, 110, 0.03);
        padding: 24px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 24px;
        margin-top: 24px;
        margin-bottom: 38px;
    }

    .summary-left {
        display: flex;
        flex-direction: column;
        gap: 10px;
        flex: 1;
        min-width: 280px;
    }

    .summary-label {
        color: #8C98A9;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .progress-row {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .progress-percent {
        font-size: 30px;
        font-weight: 800;
        color: #17233D;
        min-width: 65px;
        line-height: 1;
    }

    .progress-track-bg {
        background: #EEF2F8;
        border-radius: 999px;
        height: 9px;
        flex: 1;
        max-width: 320px;
        overflow: hidden;
    }

    .progress-fill-bar {
        background: #5865F2;
        height: 100%;
        border-radius: 999px;
        transition: width 0.35s ease;
    }

    .progress-step-count {
        color: #8C98A9;
        font-size: 12.5px;
        font-weight: 600;
        white-space: nowrap;
    }

    .roadmap-skills-tags {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }

    .skill-tag-pill {
        background: #EEF2FF;
        color: #4F46E5 !important;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
    }

    /* Timeline Stepper Container */
    .timeline-container {
        position: relative;
        padding-left: 0;
        margin-bottom: 34px;
    }

    .timeline-vertical-line {
        position: absolute;
        left: 23px;
        top: 28px;
        bottom: 50px;
        width: 2px;
        background: #E2E6F0;
        z-index: 1;
    }

    .timeline-step-row {
        display: grid;
        grid-template-columns: 46px 1fr;
        gap: 20px;
        margin-bottom: 26px;
        position: relative;
        align-items: flex-start;
    }

    .step-marker {
        width: 46px;
        height: 46px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12.5px;
        font-weight: 800;
        z-index: 2;
        transition: all 0.25s ease;
        margin-top: 2px;
    }

    .step-marker.active {
        background: #5865F2;
        color: #FFFFFF !important;
        box-shadow: 0 0 0 6px rgba(88, 101, 242, 0.16);
    }

    .step-marker.done {
        background: #168A4A;
        color: #FFFFFF !important;
        box-shadow: 0 0 0 6px rgba(22, 138, 74, 0.16);
    }

    .step-marker.locked {
        background: #F0F2F7;
        color: #AAB1BF !important;
        border: 1px solid #DFE3EB;
    }

    /* Step Card */
    .step-card {
        background: #FFFFFF;
        border: 1px solid #E1E8F4;
        border-radius: 16px;
        padding: 24px 28px;
        box-shadow: 0 4px 18px rgba(50, 70, 110, 0.03);
        transition: all 0.2s ease;
    }

    .step-card.active-card {
        border-color: #D4DAF8;
        box-shadow: 0 6px 24px rgba(88, 101, 242, 0.07);
    }

    .step-card-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 16px;
        margin-bottom: 6px;
    }

    .step-num-label {
        color: #929BAB;
        font-size: 10.5px;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .step-title {
        color: #17233D;
        font-size: 19px;
        font-weight: 800;
        margin: 4px 0 0 0;
        line-height: 1.3;
    }

    .step-status-badge {
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 800;
        white-space: nowrap;
    }

    .status-current {
        background: #EFF0FF;
        color: #5865F2 !important;
    }

    .status-completed {
        background: #EEF9F2;
        color: #36A264 !important;
    }

    .status-locked {
        background: #F0F2F5;
        color: #9299A8 !important;
    }

    .step-desc {
        color: #5C6A82;
        font-size: 14px;
        margin: 8px 0 16px 0;
        line-height: 1.6;
    }

    /* Proof Submission Container matching Student Tech Hub */
    .proof-box {
        background: #F8FAFD;
        border: 1px solid #E1E8F4;
        border-radius: 14px;
        padding: 20px 24px;
        margin-top: 18px;
    }

    .proof-demo-note {
        color: #64748B;
        font-size: 12.5px;
        margin: 14px 0 0 0;
        line-height: 1.6;
    }

    /* Transform File Uploader into the exact 'Choose a proof photo' button from Student Tech Hub */
    div[data-testid="stFileUploader"] {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stFileUploader"] > label {
        display: none !important;
    }

    /* Style the dropzone box as a clean white button */
    div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"] {
        background: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 10px !important;
        padding: 0 16px !important;
        min-height: 42px !important;
        height: 42px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        overflow: hidden !important;
    }

    div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"]:hover {
        border-color: #5865F2 !important;
        box-shadow: 0 2px 8px rgba(88, 101, 242, 0.15) !important;
    }

    /* Hide ALL internal clunky text, instructions, and size limit text to eliminate overlap */
    div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"] [data-testid="stFileUploadDropzoneInstructions"],
    div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"] small,
    div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"] span,
    div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"] svg {
        display: none !important;
    }

    /* Style the browse button as the clean '⇪ Choose a proof photo' */
    div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"] button {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        font-size: 0 !important; /* Hides default Browse files / Upload text */
        cursor: pointer !important;
        box-shadow: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        height: 100% !important;
    }

    div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"] button::after {
        content: "⇪  Choose a proof photo" !important;
        font-size: 13.5px !important;
        font-weight: 700 !important;
        color: #334155 !important;
        white-space: nowrap !important;
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
    }

    div[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"]:hover button::after {
        color: #5865F2 !important;
    }

    /* Uploaded file display */
    div[data-testid="stFileUploader"] ul {
        margin-top: 8px !important;
        padding: 0 !important;
    }

    div[data-testid="stFileUploader"] ul li {
        background: #FFFFFF !important;
        border: 1px solid #D5E2F5 !important;
        border-radius: 8px !important;
        padding: 6px 12px !important;
        font-size: 12.5px !important;
        color: #16A34A !important;
        font-weight: 700 !important;
    }

    /* Bottom Why Matters Bar */
    .roadmap-bottom-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
        margin-top: 28px;
        flex-wrap: wrap;
    }

    .why-box {
        background: #F0F6FF;
        border: 1px solid #D9E7FB;
        border-radius: 14px;
        padding: 18px 22px;
        display: flex;
        align-items: flex-start;
        gap: 14px;
        flex: 1;
        min-width: 280px;
    }

    .why-title {
        color: #203B62;
        font-size: 12px;
        font-weight: 800;
        margin: 0;
    }

    .why-text {
        color: #52647F;
        font-size: 13.5px;
        margin: 4px 0 0 0;
        line-height: 1.6;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease !important;
    }

    /* Primary button */
    button[kind="primary"] {
        background: #5865F2 !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    button[kind="primary"]:hover {
        background: #4752C4 !important;
        box-shadow: 0 4px 14px rgba(88, 101, 242, 0.4) !important;
    }

    /* Secondary outline button */
    button[kind="secondary"] {
        background: #FFFFFF !important;
        color: #334155 !important;
        border: 1px solid #D1D5DB !important;
    }
    button[kind="secondary"]:hover {
        border-color: #5865F2 !important;
        color: #5865F2 !important;
    }

    /* ---------------- FLOATING IRCTC-STYLE CHATBOT ON LEFT ---------------- */
    div[data-testid="stPopover"] {
        position: fixed !important;
        bottom: 26px !important;
        left: 26px !important;
        z-index: 999999 !important;
    }

    div[data-testid="stPopover"] > button {
        border-radius: 999px !important;
        background: linear-gradient(135deg, #5865F2, #4752C4) !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 12px 22px !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        box-shadow: 0 8px 28px rgba(88, 101, 242, 0.45) !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        transition: all 0.25s ease !important;
    }

    div[data-testid="stPopover"] > button:hover {
        transform: translateY(-2px) scale(1.04) !important;
        box-shadow: 0 12px 34px rgba(88, 101, 242, 0.6) !important;
    }

    div[data-testid="stPopoverBody"] {
        width: 420px !important;
        max-width: calc(100vw - 40px) !important;
        max-height: 580px !important;
        border-radius: 20px !important;
        box-shadow: 0 20px 60px rgba(23, 35, 61, 0.25) !important;
        border: 1px solid #E1E8F4 !important;
        padding: 18px !important;
        background: #FFFFFF !important;
        overflow-y: auto !important;
    }

    .stChatMessage {
        background: #F8FAFD !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important;
        padding: 10px 14px !important;
        margin-bottom: 8px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02) !important;
    }

    div[data-testid="stChatInput"] {
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 12px !important;
        background-color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- TOP FLOATING NAVIGATION BAR ----------------
st.markdown("""
<div class="hub-navbar">
    <div class="brand-wrap">
        <div class="brand-icon">✨</div>
        <div>
            <div class="brand-title">Student Tech Hub</div>
            <div class="brand-subtitle">Build. Learn. Showcase.</div>
        </div>
    </div>
    <div class="nav-links">
        <span class="nav-item">Home</span>
        <span class="nav-item">Dashboard</span>
        <span class="nav-item">AI Assistant</span>
        <span class="nav-item active">Roadmap</span>
        <span class="nav-item">Portfolio</span>
    </div>
    <div class="nav-actions">
        <div class="nav-btn-icon">🔔</div>
        <div class="nav-btn-icon">👤</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------- LOAD PROJECT DATA ----------------
roadmap_data = get_student_tech_hub_roadmap(st.session_state.active_project)
active_title = roadmap_data["title"]
active_desc = roadmap_data["description"]
active_skills = roadmap_data["skills"]
all_steps = roadmap_data["steps"]
total_steps = len(all_steps)


# ---------------- PROJECT HEADER (Matching Student Tech Hub) ----------------
col_header, col_btn = st.columns([4, 1.2], vertical_alignment="center")

with col_header:
    st.markdown(f"""
    <div class="roadmap-eyebrow">
        <span>🔀</span>
        <span>PROJECT ROADMAP</span>
    </div>
    <h1 class="roadmap-title">{active_title}</h1>
    <p class="roadmap-desc">{active_desc}</p>
    """, unsafe_allow_html=True)

with col_btn:
    if st.button("Change Project", use_container_width=True, type="secondary"):
        st.session_state.show_project_picker = not st.session_state.show_project_picker
        st.rerun()


# ---------------- PROJECT CATALOG PICKER (Toggled via Change Project) ----------------
if st.session_state.show_project_picker:
    catalog = get_project_catalog()
    all_titles = sorted(list(set([p.get("title", "") for p in catalog if p.get("title")])))
    if active_title not in all_titles:
        all_titles.insert(0, active_title)

    with st.container():
        st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #D9E2F1; border-radius: 14px; padding: 18px 24px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(50, 70, 110, 0.06);">
            <div style="font-weight: 800; font-size: 13px; color: #17233D; margin-bottom: 8px;">SELECT OR ENTER TARGET PROJECT:</div>
        </div>
        """, unsafe_allow_html=True)

        col_pick, col_cust, col_act = st.columns([3.5, 3.5, 1.5])
        with col_pick:
            sel_proj = st.selectbox(
                "Choose from Verified Catalog:",
                all_titles,
                index=all_titles.index(active_title) if active_title in all_titles else 0,
                label_visibility="collapsed"
            )
        with col_cust:
            cust_proj = st.text_input(
                "Or Type Custom Project Name:",
                placeholder="Or type custom project name...",
                label_visibility="collapsed"
            )
        with col_act:
            if st.button("Apply Project", use_container_width=True, type="primary"):
                chosen = cust_proj.strip() if cust_proj.strip() else sel_proj
                st.session_state.active_project = chosen
                st.session_state.step_progress = 0
                st.session_state.show_project_picker = False
                st.session_state.doubt_messages = [
                    {"role": "assistant", "content": f"Loaded project: **{chosen}**. Ask me any doubt or starter code for this roadmap!"}
                ]
                st.rerun()


# ---------------- CURRENT PROGRESS SUMMARY CARD ----------------
completed_count = st.session_state.step_progress
progress_pct = int((completed_count / total_steps) * 100) if total_steps > 0 else 0
skills_html = "".join([f'<span class="skill-tag-pill">{s}</span>' for s in active_skills])

st.markdown(f"""
<div class="roadmap-summary-card">
    <div class="summary-left">
        <span class="summary-label">CURRENT PROGRESS</span>
        <div class="progress-row">
            <span class="progress-percent">{progress_pct}%</span>
            <div class="progress-track-bg">
                <div class="progress-fill-bar" style="width: {progress_pct}%;"></div>
            </div>
            <span class="progress-step-count">{completed_count} / {total_steps} steps</span>
        </div>
    </div>
    <div class="roadmap-skills-tags">
        {skills_html}
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------- STEP BRIEF MODAL DIALOG (Distraction-free & spacious) ----------------
@st.dialog("Step Execution Brief & Guide", width="large")
def show_step_brief_dialog(step_data, project_title, skills):
    s_num = step_data.get("number", "01")
    s_title = step_data.get("title", "")
    s_desc = step_data.get("description", "")
    brief = step_data.get("brief", {})

    st.markdown(f"""
    <div style="border-bottom: 1.5px solid #EAEFF8; padding-bottom: 14px; margin-bottom: 20px;">
        <span style="font-size: 11px; font-weight: 800; color: #5865F2; letter-spacing: 0.12em; text-transform: uppercase;">STEP {s_num} OF 07</span>
        <h2 style="font-size: 24px; font-weight: 800; color: #17233D; margin: 4px 0 6px 0;">{s_title}</h2>
        <p style="font-size: 14px; color: #5C6A82; margin: 0; line-height: 1.5;">{s_desc}</p>
    </div>
    """, unsafe_allow_html=True)

    tab_overview, tab_code, tab_verify = st.tabs(["📌 Overview & Action Plan", "💻 Starter Code & Setup", "📤 Deliverables & Proof"])

    with tab_overview:
        st.markdown(f"""
        <div style="margin-top: 14px; margin-bottom: 18px;">
            <div style="font-size: 12px; font-weight: 800; color: #17233D; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;">🎯 OBJECTIVE & PURPOSE</div>
            <p style="font-size: 14.5px; color: #475569; line-height: 1.65; margin: 0;">{brief.get('overview', s_desc)}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size: 12px; font-weight: 800; color: #17233D; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 10px;">📋 ACTION CHECKLIST</div>
        """, unsafe_allow_html=True)

        milestones = brief.get("milestones", [])
        for m_idx, milestone in enumerate(milestones):
            st.checkbox(milestone, key=f"chk_dlg_{s_num}_{m_idx}")

        st.markdown("""
        <div style="font-size: 12px; font-weight: 800; color: #17233D; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 18px; margin-bottom: 8px;">🛠️ TOOLS & DEPENDENCIES</div>
        """, unsafe_allow_html=True)
        tools = brief.get("tools", skills)
        tools_pills = "".join([f'<span style="display: inline-block; background: #EEF2FF; color: #4F46E5; font-size: 12px; font-weight: 700; padding: 5px 12px; border-radius: 999px; margin-right: 8px; margin-bottom: 8px;">{t}</span>' for t in tools])
        st.markdown(f"<div>{tools_pills}</div>", unsafe_allow_html=True)

    with tab_code:
        st.markdown("<p style='font-size: 13.5px; color: #64748B; margin-top: 10px; margin-bottom: 12px;'>Copy and run this starter implementation in your project directory:</p>", unsafe_allow_html=True)
        code_snip = brief.get("starter_guide", "# No code snippet required for this step.")
        st.code(code_snip, language="python")

    with tab_verify:
        proof_text = brief.get("proof_expected", "Verify all tests pass and expected outputs are logged.")
        tips_text = brief.get("tips", "")

        st.markdown(f"""
        <div style="background: #F8FAFD; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px 20px; margin-top: 12px;">
            <div style="font-size: 12px; font-weight: 800; color: #16A34A; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px;">✓ VERIFICATION CRITERIA</div>
            <p style="font-size: 14px; color: #334155; line-height: 1.6; margin: 0;">{proof_text}</p>
            {f'<div style="margin-top: 12px; padding-top: 10px; border-top: 1px dashed #CBD5E1; font-size: 13px; color: #64748B;">💡 <strong>Pro-Tip:</strong> {tips_text}</div>' if tips_text else ''}
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    col_ask, col_close = st.columns([3, 1])
    with col_ask:
        if st.button(f"💬 Clear Doubts with AI Mentor on Step {s_num}", use_container_width=True, type="primary"):
            prompt_q = f"I am currently working on Step {s_num}: '{s_title}' for {project_title}. Please give me step-by-step guidance, common pitfalls, and starter advice."
            st.session_state.doubt_messages.append({"role": "user", "content": prompt_q})
            with st.spinner("AI Mentor preparing response..."):
                resp = answer_project_doubt(
                    question=prompt_q,
                    project_name=project_title,
                    student={"department": "Engineering", "skills": skills},
                    history=st.session_state.doubt_messages[-8:],
                    current_step=step_data
                )
                st.session_state.doubt_messages.append({"role": "assistant", "content": resp})
            st.toast(f"AI Mentor ready for Step {s_num}! Click '✨ Ask AI Mentor' on bottom-left to view.", icon="✨")
            st.rerun()


# ---------------- 7-STEP VERTICAL TIMELINE ----------------
st.markdown('<div class="timeline-container"><div class="timeline-vertical-line"></div>', unsafe_allow_html=True)

for idx, step in enumerate(all_steps):
    step_num = step["number"]
    step_title = step["title"]
    step_desc = step["description"]

    # Determine step status
    if idx < completed_count:
        status_key = "done"
        status_label = "Completed"
        status_class = "status-completed"
        marker_html = "✓"
        marker_class = "step-marker done"
    elif idx == completed_count:
        status_key = "active"
        status_label = "Current"
        status_class = "status-current"
        marker_html = step_num
        marker_class = "step-marker active"
    else:
        status_key = "locked"
        status_label = "Locked"
        status_class = "status-locked"
        marker_html = "🔒"
        marker_class = "step-marker locked"

    active_card_class = " active-card" if status_key == "active" else ""

    # Render Clean Card
    st.markdown(f"""
    <div class="timeline-step-row">
        <div class="{marker_class}">{marker_html}</div>
        <div class="step-card{active_card_class}">
            <div class="step-card-top">
                <div>
                    <span class="step-num-label">STEP {step_num}</span>
                    <h3 class="step-title">{step_title}</h3>
                </div>
                <span class="step-status-badge {status_class}">{status_label}</span>
            </div>
            <p class="step-desc">{step_desc}</p>
    """, unsafe_allow_html=True)

    # Clean action row: View Step Brief button
    col_brief_btn, col_blank = st.columns([2.2, 5])
    with col_brief_btn:
        if st.button(f"📖 View Step Brief →", key=f"open_brief_btn_{idx}", use_container_width=True, type="secondary"):
            show_step_brief_dialog(step, active_title, active_skills)

    # Active Step Proof Submission Action Box (Matching Student Tech Hub)
    if status_key == "active":
        st.markdown("""
        <div class="proof-box">
        """, unsafe_allow_html=True)

        col_upload, col_submit, col_mark = st.columns([3.2, 1.8, 1.8], vertical_alignment="center")
        with col_upload:
            uploaded_proof = st.file_uploader(
                "Choose a proof photo",
                type=["png", "jpg", "jpeg", "webp"],
                key=f"proof_upload_{idx}",
                label_visibility="collapsed"
            )
        with col_submit:
            submit_btn = st.button("Submit for review →", key=f"submit_btn_{idx}", use_container_width=True, type="primary")
        with col_mark:
            complete_btn = st.button("Mark as Complete ✓", key=f"mark_btn_{idx}", use_container_width=True, type="secondary")

        if submit_btn or complete_btn:
            st.session_state.step_progress = min(total_steps, st.session_state.step_progress + 1)
            st.rerun()

        st.markdown("""
            <p class="proof-demo-note">
                Demo mode: your photo stays in this browser session. It is not sent to a reviewer, and the step will remain pending until a reviewer workflow is connected.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# ---------------- BOTTOM SECTION: WHY THIS STEP MATTERS ----------------
current_step_obj = all_steps[min(completed_count, total_steps - 1)]
current_step_desc = current_step_obj.get("description", f"Every verified step brings {active_title} closer to your portfolio.")

st.markdown(f"""
<div class="roadmap-bottom-bar">
    <div class="why-box">
        <span style="font-size: 20px;">💡</span>
        <div>
            <div class="why-title">Why this step matters</div>
            <div class="why-text">{current_step_desc} Every verified step brings {active_title} closer to your portfolio.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------- FLOATING IRCTC-STYLE CHATBOT ON THE LEFT ----------------
# Just like IRCTC (Ask Disha), a small fixed floating icon sits at bottom-left.
# When clicked, a compact popover chat window opens right there.
with st.popover("✨ Ask AI Mentor", help="Chat with your dedicated AI Project Mentor"):
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #EEF2F6; padding-bottom: 10px; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 20px;">✨</span>
            <div>
                <div style="font-weight: 800; font-size: 15px; color: #17233D;">AI Project Mentor</div>
                <div style="font-size: 11px; font-weight: 600; color: #16A34A;">🟢 Online · {active_title}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: #EFF0FF; border-radius: 8px; padding: 6px 12px; margin-bottom: 12px; font-size: 12px; color: #5865F2; font-weight: 700;">
        📍 Current Focus: Step {current_step_obj['number']} - {current_step_obj['title']}
    </div>
    """, unsafe_allow_html=True)

    # Quick suggestion chips
    c1, c2 = st.columns(2)
    quick_choice = None
    with c1:
        if st.button("💻 Starter Code", key="pop_starter_code", use_container_width=True):
            quick_choice = f"Please provide clean, commented starter code for {current_step_obj['title']} of {active_title}."
        if st.button("📊 Free Datasets", key="pop_datasets", use_container_width=True):
            quick_choice = f"Where can I find free datasets or public resources to build {active_title}?"
    with c2:
        if st.button("💡 Explain Step", key="pop_explain", use_container_width=True):
            quick_choice = f"Explain {current_step_obj['title']} for {active_title} in simple, beginner terms with an analogy."
        if st.button("🎯 Interview Qs", key="pop_interview", use_container_width=True):
            quick_choice = f"What are the top 3 technical interview questions an interviewer will ask about {active_title}?"

    # Conversation history display inside popover
    chat_container = st.container(height=260)
    with chat_container:
        for msg in st.session_state.doubt_messages:
            r = msg["role"]
            with st.chat_message(r, avatar="✨" if r == "assistant" else "👤"):
                st.markdown(msg["content"])

    # Chat Input Box
    user_chat_msg = st.chat_input(f"Ask any doubt about {active_title}...")
    active_chat_query = quick_choice or user_chat_msg

    if active_chat_query:
        st.session_state.doubt_messages.append({"role": "user", "content": active_chat_query})
        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.markdown(active_chat_query)

            with st.chat_message("assistant", avatar="✨"):
                with st.spinner("AI Mentor thinking..."):
                    mentor_answer = answer_project_doubt(
                        question=active_chat_query,
                        project_name=active_title,
                        student={"department": roadmap_data["category"], "skills": active_skills},
                        history=st.session_state.doubt_messages[-8:],
                        current_step=current_step_obj
                    )
                    st.markdown(mentor_answer)

        st.session_state.doubt_messages.append({"role": "assistant", "content": mentor_answer})
        st.rerun()
