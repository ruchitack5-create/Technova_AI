import streamlit as st
from google import genai

st.set_page_config(
    page_title="TECHNOVA AI",
    page_icon="📚",
    layout="centered"
)

st.title("🚀 TECHNOVA AI")
st.subheader("Welcome to your learning space")
st.write("Your Personal AI Study Companion")

st.divider()

st.header("📚 AI Notes Generator")
st.write("Generate easy-to-understand study notes on any topic.")

topic = st.text_input(
    "Enter your topic",
    placeholder="Example: Artificial Intelligence"
)

level = st.selectbox(
    "Choose your study level",
    ["School", "Diploma", "Engineering", "Degree"]
)

length = st.selectbox(
    "Choose notes length",
    ["Short", "Medium", "Detailed"]
)

if st.button("✨ Generate Notes"):

    if not topic.strip():
        st.warning("Please enter a topic first.")

    else:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            client = genai.Client(api_key=api_key)

            prompt = f"""
            Act as an expert teacher.

            Create clear and accurate study notes about:
            {topic}

            Student level: {level}
            Notes length: {length}

            Include:
            1. Introduction
            2. Important definitions
            3. Main concepts with explanations
            4. Examples
            5. Key points to remember
            6. Short conclusion

            Use simple English and clear headings.
            """

            with st.spinner("Creating your notes..."):

                response = client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=prompt
                )

            st.success("Your notes are ready!")

            st.markdown(response.text)

            st.download_button(
                "⬇️ Download Notes",
                data=response.text,
                file_name="TECHNOVA_AI_Notes.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Something went wrong: {e}")

st.divider()
st.caption("TECHNOVA AI | Learn Beyond Limits")
