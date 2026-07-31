
from pathlib import Path

from langchain_community.vectorstores import FAISS

from ai_engine.services import (
    load_and_split_text,
    create_embeddings
)


# =========================================================
# PROJECT ROOT
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# KNOWLEDGE BASE FILE
# =========================================================

KNOWLEDGE_BASE = BASE_DIR / "knowledge_base.txt"


# =========================================================
# FAISS INDEX DIRECTORY
# =========================================================

FAISS_DIRECTORY = BASE_DIR / "faiss_index"


# =========================================================
# CREATE FAISS VECTORSTORE
# =========================================================

def create_vectorstore():

    chunks = load_and_split_text(
        str(KNOWLEDGE_BASE)
    )

    embeddings = create_embeddings()

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    vectorstore.save_local(
        str(FAISS_DIRECTORY)
    )

    return vectorstore


# =========================================================
# LOAD FAISS VECTORSTORE
# =========================================================

def load_vectorstore():

    embeddings = create_embeddings()

    vectorstore = FAISS.load_local(
        str(FAISS_DIRECTORY),
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore
