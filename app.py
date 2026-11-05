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
        "courses": ["SSC CGL", "SSC CHSL", "SSC MTS", "Banking (IBPS / SBI)", "Railway (RRB)", "Defence (NDA / CDS / AFCAT)", "GATE", "CAT", "MAT", "XAT", "UGC NET", "KSET", "CTET", "State TET", "CLAT", "AILET", "NATA", "CUET PG", "NEET PG", "INI-CET", "Other competitive exam"],
        "specialisations": ["Quantitative Aptitude", "Logical Reasoning", "Verbal Ability", "English", "General Awareness", "General Studies", "General Science", "Computer Knowledge", "Current Affairs", "Subject-specific preparation", "Other"]
    }
}

SUBJECTS_BY_AREA = {
    "School (Classes 6–10)": ["Mathematics", "Science", "Social Science", "English", "Kannada", "Hindi", "Computer Science", "Other"],
    "PU / Higher Secondary": ["Physics", "Chemistry", "Mathematics", "Biology", "Computer Science", "Accountancy", "Business Studies", "Economics", "English", "Other"],
    "Degree – Undergraduate": ["English", "Kannada", "History", "Political Science", "Economics", "Psychology", "Sociology", "Education", "Mathematics", "Physics", "Chemistry", "Botany", "Zoology", "Statistics", "Computer Science", "Commerce", "Accounting", "Law", "Architecture", "Design", "Pharmacy", "Physiotherapy", "Other"],
    "Degree – Postgraduate & Research": ["English", "History", "Political Science", "Economics", "Psychology", "Education", "Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "Data Science", "Commerce", "Finance", "Law", "Engineering", "Pharmacy", "Public Health", "Research Methodology", "Other"],
    "Engineering & Polytechnic": ["Engineering Mathematics", "Applied Physics", "Applied Chemistry", "Programming", "Artificial Intelligence", "Machine Learning", "Data Structures and Algorithms", "Python Programming", "Java Programming", "C Programming", "Database Management", "Operating Systems", "Computer Networks", "Electronics", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Other"],
    "Medical & AYUSH": ["Anatomy", "Physiology", "Biochemistry", "Pathology", "Pharmacology", "Microbiology", "Forensic Medicine", "Community Medicine", "General Medicine", "Surgery", "Obstetrics and Gynaecology", "Paediatrics", "Other"],
    "Nursing & Allied Health": ["Nursing Foundation", "Anatomy and Physiology", "Nutrition", "Medical-Surgical Nursing", "Child Health Nursing", "Mental Health Nursing", "Community Health Nursing", "Midwifery", "Pharmacology", "Critical Care", "Cardiovascular Nursing", "Other"],
    "UPSC & State Civil Services": ["General Studies", "CSAT", "History", "Geography", "Polity", "Economy", "Environment", "Science and Technology", "Ethics", "Current Affairs", "Essay", "Optional Subject", "Other"],
    "Other Competitive & Entrance Exams": ["Quantitative Aptitude", "Reasoning", "English", "General Awareness", "General Science", "Computer Knowledge", "Current Affairs", "Exam-specific subject", "Other"]
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

tab_notes, tab_visual, tab_exam, tab_textbook, tab_quiz, tab_doubt, tab_history = st.tabs([
    "📝 Colourful Notes",
    "🎨 Visual Learning",
    "📖 Exam Preparation",
    "📘 Textbook & PYQs",
    "🎯 Mock Test",
    "💬 Doubt Solver",
    "🕘 Previous Topics"
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


