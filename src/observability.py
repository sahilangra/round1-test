"""
Observability Module.

Provides integration with Langfuse for tracing LLM calls and document processing.
Ensures that the application fails gracefully if Langfuse is not configured or available.
"""

import logging
import os
from src.config import LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_BASE_URL

# Configure logging for the module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_langfuse_handler():
    """
    Initializes and returns the Langfuse callback handler for LangChain.
    
    This function performs a proactive authentication check to prevent 
    runtime errors during LLM calls.
    
    Returns:
        CallbackHandler: A Langfuse handler if auth is successful.
        None: If credentials are missing, auth fails, or the package is not installed.
    """
    if not LANGFUSE_SECRET_KEY or not LANGFUSE_PUBLIC_KEY:
        logger.warning("Langfuse credentials missing. Observability disabled.")
        return None

    try:
        from langfuse import Langfuse
        from langfuse.langchain import CallbackHandler
        
        # Initialize a standalone client to verify connectivity
        # This prevents the application from hanging/crashing later if the host is down.
        langfuse_client = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_BASE_URL
        )
        
        # Explicit authentication check
        if langfuse_client.auth_check():
            logger.info("Successfully connected to Langfuse")
            
            # Note: The LangChain CallbackHandler (v4.0.0+) only requires the public key
            # as it inherits the global environment/config for other parameters.
            handler = CallbackHandler(public_key=LANGFUSE_PUBLIC_KEY)
            return handler
        else:
            logger.error("Langfuse authentication failed. Check your Secret/Public keys.")
            return None
            
    except ImportError:
        logger.error("langfuse package not found. Tracing is disabled.")
        return None
    except Exception as e:
        logger.error(f"Error initializing Langfuse: {e}")
        return None
