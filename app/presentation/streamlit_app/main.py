import os
import sys

import requests
import streamlit as st

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
)


# ========== CONFIG ==========
BACKEND_URL = "http://localhost:8000"  # FastAPI must be running locally

# ========== SESSION STATE SETUP ==========
if "user" not in st.session_state:
    st.session_state.user = None
if "token" not in st.session_state:
    st.session_state.token = None


# ========== LOGIN FORM ==========
def login():
    st.set_page_config(initial_sidebar_state="collapsed")
    st.title("🕒 Oracle Timesheet Clone")
    st.subheader("Login")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your work email")
        password = st.text_input(
            "Password", type="password", placeholder="Enter your password"
        )
        submit = st.form_submit_button("Login")

        if submit and email and password:
            try:
                res = requests.post(
                    f"{BACKEND_URL}/users/login",
                    json={"email": email, "password": password},
                )
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.user = data["user"]
                    st.session_state.token = data["access_token"]
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
    st.sidebar.markdown(
        f"**Hello, {user['name']} ({user['role'].capitalize()})**"
    )
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.token = None
        st.success("Logged out!")
        st.rerun()
    page = st.sidebar.radio(
        "Menu",
        ["Timesheets", "Absences", "Meetings", "Calendar", "Endava Employees"],
    )
    # User info display at top of each page
    st.info(
        f"Logged in as: {user['name']} ({user['email']})"
        f"- Role: {user['role']}"
    )
    if page == "Timesheets":
        from app.presentation.streamlit_app.components.timesheet import (
            dashboard,
        )

        dashboard()
    elif page == "Absences":
        from app.presentation.streamlit_app.components.absences import (
            absences_dashboard,
        )

        absences_dashboard()
    elif page == "Meetings":
        from app.presentation.streamlit_app.components.meetings import (
            meetings_dashboard,
        )

        meetings_dashboard()
    elif page == "Calendar":
        from app.presentation.streamlit_app.components.calendar import (
            calendar_page,
        )

        calendar_page()
    elif page == "Endava Employees":
        from app.presentation.streamlit_app.components.employees import (
            dashboard as employees_dashboard,
        )

        employees_dashboard()


# ========== ROUTER ==========
if st.session_state.user is None:
    login()
else:
    main_menu()
