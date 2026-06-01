

from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatGroq

def build_rag(api_key=None, persist_directory=".chroma/student_rag", k=4):
    """
    RAG pipeline using Groq LLM:
    - Loads Chroma DB
    - Retriever
    - Conversational Retrieval Chain
    """

    # Embedding model
    embedder = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Load Vector Store
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedder
    )

    retriever = vectordb.as_retriever(
        search_kwargs={"k": k}
    )

    # --------------------
    # Groq LLM (Llama 3)
    # --------------------
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama3-8b-8192"   
    )

    # Build RAG Chain
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    return chain
