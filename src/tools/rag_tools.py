"""
RAG (Retrieval Augmented Generation) tools for document querying
"""

import os
from pathlib import Path
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from ..config import settings

FAISS_INDEX_PATH = "faiss_index"
UPLOAD_DIR = "uploads"

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FAISS_INDEX_PATH, exist_ok=True)

# Initialize embeddings with OpenAI
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=settings.OPENAI_API_KEY
)

def update_vector_store(file_path: str) -> None:
    """Loads, splits, and indexes a single document file with metadata."""
    loader = PyPDFLoader(file_path) if file_path.endswith(".pdf") else Docx2txtLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    
    # Add metadata for filtering and better display
    for doc in docs:
        doc.metadata["source"] = file_path
        doc.metadata["file_name"] = Path(file_path).name
        
    if os.path.exists(FAISS_INDEX_PATH) and os.listdir(FAISS_INDEX_PATH):
        db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        db.add_documents(docs)
    else:
        db = FAISS.from_documents(docs, embeddings)
    db.save_local(FAISS_INDEX_PATH)

@tool
def query_uploaded_documents(query: str) -> str:
    """
    Queries the content of all previously uploaded documents to answer a question.
    Returns the most relevant text chunks along with their source file name.
    """
    if not os.path.exists(FAISS_INDEX_PATH) or not os.listdir(FAISS_INDEX_PATH):
        return "No documents have been uploaded yet. Please upload a document first."
    try:
        db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        
        retrieved_docs = retriever.invoke(query)
        
        context_parts = []
        for doc in retrieved_docs:
            source = doc.metadata.get("file_name", "Unknown Source")
            content = doc.page_content
            context_parts.append(f"--- (Source: {source}) ---\n{content}")
            
        context = "\n\n".join(context_parts)
        
        return f"Relevant information from documents:\n{context}"
        
    except Exception as e:
        return f"Error querying documents: {e}"

