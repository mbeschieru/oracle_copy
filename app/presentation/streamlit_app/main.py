import streamlit as st
import requests
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))


# ========== CONFIG ==========
BACKEND_URL = "http://localhost:8000"  # FastAPI must be running locally

# ========== SESSION STATE SETUP ==========
if "user" not in st.session_state:
    st.session_state.user = None

# ========== LOGIN FORM ==========
def login():
    st.set_page_config(initial_sidebar_state="collapsed")
    st.title("🕒 Oracle Timesheet Clone")
    st.subheader("Login")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your work email")
        submit = st.form_submit_button("Login")

        if submit and email:
            try:
                res = requests.post(f"{BACKEND_URL}/users/login", json={"email": email})
                if res.status_code == 200:
                    st.session_state.user = res.json()
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error(f"❌ {res.json().get('detail')}")
            except Exception as e:
                st.error(f"🚫 Backend not reachable: {e}")

# ========== HOME AFTER LOGIN ==========
def main_menu():
    user = st.session_state.user
    st.sidebar.title("👋 Welcome")
    st.sidebar.markdown(f"**Hello, {user['name']} ({user['role'].capitalize()})**")
    page = st.sidebar.radio("Menu", ["Timesheets", "Absences", "Endava Employees", "Logout"])
    if page == "Timesheets":
        from app.presentation.streamlit_app.components.timesheet import dashboard
        dashboard()
    elif page == "Absences":
        from app.presentation.streamlit_app.components.absences import absences_dashboard
        absences_dashboard()
    elif page == "Endava Employees":
        from app.presentation.streamlit_app.components.employees import dashboard as employees_dashboard
        employees_dashboard()
    elif page == "Logout":
        st.session_state.user = None
        st.success("Logged out.")
        st.rerun()

# ========== ROUTER ==========
if st.session_state.user is None:
    login()
else:
    main_menu()
