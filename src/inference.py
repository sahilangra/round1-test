"""
Inference Logic Module.

This module implements the core RAG pipeline.
It handles:
1. Connecting to the ChromaDB vector store.
2. Performing similarity searches to retrieve context.
3. Managing conversational history for multi-turn dialogue.
4. Calling the Google Gemini LLM with the retrieved context and prompt template.
5. Integrating Langfuse observability for tracing.
"""

import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import CHROMA_PATH, EMBEDDING_MODEL_NAME, LLM_MODEL_NAME, TEMPERATURE

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# CHROMA_PATH is imported from config


def get_embedding_function():
    """
    Initializes and returns the HuggingFace embedding function.
    Returns:
        HuggingFaceEmbeddings: Local embeddings object.
    """
    # Using local HuggingFace embeddings to bypass Google API quota issues during ingestion/querying.
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)


def get_llm():
    """
    Initializes and returns the Google Gemini LLM object.
    Returns:
        ChatGoogleGenerativeAI: LangChain-compatible Gemini model.
    """
    return ChatGoogleGenerativeAI(
        model=LLM_MODEL_NAME, temperature=TEMPERATURE, google_api_key=GEMINI_API_KEY
    )


def query_model(query_text: str, chat_history: list = None) -> str:
    """
    The main coordinator for the RAG process.
    
    Args:
        query_text (str): The user's question.
        chat_history (list, optional): Previous messages in the session. Defaults to None.
        
    Returns:
        str: The generated response from the LLM, including document sources.
    """
    # 1. Initialize the embedding function and connect to the DB
    embeddings = get_embedding_function()
    
    # Check if the DB folder exists at all
    if not os.path.exists(CHROMA_PATH):
        return "The database is empty. Please go to the 'Ingestion' tab and upload some company documents first."

    # Connect to local ChromaDB
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    # Check if the DB actually contains any documents/ID vectors
    existing_items = db.get(include=[])
    if not existing_items.get("ids"):
        return "The database has no documents. Please go to the 'Ingestion' tab and upload some company documents first."

    # 2. Search the database for relevant chunks
    # k=5 means we retrieve the 5 most relevant semantic chunks
    results = db.similarity_search_with_relevance_scores(query_text, k=5)

    # 3. Construct the context string from retrieved documents for the LLM prompt
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # Extract sources for citation (unique set of filename + page number)
    sources = set()
    for doc, _score in results:
        source = doc.metadata.get("source", "Unknown Document")
        page = doc.metadata.get("page", "?")
        sources.add(f"{source} (Page {page})")

    formatted_sources = "\n".join([f"- {s}" for s in sources])

    # 4. Format Chat History into a string for the prompt
    history_str = ""
    if chat_history:
        # Take last 10 messages (including user/assistant pairs) to stay within context limits
        for msg in chat_history[-10:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_str += f"{role}: {msg['content']}\n"

    # 5. Load the centralized prompt template and format it
    from prompts.prompts import LEADERSHIP_RAG_PROMPT

    prompt_template = ChatPromptTemplate.from_template(LEADERSHIP_RAG_PROMPT)
    prompt = prompt_template.format(
        history=history_str if history_str else "No previous conversation.",
        context=context_text,
        question=query_text,
    )

    # 6. Initialize Langfuse Observability handler
    # Traces LLM calls for latency, cost, and debugging.
    from src.observability import get_langfuse_handler
    handler = get_langfuse_handler()
    
    llm = get_llm()
    # Pass Langfuse callbacks to the LLM invocation if credentials are set
    config = {"callbacks": [handler]} if handler else {}
    response = llm.invoke(prompt, config=config)
    

    # 7. Final Output Construction
    # Combine the LLM's logical reasoning with the specific citations found.
    final_output = f"{response.content}\n\n**Sources:**\n{formatted_sources}"

    return final_output
