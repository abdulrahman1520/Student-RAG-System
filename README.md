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
