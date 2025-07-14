import streamlit as st
import requests
from datetime import datetime, timedelta, time
from uuid import UUID
from typing import List

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
BACKEND_URL = "http://localhost:8000"        # adjust if your FastAPI runs elsewhere

def get_auth_header():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}

WEEK_START = "isoWeek"   # Monday‑first, to match Teams
COLOR_ACCEPTED = "#4CAF50"  # green
COLOR_DECLINED = "#F44336"  # red
COLOR_PENDING  = "#3F51B5"  # blue (default)

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def fetch_meetings():
    resp = requests.get(f"{BACKEND_URL}/meetings", headers=get_auth_header())
    resp.raise_for_status()
    return resp.json()                     # List[MeetingReadDTO]

def fetch_attendance(meeting_id: UUID):
    resp = requests.get(f"{BACKEND_URL}/attendance/meeting/{meeting_id}", headers=get_auth_header())
    resp.raise_for_status()
    return resp.json()                     # List[MeetingAttendanceReadDTO]

def my_response(meeting_id: UUID) -> str | None:
    """Return 'accepted', 'declined' or None (pending) for the current user."""
    for att in fetch_attendance(meeting_id):
        if att["user_id"] == st.session_state.user["user_id"]:
            return att["status"]
    return None

def respond(meeting_id: UUID, status: str):
    # 1) Do we already have a MeetingAttendance row?
    mine = my_response(meeting_id)
    if mine is None:
        payload = {"meeting_id": str(meeting_id), "status": status}
        requests.post(f"{BACKEND_URL}/attendance", headers=get_auth_header(), json=payload).raise_for_status()
    else:
        att_id = next(a["meeting_attendance_id"] for a in fetch_attendance(meeting_id)
                      if a["user_id"] == st.session_state.user["user_id"])
        params = {"status": status}
        requests.patch(f"{BACKEND_URL}/attendance/{att_id}", headers=get_auth_header(), params=params).raise_for_status()

# ------------------------------------------------------------------
# UI
# ------------------------------------------------------------------
def calendar_dashboard():
    user = st.session_state.user
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 12px;'>
            <span style='font-size: 2.5rem;'>📅</span>
            <span style='font-size: 2.2rem; font-weight: bold;'>Calendar</span>
        </div>
        <hr style='margin-top: 0.5rem; margin-bottom: 1.5rem;'>
    """, unsafe_allow_html=True)

    # ---------- Create Meeting Button ----------
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    if st.button("➕ Create Meeting", key="create_meeting_btn"):
        st.session_state["show_create_meeting_modal"] = True

    if st.session_state.get("show_create_meeting_modal", False):
        st.info("### Create New Meeting", icon="📝")
        meeting_title = st.text_input("Meeting Title", key="meeting_title")
        meeting_date = st.date_input("Date", key="meeting_date")
        meeting_time = st.time_input("Time", key="meeting_time")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=480, value=60, key="meeting_duration")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create", key="submit_create_meeting"):
                dt = datetime.combine(meeting_date, meeting_time)
                payload = {
                    "title": meeting_title,
                    "datetime": dt.isoformat(),
                    "duration_minutes": duration
                }
                resp = requests.post(f"{BACKEND_URL}/meetings/", headers=get_auth_header(), json=payload)
                if resp.status_code == 200 or resp.status_code == 201:
                    st.success("Meeting created! Please refresh the calendar.")
                    st.session_state["show_create_meeting_modal"] = False
                    st.session_state["calendar_needs_refresh"] = True
                else:
                    st.error(f"Failed to create meeting: {resp.text}")
        with col2:
            if st.button("Cancel", key="cancel_create_meeting"):
                st.session_state["show_create_meeting_modal"] = False
        st.markdown("<hr style='margin-top: 1.5rem; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)

    # ---------- Week navigation ----------
    today = datetime.today()
    week_offset = st.session_state.get("cal_week_offset", 0)
    week_start_date = (today - timedelta(days=today.weekday())) + timedelta(weeks=week_offset)
    week_end_date   = week_start_date + timedelta(days=6)

    col_prev, col_title, col_next = st.columns([1, 3, 1])
    with col_prev:
        if st.button("←", key="prev_week"):
            st.session_state.cal_week_offset = week_offset - 1
            st.rerun()
    with col_title:
        st.markdown(f"<h4 style='text-align:center; margin-bottom:0;'>{week_start_date:%B %d, %Y} – {week_end_date:%B %d}</h4>", unsafe_allow_html=True)
    with col_next:
        if st.button("→", key="next_week"):
            st.session_state.cal_week_offset = week_offset + 1
            st.rerun()
    st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)

    # — Fetch meetings --------------------------------------------------------
    meetings = fetch_meetings()
    # Filter meetings for the current week
    week_meetings = [m for m in meetings if week_start_date <= datetime.fromisoformat(m["datetime"]) <= week_end_date]

    # Build a dict: {day: [meetings]}
    meetings_by_day = {d: [] for d in DAYS}
    for m in week_meetings:
        dt = datetime.fromisoformat(m["datetime"])
        day_name = DAYS[dt.weekday()]
        meetings_by_day[day_name].append(m)

    # Display as a table
    st.markdown("<style>th, td {padding: 8px 12px;}</style>", unsafe_allow_html=True)
    st.write("### Week View")
    table_cols = st.columns(len(DAYS))
    for i, day in enumerate(DAYS):
        with table_cols[i]:
            st.markdown(f"**{day}**")
            for m in meetings_by_day[day]:
                start = datetime.fromisoformat(m["datetime"])
                end = start + timedelta(minutes=m["duration_minutes"])
                status = my_response(m["meeting_id"])
                color = COLOR_PENDING if status is None else (COLOR_ACCEPTED if status == "accepted" else COLOR_DECLINED)
                btn_label = f"{m['title']} ({start.strftime('%H:%M')} - {end.strftime('%H:%M')})"
                if st.button(btn_label, key=f"meeting_{m['meeting_id']}"):
                    st.session_state["selected_meeting"] = m["meeting_id"]
                st.markdown(f"<div style='height:6px;background:{color};border-radius:4px;margin-bottom:8px'></div>", unsafe_allow_html=True)

    # Meeting modal/section
    selected_meeting_id = st.session_state.get("selected_meeting")
    if selected_meeting_id:
        selected_meeting = next((m for m in week_meetings if m["meeting_id"] == selected_meeting_id), None)
        if selected_meeting:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(f"### {selected_meeting['title']}")
            start = datetime.fromisoformat(selected_meeting["datetime"])
            end = start + timedelta(minutes=selected_meeting["duration_minutes"])
            st.write(f"**Starts:** {start.strftime('%A, %b %d, %Y %H:%M')}")
            st.write(f"**Ends:** {end.strftime('%A, %b %d, %Y %H:%M')}")
            status_now = my_response(selected_meeting_id)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Accept", key=f"accept_{selected_meeting_id}", disabled=(status_now == "accepted")):
                    respond(selected_meeting_id, "accepted")
                    st.success("Accepted!")
                    st.rerun()
            with col2:
                if st.button("❌ Decline", key=f"decline_{selected_meeting_id}", disabled=(status_now == "declined")):
                    respond(selected_meeting_id, "declined")
                    st.warning("Declined.")
                    st.rerun()
            # Show accepted members
            accepted = []
            try:
                responses = fetch_attendance(selected_meeting_id)
                accepted = [resp for resp in responses if resp["status"] == "accepted"]
            except Exception:
                accepted = []
            st.markdown("---")
            st.subheader("Accepted Members")
            if accepted:
                for resp in accepted:
                    name = resp.get('user_name') or resp.get('user_id')
                    email = resp.get('user_email', '')
                    st.markdown(f"- <span style='color:#4CAF50;font-weight:bold'>{name}</span> (<span style='color:#888'>{email}</span>)", unsafe_allow_html=True)
            else:
                st.info("No members have accepted yet.")
            if st.button("Close", key="close_meeting_modal"):
                st.session_state["selected_meeting"] = None

# ------------------------------------------------------------------
# Entry point used by main menu
# ------------------------------------------------------------------
def calendar_page():
    if st.session_state.user is None or st.session_state.token is None:
        st.error("Please log in first.")
        return
    try:
        calendar_dashboard()
    except requests.HTTPError as err:
        st.error(f"Backend error: {err.response.text}")
