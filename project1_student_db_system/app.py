import streamlit as st
import json
import os

from database import Database
from Student import Student

from chatbot import Chatbot
from engines.FAQ_engine import StudentSQLEngine
from engines.rag_engine import RagEngine

st.set_page_config(page_title="Student System & RAG", layout="wide")
st.title("📚 Student Management & AI Chat")

# ============================================================
# Init session state
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_type = None
    st.session_state.username = None
    st.session_state.current_mode = "db"

# Separate chat histories
if "chat_history_db" not in st.session_state:
    st.session_state.chat_history_db = []

if "chat_history_rag" not in st.session_state:
    st.session_state.chat_history_rag = []

# Load users/admin
try:
    with open("admins.json", "r") as f:
        admin_creds = json.load(f)
except:
    admin_creds = {}

try:
    with open("users.json", "r") as f:
        users = json.load(f)
except:
    users = {}


# ============================================================
# LOGIN / REGISTER
# ============================================================
if not st.session_state.logged_in:

    choice = st.radio("Choose:", ["Login", "Register"])

    # ------------------ LOGIN ------------------
    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            # Admin login
            if (
                username == admin_creds.get("admin", {}).get("username")
                and password == admin_creds.get("admin", {}).get("password")
            ):
                st.session_state.logged_in = True
                st.session_state.user_type = "admin"
                st.session_state.username = username
                st.rerun()

            # User login
            elif username in users and users[username] == password:
                st.session_state.logged_in = True
                st.session_state.user_type = "user"
                st.session_state.username = username
                st.rerun()

            else:
                st.error("Wrong credentials")

    # ------------------ REGISTER ------------------
    else:
        st.subheader("Register New User")
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")

        if st.button("Register"):
            if new_u in users:
                st.error("Username already exists")

            elif new_u and new_p:
                users[new_u] = new_p
                with open("users.json", "w") as f:
                    json.dump(users, f)
                st.success("Registered successfully!")

            else:
                st.error("Fill all fields")


# ============================================================
# LOGGED IN
# ============================================================
else:

    # Connect DB
    try:
        db = Database()
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        db = None

    # ========================================================
    # ADMIN PANEL (CRUD)
    # ========================================================
    if st.session_state.user_type == "admin":

        st.sidebar.title("Admin Panel")

        # Logout (keep RAG engine)
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

        admin_choice = st.sidebar.radio(
            "Admin Menu",
            ["Chat Interface", "Add Student", "View Students", "Update Student", "Delete Student"]
        )

        # CRUD modes
        if admin_choice != "Chat Interface":
            st.title(f"🛠️ {admin_choice}")

            if not db:
                st.warning("DB unavailable.")
            else:
                # Add
                if admin_choice == "Add Student":
                    name = st.text_input("Name")
                    age = st.number_input("Age", min_value=1, max_value=100)
                    grade = st.text_input("Grade")
                    if st.button("Add"):
                        if name and grade:
                            db.insert_student(name, age, grade)
                            st.success("Student added!")
                        else:
                            st.error("Fill all fields")

                # View
                elif admin_choice == "View Students":
                    studs = db.fetch_data()
                    if studs:
                        for s in studs:
                            st.write(s.display())
                    else:
                        st.info("No students available")

                # Update
                elif admin_choice == "Update Student":
                    sid = st.number_input("Student ID", min_value=1)
                    name = st.text_input("New Name")
                    age = st.number_input("New Age", min_value=1, max_value=100)
                    grade = st.text_input("New Grade")
                    if st.button("Update"):
                        if name and grade:
                            db.update_student(sid, name, age, grade)
                            st.success("Updated!")
                        else:
                            st.error("Fill all fields")

                # Delete
                elif admin_choice == "Delete Student":
                    sid = st.number_input("Student ID", min_value=1)
                    if st.button("Delete"):
                        db.delete_student(sid)
                        st.success("Student deleted")

            if db:
                db.close()
            st.stop()

    # ========================================================
    # CHAT INTERFACE
    # ========================================================

    # Logout for regular user
    if st.session_state.user_type == "user":
        st.sidebar.title(f"Welcome, {st.session_state.username}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    st.sidebar.divider()

    # Mode switch
    chat_mode = st.sidebar.radio("Select Chat Mode:", ["Database Q&A", "PDF RAG Chat"])
    st.session_state.current_mode = "db" if chat_mode == "Database Q&A" else "rag"

    # Clear the opposite mode history
    if st.session_state.current_mode == "db":
        st.session_state.chat_history_rag = []
    else:
        st.session_state.chat_history_db = []

    current_bot = None

    # ========================================================
    # MODE 1: DATABASE CHAT
    # ========================================================
    if st.session_state.current_mode == "db":

        st.subheader("Chat with Student Database")

        st.sidebar.subheader("FAQ")

        questions = [
            "How many students?",
            "Who is the oldest student?",
            "Who is the youngest student?",
            "Show all students",
            "What is the average age?"
        ]

        for i, q in enumerate(questions):

            if st.sidebar.button(q, key=f"faq_{i}"):
                st.session_state.selected_question = q
                st.rerun()

        if db:
            sql_engine = StudentSQLEngine(db)
            current_bot = Chatbot(sql_engine)

    # ========================================================
    # MODE 2: RAG CHAT
    # ========================================================
    else:

        st.subheader("Chat with PDF Documents")

        session_id = st.session_state.username

        # Admin RAG setup
        if st.session_state.user_type == "admin":

            st.sidebar.subheader("RAG Setup")

            api_key = st.sidebar.text_input("Groq API Key", type="password")
            uploaded_files = st.sidebar.file_uploader(
                "Upload PDFs",
                type=['pdf'],
                accept_multiple_files=True
            )

            session_id = st.sidebar.text_input("Session ID", value=session_id)

            if api_key and uploaded_files and "rag_engine_instance" not in st.session_state:
                try:
                    with st.spinner("Building RAG Engine..."):
                        engine = RagEngine(api_key, uploaded_files, session_id)
                        st.session_state.rag_engine_instance = engine
                    st.success("RAG Ready!")
                except Exception as e:
                    st.error(f"RAG Error: {e}")

        # RAG available
        if "rag_engine_instance" in st.session_state:
            current_bot = Chatbot(st.session_state.rag_engine_instance)
            st.sidebar.success("RAG Online")
        else:
            if st.session_state.user_type == "admin":
                st.sidebar.info("Upload PDFs + API Key to start.")
            else:
                st.sidebar.error("RAG Offline")
                st.info("Ask admin to initialize RAG.")

    # ========================================================
    # DISPLAY HISTORY
    # ========================================================
    history = (
        st.session_state.chat_history_db
        if st.session_state.current_mode == "db"
        else st.session_state.chat_history_rag
    )

    for msg in history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # ========================================================
    # USER INPUT
    # ========================================================
    disabled = (
        st.session_state.current_mode == "rag"
        and "rag_engine_instance" not in st.session_state
    )

    user_input = st.chat_input("Ask something...", disabled=disabled)

    final_query = st.session_state.get("selected_question") or user_input

    if final_query and current_bot:

        # Select the correct history list
        history = (
            st.session_state.chat_history_db
            if st.session_state.current_mode == "db"
            else st.session_state.chat_history_rag
        )

        # User message
        history.append({"role": "user", "content": final_query})
        with st.chat_message("user"):
            st.write(final_query)

        # Bot message
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = current_bot.respond(final_query)
                st.write(answer)

        history.append({"role": "assistant", "content": answer})

        st.session_state.selected_question = None
        st.rerun()

    if db:
        db.close()
