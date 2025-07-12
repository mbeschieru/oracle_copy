import streamlit as st
import requests
from sqlalchemy.orm import sessionmaker
from app.infrastructure.config.db_config import engine
from app.infrastructure.db.models.project_models import ProjectModel

if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Please log in first.")
    st.stop()

BACKEND_URL = "http://localhost:8000"

# Helper to get auth header
def get_auth_header():
    token = st.session_state.token
    return {"Authorization": f"Bearer {token}"}

# Helper to get all projects as a dict {project_id: project_name}
def get_project_map():
    Session = sessionmaker(bind=engine)
    session = Session()
    projects = session.query(ProjectModel).all()
    project_map = {str(p.project_id): p.name for p in projects}
    session.close()
    return project_map

def get_employees_for_project(project_id, auth_header):
    url = f"{BACKEND_URL}/users/by_project/{project_id}"
    params = {"offset": 0, "limit": 100}
    resp = requests.get(url, params=params, headers=auth_header)
    if resp.status_code == 200:
        return resp.json()
    return []

def dashboard():
    st.title("👥 Endava Employees")
    user = st.session_state.user
    page = st.session_state.get("emp_page", 0)
    limit = 10
    offset = page * limit

    # Always show all users, sorted by project and grade
    url = f"{BACKEND_URL}/users/"
    params = {"offset": offset, "limit": limit}
    resp = requests.get(url, params=params, headers=get_auth_header())
    employees = resp.json() if resp.status_code == 200 else []

    if not employees:
        st.info("No employees found.")
        return

    # Get project name mapping
    project_map = get_project_map()
    # Sort by seniority (grade), then by project name
    seniority_order = {'senior': 0, 'mid': 1, 'junior': 2}
    employees.sort(key=lambda e: (seniority_order.get(e.get('grade', '').lower(), 99), project_map.get(str(e.get('project_id')), '')))

    for emp in employees:
        project_name = project_map.get(str(emp.get('project_id')), '-')
        st.markdown(f"**{emp['name']}** (<a href='mailto:{emp['email']}'>{emp['email']}</a>)  ", unsafe_allow_html=True)
        st.markdown(f"Role: {emp['role'].capitalize()} | Grade: {emp['grade']} | Project: {project_name}")
        st.markdown("---")

    col1, col2 = st.columns(2)
    if col1.button("Previous", disabled=page==0):
        st.session_state["emp_page"] = max(0, page-1)
        st.rerun()
    if col2.button("Next", disabled=len(employees)<limit):
        st.session_state["emp_page"] = page+1
        st.rerun() 