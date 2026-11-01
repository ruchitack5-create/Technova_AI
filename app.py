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