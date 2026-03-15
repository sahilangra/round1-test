"""
Document Ingestion Module.

Handles the lifecycle of document processing:
1. Loading and parsing PDFs (including table extraction).
2. Chunking text into semantically manageable pieces.
3. Managing the ChromaDB vector store (adding, deleting, and resetting data).
4. Preventing duplicate document entries via unique chunk ID generation.
"""

import os
import pdfplumber
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHROMA_PATH, CHUNK_OVERLAP, CHUNK_SIZE, EMBEDDING_MODEL_NAME

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


def get_embedding_function():
    """
    Initializes and returns the HuggingFace embedding function.
    Returns:
        HuggingFaceEmbeddings: Local embeddings object.
    """
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)


def load_documents(pdf_paths):
    """
    Loads PDF files and extracts content using pdfplumber.
    Specifically targets both paragraph text and tabular data to ensure structural data isn't lost.
    
    Args:
        pdf_paths (list): List of absolute paths to PDF files.
        
    Returns:
        list[Document]: A list of LangChain Document objects.
    """
    all_docs = []
    for path in pdf_paths:
        try:
            with pdfplumber.open(path) as pdf:
                for idx, page in enumerate(pdf.pages):
                    page_content = []

                    # 1. Extract regular text
                    text = page.extract_text()
                    if text:
                        page_content.append(text)

                    # 2. Extract tables structurally
                    # pdfplumber detects grids and returns them as lists of lists
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            # We format the table rows with pipes (|) to help the LLM recognize the structure
                            table_str = "\n".join(
                                [" | ".join(map(str, row)) for row in table if any(row)]
                            )
                            page_content.append("\n[TABLE DATA]\n" + table_str + "\n")

                    combined_content = "\n".join(page_content)

                    # Create standard Langchain Document with useful metadata
                    if combined_content.strip():
                        doc = Document(
                            page_content=combined_content,
                            metadata={
                                "source": os.path.basename(path),
                                "page": idx + 1,
                            },
                        )
                        all_docs.append(doc)

            print(
                f"Loaded {len(pdf.pages)} pages (including tables) from {os.path.basename(path)}"
            )
        except Exception as e:
            print(f"Error loading {path}: {e}")

    return all_docs


def split_documents(documents):
    """
    Splits large documents into smaller chunks.
    Uses RecursiveCharacterTextSplitter to handle natural breaks like paragraphs and sentences.
    
    Args:
        documents (list): List of LangChain Documents.
        
    Returns:
        list: List of chunked Documents.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks):
    """
    Calculates IDs for chunks and adds them to the Chroma vector database.
    Prevents duplicate entries by checking if the calculated ID already exists.
    
    Args:
        chunks (list): List of chunked Documents.
        
    Returns:
        int: Number of new documents added.
    """
    embeddings = get_embedding_function()

    # Initialize or connect to existing Chroma db
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    # --- Unique ID Generation Logic ---
    # We create a deterministic ID: "filename:page_number:chunk_index"
    # This ensures that even if we process the same file twice, we don't duplicate vectors.
    current_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        page = chunk.metadata.get("page", 0)

        chunk_id = f"{source}:{page}"

        # If it's the same page as the last chunk, increment the index
        if chunk_id == current_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0
            current_page_id = chunk_id

        # Attach the unique ID to the chunk's metadata
        chunk.metadata["id"] = f"{chunk_id}:{current_chunk_index}"

    # Extract all calculated IDs
    chunk_ids = [chunk.metadata["id"] for chunk in chunks]

    # Query the DB for existing IDs to avoid duplicates
    existing_items = db.get(include=[])  # get all IDs
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only include chunks that are not already in the database
    new_chunks = []
    new_chunk_ids = []
    for chunk, chunk_id in zip(chunks, chunk_ids):
        if chunk_id not in existing_ids:
            new_chunks.append(chunk)
            new_chunk_ids.append(chunk_id)

    if len(new_chunks):
        print(f"Adding {len(new_chunks)} new documents to DB.")
        db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("No new documents to add.")

    return len(new_chunks)


def process_documents(pdf_paths):
    """
    High-level entry point the Streamlit UI calls to run the ingestion pipeline.
    
    Args:
        pdf_paths (list): List of file paths to process.
        
    Returns:
        int: Count of successfully added chunks.
    """
    from src.observability import get_langfuse_handler
    handler = get_langfuse_handler()
    
    # 1. Load and parse the PDFs
    docs = load_documents(pdf_paths)
    if not docs:
        return 0

    # 2. Split into semantic chunks
    chunks = split_documents(docs)
    
    # 3. Add to vector store
    new_count = add_to_chroma(chunks)
    
    # 4. Optional: Log the ingestion event to Langfuse
    if handler:
        try:
            handler.langfuse.trace(
                name="Document Ingestion",
                input={"files": [os.path.basename(p) for p in pdf_paths]},
                output={"new_chunks_added": new_count}
            )
        except Exception:
            pass # Graceful failure if Langfuse is offline
            
    return new_count


def get_ingested_files():
    """
    Queries the vector database metadata to find which unique files have been processed.
    Returns:
        list: Sorted list of filenames.
    """
    embeddings = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    # Retrieve all metadata entries from the database
    data = db.get(include=["metadatas"])
    metadatas = data["metadatas"]

    # Extract unique source filenames
    sources = set()
    for meta in metadatas:
        if "source" in meta:
            sources.add(meta["source"])

    return sorted(list(sources))


def delete_file(filename):
    """
    Removes all document segments associated with a specific filename.
    
    Args:
        filename (str): The source filename to purge.
        
    Returns:
        int: Total number of chunks deleted.
    """
    embeddings = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    # Scan the metadata for matching filenames and extract their IDs
    data = db.get(include=["metadatas"])
    ids_to_delete = []
    for i, meta in enumerate(data["metadatas"]):
        if meta.get("source") == filename:
            ids_to_delete.append(data["ids"][i])

    # Delete if any matches were found
    if ids_to_delete:
        db.delete(ids=ids_to_delete)
        return len(ids_to_delete)
    return 0


def clear_all_data():
    """
    Hard-reset of the database. Deletes all vectors and then attempts to wipe the local folder.
    Returns:
        bool: True if operation completed.
    """
    try:
        embeddings = get_embedding_function()
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

        # Get all document IDs to delete from the collection
        data = db.get(include=[])
        ids = data["ids"]

        if ids:
            db.delete(ids=ids)
            print(f"Deleted {len(ids)} documents from the collection.")

        # Attempt to wipe the folder (optional, handles stubborn SQLite locks)
        import shutil

        if os.path.exists(CHROMA_PATH):
            try:
                shutil.rmtree(CHROMA_PATH)
            except Exception as e:
                # Windows might lock files while the Streamlit server is running
                print(
                    f"Note: Could not fully delete {CHROMA_PATH} directory (likely locked), but documents have been cleared. Error: {e}"
                )
        return True
    except Exception as e:
        print(f"Error resetting database: {e}")
        return False
