import streamlit as st
import time
import json
from google import genai

st.set_page_config(
    page_title="TECHNOVA AI",
    page_icon="📚",
    layout="centered"
)

st.title("🚀 TECHNOVA AI")
st.subheader("Your Personal AI Study Companion")

try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("API key missing. Check Streamlit Secrets.")
    st.stop()


def ask_ai(prompt):
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )
            return response.text
        except Exception:
            if attempt < 2:
                time.sleep(2 ** (attempt + 1))
            else:
                raise


notes_tab, question_tab, quiz_tab = st.tabs(
    ["📚 Notes", "📝 Question Bank", "🧠 Quiz"]
)


# NOTES GENERATOR
with notes_tab:
    st.header("📚 AI Notes Generator")

    topic = st.text_input("Enter your topic", key="notes_topic")

    level = st.selectbox(
        "Study level",
        ["School", "Diploma", "Engineering", "Degree"],
        key="notes_level"
    )

    length = st.selectbox(
        "Notes length",
        ["Short", "Medium", "Detailed"],
        key="notes_length"
    )

    language = st.selectbox(
        "Language",
        ["Simple English", "Kannada", "Hindi"],
        key="notes_language"
    )

    if st.button("✨ Generate Notes"):
        if not topic.strip():
            st.warning("Enter a topic first.")
        else:
            try:
                prompt = f"""
Create accurate examination notes about {topic}.
Student level: {level}
Length: {length}
Language: {language}

Include:
1. Introduction
2. Definitions
3. Main concepts
4. Examples
5. Applications
6. Important exam points
7. Conclusion

Use clear headings and simple language.
"""
                with st.spinner("Creating your notes..."):
                    result = ask_ai(prompt)

                st.success("Notes generated!")
                st.markdown(result)

                st.download_button(
                    "⬇️ Download Notes",
                    result,
                    file_name="TECHNOVA_Notes.txt"
                )

            except Exception as e:
                st.error(f"Error: {e}")


# IMPORTANT QUESTION BANK
with question_tab:
    st.header("📝 Important Question Bank")

    subject = st.text_input("Enter subject or topic", key="question_topic")

    marks = st.multiselect(
        "Select question marks",
        ["2 Marks", "5 Marks", "10 Marks"],
        default=["2 Marks", "5 Marks", "10 Marks"]
    )

    if st.button("✨ Generate Question Bank"):
        if not subject.strip():
            st.warning("Enter a subject or topic.")
        elif not marks:
            st.warning("Select at least one question type.")
        else:
            try:
                prompt = f"""
Act as an experienced engineering examination teacher.

Create an important question bank for:
Subject: {subject}

Include these question types: {marks}

For every question:
- Give a clear question.
- Provide a correct, detailed answer.
- Use simple English.
- Include examples wherever useful.
- Organize answers with headings and points.

Do not claim questions are guaranteed to appear in exams.
"""
                with st.spinner("Preparing your question bank..."):
                    result = ask_ai(prompt)

                st.success("Question bank generated!")
                st.markdown(result)

                st.download_button(
                    "⬇️ Download Question Bank",
                    result,
                    file_name="TECHNOVA_Question_Bank.txt"
                )

            except Exception as e:
                st.error(f"Error: {e}")


# AI QUIZ
with quiz_tab:
    st.header("🧠 AI Practice Quiz")

    quiz_topic = st.text_input("Enter quiz topic", key="quiz_topic")

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"]
    )

    if st.button("🎯 Generate Quiz"):
        if not quiz_topic.strip():
            st.warning("Enter a topic first.")
        else:
            try:
                prompt = f"""
Create exactly 5 multiple-choice questions about {quiz_topic}.
Difficulty: {difficulty}.

Return ONLY valid JSON in this format:
{{
 "questions": [
  {{
   "question": "Question text",
   "options": ["Option A", "Option B", "Option C", "Option D"],
   "answer": 0,
   "explanation": "Explanation"
  }}
 ]
}}

The answer must be the correct option's index:
0, 1, 2 or 3.
"""
                with st.spinner("Creating your quiz..."):
                    result = ask_ai(prompt)

                result = result.strip()
                if result.startswith("```"):
                    result = result.split("\n", 1)[1]
                    result = result.rsplit("```", 1)[0]

                quiz_data = json.loads(result)

                if len(quiz_data["questions"]) != 5:
                    raise ValueError("Quiz did not contain 5 questions.")

                st.session_state.quiz = quiz_data["questions"]
                st.session_state.quiz_submitted = False

            except Exception as e:
                st.error(f"Could not create quiz: {e}")

    if "quiz" in st.session_state:
        questions = st.session_state.quiz

        if not st.session_state.quiz_submitted:
            answers = []

            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}. {q['question']}**")

                selected = st.radio(
                    "Choose your answer:",
                    q["options"],
                    key=f"quiz_answer_{i}",
                    index=None
                )
                answers.append(selected)

            if st.button("Submit Quiz"):
                if None in answers:
                    st.warning("Please answer all questions.")
                else:
                    score = 0

                    for i, q in enumerate(questions):
                        if answers[i] == q["options"][q["answer"]]:
                            score += 1

                    st.session_state.quiz_answers = answers
                    st.session_state.quiz_score = score
                    st.session_state.quiz_submitted = True
                    st.rerun()

        else:
            st.success(
                f"Your score: {st.session_state.quiz_score}/5"
            )

            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}. {q['question']}**")
                st.write(
                    "Correct answer:",
                    q["options"][q["answer"]]
                )
                st.write("Explanation:", q["explanation"])

            if st.button("Try Another Quiz"):
                del st.session_state.quiz
                st.session_state.quiz_submitted = False
                st.rerun()


st.divider()
st.markdown("### 🌟 Learn Beyond Limits")
st.caption("TECHNOVA AI | Your Personal AI Study Companion")