import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/extract/"
API_KEY = os.getenv("API_KEY")
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


st.set_page_config(page_title="Marksheet Extractor", layout="wide", initial_sidebar_state="collapsed")


# Session State Initialization
if 'results' not in st.session_state:
    st.session_state.results = None
if 'uploaded_files_map' not in st.session_state:
    st.session_state.uploaded_files_map = {}


# Header
st.title("📄 AI-Powered Marksheet Extractor")
st.markdown(f"Upload one or more marksheets (JPG, PNG, PDF). **Max file size: {MAX_FILE_SIZE_MB} MB per file.**")


# File Uploader
all_uploaded_files = st.file_uploader(
    "Drag and drop your marksheets here",
    type=["jpg", "jpeg", "png", "pdf"],
    accept_multiple_files=True
)


# Validate uploaded files
valid_files = []
if all_uploaded_files:

    invalid_files = []
    for f in all_uploaded_files:
        if f.size <= MAX_FILE_SIZE_BYTES:
            valid_files.append(f)
        else:
            invalid_files.append(f)


    for f in invalid_files:
        st.warning(f"**{f.name}** was not processed because it is larger than the {MAX_FILE_SIZE_MB} MB limit.")


# to extract information from valid files
if valid_files:
    if st.button("✨ Extract Information from All Valid Files", use_container_width=True, type="primary"):
        st.session_state.uploaded_files_map = {f.name: f for f in valid_files}
        
        api_files = [("files", (f.name, f.getvalue(), f.type)) for f in valid_files]
        headers = {"X-API-Key": API_KEY}
        
        with st.spinner(f"Processing {len(valid_files)} files... This may take a moment."):
            try:
                response = requests.post(API_URL, files=api_files, headers=headers)
                if response.status_code == 200:
                    st.success("Processing Successful!")
                    st.session_state.results = response.json()
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
                    st.session_state.results = None
            except requests.exceptions.RequestException as e:
                st.error(f"Connection Error: Could not connect to the API. Details: {e}")
                st.session_state.results = None


# Display Results
if st.session_state.results:
    st.header("Extraction Results", divider="rainbow")

    for result in st.session_state.results:
        filename = result.get("filename")
        data = result.get("data")
        error = result.get("error")

        original_file = st.session_state.uploaded_files_map.get(filename)

        with st.container(border=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.subheader(f"📄 {filename}")
                if original_file:
                    if original_file.type in ["image/jpeg", "image/png"]:
                        st.image(original_file, width=250)
                    elif original_file.type == "application/pdf":
                        st.info("📄 PDF file uploaded.")
            with col2:
                if error:
                    st.error(f"Could not process this file. Reason: {error}")
                elif data and original_file:
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        st.download_button(
                           label="⬇️ Download JSON",
                           data=json.dumps(data, indent=2),
                           file_name=f"{filename.split('.')[0]}_extracted.json",
                           mime="application/json",
                           key=f"json_{filename}",
                           use_container_width=True
                        )
                    with btn_col2:
                         st.download_button(
                           label=f"⬇️ Download Original File",
                           data=original_file.getvalue(),
                           file_name=original_file.name,
                           key=f"original_{filename}",
                           use_container_width=True
                        )
                    with st.expander("👁️ View Extracted JSON"):
                        st.json(data)
                        