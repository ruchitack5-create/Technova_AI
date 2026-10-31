import streamlit as st
import json
import re
from google import genai

# PAGE SETTINGS
st.set_page_config(
    page_title="TECHNOVA AI",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 TECHNOVA AI")
st.subheader("Your Personal AI Learning Companion")

st.write(
    "Learn smarter. Prepare better. Achieve more."
)

# GEMINI CONNECTION
try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )
except Exception:
    st.error("API key not found. Please check Streamlit Secrets.")
    st.stop()

MODEL = "gemini-3.8-flash"


# AI FUNCTION
def ask_ai(prompt):
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text


# COMMON STUDY SETTINGS
st.sidebar.header("🎓 Learning Profile")

level = st.sidebar.selectbox(
    "Choose your category",
    [
        "School",
        "College",
        "Competitive Exams"
    ]
)

exam_options = {
    "School": [
        "Class 6", "Class 7", "Class 8",
        "Class 9", "Class 10", "Class 11",
        "Class 12"
    ],
    "College": [
        "BE / BTech", "BSc", "BCA",
        "BCom", "BA", "Diploma"
    ],
    "Competitive Exams": [
        "NEET", "JEE Main", "JEE Advanced",
        "KCET", "CUET", "UPSC",
        "SSC", "IBPS Banking", "SBI Banking",
        "NDA", "CDS"
    ]
}

course = st.sidebar.selectbox(
    "Choose course or exam",
    exam_options[level]
)

subject = st.sidebar.text_input(
    "Subject",
    placeholder="Example: Physics"
)

topic = st.sidebar.text_input(
    "Topic",
    placeholder="Example: Laws of Motion"
)

st.sidebar.caption(
    "Choose your course and enter a specific topic."
)


# MAIN TABS
notes_tab, questions_tab, quiz_tab, about_tab = st.tabs(
    [
        "📚 Study Notes",
        "📝 Question Bank",
        "🧠 Quiz",
        "ℹ️ About"
    ]
)


# TAB 1: DETAILED NOTES
with notes_tab:

    st.header("📚 Detailed Study Notes")

    depth = st.selectbox(
        "Choose explanation depth",
        ["Basic", "Detailed", "In-depth"]
    )

    language = st.selectbox(
        "Choose language",
        ["English", "Kannada", "Hindi"]
    )

    if st.button("Generate Study Notes"):

        if not subject.strip() or not topic.strip():
            st.warning("Please enter both subject and topic.")

        else:
            prompt = f"""
You are an expert teacher and educational content creator.

Create high-quality educational notes.

Education category: {level}
Course or exam: {course}
Subject: {subject}
Topic: {topic}
Explanation depth: {depth}
Language: {language}

Instructions:

1. Start with a clear introduction.
2. Explain every important concept step by step.
3. Include definitions and key terminology.
4. Explain the topic in sufficient depth.
5. Include relevant examples.
6. Include formulas and derivations wherever applicable.
7. Explain practical applications.
8. Include important points for examinations.
9. Add common mistakes and misconceptions.
10. Finish with a detailed summary.

For science subjects, explain scientific concepts accurately.
For engineering subjects, include technical details.
For NEET and JEE, focus on relevant exam concepts.

Do not give unnecessarily short answers.
Do not invent facts or formulas.
Use clear headings and subheadings.
"""

            with st.spinner("Preparing detailed notes..."):
                try:
                    result = ask_ai(prompt)
                    st.markdown(result)

                    st.download_button(
                        "⬇️ Download Notes",
                        result,
                        file_name="TECHNOVA_Notes.txt"
                    )

                except Exception as e:
                    st.error(f"Generation failed: {e}")


# TAB 2: QUESTION BANK
with questions_tab:

    st.header("📝 Important Question Bank")

    marks = st.multiselect(
        "Select question marks",
        [2, 5, 10],
        default=[2, 5, 10]
    )

    if st.button("Generate Question Bank"):

        if not subject.strip() or not topic.strip():
            st.warning("Enter subject and topic first.")

        elif not marks:
            st.warning("Select at least one mark category.")

        else:
            prompt = f"""
Act as an experienced examination question paper setter.

Course: {course}
Category: {level}
Subject: {subject}
Topic: {topic}

Generate important examination questions for:
{marks} marks.

For every question:
- Write the question clearly.
- Give a correct and sufficiently detailed answer.
- Use examples wherever needed.
- Organise answers according to marks.
- Include important keywords.
- Avoid repeating questions.

For 2 marks: concise but complete answers.
For 5 marks: structured explanations.
For 10 marks: detailed answers with headings,
examples, diagrams described in text where relevant.

Use {language if 'language' in globals() else 'English'}.
"""

            with st.spinner("Creating question bank..."):
                try:
                    result = ask_ai(prompt)
                    st.markdown(result)

                    st.download_button(
                        "⬇️ Download Questions",
                        result,
                        file_name="TECHNOVA_Question_Bank.txt"
                    )

                except Exception as e:
                    st.error(f"Generation failed: {e}")


# TAB 3: QUIZ
with quiz_tab:

    st.header("🧠 Test Your Knowledge")

    number = st.selectbox(
        "Number of questions",
        [5, 10, 15]
    )

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"]
    )

    if st.button("Generate Quiz"):

        if not subject.strip() or not topic.strip():
            st.warning("Enter subject and topic first.")

        else:
            prompt = f"""
Create {number} multiple-choice questions.

Course: {course}
Subject: {subject}
Topic: {topic}
Difficulty: {difficulty}

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
      "answer": "Option A",
      "explanation": "Detailed explanation"
    }}
  ]
}}

Rules:
- Exactly {number} questions.
- Four options per question.
- One correct answer.
- Correct answers must match one option exactly.
- Include explanations.
- No markdown or extra text outside JSON.
- Ensure scientific and factual accuracy.
"""

            with st.spinner("Preparing your quiz..."):
                try:
                    result = ask_ai(prompt)

                    match = re.search(
                        r"\{.*\}",
                        result,
                        re.DOTALL
                    )

                    if not match:
                        raise ValueError("Quiz format was invalid.")

                    quiz_data = json.loads(match.group())

                    if len(quiz_data["questions"]) != number:
                        raise ValueError("Incorrect number of questions.")

                    st.session_state.quiz_data = quiz_data
                    st.session_state.quiz_submitted = False

                except Exception as e:
                    st.error(f"Quiz generation failed: {e}")

    if "quiz_data" in st.session_state:

        quiz = st.session_state.quiz_data
        answers = []

        for i, q in enumerate(quiz["questions"]):

            st.markdown(
                f"**Q{i+1}. {q['question']}**"
            )

            answer = st.radio(
                "Choose your answer:",
                q["options"],
                key=f"question_{i}"
            )

            answers.append(answer)

        if not st.session_state.quiz_submitted:

            if st.button("Submit Quiz"):

                score = 0

                for i, q in enumerate(quiz["questions"]):
                    if answers[i] == q["answer"]:
                        score += 1

                st.session_state.quiz_score = score
                st.session_state.quiz_answers = answers
                st.session_state.quiz_submitted = True
                st.rerun()

        else:

            st.success(
                f"Your score: "
                f"{st.session_state.quiz_score}/{len(quiz['questions'])}"
            )

            for i, q in enumerate(quiz["questions"]):

                st.write(f"**Question {i+1}:** {q['question']}")

                if st.session_state.quiz_answers[i] == q["answer"]:
                    st.success("Correct answer!")

                else:
                    st.error(
                        f"Your answer: "
                        f"{st.session_state.quiz_answers[i]}"
                    )

                st.info(
                    f"Correct answer: {q['answer']}\n\n"
                    f"Explanation: {q['explanation']}"
                )

            if st.button("Try Another Quiz"):
                del st.session_state.quiz_data
                st.session_state.quiz_submitted = False
                st.rerun()


# TAB 4: ABOUT
with about_tab:

    st.header("About TECHNOVA AI")

    st.write("""
    TECHNOVA AI is an AI-powered learning platform
    designed for students.

    Our mission is to make learning easier and
    examination preparation smarter.

    Features:
    - Detailed study notes
    - Important question banks
    - Interactive MCQ quizzes
    - School and college learning
    - Competitive examination preparation

    Learn. Practice. Improve. Succeed.
    """)

    st.caption("TECHNOVA AI | Built with ❤️")