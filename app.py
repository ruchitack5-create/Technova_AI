import streamlit as st
import json
import re
import io
import os
import html

from google import genai

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
def create_study_pdf(content, style="Digital"):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=55,
        bottomMargin=50
    )

    font_name = "Helvetica"

    # Handwritten font
    if style == "Handwritten":

        font_path = os.path.join(
            "fonts",
            "PatrickHand-Regular.ttf"
        )

        if os.path.exists(font_path):

            pdfmetrics.registerFont(
                TTFont("PatrickHand", font_path)
            )

            font_name = "PatrickHand"

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=22,
        textColor=colors.HexColor("#2457A6"),
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontName=font_name,
        fontSize=16,
        textColor=colors.HexColor("#1565C0"),
        spaceBefore=12,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontName=font_name,
        fontSize=12,
        leading=19,
        spaceAfter=8
    )

    story = []

    for line in content.split("\n"):

        line = line.strip()

        if not line:
            story.append(Spacer(1, 6))
            continue

        safe_line = html.escape(line)

        safe_line = re.sub(
            r"\*\*(.*?)\*\*",
            r"<b>\1</b>",
            safe_line
        )

        if line.startswith("# "):

            story.append(
                Paragraph(
                    html.escape(line[2:]),
                    title_style
                )
            )

        elif line.startswith("## ") or line.startswith("### "):

            heading = line.lstrip("#").strip()

            story.append(
                Paragraph(
                    html.escape(heading),
                    heading_style
                )
            )

        elif line.startswith("- ") or line.startswith("* "):

            story.append(
                Paragraph(
                    "• " + safe_line[2:],
                    body_style
                )
            )

        else:

            story.append(
                Paragraph(
                    safe_line,
                    body_style
                )
            )

    def notebook_background(canvas, doc):

        canvas.saveState()

        canvas.setStrokeColor(
            colors.HexColor("#DCE8F5")
        )

        canvas.setLineWidth(0.4)

        for y in range(40, 800, 22):

            canvas.line(35, y, 560, y)

        canvas.setStrokeColor(
            colors.HexColor("#F2A0A0")
        )

        canvas.line(55, 30, 55, 810)

        canvas.restoreState()

    if style == "Handwritten":

        doc.build(
            story,
            onFirstPage=notebook_background,
            onLaterPages=notebook_background
        )

    else:

        doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()
st.header("📚 Smart AI Learning Studio")

output_type = st.selectbox(
    "What would you like TECHNOVA AI to generate?",
    [
        "Detailed Study Notes",
        "Short Revision Notes",
        "Mind Map",
        "Memory Tricks",
        "Important Topics",
        "Exam Preparation Notes"
    ]
)

depth = st.selectbox(
    "Explanation Level",
    ["Basic", "Detailed", "Advanced"]
)

note_style = st.radio(
    "Choose your notes format",
    [
        "Handwritten Notebook Style",
        "Digital Colourful Style"
    ],
    horizontal=True
)

include_examples = st.checkbox(
    "Include real-life and textbook examples",
    value=True
)

include_exam_points = st.checkbox(
    "Highlight important examination points",
    value=True
)

include_diagrams = st.checkbox(
    "Include topic-related diagrams",
    value=True
)

include_memory = st.checkbox(
    "Include memory tricks",
    value=True
)

if st.button("🚀 Generate Learning Material"):

    if not subject.strip() or not topic.strip():

        st.warning("Enter your subject and topic first.")

    else:

        prompt = f"""
You are TECHNOVA AI, an expert subject-specific
teacher and examination preparation assistant.

SELECTED INFORMATION:

Category: {category}
Course: {course}
Subject: {subject}
Topic: {topic}
Language: {language}
Level: {depth}
Requested Output: {output_type}

IMPORTANT SUBJECT RULES:

1. Follow the selected subject strictly.
2. Do not mix unrelated subjects.
3. Do not generate mathematics formulas for English literature.
4. Do not generate literary analysis for Physics.
5. Generate formulas only when relevant to the selected topic.
6. For English literature, provide summaries,
   characters, themes and literary analysis.
7. For Biology, provide classifications,
   characteristics and correct scientific examples.
8. For Chemistry, provide chemical equations,
   reactions and periodic table information where relevant.
9. For Physics, provide laws, formulas,
   SI units and numerical examples where relevant.
10. For Mathematics, provide formulas,
    derivations and step-by-step solutions.
11. If the topic does not belong to the selected subject,
    politely identify the mismatch.

CONTENT REQUIREMENTS:

Examples: {include_examples}
Exam points: {include_exam_points}
Diagrams: {include_diagrams}
Memory tricks: {include_memory}

Create content specifically for the requested output type.

If Detailed Study Notes:
Provide introduction, definitions, explanations,
examples, important concepts and summary.

If Short Revision Notes:
Provide concise points, definitions and essential facts.

If Mind Map:
Create a structured visual hierarchy using
a readable text-based tree.

If Memory Tricks:
Create meaningful mnemonics, shortcuts and
easy memorisation techniques.

If Important Topics:
Identify concepts worth prioritising for revision.
Do not claim previous-year frequency unless
actual previous-year papers are provided.

If Exam Preparation Notes:
Provide exam-oriented explanations,
important definitions and practice questions.

Use clear Markdown formatting.

Use headings, subheadings, bullet points and tables.

Do not return JSON.
Do not return code.
Do not include unrelated information.
Do not invent examination statistics.

Return only the requested educational content.
"""

        with st.spinner(
            "TECHNOVA AI is preparing your learning material..."
        ):

            try:

                result = ask_ai(prompt)

                if not result.strip():
                    raise ValueError("Empty AI response.")

                st.session_state.generated_notes = result
                st.session_state.generated_style = note_style

                st.success("Learning material generated!")

            except Exception as e:

                st.error(
                    f"Generation failed: {e}"
                )
if "generated_notes" in st.session_state:

    content = st.session_state.generated_notes

    st.markdown("---")

    st.markdown("## 📖 Your Learning Material")

    st.markdown(content)

    st.markdown("---")

    st.subheader("📥 Download Your Notes")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("✍️ Create Handwritten PDF"):

            try:

                pdf = create_study_pdf(
                    content,
                    "Handwritten"
                )

                st.download_button(
                    "Download Handwritten Notes",
                    data=pdf,
                    file_name="TECHNOVA_Handwritten_Notes.pdf",
                    mime="application/pdf"
                )

            except Exception as e:

                st.error(f"PDF error: {e}")

    with col2:

        if st.button("💻 Create Digital PDF"):

            try:

                pdf = create_study_pdf(
                    content,
                    "Digital"
                )

                st.download_button(
                    "Download Digital Notes",
                    data=pdf,
                    file_name="TECHNOVA_Digital_Notes.pdf",
                    mime="application/pdf"
                )

            except Exception as e:

                st.error(f"PDF error: {e}")

    st.download_button(
        "⬇️ Download Markdown Notes",
        data=content,
        file_name="TECHNOVA_Notes.md",
        mime="text/markdown"
    )
st.markdown(
    "<div style='text-align:center;'>Created by ❤️ Ruchita</div>",
    unsafe_allow_html=True
)