import streamlit as st
import requests

# ========== CONFIG ==========
BACKEND_URL = "http://localhost:8000"  # FastAPI must be running locally

# ========== SESSION STATE SETUP ==========
if "user" not in st.session_state:
    st.session_state.user = None

# ========== LOGIN FORM ==========
def login():
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
                    st.experimental_rerun()
                else:
                    st.error(f"❌ {res.json().get('detail')}")
            except Exception as e:
                st.error(f"🚫 Backend not reachable: {e}")

# ========== HOME AFTER LOGIN ==========
def main_menu():
    st.sidebar.title("👋 Welcome")
    user = st.session_state.user
    st.sidebar.markdown(f"**{user['name']}** ({user['role'].capitalize()})")

    page = st.sidebar.radio("Menu", ["Timesheets", "Attendance", "Logout"])

    if page == "Timesheets":
        from app.presentation.streamlit_app.pages import timesheets
        timesheets.dashboard()
    elif page == "Attendance":
        st.write("📅 Attendance Page (Coming Soon)")
    elif page == "Logout":
        st.session_state.user = None
        st.success("Logged out.")
        st.experimental_rerun()

# ========== ROUTER ==========
if st.session_state.user is None:
    login()
else:
    main_menu()
