# app.py
import streamlit as st
import os
import tempfile
import uuid
from email_generator import EmailGenerator
from ingest import (
    create_user_vectorstore,
    create_vectorstore_from_file,
    check_vectorstore_exists,
    get_vectorstore_info,
    cleanup_user_vectorstore
)
from dotenv import load_dotenv

load_dotenv()

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="AI Cold Email Generator",
    page_icon="✉️",
    layout="wide"
)

# -------------------- CUSTOM DARK THEME CSS --------------------
st.markdown("""
<style>
    /* Global Styling */
    .stApp {
        background-color: #111827;
        font-family: "Inter", sans-serif;
        color: #e5e7eb;
    }

    /* Sticky Header */
    .top-bar {
        position: sticky;
        top: 0;
        z-index: 999;
        background: #1f2937;
        padding: 1rem 0;
        border-bottom: 1px solid #374151;
        margin-bottom: 1.5rem;
    }

    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #f3f4f6;
        text-align: center;
        margin: 0;
    }

    .sub-header {
        color: #9ca3af;
        text-align: center;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }

    /* Card */
    .card {
        background: #1f2937;
        padding: 1.5rem;
        border-radius: 14px;
        border: 1px solid #374151;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 14px rgba(0,0,0,0.5);
    }

    .card-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #f9fafb;
        margin-bottom: 1rem;
        border-bottom: 2px solid #10b981;
        padding-bottom: 0.5rem;
    }

    /* Buttons */
    .stButton button {
        background: #10b981;
        color: #111827;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.6rem;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background: #059669;
        color: #ffffff;
        transform: scale(1.05);
    }

    /* Inputs */
    .stTextArea textarea, .stTextInput input {
        background: #374151;
        color: #f9fafb;
        border: 1px solid #4b5563;
        border-radius: 8px;
        padding: 10px;
        font-size: 1rem;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border: 1px solid #10b981;
        outline: none;
    }

    /* Status Boxes */
    .status-box {
        padding: 1rem;
        border-radius: 8px;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    .status-success {
        background: #064e3b;
        border: 1px solid #10b981;
        color: #d1fae5;
    }
    .status-warning {
        background: #4b5563;
        border: 1px solid #f59e0b;
        color: #fef3c7;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1f2937;
        border-right: 1px solid #374151;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- CACHE LOADER --------------------
@st.cache_resource
def load_generator(vectorstore_path="chroma_db"):
    return EmailGenerator(vectorstore_path)

# -------------------- MAIN APP --------------------
def main():
    # Initialize session state
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    if 'vectorstore_path' not in st.session_state:
        st.session_state.vectorstore_path = f"chroma_db_{st.session_state.session_id}"
    if 'generated' not in st.session_state:
        st.session_state.generated = False
    if 'job_info' not in st.session_state:
        st.session_state.job_info = {}
    if 'email' not in st.session_state:
        st.session_state.email = ""

    # Top bar
    st.markdown('<div class="top-bar"><h1 class="main-header">✉️ AI Cold Email Generator</h1><p class="sub-header">Create personalized job application emails instantly</p></div>', unsafe_allow_html=True)

    # Step 1: Portfolio Setup
    with st.container():
        st.markdown('<div class="card"><div class="card-header">📁 Step 1: Setup Your Portfolio</div>', unsafe_allow_html=True)

        portfolio_option = st.radio("Choose input method:", ["Text Input", "File Upload"], horizontal=True)

        if portfolio_option == "Text Input":
            portfolio_text = st.text_area("Your skills and experience:", height=150, placeholder="• Python Developer with 5+ years experience\n• Expertise in Django, Flask, PostgreSQL\n• Machine Learning projects...")
            
            if st.button("Save Portfolio", key="save_text"):
                if portfolio_text.strip():
                    with st.spinner("Processing portfolio..."):
                        success, message, vs_path = create_user_vectorstore(portfolio_text, st.session_state.session_id)
                        if success:
                            st.session_state.vectorstore_path = vs_path
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.warning("Please enter your portfolio content")
        else:
            uploaded_file = st.file_uploader("Upload resume (PDF/TXT):", type=['pdf', 'txt'])
            if uploaded_file and st.button("Process Resume", key="process_file"):
                with st.spinner("Processing resume..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    success, message = create_vectorstore_from_file(tmp_path, st.session_state.vectorstore_path)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                    
                    os.unlink(tmp_path)
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 2: Job Info
    with st.container():
        st.markdown('<div class="card"><div class="card-header">🎯 Step 2: Enter Job Information</div>', unsafe_allow_html=True)

        input_option = st.radio("Select input type:", ["Job URL", "Paste Description"], horizontal=True)

        if input_option == "Job URL":
            job_input = st.text_input("Job posting URL:", placeholder="https://linkedin.com/jobs/view/...")
        else:
            job_input = st.text_area("Paste job description:", height=120, placeholder="Senior Python Developer needed...\nRequirements: 5+ years Python, Django...")

        generate_disabled = not check_vectorstore_exists(st.session_state.vectorstore_path) or not job_input.strip()

        if st.button("Generate Email", type="primary", disabled=generate_disabled):
            with st.spinner("Generating email... Please wait"):
                try:
                    email_gen = load_generator(st.session_state.vectorstore_path)
                    job_info, email = email_gen.generate_email(job_input)

                    st.session_state.job_info = job_info
                    st.session_state.email = email
                    st.session_state.generated = True
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 3: Generated Email
    with st.container():
        st.markdown('<div class="card"><div class="card-header">📨 Step 3: Your Generated Email</div>', unsafe_allow_html=True)

        if st.session_state.get('generated', False):
            with st.expander("Extracted Job Requirements", expanded=False):
                st.json(st.session_state.job_info)

            email_text = st.text_area("Your email:", st.session_state.email, height=250, label_visibility="collapsed")

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(label="Download Email", data=st.session_state.email, file_name="cold_email.txt", mime="text/plain")
            with col2:
                st.code(email_text, language="markdown")
        else:
            st.info("Please complete steps 1 and 2 to generate your email.")
        st.markdown('</div>', unsafe_allow_html=True)

    # System Status
    st.markdown("---")
    status_col1, status_col2 = st.columns(2)

    with status_col1:
        st.subheader("System Status")
        if check_vectorstore_exists(st.session_state.vectorstore_path):
            st.markdown('<div class="status-box status-success">✅ Portfolio Ready</div>', unsafe_allow_html=True)
            st.caption(get_vectorstore_info(st.session_state.vectorstore_path))
        else:
            st.markdown('<div class="status-box status-warning">⚠️ Portfolio Required</div>', unsafe_allow_html=True)

    with status_col2:
        st.subheader("Tips")
        st.caption("• Include specific skills and projects")
        st.caption("• Use recent job postings")
        st.caption("• Review email before sending")

    # Cleanup on session end (optional)
    if st.button("Clear My Data", type="secondary"):
        if cleanup_user_vectorstore(st.session_state.vectorstore_path):
            st.success("Your portfolio data has been cleared!")
            st.session_state.generated = False
            st.session_state.vectorstore_path = f"chroma_db_{st.session_state.session_id}"
            st.rerun()

if __name__ == "__main__":
    main()