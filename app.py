
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
