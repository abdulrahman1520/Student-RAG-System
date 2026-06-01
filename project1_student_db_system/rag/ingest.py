from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
import chromadb
from chromadb.config import Settings
import os

def ingest_pdf(file_path, persist_directory=".chroma/student_rag", chunk_size=1000, chunk_overlap=200):
    os.makedirs(persist_directory, exist_ok=True)

    loader = PyPDFLoader(file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(docs)

    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    client = chromadb.Client(
        Settings(
            persist_directory=persist_directory,
            chroma_db_impl="duckdb+parquet"
        )
    )

    collection = client.get_or_create_collection(name="student_rag")

    texts = [c.page_content for c in chunks]
    metadatas = [c.metadata if hasattr(c, "metadata") else {} for c in chunks]
    ids = [f"{os.path.basename(file_path)}-{i}" for i in range(len(texts))]

    embeddings = embedder.embed_documents(texts)

    collection.add(
        documents=texts,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings
    )

    client.persist()
    return len(texts)
