import streamlit as st
import json
import re
import html
import urllib.parse
import urllib.request
import base64
import time
from pathlib import Path
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

.nova-mascot {{
    position: fixed; right: 22px; bottom: 22px; z-index: 999;
    width: 104px; text-align: center; padding: 10px 8px;
    border-radius: 22px; color: #fff; font-size: 12px;
    background: linear-gradient(145deg, rgba(91,33,182,.96), rgba(30,10,60,.96));
    border: 1px solid #d8b4fe; box-shadow: 0 0 22px rgba(168,85,247,.55);
    animation: nova-float 2.8s ease-in-out infinite;
}}
.nova-mascot .face {{ font-size: 38px; display:block; line-height:1.2; }}
@keyframes nova-float {{ 0%,100% {{ transform: translateY(0) rotate(-2deg); }} 50% {{ transform: translateY(-10px) rotate(2deg); }} }}
.mascot-note {{
    border: 1px solid rgba(216,180,254,.45); background: rgba(49,20,83,.78);
    border-radius: 12px; padding: 8px 12px; margin: 8px 0 14px;
    color: #f3e8ff; font-size: .9rem;
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
    """Render a colourful, notebook-inspired radial mind map with readable text."""
    branches = branches[:6] if isinstance(branches, list) else []
    width, height = 1100, 760
    cx, cy = 550, 375
    positions = [
        (275, 155), (825, 155), (275, 585),
        (825, 585), (550, 105), (550, 645)
    ]
    palette = [
        ("#fff1c7", "#d97706"), ("#dff4ff", "#0284c7"),
        ("#e5f8df", "#16a34a"), ("#fce4f2", "#db2777"),
        ("#eee7ff", "#7c3aed"), ("#dcfafa", "#0f766e")
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="Colourful educational mind map">'
    ]
    # soft paper background and decorative dots
    parts.append(f'<rect x="8" y="8" width="{width-16}" height="{height-16}" rx="28" fill="#fffdf7" stroke="#e7d9bd" stroke-width="3"/>')
    for x, y in [(45,45),(1050,45),(45,710),(1050,710)]:
        parts.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#f5c76b"/>')
    for i, branch in enumerate(branches):
        if isinstance(branch, dict):
            title = str(branch.get("title", f"Branch {i+1}"))[:48]
            children = branch.get("points", [])
        else:
            title, children = str(branch)[:48], []
        x, y = positions[i]
        fill, stroke = palette[i]
        # connector goes behind the branch card
        parts.append(f'<path d="M{cx} {cy} Q{(cx+x)//2} {(cy+y)//2} {x} {y}" '
                     f'stroke="{stroke}" stroke-width="7" stroke-linecap="round" fill="none" opacity=".78"/>')
        bx, by, bw, bh = x-175, y-76, 350, 152
        parts.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="25" fill="{fill}" stroke="{stroke}" stroke-width="3"/>')
        parts.append(f'<path d="M{bx+18} {by+16} Q{bx+80} {by-1} {bx+145} {by+14}" stroke="white" stroke-width="5" fill="none" opacity=".8"/>')
        parts.append(f'<text x="{x}" y="{by+37}" text-anchor="middle" font-size="23" font-weight="bold" font-family="Arial" fill="#29234a">{html.escape(title)}</text>')
        for j, point in enumerate(children[:3]):
            py = by + 72 + j*23
            label = str(point)[:43]
            parts.append(f'<text x="{bx+22}" y="{py}" font-size="16" font-family="Arial" fill="#403b50">• {html.escape(label)}</text>')
    parts.append(f'<rect x="385" y="315" width="330" height="120" rx="38" fill="#5b21b6" stroke="#3b0764" stroke-width="5"/>')
    parts.append(f'<text x="550" y="365" text-anchor="middle" font-size="25" font-weight="bold" font-family="Arial" fill="white">{html.escape(str(center)[:34])}</text>')
    parts.append('<text x="550" y="400" text-anchor="middle" font-size="16" font-family="Arial" fill="#f3e8ff">TECHNOVA • CONNECT THE IDEAS</text>')
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


# ------------------------- LIVE CURRENT-AFFAIRS SOURCE -------------------------

@st.cache_data(ttl=900, show_spinner=False)
def fetch_current_affairs(category, period, country="India"):
    """Fetch dated headlines from Google News RSS; never fabricate news."""
    import xml.etree.ElementTree as ET
    from datetime import datetime, timedelta, timezone
    from email.utils import parsedate_to_datetime

    query_map = {
        "National": "India national news government",
        "International": "world international affairs",
        "Government schemes & policy": "India government scheme policy ministry",
        "Economy & RBI": "India economy RBI finance",
        "Science & technology": "India science technology ISRO",
        "Environment & climate": "India environment climate",
        "Defence & security": "India defence security",
        "Awards & appointments": "India awards appointments",
        "Karnataka affairs": "Karnataka state government news",
        "All categories": "India current affairs"
    }
    query = query_map.get(category, "India current affairs")
    if country == "World":
        query = "world " + category.lower() + " current affairs"
    params = {"q": query, "hl": "en-IN", "gl": "IN", "ceid": "IN:en"}
    rss_url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0 TECHNOVA-AI/2.0"})
    with urllib.request.urlopen(req, timeout=12) as response:
        root = ET.fromstring(response.read())
    now = datetime.now(timezone.utc)
    if period == "Today":
        cutoff = now - timedelta(days=1)
    elif period == "This week":
        cutoff = now - timedelta(days=7)
    elif period == "This month":
        cutoff = now - timedelta(days=30)
    else:
        cutoff = now - timedelta(days=365)
    items = []
    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        pubdate = item.findtext("pubDate", "").strip()
        source_node = item.find("source")
        publisher = source_node.text.strip() if source_node is not None and source_node.text else "Publisher not specified"
        try:
            published = parsedate_to_datetime(pubdate)
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
        except Exception:
            published = None
        if title and link and published and published >= cutoff:
            items.append({
                "title": title,
                "link": link,
                "publisher": publisher,
                "published": published.strftime("%d %b %Y, %I:%M %p UTC")
            })
        if len(items) >= 25:
            break
    return items

# ------------------------- HEADER -------------------------

st.markdown("""
<div class="hero">
  <h1>🚀 TECHNOVA AI</h1>
  <p>Your colourful AI learning companion — understand, visualise, practise and succeed.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""<div class="nova-mascot"><span class="face">🤖</span><b>TECHNOVA AI</b><br>built by Ruchita</div>""", unsafe_allow_html=True)

# ------------------------- LEARNING INPUTS -------------------------

COURSE_OPTIONS = {
    "School (Classes 6–10)": {
        "courses": ["Class 6", "Class 7", "Class 8", "Class 9", "Class 10"],
        "specialisations": ["CBSE", "ICSE", "Karnataka State Board", "Other State Board"]
    },
    "Higher Secondary (Classes 11–12)": {
        "courses": ["Class 11 / 1st PUC", "Class 12 / 2nd PUC"],
        "specialisations": ["Science (PCMB)", "Science (PCMC)", "Commerce", "Arts / Humanities"]
    },
    "Entrance Exams (After Class 12)": {
        "courses": ["KCET", "JEE Main", "JEE Advanced / IIT-JEE", "NEET UG", "COMEDK UGET",
                    "CUET UG", "NATA", "CLAT", "AILET", "NDA", "Other entrance exam"],
        "specialisations": ["Physics", "Chemistry", "Mathematics", "Biology", "PCMB", "PCMC",
                            "English", "General Aptitude", "Logical Reasoning", "Exam-specific"]
    },
    "UPSC & State Civil Services": {
        "courses": ["UPSC Civil Services (CSE)", "KPSC KAS", "UPSC CAPF",
                    "Indian Forest Service (IFoS)", "Other civil service exam"],
        "specialisations": ["General Studies", "CSAT", "History", "Geography", "Indian Polity",
                            "Economy", "Environment and Ecology", "Science and Technology",
                            "Ethics", "Current Affairs", "Essay", "Optional subject"]
    },
    "Other Competitive Exams": {
        "courses": ["SSC CGL", "SSC CHSL", "SSC MTS", "IBPS / SBI Banking", "Railway (RRB)",
                    "Defence (NDA / CDS / AFCAT)", "CUET", "CTET / State TET",
                    "Other competitive exam"],
        "specialisations": ["Quantitative Aptitude", "Logical Reasoning", "Verbal Ability",
                            "English", "General Awareness", "General Studies", "General Science",
                            "Computer Knowledge", "Current Affairs", "Subject-specific"]
    }
}

SUBJECTS_BY_AREA = {
    "School (Classes 6–10)": ["Mathematics", "Science", "Social Science", "English", "Kannada", "Hindi", "Computer Science", "Other"],
    "Higher Secondary (Classes 11–12)": ["Physics", "Chemistry", "Mathematics", "Biology", "Computer Science", "Accountancy", "Business Studies", "Economics", "English", "Other"],
    "Entrance Exams (After Class 12)": ["Physics", "Chemistry", "Mathematics", "Biology", "English", "General Aptitude", "Logical Reasoning", "Other"],
    "UPSC & State Civil Services": ["General Studies", "CSAT", "History", "Geography", "Polity", "Economy", "Environment", "Science and Technology", "Ethics", "Current Affairs", "Essay", "Optional Subject", "Other"],
    "Other Competitive Exams": ["Quantitative Aptitude", "Reasoning", "English", "General Awareness", "General Science", "Computer Knowledge", "Current Affairs", "Exam-specific subject", "Other"]
}

with st.sidebar:
    st.header("📚 Learning setup")
    level = st.selectbox("Choose your course category", list(COURSE_OPTIONS.keys()))
    course_choice = st.selectbox("Choose course / programme / exam", COURSE_OPTIONS[level]["courses"])
    course = st.text_input("Enter your course or exam name", "") if course_choice.startswith("Other") else course_choice
    specialisation_choice = st.selectbox("Stream / branch / specialisation", COURSE_OPTIONS[level]["specialisations"])
    specialisation = st.text_input("Enter your specialisation", "") if specialisation_choice == "Other" else specialisation_choice
    subject_choices = SUBJECTS_BY_AREA[level]
    subject_choice = st.selectbox("Choose subject", subject_choices)
    subject = st.text_input("Enter your subject", "") if subject_choice == "Other" else subject_choice
    topic = st.text_input("Chapter / topic", placeholder="e.g. Human heart, Indian Constitution, Intelligent Agents")
    language = st.selectbox("Language", ["Simple English", "Kannada", "Hindi"])
    detail_level = st.selectbox("Content depth", ["Short", "Medium", "Detailed"], index=1)
    st.markdown("---")
    st.caption("Choose your course, programme, stream and subject. You can enter any chapter or topic.")

ready = bool(subject and subject.strip() and topic and topic.strip())

if not ready:
    st.info("👈 Choose your course and subject, then enter a chapter/topic in the sidebar to begin.")
else:
    st.success(f"Ready to learn: **{course} · {specialisation} · {subject} → {topic}**")

# ------------------------- MAIN TABS -------------------------

tab_notes, tab_visual, tab_exam, tab_textbook, tab_quiz, tab_doubt, tab_history, tab_current = st.tabs([
    "📝 Colourful Notes",
    "🎨 Visual Learning",
    "📖 Exam Preparation",
    "📘 Textbook & PYQs",
    "🎯 Mock Test",
    "💬 Doubt Solver",
    "🕘 Previous Topics",
    "📰 Current Affairs"
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
    st.markdown("""<div class="mascot-note">🦊 <b>Nova says:</b> Small steps today become big achievements tomorrow.</div>""", unsafe_allow_html=True)
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
    st.markdown("""<div class="mascot-note">🐼 <b>Nova says:</b> Turn difficult ideas into pictures your memory can keep.</div>""", unsafe_allow_html=True)
    st.subheader("🎨 Pictorial learning studio")
    st.write("Create colourful, notebook-inspired visual maps for a topic or an entire chapter, plus flowcharts and reference images.")
    st.caption("Mind maps are generated from AI-structured study content and rendered as SVG so labels stay readable. Cross-check important facts with your prescribed textbook.")
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
        mindmap_mode = st.selectbox(
            "Mind-map type",
            ["Topic-wise mind map", "Complete chapter mind map"],
            key="mindmap_mode"
        )
        if st.button("🌳 Generate illustrated mind map", key="mind", disabled=not ready):
            scope_instruction = (
                "Cover the selected topic only, with its key concepts and sub-concepts."
                if mindmap_mode == "Topic-wise mind map"
                else "Create a chapter-wide revision map covering the chapter's major sections, key concepts, definitions, formulas, diagrams to remember and important connections. Do not claim exhaustive textbook coverage if the chapter scope is unclear."
            )
            prompt = common_context(f"""
Return ONLY valid JSON with this structure:
{{"center":"main topic","branches":[{{"title":"branch name","points":["short point 1","short point 2","short point 3"]}}]}}
{scope_instruction}
Create 4 to 6 meaningful branches, each with 2 to 3 concise points.
Include relevant definitions, formulas, processes, diagram labels, real-life examples and memorable study tricks where they genuinely apply.
Adapt the content to the selected class or exam (for example, NEET biology, JEE physics/mathematics, UPSC analytical topics).
Keep every statement factually correct and avoid unrelated concepts. Make labels short enough to fit a colourful visual mind map.
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
        mindmap_svg = svg_mindmap(data.get("center", topic), data.get("branches", []))
        st.markdown(mindmap_svg, unsafe_allow_html=True)
        st.download_button("⬇️ Download mind map (SVG)", data=mindmap_svg, file_name="TECHNOVA_AI_Mind_Map.svg", mime="image/svg+xml")
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
    st.markdown("""<div class="mascot-note">🦉 <b>Nova says:</b> Understand the concept first; then practise with confidence.</div>""", unsafe_allow_html=True)
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
    st.markdown("""<div class="mascot-note">🐰 <b>Nova says:</b> Check the textbook, question the details, and learn deeply.</div>""", unsafe_allow_html=True)
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
    st.markdown("""<div class="mascot-note">🐯 <b>Nova says:</b> Every question is a chance to grow stronger.</div>""", unsafe_allow_html=True)
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
    st.markdown("""<div class="mascot-note">🐱 <b>Nova says:</b> Curiosity is a superpower. Ask every question.</div>""", unsafe_allow_html=True)
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
    st.markdown("""<div class="mascot-note">🐻 <b>Nova says:</b> Look how far you have come. Keep going.</div>""", unsafe_allow_html=True)
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


# ========================= LIVE CURRENT AFFAIRS ==============

with tab_current:
    st.subheader("📰 Live Current Affairs")
    st.caption("Fresh headlines retrieved from Google News RSS. Each item includes its publisher, publication date and source link. Headlines are not a substitute for checking official notifications.")
    c1, c2, c3 = st.columns(3)
    with c1:
        news_scope = st.selectbox("Coverage", ["India", "World"], key="news_scope")
    with c2:
        news_period = st.selectbox("Time period", ["Today", "This week", "This month", "Previous year"], key="news_period")
    with c3:
        news_category = st.selectbox(
            "Category",
            ["All categories", "National", "International", "Government schemes & policy",
             "Economy & RBI", "Science & technology", "Environment & climate",
             "Defence & security", "Awards & appointments", "Karnataka affairs"],
            key="news_category"
        )
    exam_filter = st.selectbox(
        "Prepare these headlines for",
        ["General awareness", "UPSC / KPSC", "KCET", "JEE", "NEET", "COMEDK / CUET", "SSC / Banking / Railway"],
        key="news_exam_filter"
    )
    if st.button("🔄 Fetch latest current affairs", key="fetch_news"):
        try:
            with st.spinner("Fetching dated headlines..."):
                fetched = fetch_current_affairs(news_category, news_period, news_scope)
            st.session_state["current_affairs_items"] = fetched
            st.session_state["current_affairs_error"] = ""
        except Exception as exc:
            st.session_state["current_affairs_error"] = str(exc)[:250]
            st.session_state["current_affairs_items"] = []

    if st.session_state.get("current_affairs_error"):
        st.error("Live news could not be retrieved right now. Please try again later. Details: " + st.session_state["current_affairs_error"])
    news_items = st.session_state.get("current_affairs_items", [])
    if news_items:
        st.success(f"Retrieved {len(news_items)} dated headlines. Verify important facts with the official source before using them in an exam answer.")
        for idx, item in enumerate(news_items, 1):
            with st.container(border=True):
                st.markdown(f"**{idx}. {html.escape(item['title'])}**")
                st.caption(f"{item['publisher']} · Published {item['published']}")
                st.markdown(f"[Read source article]({item['link']})")
        if ready and st.button("🧠 Make exam-focused revision notes from these headlines", key="news_revision"):
            headlines = "\\n".join(
                f"- {x['title']} | {x['publisher']} | {x['published']} | {x['link']}"
                for x in news_items[:20]
            )
            news_prompt = f"""
You are an exam-current-affairs tutor. Use ONLY the dated headline information below as source material.
Target exam: {exam_filter}
Student's selected subject: {subject}
Preferred language: {language}
Create concise revision notes. Do not invent missing facts, dates, figures, government scheme details or outcomes.
For each headline, state what the headline explicitly says, why it may matter for the selected exam, and what must be verified from the linked article/official source.
If a headline alone is insufficient to support a fact, clearly say "Open the source article to verify details."
Then create 5 practice MCQs based only on supported information. Mark uncertain items as not suitable for a factual quiz.
HEADLINES:
{headlines}
"""
            with st.spinner("Preparing source-grounded revision notes..."):
                revision, revision_error = ask_ai(news_prompt, 3000)
            if revision_error:
                show_error(revision_error)
            else:
                st.session_state["news_revision_notes"] = revision
    if st.session_state.get("news_revision_notes"):
        st.markdown("### 📚 Exam-focused revision")
        st.markdown(st.session_state["news_revision_notes"])
        show_download(st.session_state["news_revision_notes"], "TECHNOVA_Current_Affairs_Revision.md")
    elif not news_items:
        st.info("Tap “Fetch latest current affairs” to load headlines. The feed is fetched live when requested and cached for 15 minutes.")

# ------------------------- FOOTER ----------------------------

st.divider()
st.markdown("""
<div style="text-align:center; padding:12px;">
  <h3>🚀 TECHNOVA AI</h3>
  <p>Your Personal AI Learning Companion</p>
  <p style="color:#db2777; font-weight:700;">❤️ Built with Love by Ruchita</p>
  <small style="color:#64748b;">Learn • Visualise • Practise • Succeed</small>
</div>
""", unsafe_allow_html=True)
