from langchain_chroma import Chroma 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os

CHROMA_DIR = "./vector_db"
COLLECTION_NAME = "meeting_transcript"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name = EMBEDDING_MODEL
    )

def build_vector_store(transcript: str):
    print("Building vector store")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50
    )

    docs = splitter.create_documents([transcript])

    embedding = get_embeddings()
    vector_store = Chroma.from_documents(
        docs,
        embedding = embedding,
        collection_name = COLLECTION_NAME,
        persist_directory = CHROMA_DIR
    )
    return vector_store

def load_vector_store():
    embeddings = get_embeddings()
    return Chroma(
        collection_name = COLLECTION_NAME,
        embedding_function = embeddings,
        persist_directory = CHROMA_DIR
    )

def get_retriever(vector_store: Chroma, k: int = 3):
    return vector_store.as_retriever(
        search_type = 'similarity',
        search_kwargs = {"k": k}
    )