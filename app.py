import streamlit as st
import json
import re
import html
import urllib.parse
import urllib.request
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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Kalam:wght@400;700&family=Poppins:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #fff9f1 0%, #f4f6ff 55%, #fdf2f8 100%);
}
h1, h2, h3 { color: #30245f; }
.hero {
    padding: 24px 26px;
    border-radius: 22px;
    background: linear-gradient(110deg, #4338ca, #7c3aed, #db2777);
    color: white;
    margin-bottom: 18px;
}
.hero h1 { color: white; margin: 0; font-size: 2.25rem; }
.hero p { color: #f5eaff; margin: 6px 0 0 0; }
.note-paper {
    background: repeating-linear-gradient(#fffef9 0px, #fffef9 31px, #dbeafe 32px);
    border-left: 7px solid #f472b6;
    border-radius: 14px;
    padding: 22px 24px;
    color: #29234a;
    box-shadow: 0 5px 18px rgba(60,40,100,.08);
    font-family: 'Kalam', 'Comic Sans MS', cursive;
    line-height: 1.9;
}
.note-paper h1, .note-paper h2, .note-paper h3 {
    font-family: 'Kalam', 'Comic Sans MS', cursive;
    color: #6d28d9;
}
.tip {
    background: #fff1b8;
    border-left: 5px solid #eab308;
    border-radius: 10px;
    padding: 12px 15px;
    margin: 10px 0;
    color: #513b00;
}
.definition {
    background: #e0f2fe;
    border-left: 5px solid #0284c7;
    border-radius: 10px;
    padding: 12px 15px;
    margin: 10px 0;
    color: #123b55;
}
.success-card {
    background: #dcfce7;
    border-left: 5px solid #16a34a;
    border-radius: 10px;
    padding: 12px 15px;
    color: #14532d;
}
.small-muted { color: #64748b; font-size: .9rem; }
div.stButton > button {
    border-radius: 12px;
    border: 0;
    min-height: 44px;
    background: linear-gradient(90deg, #4f46e5, #9333ea);
    color: white;
    font-weight: 600;
}
div.stButton > button:hover { color: white; border: 1px solid #312e81; }
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
    if client is None:
        return None, "Gemini API key is missing. Add GEMINI_API_KEY in Streamlit Cloud → App settings → Secrets."
    try:
        config = types.GenerateContentConfig(
            temperature=0.35,
            max_output_tokens=max_tokens,
            response_mime_type="application/json" if json_mode else "text/plain"
        )
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
        if "429" in message or "RESOURCE_EXHAUSTED" in message:
            return None, "Gemini API limit reached. Wait a little and try again."
        if "404" in message or "NOT_FOUND" in message:
            return None, f"Model '{MODEL}' was not found for this API key. Update MODEL in app.py to a model available in your Gemini account."
        return None, f"Gemini request failed: {message[:500]}"

def parse_json(text):
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
def search_wikimedia_images(search_term, limit=4):
    query = urllib.parse.urlencode({
        "action": "query",
        "generator": "search",
        "gsrsearch": f"filetype:bitmap {search_term}",
        "gsrnamespace": 6,
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 600,
        "format": "json"
    })
    url = "https://commons.wikimedia.org/w/api.php?" + query
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "TECHNOVA-AI-Educational-App/1.0 (student project)"}
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        data = json.loads(response.read().decode("utf-8"))
    pages = data.get("query", {}).get("pages", {})
    results = []
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        image_url = info.get("thumburl") or info.get("url")
        if image_url:
            results.append({
                "title": page.get("title", "Educational image").replace("File:", ""),
                "url": image_url,
                "source": info.get("descriptionurl", "https://commons.wikimedia.org/")
            })
    return results
# =========================================================
# COURSE CATALOGUE
# =========================================================

COURSES = {
    "School (Classes 6–10)": [
        "Class 6", "Class 7", "Class 8", "Class 9", "Class 10",
        "CBSE", "ICSE", "Karnataka State Board", "Other State Board"
    ],
    "PUC / Intermediate": [
        "1st PUC PCMB", "1st PUC PCMC", "1st PUC Commerce",
        "1st PUC Arts", "2nd PUC PCMB", "2nd PUC PCMC",
        "2nd PUC Commerce", "2nd PUC Arts"
    ],
    "Entrance Examinations": [
        "JEE Main", "JEE Advanced", "NEET UG", "KCET",
        "COMEDK", "CUET", "CLAT", "NATA", "NIFT",
        "BITSAT", "AIMS", "Other Entrance Exam"
    ],
    "Degree Courses": [
        "BA", "BSc", "BCom", "BBA", "BCA", "BEd",
        "BSW", "BPharm", "BPT", "LLB", "BArch",
        "BVSc", "BDes", "Other Degree"
    ],
    "Postgraduate Courses": [
        "MA", "MSc", "MCom", "MBA", "MCA", "MEd",
        "MTech", "MPharm", "LLM", "MSW", "PhD",
        "Other Postgraduate Course"
    ],
    "Engineering": [
        "BE", "BTech", "Diploma Engineering",
        "MTech", "ME", "Other Engineering Course"
    ],
    "Medical": [
        "MBBS", "BDS", "BAMS", "BHMS", "BUMS",
        "BSMS", "MD", "MS", "DM", "MCh"
    ],
    "Nursing": [
        "ANM", "GNM", "BSc Nursing",
        "Post Basic BSc Nursing", "MSc Nursing",
        "Nurse Practitioner", "Other Nursing Course"
    ],
    "UPSC and Civil Services": [
        "UPSC Civil Services", "IAS Preparation",
        "IPS Preparation", "IFS Preparation",
        "KPSC KAS", "CAPF", "Indian Forest Service"
    ],
    "Other Competitive Exams": [
        "SSC CGL", "SSC CHSL", "SSC MTS",
        "IBPS PO", "IBPS Clerk", "SBI PO", "SBI Clerk",
        "RRB NTPC", "RRB Group D", "NDA", "CDS",
        "AFCAT", "GATE", "CAT", "MAT", "CMAT",
        "UGC NET", "KSET", "CTET", "TET",
        "Other Competitive Exam"
    ]
}

ENGINEERING_BRANCHES = [
    "Computer Science Engineering",
    "Artificial Intelligence and Machine Learning",
    "Artificial Intelligence and Data Science",
    "Information Science",
    "Information Technology",
    "Electronics and Communication",
    "Electrical and Electronics",
    "Mechanical Engineering",
    "Civil Engineering",
    "Biotechnology",
    "Chemical Engineering",
    "Automobile Engineering",
    "Other Branch"
]

MEDICAL_SPECIALISATIONS = [
    "General Medicine", "Cardiology", "Neurology",
    "Dermatology", "Paediatrics", "Orthopaedics",
    "Gynaecology", "Oncology", "Radiology",
    "Anaesthesiology", "Psychiatry", "Surgery",
    "Other Specialisation"
]

NURSING_SPECIALISATIONS = [
    "Medical Surgical Nursing", "Community Health Nursing",
    "Child Health Nursing", "Mental Health Nursing",
    "Obstetrics and Gynaecological Nursing",
    "Critical Care Nursing", "Cardiac Nursing",
    "Oncology Nursing", "Other Specialisation"
]

GENERAL_BRANCHES = [
    "General", "Computer Science", "Mathematics",
    "Physics", "Chemistry", "Biology", "Commerce",
    "Economics", "English", "History", "Political Science",
    "Psychology", "Sociology", "Other"
]

def choose_item(label, options, key):
    selected = st.selectbox(label, options, key=key)
    if selected.startswith("Other"):
        return st.text_input(
            f"Enter your {label.lower()}",
            key=key + "_custom"
        )
    return selected

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">
    <h1>🚀 TECHNOVA AI</h1>
    <p>Your Personal AI Learning Companion</p>
    <p>Learn smarter • Visualise better • Achieve more</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR: STUDENT AND COURSE SELECTION
# =========================================================

st.sidebar.title("🎓 Learning Setup")

category = st.sidebar.selectbox(
    "Select Course Category",
    list(COURSES.keys())
)

course = choose_item(
    "Select Course / Examination",
    COURSES[category],
    "course_select"
)

if category == "Engineering":
    specialisation = choose_item(
        "Select Engineering Branch",
        ENGINEERING_BRANCHES,
        "engineering_branch"
    )
elif category == "Medical":
    specialisation = choose_item(
        "Select Medical Specialisation",
        MEDICAL_SPECIALISATIONS,
        "medical_branch"
    )
elif category == "Nursing":
    specialisation = choose_item(
        "Select Nursing Specialisation",
        NURSING_SPECIALISATIONS,
        "nursing_branch"
    )
elif category in ["School (Classes 6–10)", "PUC / Intermediate"]:
    specialisation = st.sidebar.text_input(
        "Stream / Board (optional)",
        placeholder="Example: PCMB, CBSE"
    )
else:
    specialisation = choose_item(
        "Select Branch / Specialisation",
        GENERAL_BRANCHES,
        "general_branch"
    )

if category in [
    "School (Classes 6–10)",
    "PUC / Intermediate",
    "Engineering",
    "Degree Courses",
    "Postgraduate Courses",
    "Medical",
    "Nursing"
]:
    level = st.sidebar.selectbox(
        "Year / Class / Semester",
        [
            "Class 6", "Class 7", "Class 8", "Class 9", "Class 10",
            "1st PUC", "2nd PUC",
            "1st Year", "2nd Year", "3rd Year", "4th Year",
            "1st Semester", "2nd Semester",
            "3rd Semester", "4th Semester",
            "5th Semester", "6th Semester",
            "7th Semester", "8th Semester",
            "Final Year", "Other"
        ]
    )
else:
    level = st.sidebar.selectbox(
        "Preparation Level",
        ["Beginner", "Intermediate", "Advanced", "Exam Revision"]
    )

if level == "Other":
    level = st.sidebar.text_input("Enter your year / semester")

subject = st.sidebar.text_input(
    "📚 Enter Subject",
    placeholder="Example: Java, Biology, Physics"
)

topic = st.sidebar.text_input(
    "📝 Enter Topic / Chapter",
    placeholder="Example: OOP Concepts"
)

language = st.sidebar.selectbox(
    "🌐 Learning Language",
    ["English", "Kannada", "Hindi"]
)

detail_level = st.sidebar.selectbox(
    "Explanation Style",
    ["Simple and Easy", "Detailed", "Exam Oriented", "Advanced"]
)

st.sidebar.divider()

if st.sidebar.button("🔄 Reset Current Topic"):
    st.session_state.pop("generated_notes", None)
    st.session_state.pop("generated_notes_raw", None)
    st.rerun()

# =========================================================
# VALIDATE INPUT
# =========================================================

if not subject.strip():
    st.info("👈 Select your course and enter a subject to get started.")
    st.stop()

if not topic.strip():
    st.info("👈 Enter a topic or chapter to start learning.")
    st.stop()

# =========================================================
# PREVIOUS TOPICS HISTORY
# =========================================================

if "topic_history" not in st.session_state:
    st.session_state.topic_history = []

current_topic = {
    "category": category,
    "course": course,
    "specialisation": specialisation,
    "level": level,
    "subject": subject,
    "topic": topic
}

if current_topic not in st.session_state.topic_history:
    st.session_state.topic_history.insert(0, current_topic)

st.session_state.topic_history = (
    st.session_state.topic_history[:30]
)

# =========================================================
# DASHBOARD TABS
# =========================================================

tabs = st.tabs([
    "📒 Smart Notes",
    "🧠 Mind Maps",
    "🔀 Flowcharts",
    "🖼️ Topic Images",
    "📝 Exam Preparation",
    "🎯 Mock Tests",
    "💬 Doubt Solver",
    "📚 Previous Topics"
])

# =========================================================
# TAB 1: SMART NOTES
# =========================================================

with tabs[0]:
    st.header("📒 Colourful Digital Notes")

    st.write(
        f"**{subject} → {topic}**"
    )

    if st.button("✨ Generate Smart Notes", key="notes_btn"):
        prompt = common_context("""
Create colourful, well-organised educational notes.

Include:
1. Topic introduction.
2. Important definitions.
3. Main concepts with headings.
4. Step-by-step explanations.
5. Important points.
6. Relevant examples from the selected subject.
7. Diagrams described using text where useful.
8. Important formulas ONLY if relevant.
9. Exam tips.
10. Quick revision summary.
11. Five important questions with answers.

Use Markdown headings, bullets, numbered steps and tables.
Use simple explanations and avoid unrelated content.
""")

        with st.spinner("Preparing your digital notebook..."):
            answer, error = ask_ai(prompt, max_tokens=4500)

        if error:
            show_error(error)
        else:
            st.session_state.generated_notes_raw = answer
            st.session_state.generated_notes = answer

    if st.session_state.get("generated_notes"):
        st.markdown(
            f'<div class="note-paper">{st.session_state.generated_notes}</div>',
            unsafe_allow_html=True
        )
        show_download(
            st.session_state.generated_notes,
            "TECHNOVA_AI_Notes.txt"
        )

# =========================================================
# TAB 2: MIND MAP
# =========================================================

with tabs[1]:
    st.header("🧠 Visual Mind Map")

    if st.button("Generate Colourful Mind Map", key="mind_btn"):
        prompt = common_context("""
Create a mind map for this topic.
Return ONLY valid JSON in this format:
{
  "center": "Main topic",
  "branches": [
    {"title": "Branch 1", "points": ["Point 1", "Point 2"]},
    {"title": "Branch 2", "points": ["Point 1", "Point 2"]}
  ]
}
Use 4 to 6 important branches.
Keep each point short and accurate.
""")

        with st.spinner("Creating your mind map..."):
            answer, error = ask_ai(
                prompt,
                max_tokens=1800,
                json_mode=True
            )

        if error:
            show_error(error)
        else:
            try:
                data = parse_json(answer)
                st.session_state.mindmap_data = data
            except Exception:
                show_error("Mind map format was incorrect. Please try again.")

    if st.session_state.get("mindmap_data"):
        data = st.session_state.mindmap_data
        st.markdown(
            svg_mindmap(
                data.get("center", topic),
                data.get("branches", [])
            ),
            unsafe_allow_html=True
        )

# =========================================================
# TAB 3: FLOWCHART
# =========================================================

with tabs[2]:
    st.header("🔀 Pictorial Flowchart")

    if st.button("Generate Flowchart", key="flow_btn"):
        prompt = common_context("""
Create a clear flowchart for this topic.
Return ONLY valid JSON:
{
  "title": "Flowchart title",
  "steps": [
    "Step 1",
    "Step 2",
    "Step 3",
    "Step 4",
    "Step 5"
  ]
}
Give 4 to 8 short steps in the correct order.
For a process, show its actual sequence.
For a theory topic, show the logical learning structure.
""")

        with st.spinner("Drawing your flowchart..."):
            answer, error = ask_ai(
                prompt,
                max_tokens=1400,
                json_mode=True
            )

        if error:
            show_error(error)
        else:
            try:
                st.session_state.flow_data = parse_json(answer)
            except Exception:
                show_error("Flowchart format was incorrect. Please try again.")

    if st.session_state.get("flow_data"):
        data = st.session_state.flow_data
        st.subheader(data.get("title", topic))
        st.markdown(
            svg_flowchart(data.get("steps", [])),
            unsafe_allow_html=True
        )

# =========================================================
# TAB 4: RELEVANT TOPIC IMAGES
# =========================================================

with tabs[3]:
    st.header("🖼️ Topic-Related Educational Images")

    if st.button("Find Relevant Images", key="images_btn"):
        search_term = f"{subject} {topic} educational diagram"
        with st.spinner("Searching educational images..."):
            try:
                st.session_state.topic_images = search_wikimedia_images(
                    search_term
                )
            except Exception as exc:
                st.session_state.topic_images = []
                st.warning(f"Image search failed: {str(exc)[:200]}")

    images = st.session_state.get("topic_images", [])

    if images:
        cols = st.columns(2)
        for index, item in enumerate(images):
            with cols[index % 2]:
                st.image(item["url"], use_container_width=True)
                st.caption(item["title"])
                st.markdown(
                    f"[View original source]({item['source']})"
                )
    else:
        st.info(
            "Generate images to see relevant educational pictures. "
            "Image availability depends on Wikimedia Commons."
        )
# =========================================================
# TAB 5: EXAM PREPARATION
# =========================================================

with tabs[4]:
    st.header("📝 Exam Preparation Centre")

    exam_type = st.selectbox(
        "Choose what you want to prepare",
        [
            "2 Marks Questions",
            "4 Marks Questions",
            "5 Marks Questions",
            "6 Marks Questions",
            "Important Questions",
            "PYQ-Style Practice Questions",
            "Definitions",
            "Formulas and Key Concepts",
            "Quick Revision",
            "Memory Tricks",
            "Real-World Examples"
        ],
        key="exam_type"
    )

    if st.button("Generate Exam Material", key="exam_btn"):
        prompt = common_context(f"""
Generate material for: {exam_type}.

Requirements:
- Stay strictly relevant to the selected subject and topic.
- Give accurate, exam-oriented answers.
- Include examples wherever useful.
- Use clear headings and numbered points.
- For numerical topics, include suitable solved examples.
- For theory topics, explain concepts with relevant examples.
- Do not generate irrelevant formulas.
- Do not claim generated practice questions are verified official PYQs.

If PYQ-style practice is selected, create questions similar in style
to examination questions and clearly label them as practice questions.
""")

        with st.spinner("Preparing your exam material..."):
            answer, error = ask_ai(prompt, max_tokens=3500)

        if error:
            show_error(error)
        else:
            st.session_state.exam_material = answer

    if st.session_state.get("exam_material"):
        st.markdown(
            f'<div class="note-paper">{st.session_state.exam_material}</div>',
            unsafe_allow_html=True
        )
        show_download(
            st.session_state.exam_material,
            "TECHNOVA_Exam_Preparation.txt"
        )


# =========================================================
# TAB 6: INTERACTIVE MOCK TEST
# =========================================================

with tabs[5]:
    st.header("🎯 Interactive Mock Test")

    number_of_questions = st.selectbox(
        "Number of questions",
        [5, 10, 15, 20],
        key="quiz_count"
    )

    if st.button("🚀 Generate Mock Test", key="quiz_btn"):
        prompt = common_context(f"""
Create exactly {number_of_questions} multiple-choice questions
for the selected subject and topic.

Return ONLY valid JSON in this exact structure:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": 0,
      "explanation": "Explanation of the correct answer"
    }}
  ]
}}

Rules:
- answer must be an integer from 0 to 3.
- Include exactly four options per question.
- Questions must be relevant to the selected topic.
- Do not repeat questions.
- Provide accurate answers and explanations.
""")

        with st.spinner("Preparing your mock examination..."):
            answer, error = ask_ai(
                prompt,
                max_tokens=3500,
                json_mode=True
            )

        if error:
            show_error(error)
        else:
            try:
                quiz_data = parse_json(answer)
                questions = quiz_data.get("questions", [])

                if not questions:
                    raise ValueError("No questions generated.")

                valid_questions = []

                for q in questions:
                    options = q.get("options", [])
                    correct = q.get("answer")

                    if (
                        isinstance(q.get("question"), str)
                        and isinstance(options, list)
                        and len(options) == 4
                        and isinstance(correct, int)
                        and 0 <= correct < 4
                    ):
                        valid_questions.append(q)

                if not valid_questions:
                    raise ValueError("Questions were not in the expected format.")

                st.session_state.mock_test = valid_questions
                st.session_state.mock_submitted = False
                st.session_state.mock_answers = {}

            except Exception as exc:
                show_error(
                    f"Could not prepare the mock test: {str(exc)}. Please try again."
                )

    questions = st.session_state.get("mock_test", [])

    if questions:
        st.divider()
        st.subheader(f"📋 {subject}: {topic}")

        if not st.session_state.get("mock_submitted", False):

            with st.form("mock_test_form"):
                answers = {}

                for i, q in enumerate(questions):
                    st.markdown(f"### Question {i + 1}")
                    st.write(q["question"])

                    selected = st.radio(
                        "Choose your answer:",
                        q["options"],
                        index=None,
                        key=f"mock_answer_{i}"
                    )

                    answers[i] = selected
                    st.divider()

                submitted = st.form_submit_button(
                    "Submit My Answers"
                )

            if submitted:
                st.session_state.mock_answers = answers
                st.session_state.mock_submitted = True
                st.rerun()

        else:
            answers = st.session_state.mock_answers
            score = 0

            for i, q in enumerate(questions):
                correct_index = q["answer"]
                correct_option = q["options"][correct_index]
                selected = answers.get(i)

                if selected == correct_option:
                    score += 1

            percentage = (score / len(questions)) * 100

            st.success("🎉 Your test has been evaluated!")

            col1, col2, col3 = st.columns(3)

            col1.metric("Your Score", f"{score}/{len(questions)}")
            col2.metric("Percentage", f"{percentage:.1f}%")

            if percentage >= 80:
                result = "Excellent! 🌟"
            elif percentage >= 60:
                result = "Good job! 👏"
            elif percentage >= 40:
                result = "Keep practising! 💪"
            else:
                result = "Don't give up. Keep learning! ❤️"

            col3.metric("Performance", result)

            st.progress(int(percentage))

            st.subheader("📖 Answer Review")

            for i, q in enumerate(questions):
                correct_index = q["answer"]
                correct_option = q["options"][correct_index]
                selected = answers.get(i)

                st.markdown(f"**Q{i + 1}. {q['question']}**")

                if selected == correct_option:
                    st.success(f"Correct: {correct_option}")
                else:
                    st.error(
                        f"Your answer: {selected if selected else 'Not answered'}"
                    )
                    st.info(f"Correct answer: {correct_option}")

                st.write(
                    "Explanation: " + q.get(
                        "explanation",
                        "No explanation provided."
                    )
                )

                st.divider()

            if st.button("🔄 Take Another Mock Test"):
                st.session_state.mock_test = []
                st.session_state.mock_submitted = False
                st.session_state.mock_answers = {}
                st.rerun()


# =========================================================
# TAB 7: DOUBT SOLVER
# =========================================================

with tabs[6]:
    st.header("💬 Ask TECHNOVA AI")

    st.write(
        "Ask any question related to your selected subject."
    )

    doubt = st.text_area(
        "Enter your doubt here:",
        placeholder="Example: Explain this concept with an easy example...",
        height=140,
        key="doubt_input"
    )

    if st.button("🤖 Solve My Doubt", key="doubt_btn"):

        if not doubt.strip():
            st.warning("Please enter your question first.")

        else:
            prompt = common_context(f"""
Answer this student's doubt:

{doubt}

Instructions:
1. Explain in simple language.
2. Break difficult concepts into steps.
3. Give a relevant example.
4. Include a diagram description if useful.
5. Avoid unrelated information.
6. If the question is outside the selected subject or topic,
   politely explain that and ask the student to select the relevant topic.
""")

            with st.spinner("Thinking about your question..."):
                answer, error = ask_ai(prompt, max_tokens=2500)

            if error:
                show_error(error)
            else:
                st.markdown(
                    f'<div class="note-paper">{answer}</div>',
                    unsafe_allow_html=True
                )


# =========================================================
# TAB 8: PREVIOUS TOPICS
# =========================================================

with tabs[7]:
    st.header("📚 Your Previous Topics")

    st.write(
        "Your recently selected topics are listed here during this app session."
    )

    history = st.session_state.get("topic_history", [])

    if history:

        for i, item in enumerate(history):

            with st.expander(
                f"📖 {item['subject']} — {item['topic']}"
            ):
                st.write(f"**Category:** {item['category']}")
                st.write(f"**Course:** {item['course']}")
                st.write(
                    f"**Specialisation:** {item['specialisation']}"
                )
                st.write(f"**Year / Level:** {item['level']}")
                st.write(f"**Subject:** {item['subject']}")
                st.write(f"**Topic:** {item['topic']}")

                if i == 0:
                    st.caption("Currently selected topic")

        if st.button("🗑️ Clear Topic History"):
            st.session_state.topic_history = []
            st.rerun()

    else:
        st.info("You haven't selected any topics yet.")


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown("""
<div style="
    text-align:center;
    padding:20px;
    border-radius:16px;
    background:linear-gradient(100deg,#ede9fe,#fce7f3);
    color:#4338ca;
">
    <h3>🚀 TECHNOVA AI</h3>
    <p>Your Personal AI Learning Companion</p>
    <p>❤️ Built with Love by Ruchita</p>
</div>
""", unsafe_allow_html=True)