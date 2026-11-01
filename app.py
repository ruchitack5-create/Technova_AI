import streamlit as st
from google import genai
import time

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="TECHNOVA AI",
    page_icon="🚀",
    layout="wide"
)

# ==========================================
# GEMINI CONFIGURATION
# ==========================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

MODEL = "gemini-3.5-flash-lite"

# ==========================================
# CUSTOM DESIGN
# ==========================================

st.markdown("""
<style>

.main {
    background-color: #0e1117;
}

.stButton>button {
    width: 100%;
    border-radius: 10px;
    height: 45px;
    background-color: #2563eb;
    color: white;
    font-weight: bold;
}

.stButton>button:hover {
    background-color: #1d4ed8;
    color: white;
}

h1 {
    color: #60a5fa;
}

h2, h3 {
    color: #38bdf8;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER
# ==========================================

st.title("🚀 TECHNOVA AI")

st.subheader("Your Personal AI Learning Companion")

st.caption(
    "Learn smarter | Prepare better | Achieve more"
)

st.divider()

# ==========================================
# SESSION STATE
# ==========================================

if "results" not in st.session_state:
    st.session_state.results = {}

# ==========================================
# AI GENERATION FUNCTION
# ==========================================

def generate_ai(prompt, max_tokens=3500):

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={
                "temperature": 0.4,
                "max_output_tokens": max_tokens
            }
        )

        if response.text:
            return response.text

        return "No response generated. Please try again."

    except Exception as e:

        error = str(e)

        if "503" in error or "UNAVAILABLE" in error:
            return (
                "⚠️ Gemini servers are currently busy. "
                "Please try again after a few seconds."
            )

        if "429" in error or "RESOURCE_EXHAUSTED" in error:
            return (
                "⚠️ API usage limit reached. "
                "Please try again later."
            )

        return f"⚠️ Generation error: {error}"


# ==========================================
# COMMON INPUTS
# ==========================================

st.header("📚 Learning Dashboard")

col1, col2 = st.columns(2)

with col1:

    level = st.selectbox(
        "Select Education Level",
        [
            "School",
            "Diploma",
            "Engineering",
            "Degree"
        ]
    )

with col2:

    subject = st.selectbox(
        "Select Subject",
        [
            "Artificial Intelligence",
            "Machine Learning",
            "Data Structures and Algorithms",
            "Python Programming",
            "Java Programming",
            "C Programming",
            "Computer Science",
            "Mathematics",
            "Physics",
            "Chemistry",
            "Biology",
            "English",
            "Kannada",
            "Electronics",
            "Electrical Engineering",
            "Database Management",
            "Operating Systems",
            "Computer Networks",
            "Other"
        ]
    )

if subject == "Other":

    subject = st.text_input(
        "Enter your subject name"
    )

topic = st.text_input(
    "📖 Enter Chapter / Topic",
    placeholder="Example: Intelligent Agents, JVM Architecture..."
)

col3, col4 = st.columns(2)

with col3:

    language = st.selectbox(
        "Select Language",
        [
            "Simple English",
            "Kannada",
            "Hindi"
        ]
    )

with col4:

    difficulty = st.selectbox(
        "Notes Length",
        [
            "Short",
            "Medium",
            "Detailed"
        ]
    )

st.divider()

# ==========================================
# VALIDATION
# ==========================================

def validate_inputs():

    if not subject or not subject.strip():

        st.error("Please select or enter a valid subject.")
        return False

    if not topic or not topic.strip():

        st.error("Please enter a chapter or topic.")
        return False

    return True


# ==========================================
# PROMPT BUILDER
# ==========================================

def build_prompt(task):

    return f"""
You are TECHNOVA AI, an expert educational tutor.

STUDENT DETAILS:

Education Level: {level}
Subject: {subject}
Chapter / Topic: {topic}
Language: {language}
Difficulty: {difficulty}

IMPORTANT RULES:

1. Answer strictly according to the selected subject.
2. Never mix topics from unrelated subjects.
3. Use correct technical terminology.
4. Explain difficult concepts in simple language.
5. Include relevant examples.
6. Use headings and subheadings.
7. Avoid unnecessary explanations.
8. Make answers useful for examinations.
9. Do not invent factual information.
10. If information is uncertain, clearly mention it.

TASK:

{task}

Generate the answer in well-organized Markdown.
"""


# ==========================================
# FEATURE TABS
# ==========================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 AI Notes",
    "❓ Doubt Solver",
    "📚 Exam Preparation",
    "🧠 Mind Maps",
    "🎯 Mock Test"
])


# ==========================================
# TAB 1 - AI NOTES
# ==========================================

with tab1:

    st.header("📝 Smart AI Notes")

    st.write(
        "Generate structured notes for any chapter or topic."
    )

    if st.button("Generate AI Notes", key="notes"):

        if validate_inputs():

            prompt = build_prompt(f"""
Create complete study notes for the selected chapter.

Include:

1. Introduction
2. Definition
3. Important concepts
4. Detailed explanation
5. Important points
6. Relevant examples
7. Advantages and disadvantages, if applicable
8. Applications
9. Important formulas, if applicable
10. Short revision summary

Notes length: {difficulty}

Make the notes suitable for {level} students.

Do not add unrelated formulas or concepts.
""")

            with st.spinner("Generating your study notes..."):

                result = generate_ai(prompt, 4500)

            st.session_state.results["notes"] = result

    if "notes" in st.session_state.results:

        st.markdown(st.session_state.results["notes"])

        st.download_button(
            "⬇️ Download Notes",
            data=st.session_state.results["notes"],
            file_name="TECHNOVA_AI_Notes.txt",
            mime="text/plain"
        )


# ==========================================
# TAB 2 - DOUBT SOLVER
# ==========================================

with tab2:

    st.header("❓ AI Doubt Solver")

    doubt = st.text_area(
        "Ask your question",
        placeholder="Type your doubt here...",
        height=120
    )

    if st.button("Solve My Doubt"):

        if not doubt.strip():

            st.warning("Please enter your question.")

        else:

            prompt = f"""
You are an expert tutor.

Student Level: {level}
Subject: {subject}
Chapter: {topic}
Language: {language}

Student Question:

{doubt}

Instructions:

1. Understand the question carefully.
2. Answer according to the selected subject.
3. Explain step by step.
4. Include an example.
5. Use simple language.
6. Include a diagram description if useful.
7. Do not answer an unrelated question as if it belongs
to the selected subject.
"""

            with st.spinner("Solving your doubt..."):

                result = generate_ai(prompt, 2500)

            st.markdown(result)


# ==========================================
# TAB 3 - EXAM PREPARATION
# ==========================================

with tab3:

    st.header("📚 Exam Preparation")

    exam_option = st.selectbox(
        "Choose Exam Material",
        [
            "Important Questions",
            "2 Mark Questions",
            "4 Mark Questions",
            "5 Mark Questions",
            "6 Mark Questions",
            "Chapter-wise PYQ-style Questions",
            "Topic-wise Revision",
            "Formulas and Definitions"
        ]
    )

    number_questions = st.slider(
        "Number of Questions",
        5,
        30,
        10
    )

    if st.button("Generate Exam Material"):

        if validate_inputs():

            prompt = build_prompt(f"""
Generate examination preparation material.

Selected option: {exam_option}

Number of questions: {number_questions}

Instructions:

1. Generate questions strictly from the selected topic.
2. Give accurate answers.
3. Explain answers according to their marks.
4. Use suitable examples.
5. Include diagrams where necessary.
6. Highlight important keywords.
7. Keep the answers examination-oriented.

For PYQ-style questions:
Generate questions similar to previous-year examination
patterns. Do not falsely claim that AI-generated questions
are verified actual previous-year questions.

For revision:
Include important definitions, concepts and key points.
""")

            with st.spinner("Preparing examination material..."):

                result = generate_ai(prompt, 4500)

            st.session_state.results["exam"] = result

    if "exam" in st.session_state.results:

        st.markdown(st.session_state.results["exam"])

        st.download_button(
            "⬇️ Download Exam Material",
            data=st.session_state.results["exam"],
            file_name="TECHNOVA_Exam_Preparation.txt",
            mime="text/plain"
        )


# ==========================================
# TAB 4 - MIND MAPS
# ==========================================

with tab4:

    st.header("🧠 Visual Learning Centre")

    visual_option = st.selectbox(
        "Select Visual Learning Tool",
        [
            "Mind Map",
            "Topic Diagram",
            "Flowchart",
            "Memory Tricks",
            "Real-Life Examples"
        ]
    )

    if st.button("Generate Visual Learning Material"):

        if validate_inputs():

            prompt = build_prompt(f"""
Create the following learning material:

{visual_option}

Requirements:

For Mind Maps:
- Start with the main topic.
- Create branches and sub-branches.
- Include important concepts.
- Use an easy-to-understand tree structure.

For Topic Diagram:
- Create a clear labelled educational diagram.
- Explain every component.
- Use ASCII diagram format where appropriate.

For Flowchart:
- Use arrows and logical steps.
- Explain the process step by step.

For Memory Tricks:
- Create easy mnemonics.
- Give simple memorization techniques.
- Explain how to remember important concepts.

For Real-Life Examples:
- Give relevant practical examples.
- Connect theory with real-world applications.

Keep everything related to the selected subject and topic.
""")

            with st.spinner("Creating visual learning material..."):

                result = generate_ai(prompt, 3000)

            st.session_state.results["visual"] = result

    if "visual" in st.session_state.results:

        st.markdown(
            st.session_state.results["visual"]
        )

        st.download_button(
            "⬇️ Download Learning Material",
            data=st.session_state.results["visual"],
            file_name="TECHNOVA_Visual_Learning.txt",
            mime="text/plain"
        )


# ==========================================
# TAB 5 - MOCK TEST
# ==========================================

with tab5:

    st.header("🎯 AI Mock Test")

    st.write(
        "Practice questions and test your knowledge."
    )

    test_level = st.selectbox(
        "Select Test Difficulty",
        [
            "Easy",
            "Medium",
            "Hard"
        ]
    )

    test_count = st.selectbox(
        "Number of Questions",
        [5, 10, 15, 20]
    )

    if st.button("Start Mock Test"):

        if validate_inputs():

            prompt = build_prompt(f"""
Create a mock examination.

Difficulty: {test_level}
Number of questions: {test_count}

Include:

1. Multiple-choice questions.
2. Four options for each question.
3. One correct answer.
4. Questions strictly from the selected chapter.
5. A separate answer key at the end.

Do not reveal the correct answer immediately
after each question.

Use this format:

Q1. Question

A) Option
B) Option
C) Option
D) Option

Continue until all questions are generated.

At the end provide:

ANSWER KEY:

Q1 - B
Q2 - A

Ensure the answer key is accurate.
""")

            with st.spinner("Preparing your mock test..."):

                result = generate_ai(prompt, 4000)

            st.session_state.results["mock"] = result

    if "mock" in st.session_state.results:

        st.markdown(st.session_state.results["mock"])

        st.download_button(
            "⬇️ Download Mock Test",
            data=st.session_state.results["mock"],
            file_name="TECHNOVA_Mock_Test.txt",
            mime="text/plain"
        )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown(
    """
    <div style="text-align:center">

    🚀 <b>TECHNOVA AI</b>

    <p>Your Personal AI Learning Companion</p>

    <small>Learn • Practice • Improve • Succeed</small>

    </div>
    """,
    unsafe_allow_html=True
)
# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; padding:20px;">

        <h2>🚀 TECHNOVA AI</h2>

        <p>Your Personal AI Learning Companion</p>

        <p>Learn • Practice • Improve • Succeed</p>

        <hr>

        <p style="font-size:16px; color:#f472b6;">
            ❤️ Built with Love by <b>Ruchita</b>
        </p>

        <small>© 2026 TECHNOVA AI. All Rights Reserved.</small>

    </div>
    """,
    unsafe_allow_html=True
)