import streamlit as st
import json
import re
import html
import urllib.parse
import urllib.request
import base64
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
bg_path = Path(__file__).parent / "file_00000000a1148208ac1acae3470dd546.png"

if bg_path.exists():
    with open(bg_path, "rb") as img:
        bg_encoded = base64.b64encode(img.read()).decode()
else:
    st.warning("Background image not found!")
    bg_encoded = ""
# ------------------------- DESIGN -------------------------

st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Kalam:wght@400;700&family=Poppins:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Poppins', sans-serif;
}}

.stApp {{
    background-image:
    linear-gradient(
        rgba(5, 0, 20, 0.65),
        rgba(5, 0, 20, 0.75)
    ),
    url("data:image/png;base64,{bg_encoded}");

    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
}}

[data-testid="stHeader"] {{
    background: rgba(5, 0, 20, 0.35);
}}

[data-testid="stSidebar"] {{
    background: rgba(12, 4, 30, 0.95);
}}

h1, h2, h3 {{
    color: #e6ccff;
}}

.hero {{
    padding: 28px;
    border-radius: 22px;
    background: linear-gradient(
        110deg,
        rgba(20, 0, 45, 0.92),
        rgba(75, 0, 130, 0.85),
        rgba(130, 50, 220, 0.75)
    );
    color: white;
    margin-bottom: 20px;
    border: 1px solid #b76aff;
    box-shadow: 0 0 22px rgba(160, 70, 255, 0.5);
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
    background: rgba(25, 12, 45, 0.92);
    border-left: 7px solid #b76aff;
    border-radius: 14px;
    padding: 22px 24px;
    color: #f5eaff;
    box-shadow: 0 5px 20px rgba(130, 50, 220, 0.2);
    font-family: 'Kalam', cursive;
    line-height: 1.9;
}}

.note-paper h1,
.note-paper h2,
.note-paper h3 {{
    font-family: 'Kalam', cursive;
    color: #d8aaff;
}}

.tip {{
    background: rgba(90, 55, 10, 0.85);
    border-left: 5px solid #eab308;
    border-radius: 10px;
    padding: 12px 15px;
    margin: 10px 0;
    color: #fff0bd;
}}

.definition {{
    background: rgba(25, 45, 85, 0.88);
    border-left: 5px solid #60a5fa;
    border-radius: 10px;
    padding: 12px 15px;
    margin: 10px 0;
    color: #dbeafe;
}}

.success-card {{
    background: rgba(15, 65, 45, 0.88);
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
    box-shadow: 0 0 12px rgba(147, 51, 234, 0.4);
}}

div.stButton > button:hover {{
    color: white;
    border: 1px solid #e9d5ff;
    box-shadow: 0 0 20px #9333ea;
}}

</style>
""", unsafe_allow_html=True)

# ------------------------- API CLIENT -------------------------
@st.cache_resource
def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY", "")

    if not api_key:
        return None

    retry_options = types.HttpRetryOptions(
        attempts=4,
        initial_delay=2.0,
        max_delay=8.0,
        exp_base=2.0,
        jitter=0.0,
        http_status_codes=[503]
    )

    http_options = types.HttpOptions(
        retry_options=retry_options
    )

    return genai.Client(
        api_key=api_key,
        http_options=http_options
    )

client = get_client()

client = get_client()
def ask_ai(prompt, max_tokens=3500, json_mode=False):

    if client is None:
        return None, (
            "Gemini API key is missing. "
            "Please configure GEMINI_API_KEY in Streamlit Secrets."
        )

    try:

        config = types.GenerateContentConfig(
            temperature=0.35,
            max_output_tokens=max_tokens,
            response_mime_type=(
                "application/json" if json_mode else "text/plain"
            )
        )

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=config
        )

        answer = response.text or ""

        if not answer.strip():
            return None, (
                "The AI returned an empty response. "
                "Please try again."
            )

        return answer, None

    except Exception as exc:

        error_code = getattr(exc, "code", None)
        message = str(exc)

        if error_code == 503 or "503" in message or "UNAVAILABLE" in message:

            return None, (
                "✨ TECHNOVA AI is experiencing high demand right now. "
                "We tried processing your request several times, "
                "but Gemini is temporarily unavailable. "
                "Please wait a little and try again."
            )

        if error_code == 429 or "429" in message or "RESOURCE_EXHAUSTED" in message:

            return None, (
                "⚡ AI request limit reached. "
                "Please wait before trying again."
            )

        if error_code == 404 or "404" in message or "NOT_FOUND" in message:

            return None, (
                f"Model '{MODEL}' is unavailable. "
                "Please check your Gemini model configuration."
            )

        return None, (
            "Something went wrong while generating your content. "
            "Please try again later."
        )

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

COURSE_OPTIONS = {
    "School (Classes 6–10)": {
        "courses": ["Class 6", "Class 7", "Class 8", "Class 9", "Class 10"],
        "specialisations": ["General curriculum", "CBSE", "ICSE", "State Board", "Other board"]
    },
    "PU / Higher Secondary": {
        "courses": ["1st PUC / Class 11", "2nd PUC / Class 12"],
        "specialisations": ["Science (PCMB)", "Science (PCMC)", "Commerce", "Arts / Humanities", "JEE Main", "JEE Advanced", "NEET UG", "KCET", "COMEDK", "CUET UG", "Other entrance exam"]
    },
    "Degree – Undergraduate": {
        "courses": ["BA", "BSc", "BCom", "BBA", "BCA", "BSW", "BEd", "BPEd", "BE / BTech", "BArch", "BDes", "BFA", "BHM", "BPharm", "PharmD", "BPT", "BOT", "LLB", "BVoc", "Other undergraduate degree"],
        "specialisations": ["General", "Computer Science", "Artificial Intelligence / AIML", "Mathematics", "Physics", "Chemistry", "Biology", "Botany", "Zoology", "Statistics", "Economics", "English", "Kannada", "History", "Political Science", "Psychology", "Sociology", "Commerce", "Accounting and Finance", "Education", "Law", "Architecture", "Design", "Hospitality", "Pharmacy", "Physiotherapy", "Other"]
    },
    "Degree – Postgraduate & Research": {
        "courses": ["MA", "MSc", "MCom", "MBA", "MCA", "MEd", "MTech", "ME", "MSW", "LLM", "MPharm", "MPH", "PhD", "Other postgraduate / research course"],
        "specialisations": ["Computer Science", "Artificial Intelligence / AIML", "Data Science", "Mathematics", "Physics", "Chemistry", "Biology", "Commerce", "Finance", "Economics", "English", "History", "Political Science", "Psychology", "Education", "Social Work", "Law", "Engineering", "Pharmacy", "Public Health", "Other"]
    },
    "Engineering & Polytechnic": {
        "courses": ["Diploma", "BE", "BTech", "ME", "MTech", "Other engineering course"],
        "specialisations": ["AIML", "Computer Science", "Information Science", "Data Science", "Electronics and Communication", "Electrical and Electronics", "Electrical Engineering", "Mechanical", "Civil", "Chemical", "Automobile", "Biotechnology", "Other branch"]
    },
    "Medical & AYUSH": {
        "courses": ["MBBS", "BDS", "BAMS", "BHMS", "BUMS", "BSMS", "BNYS", "BVSc & AH", "MD", "MS", "MDS", "Other medical / AYUSH course"],
        "specialisations": ["Anatomy", "Physiology", "Biochemistry", "Pathology", "Pharmacology", "Microbiology", "Forensic Medicine", "Community Medicine", "General Medicine", "General Surgery", "Cardiology", "Neurology", "Dermatology", "Orthopaedics", "Radiology", "Psychiatry", "Obstetrics and Gynaecology", "Paediatrics", "Ophthalmology", "ENT", "Anaesthesiology", "Other"]
    },
    "Nursing & Allied Health": {
        "courses": ["BSc Nursing", "GNM", "ANM", "Post Basic BSc Nursing", "MSc Nursing", "BPT", "BOT", "BMLT", "BSc Radiology / Imaging", "BSc Operation Theatre Technology", "BSc Anaesthesia Technology", "BSc Medical Lab Technology", "Other allied health course"],
        "specialisations": ["Nursing Foundation", "Medical-Surgical Nursing", "Cardiac / Cardiovascular Nursing", "Critical Care Nursing", "Emergency Nursing", "Paediatric Nursing", "Psychiatric / Mental Health Nursing", "Community Health Nursing", "Obstetric and Gynaecological Nursing", "Oncology Nursing", "Neonatal Nursing", "Orthopaedic Nursing", "Anatomy and Physiology", "Nutrition", "Pharmacology", "Other"]
    },
    "UPSC & State Civil Services": {
        "courses": ["UPSC Civil Services (CSE)", "KPSC KAS", "UPSC CAPF", "Indian Forest Service (IFoS)", "Other civil service exam"],
        "specialisations": ["General Studies", "CSAT", "History", "Geography", "Indian Polity", "Economy", "Environment and Ecology", "Science and Technology", "Ethics", "Current Affairs", "Essay", "Optional subject", "Other"]
    },
    "Other Competitive & Entrance Exams": {
        "courses": ["SSC CGL", "SSC CHSL", "SSC MTS", "Banking (IBPS / SBI)", "Railway (RRB)", "Defence (NDA / CDS / AFCAT)", "GATE", "