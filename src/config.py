"""
Configuration settings for the Insight Agent.
Centralizes model names, storage paths, and processing parameters.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Model Configurations ---

# Local embedding model (avoids Google API quota limits for ingestion)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# LLM model for generation
LLM_MODEL_NAME = "gemini-2.5-flash"

# Controls randomness: 0.1 is very factual/stable, suitable for report analysis
TEMPERATURE = 0.1

# --- Storage Paths ---

# Local directory where ChromaDB stores the vector database
CHROMA_PATH = "chroma_db"

# --- Processing Parameters ---

# Size of document chunks (in tokens/characters depending on splitter)
CHUNK_SIZE = 1000

# Overlap ensures context is preserved between consecutive chunks
CHUNK_OVERLAP = 200

# --- Langfuse Observability ---

# Credentials for Langfuse tracing
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY")
LANGFUSE_BASE_URL = os.environ.get("LANGFUSE_BASE_URL", "http://localhost:3000")
