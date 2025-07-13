import streamlit as st
import requests
from datetime import datetime, timedelta
from uuid import UUID
from streamlit_calendar import calendar
from typing import List

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
BACKEND_URL = "http://localhost:8000"        # adjust if your FastAPI runs elsewhere
TOKEN       = st.session_state.get("token")  # set at login

HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

WEEK_START = "isoWeek"   # Monday‑first, to match Teams
COLOR_ACCEPTED = "#4CAF50"  # green
COLOR_DECLINED = "#F44336"  # red
COLOR_PENDING  = "#3F51B5"  # blue (default)

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def fetch_meetings():
    resp = requests.get(f"{BACKEND_URL}/meetings", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()                     # List[MeetingReadDTO]

def fetch_attendance(meeting_id: UUID):
    resp = requests.get(f"{BACKEND_URL}/attendance/meeting/{meeting_id}", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()                     # List[MeetingAttendanceReadDTO]

def my_response(meeting_id: UUID) -> str | None:
    """Return 'accepted', 'declined' or None (pending) for the current user."""
    for att in fetch_attendance(meeting_id):
        if att["user_id"] == st.session_state.user["user_id"]:
            return att["status"]
    return None

def respond(meeting_id: UUID, status: str):
    # 1) Do we already have an attendance row?
    mine = my_response(meeting_id)
    if mine is None:
        payload = {"meeting_id": str(meeting_id), "status": status}
        requests.post(f"{BACKEND_URL}/attendance", headers=HEADERS, json=payload).raise_for_status()
    else:
        att_id = next(a["meeting_attendance_id"] for a in fetch_attendance(meeting_id)
                      if a["user_id"] == st.session_state.user["user_id"])
        params = {"status": status}
        requests.patch(f"{BACKEND_URL}/attendance/{att_id}", headers=HEADERS, params=params).raise_for_status()

# ------------------------------------------------------------------
# UI
# ------------------------------------------------------------------
def calendar_dashboard():
    st.title("📆 Calendar")

    # ---------- Week navigation ----------
    today = datetime.today()
    week_offset = st.session_state.get("cal_week_offset", 0)
    week_start_date = (today - timedelta(days=today.weekday())) + timedelta(weeks=week_offset)
    week_end_date   = week_start_date + timedelta(days=6)

    col_prev, col_title, col_next = st.columns([1, 3, 1])
    with col_prev:
        if st.button("←︎"):
            st.session_state.cal_week_offset = week_offset - 1
            st.rerun()                                    # NEW
    with col_title:
        st.subheader(f"{week_start_date:%B %d, %Y} – {week_end_date:%B %d}")
    with col_next:
        if st.button("→"):
            st.session_state.cal_week_offset = week_offset + 1
            st.rerun()                        

    #  — Fetch meetings --------------------------------------------------------
    meetings = fetch_meetings()

    # Build FullCalendar‑style event dicts
    events = []
    for m in meetings:
        start = datetime.fromisoformat(m["datetime"])
        end   = start + timedelta(minutes=m["duration_minutes"])
        status = my_response(m["meeting_id"])
        color  = COLOR_PENDING if status is None else (
                    COLOR_ACCEPTED if status == "accepted" else COLOR_DECLINED
                 )
        events.append({
            "id": m["meeting_id"],
            "title": m["title"],
            "start": start.isoformat(),
            "end":   end.isoformat(),
            "color": color,
            "extendedProps": {"status": status},
        })

    #  — Render FullCalendar ---------------------------------------------------

    clicked = calendar(
        events=events,
        options={
            "initialView": "timeGridWeek",
            "initialDate": week_start_date.strftime("%Y-%m-%d"),
            "firstDay": 1,
            "height": "auto",
            "headerToolbar": False,
        },
        key=f"calendar_{week_start_date:%Y%m%d}",          # NEW
    )
    if clicked and "event" in clicked:

        event_data = clicked["event"]
        meeting_id = UUID(event_data["id"])
        title      = event_data["title"]
        status_now = event_data.get("extendedProps", {}).get("status")

        with st.modal(f"Respond to “{title}”"):
            st.write(f"**Starts:** {event_data['start']}")
            st.write(f"**Ends:**   {event_data['end']}")
            st.write("---")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Accept",
                         key=f"acc_{meeting_id}",
                         disabled=(status_now == "accepted")):
                respond(meeting_id, "accepted")
                st.success("Accepted!")
                st.rerun()

        with col2:
            if st.button("❌ Decline",
                         key=f"dec_{meeting_id}",
                         disabled=(status_now == "declined")):
                respond(meeting_id, "declined")
                st.warning("Declined.")
                st.rerun()

    elif clicked and "event" not in clicked:
        st.info("Clicked an empty slot.")

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
