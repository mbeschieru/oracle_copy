import streamlit as st
import requests
from datetime import date, timedelta
from uuid import uuid4

BACKEND_URL = "http://localhost:8000"

def get_week_start(selected_date):
    return selected_date - timedelta(days=selected_date.weekday())

def dashboard():
    st.title("📊 My Timesheets")

    user = st.session_state.user
    st.markdown(f"Logged in as **{user['name']}** ({user['role'].capitalize()})")

    selected_date = st.date_input("📅 Select week", value=date.today())
    week_start = get_week_start(selected_date)
    st.markdown(f"**Week starting:** {week_start}")

    # Load existing timesheet
    ts_url = f"{BACKEND_URL}/timesheets/user/{user['user_id']}/week?week_start={week_start}"
    response = requests.get(ts_url)

    existing_timesheet = None
    if response.status_code == 200:
        existing_timesheet = response.json()
        st.success("✅ Existing timesheet loaded.")
    else:
        st.info("📝 No timesheet found for this week. You can create one below.")

    # Show form to enter time entries (if not submitted)
    if not existing_timesheet or not existing_timesheet["approved"]:
        st.subheader("Add Time Entries")

        entries = []
        for i in range(5):  # Max 5 entries
            with st.expander(f"Entry #{i+1}"):
                entry_day = st.date_input(f"Day", key=f"day_{i}", value=week_start + timedelta(days=i))
                hours = st.number_input("Hours", min_value=0.0, max_value=24.0, step=0.5, key=f"hours_{i}")
                project_id = st.text_input("Project ID (UUID)", key=f"project_{i}")
                description = st.text_input("Description", key=f"description_{i}")

                if hours and project_id and description:
                    entries.append({
                        "day": str(entry_day),
                        "hours": hours,
                        "project_id": project_id,
                        "description": description
                    })

        if st.button("📤 Submit Timesheet"):
            payload = {
                "user_id": user["user_id"],
                "week_start": str(week_start),
                "entries": entries
            }
            try:
                res = requests.post(f"{BACKEND_URL}/timesheets", json=payload)
                if res.status_code == 200:
                    st.success("✅ Timesheet submitted!")
                    st.experimental_rerun()
                else:
                    st.error(f"❌ {res.json().get('detail')}")
            except Exception as e:
                st.error(f"🚫 Could not connect to backend: {e}")
    else:
        st.warning("🚫 Timesheet already submitted and approved for this week.")
