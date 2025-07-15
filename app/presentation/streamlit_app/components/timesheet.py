from datetime import date, timedelta

import requests
import streamlit as st

if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Please log in first.")
    st.stop()

BACKEND_URL = "http://localhost:8000"


# Helper to get auth header
def get_auth_header():
    token = st.session_state.token
    return {"Authorization": f"Bearer {token}"}


def get_week_start(selected_date):
    return selected_date - timedelta(days=selected_date.weekday())


def dashboard():
    st.title("📊 My Timesheets")

    user = st.session_state.user
    st.markdown(
        f"Logged in as **{user['name']}** ({user['role'].capitalize()})"
    )

    # Manager: select employee
    target_user_id = user["user_id"]
    target_user_project_id = user.get("project_id")
    target_user_name = user["name"]
    if user["role"] == "manager":
        st.subheader("Select Employee")
        # Get employees by project
        params = {"offset": 0, "limit": 10}
        emp_url = f"{BACKEND_URL}/users/by_project/{user['project_id']}"
        emp_resp = requests.get(
            emp_url, params=params, headers=get_auth_header()
        )
        employees = emp_resp.json() if emp_resp.status_code == 200 else []
        emp_options = {
            f"{e['name']} ({e['email']})": (
                e["user_id"],
                e.get("project_id"),
                e["name"],
            )
            for e in employees
        }
        if emp_options:
            selected = st.selectbox("Employee", list(emp_options.keys()))
            target_user_id, target_user_project_id, target_user_name = (
                emp_options[selected]
            )
        else:
            st.info("No employees found for your project.")
            return

    # Week navigation state
    if "ts_week_start" not in st.session_state:
        st.session_state["ts_week_start"] = get_week_start(date.today())
    week_start = st.session_state["ts_week_start"]
    col_prev, col_date, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("⬅️ Previous week", key="ts_prev_week"):
            st.session_state["ts_week_start"] = week_start - timedelta(days=7)
            st.rerun()
    with col_next:
        if st.button("Next week ➡️", key="ts_next_week"):
            st.session_state["ts_week_start"] = week_start + timedelta(days=7)
            st.rerun()
    with col_date:
        selected_date = st.date_input(
            "📅 Select week (Monday only)",
            value=week_start,
            key="ts_date_input",
        )
        if selected_date.weekday() == 0 and selected_date != week_start:
            st.session_state["ts_week_start"] = selected_date
            st.rerun()
    week_start = st.session_state["ts_week_start"]
    st.markdown(f"**Week starting:** {week_start}")

    # Load existing timesheet
    ts_url = f"{BACKEND_URL}/timesheets/user/{target_user_id}/week?week_start={
        week_start
    }"
    response = requests.get(ts_url, headers=get_auth_header())

    existing_timesheet = None
    if response.status_code == 200:
        existing_timesheet = response.json()
        st.success("✅ Existing timesheet loaded.")
    else:
        if user["role"] == "manager" and target_user_id != user["user_id"]:
            st.info(
                f"{target_user_name} didn't submit their timesheet."
            )
        else:
            st.info(
                "📝 No timesheet found for this week. You can create one below."
            )

    # Show submitted timesheet entries if one exists
    if existing_timesheet:
        st.subheader("Submitted Time Entries")
        # Show status badge
        status = existing_timesheet.get("status", "pending")
        status_desc = existing_timesheet.get("status_description")
        status_color = {
            "pending": "#FFD600",  # yellow
            "accepted": "#00C853",  # green
            "declined": "#D50000",  # red
        }.get(status, "#FFD600")
        status_label = status.capitalize()
        st.markdown(
            f'<span style="background-color:{status_color}; color:black;'
            f'padding:4px 12px; border-radius:8px; font-weight:bold;">{
                status_label
            }</span>',
            unsafe_allow_html=True,
        )
        if status_desc:
            st.info(f"Status note: {status_desc}")
        for i, entry in enumerate(existing_timesheet.get("entries", []), 1):
            with st.expander(f"Entry #{i}", expanded=True):
                st.markdown(f"**Day:** {entry['day']}")
                st.markdown(f"**Hours:** {entry['hours']}")
                st.markdown(f"**Project ID:** {entry['project_id']}")
                st.markdown(f"**Description:** {entry['description']}")
        # Manager can approve/decline if status is pending
        if (
            user["role"] == "manager"
            and target_user_id != user["user_id"]
            and status == "pending"
        ):
            approve_desc = st.text_input(
                "Approval description (optional)",
                value="All ok",
                key="approve_desc",
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Approve Timesheet"):
                    approve_url = f"{BACKEND_URL}/timesheets/approve/{
                        existing_timesheet['timesheet_id']
                    }"
                    resp = requests.post(
                        approve_url,
                        json={"description": approve_desc},
                        headers=get_auth_header(),
                    )
                    if resp.status_code == 200:
                        st.success("✅ Timesheet approved!")
                        st.rerun()
                    else:
                        try:
                            error_detail = resp.json().get(
                                "detail", "Failed to approve timesheet"
                            )
                        except Exception:
                            error_detail = "Failed to approve timesheet"
                            f"(status {resp.status_code}): {resp.text}"

                        st.error(f"❌ {error_detail}")
            with col2:
                if st.button("❌ Decline Timesheet"):
                    decline_reason = st.text_area(
                        "Reason for decline", key="decline_reason_popup"
                    )
                    if st.button("Submit Decline", key="submit_decline"):
                        if not decline_reason.strip():
                            st.warning(
                                "Please provide a reason for declining."
                            )
                        else:
                            decline_url = f"{BACKEND_URL}/timesheets/decline/{
                                existing_timesheet['timesheet_id']
                            }"
                            resp = requests.post(
                                decline_url,
                                json={"description": decline_reason},
                                headers=get_auth_header(),
                            )
                            if resp.status_code == 200:
                                st.success("❌ Timesheet declined!")
                                st.rerun()
                            else:
                                try:
                                    error_detail = resp.json().get(
                                        "detail", "Failed to decline timesheet"
                                    )
                                except Exception:
                                    error_detail = "Failed to decline"
                                    f'(status {resp.status_code}): {resp.text}'
                                st.error(f"❌ {error_detail}")
    # Only allow timesheet creation for self and not for managers
    elif (
        user["role"] != "manager"
        and target_user_id == user["user_id"]
        and (
            not existing_timesheet
            or not existing_timesheet.get("approved", False)
        )
    ):
        st.subheader("Add Time Entries")

        # Standard fill state
        if "standard_entries" not in st.session_state:
            st.session_state["standard_entries"] = [None] * 5

        def fill_standard():
            week_days = [week_start + timedelta(days=i) for i in range(5)]
            st.session_state["standard_entries"] = [
                {
                    "day": d,
                    "hours": 8.0,
                    "project_id": target_user_project_id or "",
                    "description": "Worked 8 hours",
                }
                for d in week_days
            ]

        st.button("Complete Standard", on_click=fill_standard)

        entries = []
        for i in range(5):  # Max 5 entries
            with st.expander(f"Entry #{i+1}"):
                # Use standard entry if filled
                std = st.session_state["standard_entries"][i]
                entry_day = st.date_input(
                    "Day",
                    key=f"day_{i}",
                    value=(
                        std["day"] if std else week_start + timedelta(days=i)
                    ),
                )
                hours = st.number_input(
                    "Hours",
                    min_value=0.0,
                    max_value=24.0,
                    step=0.5,
                    key=f"hours_{i}",
                    value=std["hours"] if std else 0.0,
                )
                # Auto-complete project_id
                project_id = st.text_input(
                    "Project ID (UUID)",
                    value=(
                        std["project_id"]
                        if std
                        else target_user_project_id or ""
                    ),
                    key=f"project_{i}",
                    disabled=True,
                )
                description = st.text_input(
                    "Description",
                    key=f"description_{i}",
                    value=std["description"] if std else "",
                )

                if hours and project_id and description:
                    entries.append(
                        {
                            "day": str(entry_day),
                            "hours": hours,
                            "project_id": project_id,
                            "description": description,
                        }
                    )
        can_create = week_start.weekday() == 0
        if st.button("📤 Submit Timesheet", disabled=not can_create):
            payload = {"week_start": str(week_start), "entries": entries}
            try:
                res = requests.post(
                    f"{BACKEND_URL}/timesheets",
                    json=payload,
                    headers=get_auth_header(),
                )
                if res.status_code == 200:
                    st.success("✅ Timesheet submitted!")
                    st.rerun()
                else:
                    st.error(f"❌ {res.json().get('detail')}")
            except Exception as e:
                st.error(f"🚫 Could not connect to backend: {e}")
    elif target_user_id == user["user_id"] and user["role"] != "manager":
        st.warning(
            "🚫 Timesheet already submitted and approved for this week."
        )
