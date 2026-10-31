
import streamlit as st
import json
import re
from google import genai

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="TECHNOVA AI",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 TECHNOVA AI")
st.subheader("Your Personal AI Learning Companion")

st.write(
    "Learn smarter. Practice better. Achieve more."
)


# ==========================================
# GEMINI API CONNECTION
# ==========================================

try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )
except Exception:
    st.error(
        "API key not found. Please check Streamlit Secrets."
    )
    st.stop()

MODEL = "gemini-3.8-flash"


def ask_ai(prompt):
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "max_output_tokens": 8192
        }
    )

    if not response.text:
        raise ValueError("AI returned an empty response.")

    return response.text


# ==========================================
# COURSE DATABASE
# ==========================================

school_courses = [
    "Class 6",
    "Class 7",
    "Class 8",
    "Class 9",
    "Class 10",
    "Class 11",
    "Class 12"
]

college_courses = [
    "BE / BTech",
    "BSc",
    "MSc",
    "BSc Nursing",
    "GNM Nursing",
    "ANM Nursing",
    "MBBS",
    "BAMS",
    "BHMS",
    "BUMS",
    "BBA",
    "MBA",
    "BCA",
    "MCA",
    "BCom",
    "MCom",
    "BA",
    "MA",
    "BPharm",
    "MPharm",
    "DPharm",
    "BPT",
    "MPT",
    "LLB",
    "LLM",
    "BEd",
    "MEd",
    "Diploma - Electrical",
    "Diploma - Mechanical",
    "Diploma - Civil",
    "Diploma - Computer Science",
    "Diploma - Electronics",
    "Diploma - Automobile",
    "Diploma - Chemical",
    "Diploma - Architecture"
]

competitive_exams = [
    "NEET UG",
    "JEE Main",
    "JEE Advanced",
    "KCET",
    "COMEDK",
    "CUET",
    "UPSC",
    "SSC",
    "IBPS Banking",
    "SBI Banking",
    "NDA",
    "CDS",
    "CAT",
    "GATE",
    "CLAT",
    "Other Competitive Exam"
]


# ==========================================
# SIDEBAR - LEARNING PROFILE
# ==========================================

st.sidebar.title("🎓 Learning Profile")

category = st.sidebar.selectbox(
    "Choose your category",
    [
        "School",
        "College",
        "Competitive Exams"
    ]
)

if category == "School":

    course = st.sidebar.selectbox(
        "Choose your class",
        school_courses
    )

elif category == "College":

    course = st.sidebar.selectbox(
        "Choose your course",
        college_courses
    )

else:

    course = st.sidebar.selectbox(
        "Choose your exam",
        competitive_exams
    )

subject = st.sidebar.text_input(
    "Subject",
    placeholder="Example: Physics"
)

topic = st.sidebar.text_input(
    "Topic / Concept",
    placeholder="Example: Laws of Motion"
)

language = st.sidebar.selectbox(
    "Output Language",
    [
        "English",
        "Kannada",
        "Hindi"
    ]
)

st.sidebar.caption(
    "Select your course and enter a topic to begin."
)


# ==========================================
# MAIN TABS
# ==========================================

notes_tab, questions_tab, quiz_tab, about_tab = st.tabs(
    [
        "📚 Study Notes",
        "📝 Question Bank",
        "🧠 Quiz",
        "ℹ️ About"
    ]
)


# ==========================================
# TAB 1 - DETAILED STUDY NOTES
# ==========================================

with notes_tab:

    st.header("📚 Detailed Study Notes")

    depth = st.selectbox(
        "Choose Explanation Depth",
        [
            "Basic",
            "Detailed",
            "In-depth"
        ]
    )

    include_examples = st.checkbox(
        "Include examples",
        value=True
    )

    include_exam_points = st.checkbox(
        "Include important exam points",
        value=True
    )

    if st.button("Generate Study Notes"):

        if not subject.strip() or not topic.strip():

            st.warning(
                "Please enter subject and topic in the sidebar."
            )

        else:

            prompt = f"""
You are an expert teacher and educational content creator.

Create comprehensive educational notes.

Category: {category}
Course or Exam: {course}
Subject: {subject}
Topic: {topic}
Explanation Depth: {depth}
Language: {language}

Follow these instructions:

1. Give a clear introduction.
2. Explain the topic step by step.
3. Include important definitions.
4. Explain concepts in sufficient depth.
5. Include relevant subtopics.
6. Include formulas and derivations wherever applicable.
7. Explain practical applications.
8. Include examples: {include_examples}.
9. Include important examination points: {include_exam_points}.
10. Explain common mistakes and misconceptions.
11. Finish with a detailed summary.
12. Include important keywords.

For engineering, include technical explanations.
For nursing and medical courses, use accurate
educational terminology.
For NEET and JEE, focus on relevant examination concepts.
For school students, use age-appropriate explanations.

Do not give unnecessarily short answers.
Do not invent facts or formulas.
Use clear headings and subheadings.
Mention when syllabus-specific information needs verification.
"""

            with st.spinner("Creating detailed notes..."):

                try:

                    result = ask_ai(prompt)

                    st.markdown(result)

                    st.download_button(
                        "⬇️ Download Notes",
                        data=result,
                        file_name="TECHNOVA_Study_Notes.txt"
                    )

                except Exception as e:

                    st.error(
                        f"Notes generation failed: {e}"
                    )


# ==========================================
# TAB 2 - QUESTION BANK
# ==========================================

with questions_tab:

    st.header("📝 Important Question Bank")

    marks = st.multiselect(
        "Select Question Marks",
        [2, 5, 10],
        default=[2, 5, 10]
    )

    if st.button("Generate Question Bank"):

        if not subject.strip() or not topic.strip():

            st.warning(
                "Please enter subject and topic in the sidebar."
            )

        elif not marks:

            st.warning(
                "Please select at least one mark category."
            )

        else:

            prompt = f"""
Act as an experienced examination question setter.

Category: {category}
Course or Exam: {course}
Subject: {subject}
Topic: {topic}
Language: {language}

Generate important questions for:
{marks} marks.

For 2-mark questions:
Give concise and complete answers.

For 5-mark questions:
Give structured explanations with examples.

For 10-mark questions:
Give detailed answers with headings,
subheadings, examples and diagrams described in text.

Include:
1. Important examination questions.
2. Correct and sufficiently detailed answers.
3. Relevant examples.
4. Important keywords.
5. Numerical problems wherever appropriate.

Avoid repeated questions.
Match the course or examination level.
Do not invent syllabus-specific information.
"""

            with st.spinner("Preparing question bank..."):

                try:

                    result = ask_ai(prompt)

                    st.markdown(result)

                    st.download_button(
                        "⬇️ Download Question Bank",
                        data=result,
                        file_name="TECHNOVA_Question_Bank.txt"
                    )

                except Exception as e:

                    st.error(
                        f"Question generation failed: {e}"
                    )


# ==========================================
# TAB 3 - INTERACTIVE QUIZ
# ==========================================

with quiz_tab:

    st.header("🧠 Test Your Knowledge")

    number = st.selectbox(
        "Number of Questions",
        [5, 10, 15]
    )

    difficulty = st.selectbox(
        "Difficulty Level",
        [
            "Easy",
            "Medium",
            "Hard"
        ]
    )

    if st.button("Generate Quiz"):

        if not subject.strip() or not topic.strip():

            st.warning(
                "Please enter subject and topic in the sidebar."
            )

        else:

            prompt = f"""
Create exactly {number} multiple-choice questions.

Category: {category}
Course or Exam: {course}
Subject: {subject}
Topic: {topic}
Difficulty: {difficulty}
Language: {language}

Return ONLY valid JSON in this format:

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
            "answer": "Exact correct option text",
            "explanation": "Detailed explanation"
        }}
    ]
}}

Rules:
- Exactly {number} questions.
- Exactly four options per question.
- Only one correct answer.
- Answer must match one option exactly.
- Give useful explanations.
- Avoid repeated questions.
- Ensure factual accuracy.
- No markdown outside JSON.
"""

            with st.spinner("Creating your quiz..."):

                try:

                    result = ask_ai(prompt)

                    match = re.search(
                        r"\{.*\}",
                        result,
                        re.DOTALL
                    )

                    if not match:

                        raise ValueError(
                            "AI returned an invalid quiz format."
                        )

                    quiz_data = json.loads(match.group())

                    quiz_questions = quiz_data["questions"]

                    if len(quiz_questions) != number:

                        raise ValueError(
                            "Incorrect number of questions."
                        )

                    for q in quiz_questions:

                        if (
                            len(q["options"]) != 4
                            or q["answer"] not in q["options"]
                            or not q.get("explanation")
                        ):

                            raise ValueError(
                                "One or more quiz questions are invalid."
                            )

                    st.session_state.quiz_data = quiz_questions

                    st.session_state.quiz_submitted = False

                    st.session_state.quiz_version = (
                        st.session_state.get("quiz_version", 0) + 1
                    )

                    st.session_state.quiz_answers = {}

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Quiz generation failed: {e}"
                    )


    if "quiz_data" in st.session_state:

        quiz_questions = st.session_state.quiz_data

        if not st.session_state.quiz_submitted:

            with st.form("quiz_form"):

                answers = {}

                for i, q in enumerate(quiz_questions):

                    st.markdown(
                        f"**Q{i + 1}. {q['question']}**"
                    )

                    answers[i] = st.radio(
                        "Choose your answer:",
                        q["options"],
                        index=None,
                        key=(
                            f"quiz_{st.session_state.quiz_version}_{i}"
                        )
                    )

                submitted = st.form_submit_button(
                    "Submit Quiz"
                )

                if submitted:

                    if any(
                        answer is None
                        for answer in answers.values()
                    ):

                        st.warning(
                            "Please answer every question."
                        )

                    else:

                        score = sum(
                            1
                            for i, q in enumerate(quiz_questions)
                            if answers[i] == q["answer"]
                        )

                        st.session_state.quiz_answers = answers

                        st.session_state.quiz_score = score

                        st.session_state.quiz_submitted = True

                        st.rerun()

        else:

            score = st.session_state.quiz_score

            total = len(quiz_questions)

            percentage = (score / total) * 100

            st.success(
                f"Your Score: {score}/{total}"
            )

            st.write(
                f"Your Percentage: {percentage:.1f}%"
            )

            for i, q in enumerate(quiz_questions):

                st.markdown(
                    f"**Q{i + 1}. {q['question']}**"
                )

                user_answer = (
                    st.session_state.quiz_answers[i]
                )

                if user_answer == q["answer"]:

                    st.success(
                        f"Your answer: {user_answer}"
                    )

                else:

                    st.error(
                        f"Your answer: {user_answer}"
                    )

                    st.info(
                        f"Correct answer: {q['answer']}"
                    )

                st.write(
                    f"Explanation: {q['explanation']}"
                )

            if st.button("Try Another Quiz"):

                del st.session_state.quiz_data

                st.session_state.quiz_submitted = False

                st.session_state.quiz_answers = {}

                st.rerun()


# ==========================================
# TAB 4 - ABOUT TECHNOVA AI
# ==========================================

with about_tab:

    st.header("About TECHNOVA AI")

    st.write("""
    TECHNOVA AI is an AI-powered educational platform
    designed for school students, college students
    and competitive examination aspirants.

    Our features:

    📚 Detailed topic-wise study notes

    📝 Important question banks

    🧠 Interactive MCQ quizzes

    🎓 Multiple educational courses

    🎯 Competitive examination preparation

    Our mission is to make learning easier,
    smarter and more accessible.

    Learn. Practice. Improve. Succeed.
    """)


# ==========================================
# FOOTER - CREATOR SIGNATURE
# ==========================================

st.markdown("---")

st.markdown(
    """
    <h3 style="text-align:center;">
        TECHNOVA AI 🚀
    </h3>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style="text-align:center; font-size:16px;">
        Built with ❤️ by <b>Ruchita</b>
    </p>
    """,
    unsafe_allow_html=True
)