"""
Main entry point for the Insight Agent.
This module handles the sidebar navigation and page routing for the Streamlit application.
"""

import streamlit as st

st.set_page_config(
    page_title="Insight Agent", page_icon="🤖", layout="wide"
)

st.title("Insight Agent")
st.markdown("""
Welcome to the Insight Agent. 

This platform allows leadership and stakeholders to query company documents and receive concise, factual answers grounded in the organization's internal data.

### Navigation
- **Inference**: Ask open-ended strategic questions about company performance.
- **Ingestion**: Upload new annual reports, quarterly updates, and strategy notes.
""")
