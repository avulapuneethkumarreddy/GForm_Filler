import os
import streamlit as st
from pathlib import Path
from answer_retrever import rag_pipeline_with_refresh
from form_filler import fill_google_form
import shutil

# Set page configuration
st.set_page_config(
    page_title="Google Form Auto-Filler",
    page_icon="🧠",
    layout="centered"
)

# --- App Title ---
st.title("🧠 Google Form Auto-Filler")
st.write("""
This app automatically fills Google Forms using Gemini LLM — powered by your uploaded documents and general knowledge.
""")

# --- File Upload Section ---
st.header("📁 Upload Your Supporting Documents (Optional)")
uploaded_files = st.file_uploader(
    "Upload your files here (PDF, DOCX, or TXT).",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

# --- Save Uploaded Files Temporarily ---
uploaded_file_paths = []
save_dir = Path("uploaded_docs")

if uploaded_files:
    save_dir.mkdir(exist_ok=True)

    st.info("💾 Saving uploaded files...")
    for uploaded_file in uploaded_files:
        file_path = save_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        uploaded_file_paths.append(str(file_path))

# --- Show Uploaded Files ---
if uploaded_file_paths:
    st.success("✅ Uploaded files saved successfully!")
    st.write("**Uploaded File Paths:**")
    for path in uploaded_file_paths:
        st.code(path, language="bash")
else:
    st.warning("No files uploaded yet — the model will rely on common knowledge.")

# --- Form URL Input ---
st.header("🔗 Enter Google Form Link")
form_url = st.text_input("Paste your Google Form URL here:")

# --- Run Button ---
if st.button("🚀 Run Auto-Filler"):
    if not form_url:
        st.error("Please enter a valid Google Form link.")
    else:
        st.write("### 🚀 Starting the Google Form Auto-Filler Process...")
        st.write(f"📄 Using document(s): {', '.join(uploaded_file_paths) if uploaded_file_paths else 'None'}")

        try:
            with st.spinner("🧠 Generating answers from documents... Please wait..."):
                filled_form_data = rag_pipeline_with_refresh(
                    form_url,
                    uploaded_file_paths,
                    top_k=3,
                    context_refresh_interval=5
                )

            st.success("✅ Answers generated successfully!")
            st.write("---")
            for q in filled_form_data:
                st.markdown(f"**❓ Question:** {q['question']}")
                st.markdown(f"**✔️ Answer:** {q.get('answer', 'No answer found')}")
                st.write("---")

            st.info("🤖 Launching browser to auto-fill the form...")
            fill_google_form(form_url, filled_form_data)

            st.success("🎉 Process complete! The browser window has been left open for your review.")

        except Exception as e:
            st.error(f"❌ An error occurred: {e}")

        finally:
            # --- Delete uploaded files safely ---
            if save_dir.exists():
                try:
                    shutil.rmtree(save_dir)
                    # st.info("🧹 Temporary uploaded files deleted successfully.")
                except Exception as cleanup_error:
                    # st.warning(f"⚠️ Could not delete uploaded files: {cleanup_error}")
                    pass

# --- Footer ---
st.markdown("""
---
**Developed by:** Avula Puneeth Kumar Reddy  
🔹 *GoogleFormFiller Project*  
""")
