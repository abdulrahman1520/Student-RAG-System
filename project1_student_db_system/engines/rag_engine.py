# engines/rag_engine.py
import os
import shutil
from .base import ChatEngine


from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_text_splitters import RecursiveCharacterTextSplitter 

from langchain_groq import ChatGroq

from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

PERSIST_DIR = "chroma_db"

class RagEngine(ChatEngine):
    def __init__(self, api_key, uploaded_files, session_id):
        self.session_id = session_id
        self.chat_history = [] 
        

        db_path = os.path.join(PERSIST_DIR, self.session_id)
        
        # 1. Setup Embeddings
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        #  (Persistence Check)
        if os.path.exists(db_path):
        
            self.vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)
            print(f"Loaded existing Chroma DB for session {session_id}")
        else:
            #  (Ingestion)
            
            # 2.1. Load & Process PDFs
            docs = []
            if not uploaded_files:
                 raise ValueError("PDF files are required to initialize RAG Engine.")
                 
            for uploaded_file in uploaded_files:
                # Save to temp file
                file_path = f"temp_{uploaded_file.name}"
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                loader = PyPDFLoader(file_path)
                docs.extend(loader.load())
                os.remove(file_path) # Clean up temp file
            
            # 2.2. Split Text
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)
            
            # 2.3. Create Vector Store AND PERSIST
            os.makedirs(db_path, exist_ok=True) 
            self.vectorstore = Chroma.from_documents(
                documents=splits, 
                embedding=embeddings, 
                persist_directory=db_path 
            )
            self.vectorstore.persist()
            print(f"Created and persisted new Chroma DB for session {session_id}")
            
        # 3. Setup LLM
        if not api_key:
             raise ValueError("Groq API Key is required.")
        self.llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.1-8b-instant")
        
        # 4. Setup Retriever and Chain
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5}) 
        self._setup_chains()

    #  LCEL
    def _get_standalone_question(self, query_data, contextualize_q_prompt):
    
        if not query_data["chat_history"]:
            return query_data["input"]
        
     #  LLM
        rephrase_chain = (
            contextualize_q_prompt
            | self.llm.bind(stop=["\n"]) 
            | StrOutputParser()
        )
        
        return rephrase_chain.invoke(query_data)


    def _setup_chains(self):
        # 1. Contextualize Question Prompt 
        contextualize_q_system_prompt = """Given the chat history and the latest user question, rephrase the latest question into a standalone question that can be fully understood without the chat history."""
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"), 
            ("human", "{input}"),
        ])
        
        # 2. Main RAG Prompt 
        qa_system_prompt = """You are a helpful assistant. Answer the user's question only based on the following retrieved context. If the context does not contain the answer, say 'I cannot find the answer in the provided documents.'
        
        Context: {context}"""
        
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"), 
        ])

        # 3. Contextualized Retrieval Logic (LCEL)
        
        
        question_rewriter = RunnableLambda(lambda x: self._get_standalone_question(x, contextualize_q_prompt))
        
        
        context_chain = (
            question_rewriter
            | self.retriever
            | (lambda docs: "\n\n".join(doc.page_content for doc in docs)) 
        )
        
        # 4. Final RAG Chain
        self.rag_chain = (
            RunnableParallel(
                context=context_chain, 
                input=RunnablePassthrough(), # 
                chat_history=RunnablePassthrough() 
            )
    
            | {
                "input": lambda x: x["input"]["input"], 
                "chat_history": lambda x: x["input"]["chat_history"], 
                "context": lambda x: x["context"]
            }
            | qa_prompt 
            | self.llm 
            | StrOutputParser() 
        )

    def answer(self, query: str) -> str:
       
        response = self.rag_chain.invoke({
            "input": query, 
            "chat_history": self.chat_history
        })
        
 
        self.chat_history.append(HumanMessage(content=query))
        self.chat_history.append(AIMessage(content=response))
        
        return response