
import streamlit as st
import time
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
st.write("Generate smart and detailed study notes.")

topic = st.text_input("Enter your topic")

level = st.selectbox(
    "Choose your study level",
    ["School", "Diploma", "Engineering", "Degree"]
)

length = st.selectbox(
    "Choose notes length",
    ["Short", "Medium", "Detailed"]
)

language = st.selectbox(
    "Choose language",
    ["Simple English", "Kannada", "Hindi"]
)

if st.button("✨ Generate Notes"):

    if not topic.strip():
        st.warning("Please enter a topic.")

    else:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            client = genai.Client(api_key=api_key)

            prompt = f"""
Act as an expert teacher.

Create accurate study notes about {topic}.

Student level: {level}
Notes length: {length}
Language: {language}

Include:
1. Introduction
2. Important definitions
3. Main concepts with explanations
4. Real-life examples
5. Advantages and applications
6. Important examination points
7. Short conclusion

Use clear headings and simple language.
Make the notes suitable for examinations.
"""

            with st.spinner("Generating your notes..."):

                response = None

                for attempt in range(3):
                    try:
                        response = client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=prompt
                        )
                        break

                    except Exception as error:
                        if "503" in str(error) and attempt < 2:
                            time.sleep(2 ** (attempt + 1))
                        else:
                            raise

            if response and response.text:

                st.success("Your notes are ready!")

                st.markdown(response.text)

                st.download_button(
                    "⬇️ Download Notes",
                    response.text,
                    file_name="TECHNOVA_AI_Notes.txt"
                )

            else:
                st.error("No notes generated. Try again.")

        except KeyError:
            st.error("Gemini API key is missing in Streamlit Secrets.")

        except Exception as error:
            st.error(f"Error: {error}")

st.divider()
st.markdown("### 🌟 Learn Beyond Limits")
st.caption("TECHNOVA AI | Your Personal AI Study Companion")