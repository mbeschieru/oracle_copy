from datetime import date, timedelta

import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"


def get_auth_header():
    token = st.session_state.token
    return {"Authorization": f"Bearer {token}"}


def get_week_start(selected_date):
    return selected_date - timedelta(days=selected_date.weekday())


def absences_dashboard():
    st.title("🛌 Absences")
    user = st.session_state.user
    st.markdown(
        f"Logged in as **{user['name']}** ({user['role'].capitalize()})"
    )

    # Week navigation state
    if "abs_week_start" not in st.session_state:
        st.session_state["abs_week_start"] = get_week_start(date.today())
    week_start = st.session_state["abs_week_start"]
    col_prev, col_date, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("⬅️ Previous week", key="abs_prev_week"):
            st.session_state["abs_week_start"] = week_start - timedelta(days=7)
            st.rerun()
    with col_next:
        if st.button("Next week ➡️", key="abs_next_week"):
            st.session_state["abs_week_start"] = week_start + timedelta(days=7)
            st.rerun()
    with col_date:
        selected_date = st.date_input(
            "📅 Select week (Monday only)",
            value=week_start,
            key="abs_date_input",
        )
        if selected_date.weekday() == 0 and selected_date != week_start:
            st.session_state["abs_week_start"] = selected_date
            st.rerun()
    week_start = st.session_state["abs_week_start"]
    st.markdown(f"**Week starting:** {week_start}")

    # User: create absence
    if user["role"] != "manager":
        st.subheader("Request Absence")
        # Only allow creation for Monday week_start
        days = st.multiselect(
            "Select absent days (in this week)",
            [week_start + timedelta(days=i) for i in range(5)],
            format_func=lambda d: d.strftime("%A, %Y-%m-%d"),
        )
        reason = st.text_input("Reason for absence")
        if st.button(
            "Submit Absence Request", disabled=not days or not reason
        ):
            payload = {
                "week_start": str(week_start),
                "days": [str(d) for d in days],
                "reason": reason,
            }
            try:
                res = requests.post(
                    f"{BACKEND_URL}/absences/",
                    json=payload,
                    headers=get_auth_header(),
                )
                if res.status_code == 200:
                    st.success("✅ Absence request submitted!")
                    st.rerun()
                else:
                    st.error(
                        f"❌ {res.json().get('detail',
                                            'Failed to submit absence')}"
                    )
            except Exception as e:
                st.error(f"🚫 Could not connect to backend: {e}")

    # Show user's absences
    st.subheader("My Absences")
    resp = requests.get(f"{BACKEND_URL}/absences/", headers=get_auth_header())
    absences = resp.json() if resp.status_code == 200 else []
    for a in absences:
        status = a.get("status", "pending")
        status_desc = a.get("status_description")
        status_color = {
            "pending": "#FFD600",
            "accepted": "#00C853",
            "declined": "#D50000",
        }.get(status, "#FFD600")
        st.markdown(
            f'<span style="background-color:{status_color}; color:black; '
            f'padding:4px 12px; border-radius:8px; font-weight:bold;">'
            f'{status.capitalize()}</span>'
        )
        st.markdown(f"**Week:** {a['week_start']}")
        st.markdown(f"**Days:** {', '.join(a['days'])}")
        st.markdown(f"**Reason:** {a['reason']}")
        if status_desc:
            st.info(f"Status note: {status_desc}")
        st.markdown("---")

    # Manager: view/approve/decline absences for project
    if user["role"] == "manager":
        st.subheader("Project Absences for Week")
        project_id = user["project_id"]
        mgr_resp = requests.get(
            f"{BACKEND_URL}/absences/project/{project_id}/week",
            params={"week_start": str(week_start)},
            headers=get_auth_header(),
        )
        mgr_absences = mgr_resp.json() if mgr_resp.status_code == 200 else []
        # Fetch all employees for the project for name lookup
        from app.presentation.streamlit_app.components.employees import (
            get_employees_for_project,
        )

        employees = get_employees_for_project(project_id, get_auth_header())
        user_map = {e["user_id"]: e for e in employees}
        # Employee availability toggle
        show_availability = st.checkbox(
            "Show Employee Availability for Week", key="show_availability"
        )
        if show_availability:
            absent_user_ids = {
                a["user_id"] for a in mgr_absences if a["status"] == "accepted"
            }
            available = [
                e for e in employees if e["user_id"] not in absent_user_ids
            ]
            absent = [e for e in employees if e["user_id"] in absent_user_ids]

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### ✅ Available Employees:")
                if available:
                    for e in available:
                        st.markdown(f"- {e['name']} ({e['email']})")
                else:
                    st.info("All employees are absent this week")

            with col2:
                st.markdown("### ❌ Absent Employees:")
                if absent:
                    for e in absent:
                        st.markdown(f"- {e['name']} ({e['email']})")
                else:
                    st.info("No absent employees this week")
        for a in mgr_absences:
            status = a.get("status", "pending")
            status_desc = a.get("status_description")
            status_color = {
                "pending": "#FFD600",
                "accepted": "#00C853",
                "declined": "#D50000",
            }.get(status, "#FFD600")
            user_info = user_map.get(a["user_id"])
            user_display = (
                user_info["name"] + f" ({user_info['email']})"
                if user_info
                else a["user_id"]
            )
            st.markdown(f"**User:** {user_display}")
            st.markdown(f"**Week:** {a['week_start']}")
            st.markdown(f"**Days:** {', '.join(a['days'])}")
            st.markdown(f"**Reason:** {a['reason']}")
            if status_desc:
                st.info(f"Status note: {status_desc}")
            if status == "pending":
                approve_desc = st.text_input(
                    f"Approval description (optional) for "
                    f"{user_info['name'] if user_info else a['user_id']}",
                    value="All ok",
                    key=f"approve_desc_{a['absence_id']}",
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(
                        "✅ Approve",
                        key=f"approve_{a['absence_id']}"
                    ):
                        approve_url = (
                            f"{BACKEND_URL}/absences/approve/{a['absence_id']}"
                        )
                        resp = requests.post(
                            approve_url,
                            json={"description": approve_desc},
                            headers=get_auth_header(),
                        )
                        if resp.status_code == 200:
                            st.success("✅ Absence approved!")
                            st.rerun()
                        else:
                            st.error(
                                f"❌ {resp.json().get('detail',
                                                     'Failed to approve '
                                                     'absence')}"
                            )
                with col2:
                    if st.button(
                        "❌ Decline",
                        key=f"decline_{a['absence_id']}"
                    ):
                        st.session_state[
                            f"show_decline_{a['absence_id']}"
                        ] = True
                    if st.session_state.get(
                        f"show_decline_{a['absence_id']}", False
                    ):
                        decline_reason = st.text_area(
                            f"Decline reason for {
                                user_info['name'] if user_info
                                else a['user_id']
                            }",
                            key=f"decline_reason_{a['absence_id']}"
                        )
                        submit_col, cancel_col = st.columns(2)
                        with submit_col:
                            if st.button(
                                "Submit Decline",
                                key=f"submit_decline_{a['absence_id']}",
                            ):
                                if not decline_reason.strip():
                                    st.warning(
                                        "Please provide a reason"
                                        +
                                        " for declining"
                                    )
                                else:
                                    decline_url = (
                                        f"{BACKEND_URL}/absences/decline/{
                                            a['absence_id']
                                        }"
                                    )
                                    resp = requests.post(
                                        decline_url,
                                        json={"description": decline_reason},
                                        headers=get_auth_header(),
                                    )
                                    if resp.status_code == 200:
                                        st.success("❌ Absence declined!")
                                        st.session_state[
                                            f"show_decline_{a['absence_id']}"
                                        ] = False
                                        st.rerun()
                                    else:
                                        st.error(
                                            f"❌ {resp.json().get(
                                                'detail',
                                                'Failed to decline absence'
                                            )}"
                                        )
                        with cancel_col:
                            if st.button(
                                "Cancel",
                                key=f"cancel_decline_{a['absence_id']}",
                            ):
                                st.session_state[
                                    f"show_decline_{a['absence_id']}"
                                ] = False
            st.markdown("---")
