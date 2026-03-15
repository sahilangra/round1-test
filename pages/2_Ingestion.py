"""
Ingestion Page - Knowledge Base Management.

This page allows administrators to:
- Upload and process PDF files.
- Monitor which files are currently indexed in the vector store.
- Delete specific files if they are outdated.
- Perform a hard reset of the entire database.
"""

import os
import shutil
import streamlit as st
import src.ingestion as process_module

# Configure page settings
st.set_page_config(page_title="Data Ingestion", page_icon="📁")

st.title("Data Ingestion Pipeline")
st.markdown(
    "Upload organization specific PDF documents. These will be chunked and vectorized for high-retrieval accuracy."
)

# Multi-file uploader component
uploaded_files = st.file_uploader(
    "Upload Company Documents (PDF)", type=["pdf"], accept_multiple_files=True
)

# --- Document Processing Loop ---
if st.button("Process Documents"):
    if not uploaded_files:
        st.warning("Please upload at least one PDF document.")
    else:
        # Create a temporary local directory to store the uploaded files for pdfplumber to read.
        os.makedirs("temp_uploads", exist_ok=True)

        saved_paths = []
        for file in uploaded_files:
            file_path = os.path.join("temp_uploads", file.name)
            with open(file_path, "wb") as f:
                # Write the binary content of the uploaded Streamlit object to a local file.
                f.write(file.getbuffer())
            saved_paths.append(file_path)

        try:
            with st.spinner(
                "Processing documents... Parsing text, extracting tables, and vectorizing chunks."
            ):
                # Trigger the backend ingestion logic
                new_chunks = process_module.process_documents(saved_paths)

            st.success(
                f"Success! Embedded {new_chunks} new pieces of information. The knowledge base is now updated."
            )
        except Exception as e:
            st.error(f"Failed to process documents. Error: {e}")

        # Cleanup: Remove temporary files immediately after processing
        shutil.rmtree("temp_uploads", ignore_errors=True)

st.divider()
st.header("Manage Knowledge Base")

# --- Database Management ---

# 1. Fetch and Display Ingested Files
files = process_module.get_ingested_files()

if not files:
    st.info("The knowledge base is currently empty. Start by uploading files above.")
else:
    st.write(f"Currently tracking **{len(files)}** unique documents:")
    for file in files:
        # Layout with columns to provide a 'Delete' button next to each filename
        col1, col2 = st.columns([0.8, 0.2])
        col1.write(f"{file}")
        if col2.button("Delete", key=file):
            process_module.delete_file(file)
            st.success(f"Removed vectors for: {file}")
            st.rerun() # Refresh list

    st.divider()

    # 2. Hard Reset Utility
    st.subheader("System Reset")
    st.warning("Clearing all data will permanently remove all vectors and the local index.")
    if st.button("Reset Knowledge Base", type="primary"):
        if process_module.clear_all_data():
            st.success("Database fully cleared.")
            st.rerun()
        else:
            st.error("Failed to fully clear the database directory (it might be locked by another process).")
