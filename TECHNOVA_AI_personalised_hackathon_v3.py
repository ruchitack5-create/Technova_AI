import streamlit as st
import json
import re
import html
import urllib.parse
import urllib.request
import base64
import time
import math
from datetime import date, datetime, timedelta
from pathlib import Path
import pandas as pd
from google import genai
from google.genai import types

# =========================================================
# TECHNOVA AI | Single-file Streamlit learning platform
# =========================================================

st.set_page_config(
    page_title="TECHNOVA AI",
    page_icon="🚀",
    layout="wide"
)

MODEL = "gemini-3.5-flash-lite"

# ------------------------- DESIGN -------------------------

# Keep technova_bg.png in the same GitHub folder as app.py.
# If the image is missing, the app safely falls back to a dark purple gradient.
bg_path = Path(__file__).parent / "technova_bg.png"
bg_encoded = ""
if bg_path.exists():
    bg_encoded = base64.b64encode(bg_path.read_bytes()).decode("utf-8")

background_css = (
    f'url("data:image/png;base64,{bg_encoded}")'
    if bg_encoded
    else 'radial-gradient(circle at 20% 15%, #32105f 0%, #10051f 42%, #03020a 100%)'
)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Kalam:wght@400;700&family=Poppins:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Poppins', sans-serif;
}}

.stApp {{
    background-image:
        linear-gradient(rgba(4, 1, 15, 0.70), rgba(4, 1, 15, 0.82)),
        {background_css};
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
}}

[data-testid="stHeader"] {{
    background: rgba(5, 0, 20, 0.35);
}}

[data-testid="stSidebar"] {{
    background: rgba(12, 4, 30, 0.96);
    border-right: 1px solid rgba(183, 106, 255, 0.35);
}}

[data-testid="stSidebar"] * {{
    color: #f3e8ff;
}}

h1, h2, h3 {{
    color: #ead5ff;
}}

p, label, .stMarkdown, [data-testid="stCaptionContainer"] {{
    color: #f1eaff;
}}

.hero {{
    padding: 28px;
    border-radius: 22px;
    background: linear-gradient(110deg, rgba(20, 0, 45, 0.94), rgba(75, 0, 130, 0.88), rgba(130, 50, 220, 0.78));
    color: white;
    margin-bottom: 20px;
    border: 1px solid #b76aff;
    box-shadow: 0 0 22px rgba(160, 70, 255, 0.42);
    backdrop-filter: blur(12px);
}}

.hero h1 {{
    color: white;
    margin: 0;
    font-size: 2.25rem;
}}

.hero p {{
    color: #f0ddff;
    margin: 6px 0 0 0;
}}

.note-paper {{
    background: rgba(25, 12, 45, 0.94);
    border-left: 7px solid #b76aff;
    border-radius: 14px;
    padding: 22px 24px;
    color: #f5eaff;
    box-shadow: 0 5px 20px rgba(130, 50, 220, 0.22);
    font-family: 'Kalam', cursive;
    line-height: 1.9;
}}

.note-paper h1, .note-paper h2, .note-paper h3 {{
    font-family: 'Kalam', cursive;
    color: #d8aaff;
}}

.tip {{
    background: rgba(90, 55, 10, 0.90);
    border-left: 5px solid #eab308;
    border-radius: 10px;
    padding: 12px 15px;
    margin: 10px 0;
    color: #fff0bd;
}}

.definition {{
    background: rgba(25, 45, 85, 0.92);
    border-left: 5px solid #60a5fa;
    border-radius: 10px;
    padding: 12px 15px;
    margin: 10px 0;
    color: #dbeafe;
}}

.success-card {{
    background: rgba(15, 65, 45, 0.92);
    border-left: 5px solid #22c55e;
    border-radius: 10px;
    padding: 12px 15px;
    color: #dcfce7;
}}

.small-muted {{
    color: #c4b5fd;
    font-size: .9rem;
}}

div.stButton > button {{
    border-radius: 12px;
    border: 1px solid #b76aff;
    min-height: 44px;
    background: linear-gradient(90deg, #5100a8, #9333ea);
    color: white;
    font-weight: 600;
    box-shadow: 0 0 12px rgba(147, 51, 234, 0.35);
}}

div.stButton > button:hover {{
    color: white;
    border: 1px solid #e9d5ff;
    box-shadow: 0 0 20px #9333ea;
}}

[data-testid="stTabs"] button[aria-selected="true"] {{
    color: #e9d5ff;
    border-bottom-color: #c084fc;
}}

[data-testid="stExpander"] {{
    background: rgba(20, 8, 40, 0.82);
    border: 1px solid rgba(183, 106, 255, 0.35);
    border-radius: 12px;
}}

input, textarea, [data-baseweb="select"] > div {{
    background-color: rgba(20, 10, 38, 0.92) !important;
    color: #f5eaff !important;
}}
</style>
""", unsafe_allow_html=True)

# ------------------------- API CLIENT -------------------------

@st.cache_resource
def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

client = get_client()

def ask_ai(prompt, max_tokens=3500, json_mode=False):
    """Call Gemini with bounded retries for temporary server failures."""
    if client is None:
        return None, "Gemini API key is missing. Add GEMINI_API_KEY in Streamlit Cloud → App settings → Secrets."

    config = types.GenerateContentConfig(
        temperature=0.35,
        max_output_tokens=max_tokens,
        response_mime_type="application/json" if json_mode else "text/plain"
    )

    # One original attempt plus at most three retries: wait 2s, 4s, then 8s.
    retry_delays = (2, 4, 8)
    for attempt in range(len(retry_delays) + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=config
            )
            answer = response.text or ""
            if not answer.strip():
                return None, "The AI returned an empty response. Please try again."
            return answer, None

        except Exception as exc:
            message = str(exc)
            upper_message = message.upper()

            # Retry only transient server/service errors. Do not repeatedly send
            # requests for invalid models, bad requests, or exhausted quotas.
            is_temporary_server_error = any(
                marker in upper_message
                for marker in ("503", "UNAVAILABLE", "502", "504", "500 INTERNAL")
            )

            if is_temporary_server_error and attempt < len(retry_delays):
                time.sleep(retry_delays[attempt])
                continue

            if "429" in message or "RESOURCE_EXHAUSTED" in upper_message:
                return None, "Gemini is temporarily rate-limiting requests or your API quota has been reached. Please wait before trying again."
            if "404" in message or "NOT_FOUND" in upper_message:
                return None, f"Model '{MODEL}' was not found for this API key. Update MODEL in app.py only after checking which models your API key supports."
            if is_temporary_server_error:
                return None, "Gemini is experiencing high demand right now. TECHNOVA AI tried again automatically, but the service is still busy. Please wait a moment and try once more."
            return None, f"Gemini request failed: {message[:300]}"

    return None, "Gemini is temporarily unavailable. Please try again in a moment."

def parse_json(text):
    """Parse model JSON even if it accidentally adds code fences."""
    if not text:
        raise ValueError("Empty JSON response")
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            return json.loads(cleaned[start:end + 1])
        raise

def normalise_mindmap(data, fallback_topic):
    """Convert common AI mind-map JSON shapes into TECHNOVA's format."""
    if isinstance(data, str):
        data = parse_json(data)
    if isinstance(data, list):
        data = {"branches": data}
    if not isinstance(data, dict):
        raise ValueError("Mind map must be a JSON object.")

    for key in ("mindmap", "mind_map", "result", "data"):
        if isinstance(data.get(key), (dict, list)):
            data = data[key]
            break

    center = (data.get("center") or data.get("main_topic") or
              data.get("title") or data.get("topic") or fallback_topic)
    branches = (data.get("branches") or data.get("main_branches") or
                data.get("topics") or data.get("nodes") or data.get("children"))

    if isinstance(branches, dict):
        branches = [{"title": key, "points": value}
                    for key, value in branches.items()]
    if not isinstance(branches, list):
        raise ValueError("No readable mind-map branches found.")

    cleaned = []
    for branch in branches:
        if isinstance(branch, str):
            cleaned.append({"title": branch, "points": []})
        elif isinstance(branch, dict):
            title = (branch.get("title") or branch.get("name") or
                     branch.get("label") or branch.get("topic") or "Concept")
            points = (branch.get("points") or branch.get("subtopics") or
                      branch.get("children") or branch.get("details") or [])
            if isinstance(points, str):
                points = [points]
            if isinstance(points, list):
                points = [str(item.get("title", item.get("name", "Concept")))
                          if isinstance(item, dict) else str(item)
                          for item in points]
            else:
                points = []
            cleaned.append({"title": str(title), "points": points[:4]})

    if not cleaned:
        raise ValueError("Mind map contains no usable branches.")
    return {"center": str(center), "branches": cleaned[:6]}

def common_context(task):
    return f"""
You are TECHNOVA AI, a careful educational tutor.
Education level: {level}
Selected course / exam: {course}
Course stream / specialisation: {specialisation}
Subject: {subject}
Topic/chapter: {topic}
Preferred language: {language}
Student's requested level: {detail_level}

STRICT ACCURACY RULES:
- Stay specifically within the selected subject and topic.
- Do not mix in unrelated subject content.
- Explain in student-friendly language suitable for the education level.
- Use correct terminology, units, equations and examples.
- If a topic is ambiguous, state the assumption briefly.
- Never invent actual previous-year questions, sources or facts.
- Use the requested language consistently.

TASK:
{task}
"""

# ------------------------- SAFE DISPLAY HELPERS -------------------------

def show_error(error):
    st.error(error)

def show_download(text, filename):
    st.download_button(
        "⬇️ Download",
        data=text,
        file_name=filename,
        mime="text/plain",
        use_container_width=False
    )

def svg_flowchart(steps):
    """Build a clean responsive SVG flowchart from a list of step labels."""
    steps = [str(x)[:90] for x in steps[:8] if str(x).strip()]
    if not steps:
        steps = ["Start", "Understand the input", "Process information", "Produce result", "End"]
    width, box_h, gap = 760, 66, 30
    height = 35 + len(steps) * (box_h + gap)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Flowchart">']
    for i, label in enumerate(steps):
        y = 20 + i * (box_h + gap)
        fill = ["#ede9fe", "#dbeafe", "#dcfce7", "#fce7f3"][i % 4]
        stroke = ["#7c3aed", "#2563eb", "#16a34a", "#db2777"][i % 4]
        safe = html.escape(label)
        parts.append(f'<rect x="100" y="{y}" width="560" height="{box_h}" rx="17" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>')
        parts.append(f'<text x="380" y="{y+40}" text-anchor="middle" font-size="19" font-family="Arial" fill="#27234a">{safe}</text>')
        if i < len(steps) - 1:
            cy = y + box_h
            parts.append(f'<path d="M380 {cy} L380 {cy+gap-7}" stroke="#64748b" stroke-width="3" fill="none"/>')
            parts.append(f'<path d="M372 {cy+gap-15} L380 {cy+gap-5} L388 {cy+gap-15}" stroke="#64748b" stroke-width="3" fill="none"/>')
    parts.append("</svg>")
    return "".join(parts)

def svg_mindmap(center, branches):
    """Build a simple colourful mind map SVG."""
    branches = branches[:6] if isinstance(branches, list) else []
    width, height = 820, 480
    cx, cy = 410, 240
    positions = [(410,65),(675,145),(675,340),(410,415),(145,340),(145,145)]
    palette = ["#dbeafe","#dcfce7","#fce7f3","#fef3c7","#ede9fe","#cffafe"]
    strokes = ["#2563eb","#16a34a","#db2777","#d97706","#7c3aed","#0891b2"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Mind map">']
    for i, branch in enumerate(branches):
        if isinstance(branch, dict):
            title = str(branch.get("title", f"Branch {i+1}"))[:55]
            children = branch.get("points", [])
        else:
            title, children = str(branch)[:55], []
        x, y = positions[i]
        parts.append(f'<path d="M{cx} {cy} Q{(cx+x)//2} {(cy+y)//2-12} {x} {y}" stroke="{strokes[i]}" stroke-width="4" fill="none"/>')
        parts.append(f'<rect x="{x-100}" y="{y-27}" width="200" height="54" rx="18" fill="{palette[i]}" stroke="{strokes[i]}" stroke-width="2"/>')
        parts.append(f'<text x="{x}" y="{y+6}" text-anchor="middle" font-size="16" font-family="Arial" font-weight="bold" fill="#29234a">{html.escape(title)}</text>')
        if children:
            child_text = " • ".join(str(c)[:22] for c in children[:3])
            parts.append(f'<text x="{x}" y="{y+45 if y < cy else y+48}" text-anchor="middle" font-size="11" font-family="Arial" fill="#475569">{html.escape(child_text[:75])}</text>')
    parts.append(f'<rect x="300" y="205" width="220" height="70" rx="23" fill="#4338ca" stroke="#312e81" stroke-width="2"/>')
    parts.append(f'<text x="410" y="246" text-anchor="middle" font-size="19" font-family="Arial" font-weight="bold" fill="white">{html.escape(str(center)[:30])}</text>')
    parts.append("</svg>")
    return "".join(parts)

@st.cache_data(ttl=3600, show_spinner=False)
def search_wikimedia_images(subject_name, topic_name, style="Textbook-style labelled diagram", limit=6):
    """Search Commons for topic-specific diagrams; these are NOT claimed to be NCERT originals."""
    search_phrases = [
        f'"{topic_name}" "{subject_name}" labelled diagram',
        f'"{topic_name}" "{subject_name}" textbook illustration',
        f'{topic_name} {subject_name} educational scientific diagram'
    ]
    if "anatomy" in style.lower() or "biology" in style.lower():
        search_phrases.insert(0, f'{topic_name} {subject_name} anatomy biology labelled illustration')
    elif "schematic" in style.lower() or "physics" in style.lower():
        search_phrases.insert(0, f'{topic_name} {subject_name} schematic physics diagram')
    elif "chemistry" in style.lower():
        search_phrases.insert(0, f'{topic_name} {subject_name} chemistry structure diagram')

    results, seen = [], set()
    for phrase in search_phrases:
        query = urllib.parse.urlencode({
            "action": "query",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {phrase}",
            "gsrnamespace": 6,
            "gsrlimit": limit,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": 700,
            "format": "json"
        })
        url = "https://commons.wikimedia.org/w/api.php?" + query
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "TECHNOVA-AI-Educational-App/1.1 (educational reference search)"}
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            continue

        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            title = page.get("title", "Educational image").replace("File:", "")
            title_key = title.casefold()
            if title_key in seen:
                continue
            info = (page.get("imageinfo") or [{}])[0]
            image_url = info.get("thumburl") or info.get("url")
            if image_url:
                seen.add(title_key)
                results.append({
                    "title": title,
                    "url": image_url,
                    "source": info.get("descriptionurl", "https://commons.wikimedia.org/"),
                    "license": info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "Check source page"),
                    "caption": "Community-hosted reference image — verify labels and source before study use."
                })
            if len(results) >= limit:
                return results[:limit]
    return results[:limit]

# ------------------------- HEADER -------------------------

st.markdown("""
<div class="hero">
  <h1>🚀 TECHNOVA AI</h1>
  <p>Your colourful AI learning companion — understand, visualise, practise and succeed.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------- LEARNING INPUTS -------------------------

with st.sidebar:
    st.header("📚 Tell TECHNOVA about your studies")
    st.caption("No fixed class, course, branch or subject lists. Enter the details that match your own education.")
    level = st.text_input("Your education level", placeholder="e.g. 2nd-year engineering, Class 10, MBA, self-learning")
    course = st.text_input("Course / programme / exam (optional)", placeholder="e.g. BE in AIML, CBSE, NEET, Python certification")
    specialisation = st.text_input("Branch / stream / specialisation (optional)", placeholder="e.g. Artificial Intelligence and Machine Learning")
    subject = st.text_input("Subject", placeholder="e.g. Data Structures, Biology, Economics")
    topic = st.text_input("Chapter / topic", placeholder="e.g. Linked Lists, Human Heart, Microeconomics")
    language = st.text_input("Preferred response language", value="Simple English", placeholder="e.g. Kannada, Hindi, English")
    detail_level = st.text_input("How detailed should the explanation be?", value="Medium", placeholder="e.g. brief, beginner-friendly, detailed")
    st.markdown("---")
    st.caption("You can type any education system, qualification, subject, chapter and language.")

ready = bool(subject.strip() and topic.strip())

if not ready:
    st.info("👈 Enter your subject and chapter/topic in the sidebar to begin. Other education details are optional.")
else:
    context_parts = [x for x in [level, course, specialisation, subject, topic] if x.strip()]
    st.success("Ready to learn: **" + " · ".join(context_parts) + "**")

# ------------------------- MAIN TABS -------------------------

tab_notes, tab_visual, tab_exam, tab_textbook, tab_quiz, tab_doubt, tab_history, tab_planner = st.tabs([
    "📝 Colourful Notes",
    "🎨 Visual Learning",
    "📖 Exam Preparation",
    "📘 Textbook & PYQs",
    "🎯 Mock Test",
    "💬 Doubt Solver",
    "🕘 Previous Topics",
    "🗓️ Smart Study Planner"
])

def save_topic_history(activity):
    entry = {
        "course": course,
        "specialisation": specialisation,
        "subject": subject,
        "topic": topic,
        "activity": activity
    }
    history = st.session_state.get("topic_history", [])
    # Keep the newest matching activity at the top and avoid consecutive duplicates.
    if not history or history[0] != entry:
        history.insert(0, entry)
    st.session_state["topic_history"] = history[:40]

# ========================= NOTES ============================

with tab_notes:
    st.subheader("📝 Digital handwritten-style notes")
    st.write("Notebook-inspired pages with coloured definitions, key points, examples and exam tips.")
    if st.button("✨ Create my notes", key="make_notes", disabled=not ready):
        prompt = common_context(f"""
Create {detail_level.lower()} study notes in a visually organised structure.
Use Markdown headings and these exact labels where relevant:
## 🌸 Introduction
## 🔵 Definition
## 🟣 Main concepts
## 🟢 Step-by-step explanation
## 🧡 Important points
## 📌 Formulae / key terms (only if relevant)
## 🌍 Real-life examples
## ⭐ Exam tip
## 📝 Quick revision
Keep paragraphs short. Use bullet points and simple examples.
Do not include sections that genuinely do not apply to this topic.
""")
        with st.spinner("Writing and decorating your digital notes..."):
            answer, error = ask_ai(prompt, 4500)
        if error:
            show_error(error)
        else:
            st.session_state["notes"] = answer
            save_topic_history("Colourful notes")

    if st.session_state.get("notes"):
        st.markdown('<div class="note-paper">', unsafe_allow_html=True)
        st.markdown(st.session_state["notes"])
        st.markdown("</div>", unsafe_allow_html=True)
        show_download(st.session_state["notes"], "TECHNOVA_AI_Colourful_Notes.md")

# ========================= VISUAL LEARNING ==================

with tab_visual:
    st.subheader("🎨 Pictorial learning studio")
    st.write("Generate graphical flowcharts and mind maps, then find topic-related reference images.")
    v1, v2 = st.columns(2)
    with v1:
        if st.button("🔀 Generate pictorial flowchart", key="flow", disabled=not ready):
            prompt = common_context("""
Return ONLY valid JSON with this structure:
{"title":"short title","steps":["step 1","step 2","step 3","step 4","step 5"],"explanation":"brief explanation"}
Create 4 to 8 logical steps in correct order. Each step must be short enough to fit inside a flowchart box. Keep it specific to the topic.
""")
            with st.spinner("Drawing your flowchart..."):
                answer, error = ask_ai(prompt, 1600, json_mode=True)
            if error:
                show_error(error)
            else:
                try:
                    st.session_state["flow_data"] = parse_json(answer)
                    save_topic_history("Pictorial flowchart")
                except Exception:
                    st.error("The flowchart data was not in a readable format. Please try again.")
    with v2:
        if st.button("🌳 Generate colourful mind map", key="mind", disabled=not ready):
            prompt = common_context("""
Return ONLY valid JSON with this structure:
{"center":"main topic","branches":[{"title":"branch name","points":["point 1","point 2"]}]}
Create 4 to 6 branches. Each branch should have 1 to 3 short related points. Keep all branches relevant to the chosen topic.
""")
            with st.spinner("Building your mind map..."):
                answer, error = ask_ai(prompt, 1800, json_mode=True)
            if error:
                show_error(error)
            else:
                try:
                    data = parse_json(answer)
                    st.session_state["mind_data"] = normalise_mindmap(data, topic)
                    save_topic_history("Colourful mind map")
                except Exception as exc:
                    st.error(f"Mind map generation failed: {str(exc)}")

    if st.session_state.get("flow_data"):
        data = st.session_state["flow_data"]
        st.markdown(f"### 🔀 {html.escape(str(data.get('title', 'Topic flowchart')))}")
        st.markdown(svg_flowchart(data.get("steps", [])), unsafe_allow_html=True)
        if data.get("explanation"):
            st.info(data["explanation"])

    if st.session_state.get("mind_data"):
        data = st.session_state["mind_data"]
        st.markdown(f"### 🌳 {html.escape(str(data.get('center', topic)))}")
        st.markdown(svg_mindmap(data.get("center", topic), data.get("branches", [])), unsafe_allow_html=True)
        with st.expander("Read mind-map branch details"):
            for branch in data.get("branches", []):
                if isinstance(branch, dict):
                    st.markdown(f"**{branch.get('title', 'Branch')}**")
                    for point in branch.get("points", []):
                        st.write("•", point)

    st.divider()
    st.markdown("### 🖼️ Textbook-style topic diagrams and illustrations")
    st.caption("TECHNOVA searches public educational reference images and prioritises labelled, topic-specific diagrams. These results are not automatically official NCERT images.")
    image_style = st.selectbox(
        "Choose diagram style",
        ["Textbook-style labelled diagram", "Biology / anatomy illustration", "Chemistry structure diagram", "Physics schematic / ray diagram", "General educational illustration"],
        key="image_style"
    )
    if st.button("Find relevant textbook-style images", key="images", disabled=not ready):
        try:
            with st.spinner("Searching for labelled diagrams related to your exact topic..."):
                st.session_state["topic_images"] = search_wikimedia_images(subject, topic, image_style, 6)
                save_topic_history("Topic reference images")
        except Exception as exc:
            st.session_state["topic_images"] = []
            st.warning(f"Image search is temporarily unavailable: {str(exc)[:220]}")
    images = st.session_state.get("topic_images", [])
    if images:
        cols = st.columns(2)
        for index, item in enumerate(images):
            with cols[index % 2]:
                st.image(item["url"], use_container_width=True)
                st.caption(item["title"])
                st.caption(f"Licence: {item.get('license', 'Check source page')}")
                st.markdown(f"[Open image source and verify details]({item['source']})")
    elif "topic_images" in st.session_state:
        st.info("No close matches were found. Try a more specific topic name or another diagram style.")

    st.info("For exam revision, compare every diagram with your prescribed textbook. Image labels and licences must be checked on the original source page.")

    st.markdown("### 🧩 Need a custom labelled explanation?")
    st.caption("Use the Doubt Solver to request a step-by-step explanation of a specific diagram, its labels and how to remember them.")

# ========================= EXAM PREPARATION =================

with tab_exam:
    st.subheader("📖 Exam preparation")
    exam_type = st.selectbox(
        "Choose material",
        [
            "Important questions with answers",
            "2-mark questions with answers",
            "4-mark questions with answers",
            "5-mark questions with answers",
            "6-mark questions with answers",
            "Chapter-wise PYQ-style practice questions",
            "Definitions and formulae",
            "Topic-wise quick revision",
            "Memory tricks and mnemonics",
            "Real-world examples"
        ],
        key="exam_type"
    )
    count = st.slider("Number of questions / points", 5, 20, 10)
    if st.button("📚 Generate exam material", key="exam_generate", disabled=not ready):
        prompt = common_context(f"""
Create: {exam_type}
Number requested: {count}
For mark-based answers, make the answer depth appropriate to the marks.
Use headings, numbered points and a relevant example where appropriate.
For chapter-wise PYQ-style practice, create topic-specific questions resembling the selected exam pattern. Clearly label them as AI-generated practice questions, NOT verified previous-year questions. Never invent a year, paper code, shift or official source.
For formulae, only include formulas genuinely relevant to this topic and define every symbol.
For memory tricks, give a mnemonic and explain what each part represents.
""")
        with st.spinner("Preparing your exam material..."):
            answer, error = ask_ai(prompt, 4500)
        if error:
            show_error(error)
        else:
            st.session_state["exam_material"] = answer
            save_topic_history(exam_type)
    if st.session_state.get("exam_material"):
        st.markdown(st.session_state["exam_material"])
        show_download(st.session_state["exam_material"], "TECHNOVA_AI_Exam_Preparation.md")

# ========================= TEXTBOOK & OFFICIAL PYQ HUB ======

with tab_textbook:
    st.subheader("📘 Textbook and official question-paper hub")
    st.write("Open trusted textbook and examination portals. TECHNOVA links to official sources instead of copying copyrighted textbook pages into the app.")

    st.markdown("#### 📚 NCERT textbooks")
    st.markdown("- [Open NCERT online textbooks](https://ncert.nic.in/textbook.php)")
    st.markdown("- [Open ePathshala digital textbooks and learning resources](https://epathshala.nic.in/)")
    st.caption("Choose the correct class, subject, language and current textbook edition on the official portal. Chapter names and page numbers can change between editions.")

    st.markdown("#### 📝 Official previous-year question-paper portals")
    exam_name = f"{course} {specialisation}".lower()
    if "neet" in exam_name:
        st.markdown("- [NEET official NTA website](https://neet.nta.nic.in/)")
        st.markdown("- [NEET NTA archive](https://neet.nta.nic.in/archive/)")
    elif "jee" in exam_name:
        st.markdown("- [JEE Main official NTA website and question papers](https://jeemain.nta.nic.in/)")
    elif "upsc" in exam_name or "civil services" in exam_name or "kpsc" in exam_name:
        st.markdown("- [UPSC official previous question papers](https://upsc.gov.in/examinations/previous-question-papers)")
        st.markdown("- [UPSC question-paper archive](https://cms.upsc.gov.in/exam-documents/question-papers/)")
    else:
        st.markdown("- [National Testing Agency (NTA)](https://www.nta.ac.in/)")
        st.markdown("- [NTA downloads and examination resources](https://www.nta.ac.in/Downloads)")
        st.markdown("- [Karnataka Examinations Authority (KEA)](https://cetonline.karnataka.gov.in/kea/)")
        st.markdown("- [UPSC previous question papers](https://upsc.gov.in/examinations/previous-question-papers)")

    st.warning("AI-generated practice questions are not official PYQs. Use the official portals above to verify original papers, years and answer keys.")

    st.markdown("#### 🧭 Topic-to-textbook study guide")
    st.caption("Generate a study checklist for the selected topic. TECHNOVA will not invent textbook page numbers or claim an exact NCERT chapter unless it can verify it.")
    if st.button("Create textbook study checklist", key="textbook_checklist", disabled=not ready):
        prompt = common_context("""
Create a concise textbook-alignment checklist for this topic.
Include:
1. Core concepts the student should locate in their prescribed textbook.
2. Key terms, definitions, diagrams, tables or equations to review, only when relevant.
3. 5 self-check questions for active recall.
4. A short checklist for comparing notes with the textbook.
Do NOT invent textbook page numbers, chapter numbers, quotations or exact NCERT section titles.
If you are not certain of the exact textbook chapter title, say: 'Please confirm the chapter title in your current textbook edition.'
Clearly distinguish general topic guidance from verified textbook references.
""")
        with st.spinner("Building your textbook study checklist..."):
            answer, error = ask_ai(prompt, 2200)
        if error:
            show_error(error)
        else:
            st.session_state["textbook_checklist"] = answer
            save_topic_history("Textbook study checklist")

    if st.session_state.get("textbook_checklist"):
        st.markdown(st.session_state["textbook_checklist"])
        show_download(st.session_state["textbook_checklist"], "TECHNOVA_Textbook_Checklist.md")


# ========================= INTERACTIVE MOCK TEST ============

with tab_quiz:
    st.subheader("🎯 Interactive mock test")
    st.write("Generate MCQs, select answers, submit and receive your score.")
    quiz_difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key="quiz_difficulty")
    quiz_count = st.selectbox("Number of questions", [5, 10, 15], key="quiz_count")
    if st.button("⚡ Generate mock test", key="quiz_generate", disabled=not ready):
        prompt = common_context(f"""
Return ONLY valid JSON in this exact structure:
{{"questions":[{{"question":"question text","options":{{"A":"option A","B":"option B","C":"option C","D":"option D"}},"answer":"A","explanation":"short explanation"}}]}}
Create exactly {quiz_count} multiple-choice questions at {quiz_difficulty} difficulty.
All questions must be from the selected subject and topic. Each answer must be exactly A, B, C or D. Make sure the correct answer is actually correct and the options are unambiguous.
""")
        with st.spinner("Creating your interactive test..."):
            answer, error = ask_ai(prompt, 3800, json_mode=True)
        if error:
            show_error(error)
        else:
            try:
                quiz = parse_json(answer)
                questions = quiz.get("questions", [])
                valid = []
                for q in questions:
                    opts = q.get("options", {})
                    correct = str(q.get("answer", "")).upper()
                    if q.get("question") and all(k in opts for k in ["A", "B", "C", "D"]) and correct in ["A", "B", "C", "D"]:
                        valid.append(q)
                if not valid:
                    st.error("The AI did not return valid questions. Please generate the test again.")
                else:
                    st.session_state["quiz_questions"] = valid
                    save_topic_history("Mock test")
                    st.session_state["quiz_submitted"] = False
                    st.session_state["quiz_answers"] = {}
            except Exception:
                st.error("The mock test response could not be read. Please generate it again.")

    questions = st.session_state.get("quiz_questions", [])
    if questions:
        st.markdown(f"**Your test:** {len(questions)} questions · {quiz_difficulty} level")
        with st.form("mock_test_form"):
            answers = {}
            for idx, q in enumerate(questions):
                st.markdown(f"#### Q{idx+1}. {q['question']}")
                labels = [f"{key}) {q['options'][key]}" for key in ["A", "B", "C", "D"]]
                choice = st.radio(
                    "Choose one answer",
                    labels,
                    index=None,
                    key=f"answer_{idx}",
                    label_visibility="collapsed"
                )
                answers[str(idx)] = choice[0] if choice else None
                st.markdown("---")
            submitted = st.form_submit_button("✅ Submit test and calculate score")
        if submitted:
            score = 0
            for idx, q in enumerate(questions):
                if answers.get(str(idx)) == str(q["answer"]).upper():
                    score += 1
            st.session_state["quiz_answers"] = answers
            st.session_state["quiz_score"] = score
            st.session_state["quiz_submitted"] = True

        if st.session_state.get("quiz_submitted"):
            score = st.session_state["quiz_score"]
            total = len(questions)
            percentage = round((score / total) * 100)
            st.success(f"Your score: {score}/{total} ({percentage}%)")
            st.progress(percentage)
            if percentage >= 80:
                st.balloons()
                st.markdown('<div class="success-card">Excellent work! Keep revising to maintain your score.</div>', unsafe_allow_html=True)
            elif percentage >= 50:
                st.info("Good effort! Review the explanations and practise once more.")
            else:
                st.warning("Keep going. Read the explanations and try another practice test.")
            st.markdown("### Answer review")
            for idx, q in enumerate(questions):
                chosen = st.session_state["quiz_answers"].get(str(idx))
                correct = str(q["answer"]).upper()
                if chosen == correct:
                    st.markdown(f"🟢 **Q{idx+1}: Correct** — {correct}) {q['options'][correct]}")
                else:
                    chosen_text = f"{chosen}) {q['options'][chosen]}" if chosen else "Not answered"
                    st.markdown(f"🔴 **Q{idx+1}: Incorrect** — Your answer: {chosen_text}. Correct: {correct}) {q['options'][correct]}")
                if q.get("explanation"):
                    st.caption(q["explanation"])

# ========================= DOUBT SOLVER =====================

with tab_doubt:
    st.subheader("💬 Ask TECHNOVA AI")
    doubt = st.text_area(
        "Type your question",
        placeholder="Ask for an explanation, a worked example, a labelled diagram description or help with a difficult concept...",
        height=130
    )
    if st.button("🧠 Explain my doubt", key="doubt_btn"):
        if not ready:
            st.warning("First select your subject and enter a topic in the sidebar.")
        elif not doubt.strip():
            st.warning("Please type your question.")
        else:
            prompt = common_context(f"""
Answer this student's question:
{doubt}

Explain step by step in {language}.
Include one relevant example.
If a diagram would help, provide a clear labelled text/ASCII diagram and explain its parts.
Keep the answer tied to the selected subject and topic. If the question is outside the selected topic, politely say so and answer only if it is still within the selected subject.
""")
            with st.spinner("Thinking through your question..."):
                answer, error = ask_ai(prompt, 3000)
            if error:
                show_error(error)
            else:
                st.markdown(answer)
                save_topic_history("Doubt solving")

# ========================= PREVIOUS TOPICS ==================

with tab_history:
    st.subheader("🕘 Your recently studied topics")
    st.caption("Topics are kept in this browser session. They may reset when the app session restarts.")
    history = st.session_state.get("topic_history", [])
    if history:
        for index, item in enumerate(history):
            with st.expander(f"{item['topic']} · {item['subject']} · {item['activity']}"):
                st.write(f"**Course:** {item['course']}")
                st.write(f"**Stream / specialisation:** {item['specialisation']}")
                st.write(f"**Subject:** {item['subject']}")
                st.write(f"**Topic:** {item['topic']}")
                st.write(f"**Last activity:** {item['activity']}")
        if st.button("🗑️ Clear topic history", key="clear_history"):
            st.session_state["topic_history"] = []
            st.rerun()
    else:
        st.info("Your studied topics will appear here after you generate notes, diagrams, exam material or mock tests.")


# ====================== SMART STUDY PLANNER ======================

SAMPLE_CURRICULUM = [
    {"topic_id":"MATH-01","subject":"Engineering Mathematics","topic":"Matrices and determinants","difficulty":"Medium","estimated_hours":3,"importance":5,"prerequisites":[]},
    {"topic_id":"MATH-02","subject":"Engineering Mathematics","topic":"Eigenvalues and eigenvectors","difficulty":"Hard","estimated_hours":4,"importance":5,"prerequisites":["MATH-01"]},
    {"topic_id":"PROG-01","subject":"Programming","topic":"Variables, data types and operators","difficulty":"Easy","estimated_hours":2,"importance":4,"prerequisites":[]},
    {"topic_id":"PROG-02","subject":"Programming","topic":"Conditional statements and loops","difficulty":"Medium","estimated_hours":3,"importance":5,"prerequisites":["PROG-01"]},
    {"topic_id":"DSA-01","subject":"Data Structures","topic":"Arrays and linked lists","difficulty":"Medium","estimated_hours":4,"importance":5,"prerequisites":["PROG-02"]},
    {"topic_id":"DSA-02","subject":"Data Structures","topic":"Stacks and queues","difficulty":"Medium","estimated_hours":3,"importance":4,"prerequisites":["DSA-01"]},
    {"topic_id":"AI-01","subject":"Artificial Intelligence","topic":"Introduction to AI and intelligent agents","difficulty":"Easy","estimated_hours":2,"importance":4,"prerequisites":[]},
    {"topic_id":"AI-02","subject":"Artificial Intelligence","topic":"Search algorithms","difficulty":"Hard","estimated_hours":4,"importance":5,"prerequisites":["AI-01"]}
]


def planner_read_curriculum(uploaded):
    if uploaded is None:
        return pd.DataFrame(SAMPLE_CURRICULUM), "Built-in engineering sample"
    name = uploaded.name.lower()
    if name.endswith('.json'):
        raw = json.load(uploaded)
        if isinstance(raw, dict):
            rows = raw.get('topics', raw.get('curriculum', raw.get('subjects', [])))
            if isinstance(rows, dict):
                flattened = []
                for subj, topics in rows.items():
                    if isinstance(topics, list):
                        for item in topics:
                            item = {"subject": subj, **(item if isinstance(item, dict) else {"topic": str(item)})}
                            flattened.append(item)
                rows = flattened
        else:
            rows = raw
        if not isinstance(rows, list) or not rows:
            raise ValueError("JSON must contain a non-empty topics/curriculum list.")
        df = pd.DataFrame(rows)
    elif name.endswith('.csv'):
        df = pd.read_csv(uploaded)
    else:
        raise ValueError("Upload a .json or .csv curriculum file.")
    aliases = {"name":"topic", "chapter":"topic", "topic_name":"topic", "hours":"estimated_hours", "study_hours":"estimated_hours", "weight":"importance", "difficulty_level":"difficulty", "id":"topic_id", "prerequisite":"prerequisites"}
    df = df.rename(columns={c: aliases[c.lower()] for c in df.columns if c.lower() in aliases and aliases[c.lower()] not in df.columns})
    if 'topic' not in df.columns:
        raise ValueError("Curriculum needs a 'topic' column/field.")
    if 'topic_id' not in df.columns:
        df['topic_id'] = [f"TOP-{i+1:03d}" for i in range(len(df))]
    if 'subject' not in df.columns:
        df['subject'] = 'General'
    if 'difficulty' not in df.columns:
        df['difficulty'] = 'Medium'
    if 'estimated_hours' not in df.columns:
        df['estimated_hours'] = 2
    if 'importance' not in df.columns:
        df['importance'] = 3
    if 'prerequisites' not in df.columns:
        df['prerequisites'] = ''
    return df, uploaded.name


def planner_list(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    text_value = str(value).strip()
    if not text_value or text_value.lower() == 'nan':
        return []
    try:
        parsed = json.loads(text_value)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
    except Exception:
        pass
    return [x.strip() for x in re.split(r'[;,|]', text_value) if x.strip()]


def planner_analyse(df, progress_df):
    data = df.copy()
    data['topic_id'] = data['topic_id'].astype(str)
    data['topic'] = data['topic'].astype(str)
    data['subject'] = data['subject'].fillna('General').astype(str)
    data['estimated_hours'] = pd.to_numeric(data['estimated_hours'], errors='coerce').fillna(2).clip(lower=0.25)
    data['importance'] = pd.to_numeric(data['importance'], errors='coerce').fillna(3).clip(1, 5)
    data['difficulty'] = data['difficulty'].fillna('Medium').astype(str).str.title()
    data['prerequisites_list'] = data['prerequisites'].apply(planner_list)
    if data['topic_id'].duplicated().any():
        raise ValueError('Each topic_id must be unique. Please fix duplicate IDs in your curriculum.')
    progress = {}
    if progress_df is not None and not progress_df.empty:
        if 'topic_id' not in progress_df.columns or 'completion' not in progress_df.columns:
            raise ValueError("Progress CSV needs 'topic_id' and 'completion' columns.")
        for _, row in progress_df.iterrows():
            try:
                progress[str(row['topic_id'])] = max(0, min(100, float(row['completion'])))
            except Exception:
                continue
    data['completion'] = data['topic_id'].map(progress).fillna(0)
    diff_map = {'easy':1, 'medium':2, 'hard':3, 'very hard':4}
    data['difficulty_score'] = data['difficulty'].str.lower().map(diff_map).fillna(2)
    data['remaining_hours'] = data['estimated_hours'] * (1 - data['completion'] / 100)
    data['priority_score'] = (
        data['importance'] * 0.40 + data['difficulty_score'] * 0.25 +
        (100 - data['completion']) / 100 * 3.0 +
        data['remaining_hours'].clip(upper=8) / 8 * 1.0
    )
    known = set(data['topic_id'])
    missing = {r['topic_id']: [x for x in r['prerequisites_list'] if x not in known] for _, r in data.iterrows()}
    missing = {k:v for k,v in missing.items() if v}
    # Kahn topological sort; ties are resolved by higher calculated priority.
    lookup = data.set_index('topic_id').to_dict('index')
    indegree = {tid:0 for tid in known}
    children = {tid:[] for tid in known}
    for _, row in data.iterrows():
        tid = row['topic_id']
        for pre in row['prerequisites_list']:
            if pre in known:
                indegree[tid] += 1
                children[pre].append(tid)
    priority = data.set_index('topic_id')['priority_score'].to_dict()
    ready_ids = [tid for tid, deg in indegree.items() if deg == 0]
    ordered = []
    while ready_ids:
        ready_ids.sort(key=lambda x: priority.get(x, 0), reverse=True)
        tid = ready_ids.pop(0)
        ordered.append(tid)
        for child in children[tid]:
            indegree[child] -= 1
            if indegree[child] == 0:
                ready_ids.append(child)
    cycle_ids = [tid for tid in known if tid not in ordered]
    ordered += sorted(cycle_ids, key=lambda x: priority.get(x, 0), reverse=True)
    rank = {tid:i for i,tid in enumerate(ordered)}
    data['sequence'] = data['topic_id'].map(rank)
    data = data.sort_values(['sequence','priority_score'], ascending=[True,False]).reset_index(drop=True)
    return data, missing, cycle_ids


def planner_make_timetable(analysis, start_day, exam_day, daily_hours, study_days,
                           start_time, session_minutes=50, break_minutes=10):
    """Allocate topic work into daily available hours and clock-time study sessions."""
    available_dates = []
    cursor = start_day
    allowed = set(range(7)) if study_days == 7 else (set(range(6)) if study_days == 6 else set(range(5)))
    while cursor <= exam_day:
        if cursor.weekday() in allowed:
            available_dates.append(cursor)
        cursor += timedelta(days=1)
    if not available_dates:
        raise ValueError('No study days are available before the exam date.')

    slots = []
    day_index = 0
    remaining_today = float(daily_hours)
    clock_minutes = start_time.hour * 60 + start_time.minute
    session_count_today = 0

    for _, row in analysis.iterrows():
        hours = float(row['remaining_hours'])
        if hours <= 0.01:
            continue
        while hours > 0.001 and day_index < len(available_dates):
            if remaining_today <= 0.001:
                day_index += 1
                remaining_today = float(daily_hours)
                clock_minutes = start_time.hour * 60 + start_time.minute
                session_count_today = 0
                continue

            if session_count_today > 0:
                clock_minutes += int(break_minutes)
            chunk = min(hours, remaining_today, float(session_minutes) / 60.0)
            duration_minutes = max(1, int(round(chunk * 60)))
            end_minutes = clock_minutes + duration_minutes
            start_label = f"{clock_minutes // 60:02d}:{clock_minutes % 60:02d}"
            end_label = f"{end_minutes // 60:02d}:{end_minutes % 60:02d}"
            slots.append({
                'date': available_dates[day_index].isoformat(),
                'start_time': start_label, 'end_time': end_label,
                'subject': row['subject'], 'topic': row['topic'], 'topic_id': row['topic_id'],
                'hours': round(chunk, 2), 'priority': round(float(row['priority_score']), 2),
                'task': 'Learn / practise' if float(row['completion']) < 50 else 'Revise / complete'
            })
            hours -= chunk
            remaining_today -= chunk
            clock_minutes = end_minutes
            session_count_today += 1
        if hours > 0.001:
            slots.append({'date':'Beyond exam date','start_time':'—','end_time':'—',
                          'subject':row['subject'],'topic':row['topic'], 'topic_id':row['topic_id'],
                          'hours':round(hours,2),'priority':round(float(row['priority_score']),2),
                          'task':'Remaining workload'})
    return pd.DataFrame(slots)


with tab_planner:
    st.subheader('🗓️ Personalised Study Plan Generator')
    st.write('Upload your topics or type them into a curriculum file, tell us how much time you have, and get a timetable arranged around your availability.')
    st.info('This is the hackathon module: structured JSON/CSV input → curriculum analysis → prerequisite ordering → difficulty and priority scoring → personalised timetable → progress-based adaptation.')
    c1, c2 = st.columns(2)
    with c1:
        curriculum_file = st.file_uploader('Upload curriculum (.json or .csv)', type=['json','csv'], key='tn_curriculum')
    with c2:
        progress_file = st.file_uploader('Upload student progress (.csv)', type=['csv'], key='tn_progress')
    st.markdown("#### ⏰ Your available study time")
    p1,p2,p3 = st.columns(3)
    with p1:
        plan_start = st.date_input('Plan starts', value=date.today(), key='tn_start')
        exam_date = st.date_input('Exam / target date', value=date.today()+timedelta(days=14), min_value=date.today(), key='tn_exam')
    with p2:
        daily_hours = st.number_input('How many hours can you study per day?', min_value=0.5, max_value=16.0, value=3.0, step=0.5, key='tn_hours')
        study_days = st.selectbox('How many days per week can you study?', [1,2,3,4,5,6,7], index=6, key='tn_days')
    with p3:
        study_start_time = st.time_input('What time can you start?', value=datetime.strptime('17:00','%H:%M').time(), key='tn_start_time')
        session_minutes = st.selectbox('Preferred focus-session length', [25, 40, 50, 60, 90], index=2, key='tn_session')
        break_minutes = st.selectbox('Break between sessions (minutes)', [5, 10, 15, 20], index=1, key='tn_break')
    st.caption('The timetable uses your daily available hours, weekly study days, preferred start time, focus-session length and break duration.')
    if st.button('⚡ Analyse curriculum & generate my plan', type='primary', key='tn_generate_plan'):
        try:
            base_df, curriculum_source = planner_read_curriculum(curriculum_file)
            progress_data = pd.read_csv(progress_file) if progress_file is not None else pd.DataFrame(columns=['topic_id','completion'])
            analysed, missing_prereqs, cycle_ids = planner_analyse(base_df, progress_data)
            timetable = planner_make_timetable(analysed, plan_start, exam_date, daily_hours, study_days, study_start_time, session_minutes, break_minutes)
            st.session_state['tn_plan_analysis'] = analysed
            st.session_state['tn_plan_timetable'] = timetable
            st.session_state['tn_plan_missing'] = missing_prereqs
            st.session_state['tn_plan_cycles'] = cycle_ids
            st.session_state['tn_plan_source'] = curriculum_source
            st.session_state['tn_plan_progress'] = progress_data
        except Exception as exc:
            st.error(f'Could not generate the plan: {exc}')
    if 'tn_plan_analysis' in st.session_state:
        analysed = st.session_state['tn_plan_analysis']
        timetable = st.session_state['tn_plan_timetable']
        missing_prereqs = st.session_state.get('tn_plan_missing', {})
        cycle_ids = st.session_state.get('tn_plan_cycles', [])
        st.success(f"Plan generated from {st.session_state.get('tn_plan_source','uploaded curriculum')}.")
        k1,k2,k3,k4 = st.columns(4)
        k1.metric('Curriculum topics', len(analysed))
        k2.metric('Completed', f"{(analysed['completion'] >= 100).sum()}")
        k3.metric('Study hours left', f"{analysed['remaining_hours'].sum():.1f} h")
        k4.metric('Scheduled sessions', len(timetable))
        if missing_prereqs:
            st.warning('Some prerequisite IDs are missing from the curriculum: ' + '; '.join(f'{k}: {", ".join(v)}' for k,v in missing_prereqs.items()))
        if cycle_ids:
            st.error('A prerequisite cycle was detected for: ' + ', '.join(cycle_ids) + '. Check these relationships; their order is only a fallback.')
        st.markdown('#### 1. Curriculum analysis & priority')
        display_cols = ['sequence','topic_id','subject','topic','difficulty','estimated_hours','completion','remaining_hours','importance','priority_score','prerequisites']
        st.dataframe(analysed[display_cols], use_container_width=True, hide_index=True)
        st.markdown('#### 2. Your availability-based timetable')
        if timetable.empty:
            st.success('All uploaded topics are already marked complete!')
        else:
            st.dataframe(timetable, use_container_width=True, hide_index=True)
            st.download_button('⬇️ Download timetable CSV', timetable.to_csv(index=False).encode('utf-8'), 'technova_personalised_study_plan.csv', 'text/csv')
            st.download_button('⬇️ Download timetable JSON', timetable.to_json(orient='records', indent=2).encode('utf-8'), 'technova_personalised_study_plan.json', 'application/json')
        st.markdown('#### 3. Update progress & adapt')
        st.caption('Enter completion percentages for topics you have studied. Generate the plan again to recalculate priority and remaining time.')
        progress_update = analysed[['topic_id','subject','topic','completion']].copy()
        edited_progress = st.data_editor(progress_update, use_container_width=True, hide_index=True,
            column_config={'completion':st.column_config.NumberColumn('Completion %', min_value=0, max_value=100, step=5)},
            disabled=['topic_id','subject','topic'], key='tn_progress_editor')
        if st.button('🔄 Recalculate using updated progress', key='tn_recalculate'):
            try:
                new_progress = edited_progress[['topic_id','completion']].copy()
                updated_analysis, updated_missing, updated_cycles = planner_analyse(
                    st.session_state['tn_plan_analysis'].drop(columns=['prerequisites_list','difficulty_score','remaining_hours','priority_score','sequence'], errors='ignore'),
                    new_progress
                )
                updated_timetable = planner_make_timetable(updated_analysis, plan_start, exam_date, daily_hours, study_days, study_start_time, session_minutes, break_minutes)
                st.session_state['tn_plan_analysis'] = updated_analysis
                st.session_state['tn_plan_timetable'] = updated_timetable
                st.session_state['tn_plan_missing'] = updated_missing
                st.session_state['tn_plan_cycles'] = updated_cycles
                st.session_state['tn_plan_progress'] = new_progress
                st.success('Progress saved for this app session. Your priority scores and timetable have been recalculated.')
                st.rerun()
            except Exception as exc:
                st.error(f'Could not update progress: {exc}')
        st.download_button('⬇️ Download current progress CSV', analysed[['topic_id','completion']].to_csv(index=False).encode('utf-8'), 'technova_updated_progress.csv', 'text/csv')
        st.markdown('#### 4. Gemini learning recommendations (optional)')
        if st.button('✨ Get AI study recommendations', key='tn_ai_recommendations'):
            payload = analysed[['topic_id','subject','topic','difficulty','completion','remaining_hours','importance','priority_score','prerequisites']].to_dict(orient='records')
            prompt = f"""You are TECHNOVA AI, a careful study coach. Based only on this structured curriculum analysis, give concise personalised study recommendations. Identify the top priorities, explain prerequisite order, suggest active-recall/revision methods and a realistic daily routine within {daily_hours} hours/day. Do not change the computed timetable, invent syllabus facts, or claim unsupported marks predictions. Return clear Markdown.\n\nCURRICULUM DATA:\n{json.dumps(payload, ensure_ascii=False, default=str)}"""
            with st.spinner('Preparing recommendations...'):
                recommendation, ai_error = ask_ai(prompt, 1800)
            if ai_error:
                st.warning(ai_error + ' The rule-based timetable and priority analysis remain available.')
            else:
                st.markdown(recommendation)
        st.caption('Method note: priority is a transparent heuristic using importance, difficulty, completion gap and remaining estimated hours. It is not a validated prediction of exam marks. Prerequisites determine topic ordering; review the warnings and uploaded data for accuracy.')
    else:
        st.markdown('#### Try the built-in sample')
        st.dataframe(pd.DataFrame(SAMPLE_CURRICULUM), use_container_width=True, hide_index=True)
        st.download_button('⬇️ Download sample curriculum JSON', json.dumps({'topics':SAMPLE_CURRICULUM}, indent=2).encode('utf-8'), 'sample_engineering_curriculum.json', 'application/json')
        st.download_button('⬇️ Download sample progress CSV', 'topic_id,completion\nMATH-01,100\nPROG-01,80\nAI-01,40\n'.encode('utf-8'), 'sample_student_progress.csv', 'text/csv')


# ------------------------- FOOTER ----------------------------

st.divider()
st.markdown("""
<div style="text-align:center; padding:12px;">
  <h3>🚀 TECHNOVA AI</h3>
  <p>Your Personal AI Learning Companion</p>
  <small style="color:#c4b5fd;">Learn • Visualise • Practise • Plan • Succeed</small>
</div>
""", unsafe_allow_html=True)
