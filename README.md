
# 🎓 Student Database Management System with Chatbot & RAG

A full-stack web application built with **Python (OOP)**, **Streamlit**, and **MySQL** that combines student database management with two AI chat modes — a database Q&A chatbot and a conversational RAG engine powered by LangChain.

---

## 📌 Features

### 🔐 Authentication
- Login and registration for both **Admin** and **normal users**
- Admin credentials stored in `admins.json`
- User credentials stored in `users.json`
- Passwords stored securely (no plain-text)

### 🛠️ Admin Panel (CRUD)
- Add, Update, Delete, and View students
- Full access to both chat modes
- **PDF upload to RAG engine** (admin only)

### 💬 Chat Modes (available to all users)
- **Database Q&A** — Ask questions about student data via predefined SQL-backed queries with FAQ quick-buttons
- **PDF RAG Chat** — Conversational Q&A grounded in uploaded PDF documents (admin uploads PDFs, all users can chat)

---

## 🗂️ Project Structure

```
student_management_system/
│
├── app.py                    # Main Streamlit app (auth + CRUD + chat)
├── Student.py                # Student class (OOP)
├── database.py               # Database class — MySQL CRUD operations
├── chatbot.py                # Chatbot facade — wraps any ChatEngine
├── engines/
│   ├── FAQ_engine.py         # StudentSQLEngine — queries student DB
│   └── rag_engine.py         # RagEngine — LangChain RAG pipeline
├── admins.json               # Admin credentials
├── users.json                # Registered user credentials
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR-USERNAME/student-management-system.git
cd student-management-system
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up MySQL Database
```sql
CREATE DATABASE student_db;
USE student_db;

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    age INT,
    grade VARCHAR(50)
);
```

### 5. Configure admin credentials
Create `admins.json`:
```json
{
  "admin": {
    "username": "admin",
    "password": "your_password"
  }
}
```

`users.json` is auto-created when the first user registers.

### 6. Run the app
```bash
streamlit run app.py
```

---

## 💬 How to Use

### As Admin
1. Log in with admin credentials
2. Use the sidebar to manage students (Add / View / Update / Delete)
3. Switch to **Chat Interface** from the sidebar
4. In **PDF RAG Chat** mode: enter your Groq API key, upload PDFs, and set a Session ID to initialize the RAG engine
5. Once RAG is initialized, all users can chat with the uploaded documents

### As Normal User
1. Register a new account or log in
2. Choose between **Database Q&A** or **PDF RAG Chat** from the sidebar
3. Use quick FAQ buttons for common database questions, or type freely
4. In RAG mode, chat is available once admin has initialized the engine

---

## 🧱 OOP Design (Strategy Pattern)

The chatbot uses the **Strategy Pattern** — swap the engine without touching the UI:

```
Chatbot (facade)
    └── ChatEngine (protocol/interface)
            ├── StudentSQLEngine   ← answers questions from MySQL
            └── RagEngine          ← answers questions from PDFs via LangChain
```

---

## 🔑 API Key Security

- Groq API key is entered at runtime in the UI
- Stored only in `st.session_state` — **never written to disk**

---

## 📦 Dependencies

```
streamlit
mysql-connector-python
langchain
langchain-groq
langchain-community
chromadb
pypdf
sentence-transformers
pandas
```

---

## 🚀 Future Enhancements

- SHA-256 password hashing
- Admin bulk CSV upload for students
- RAGAS evaluation for RAG quality
- Streaming token output
- Support for Pinecone / FAISS vector stores
```
