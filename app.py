
import streamlit as st

st.set_page_config(
    page_title="TECHNOVA AI",
    page_icon="🎓",
    layout="wide"
)

# Custom design
st.markdown("""
<style>
.stApp {
    background-color: #101426;
    color: white;
}
h1 {
    color: #8B9CFF;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Application title
st.title("TECHNOVA AI")
st.markdown("### Learn Beyond Limits")

st.write("Your Personal AI Study Companion")

st.divider()

# Student details
st.sidebar.title("TECHNOVA AI")

name = st.sidebar.text_input("Your Name")

level = st.sidebar.selectbox(
    "Education Level",
    ["School", "PUC", "Diploma",
     "Engineering", "Degree"]
)

language = st.sidebar.selectbox(
    "Preferred Language",
    ["English", "Kannada", "Hindi",
     "Tamil", "Telugu"]
)

st.subheader("Welcome to your learning space!")

if name:
    st.write(f"Hello, {name}! 👋")

st.write("Choose what you want to do today.")

# Learning tools
tab1, tab2, tab3, tab4 = st.tabs([
    "📚 Notes",
    "🧠 Doubts",
    "📝 Exams",
    "🎯 Quiz"
])

with tab1:
    st.subheader("Smart Notes Generator")
    topic = st.text_input("Enter your subject or topic")

    if st.button("Generate Notes"):
        st.info("Our AI Notes Generator is coming soon!")

with tab2:
    st.subheader("AI Doubt Solver")
    question = st.text_area("Ask your academic question")

    if st.button("Solve My Doubt"):
        st.info("Our AI Doubt Solver is coming soon!")

with tab3:
    st.subheader("Exam Preparation")

    marks = st.selectbox(
        "Select answer marks",
        [2, 5, 10, 15]
    )

    exam_question = st.text_input("Enter your question")

    if st.button("Prepare Answer"):
        st.info("Our Exam Answer Generator is coming soon!")

with tab4:
    st.subheader("Quiz Generator")

    subject = st.text_input("Enter subject name")

    if st.button("Create Quiz"):
        st.info("Our Quiz Generator is coming soon!")

st.divider()

st.caption("© 2026 TECHNOVA AI | Learn Beyond Limits")
