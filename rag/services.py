from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def load_and_split_text(file_path):

    loader = TextLoader(
        file_path,
        encoding="utf-8"
    )

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=50,
        chunk_overlap=0
    )

    chunks = splitter.split_documents(documents)

    return chunks


def create_embeddings():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return embeddings


def create_faiss_index(file_path):

    chunks = load_and_split_text(file_path)

    embeddings = create_embeddings()

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    return vectorstore