"""
Inference Page - Chat Interface.

This module provides the Streamlit UI for the RAG agent. 
It supports:
- Multi-turn conversation via Streamlit session state.
- Real-time chart rendering from structured JSON in LLM responses.
- Citation display for grounded answers.
"""

import streamlit as st
import json
import re
import pandas as pd
import src.inference as inference_module

# Configure page settings
st.set_page_config(page_title="Leadership Inference", page_icon="📈")

st.title("Insight Interface")
st.markdown(
    "Query the company's internal knowledge base. The agent provides factual answers with sources."
)

# --- Session State Management ---
# We store 'messages' in session state to maintain chat history across app reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar control for resetting the current conversation
with st.sidebar:
    if st.button("Clear History"):
        st.session_state.messages = []
        st.rerun()

# --- Message Display ---
# Render all previously stored messages in the chat UI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Interaction Logic ---
if prompt := st.chat_input("E.g., Hi, what can you do for me?"):
    # 1. Display and store user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        # Placeholder for streaming/loading effect
        message_placeholder = st.empty()

        try:
            with st.spinner("Analyzing documents..."):
                # Call the RAG backend
                # passing chat_history allows the agent to resolve pronouns like "it" or "that"
                response = inference_module.query_model(
                    prompt, chat_history=st.session_state.messages
                )
        except Exception as e:
            response = f"An error occurred while analyzing the documents: {e}"

        display_text = response
        chart_json = None

        # --- Dynamic Chart Rendering ---
        # The agent is instructed to wrap structured data in <chart_data> tags.
        # Here we extract that JSON and render it as a Streamlit chart.
        match = re.search(r"<chart_data>(.*?)</chart_data>", response, re.DOTALL)
        if match:
            try:
                # Parse the JSON blob
                chart_json = json.loads(match.group(1).strip())
                # Remove the raw XML/JSON from the text displayed to the user
                display_text = response.replace(match.group(0), "").strip()
            except Exception:
                # If parsing fails, we just display the raw text (fallback)
                pass

        # Display the descriptive text
        message_placeholder.markdown(display_text)

        # If a valid chart was found, render it
        if chart_json:
            st.subheader(chart_json.get("title", "Data Visualization"))
            
            # Convert JSON data to pandas for Streamlit's native charting
            df = pd.DataFrame(chart_json["data"])
            
            # Use the first column as the X-axis/Index
            index_col = df.columns[0]
            df = df.set_index(index_col)

            if chart_json.get("type") == "bar":
                st.bar_chart(df)
            else:
                st.line_chart(df)

    # Store assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response})
