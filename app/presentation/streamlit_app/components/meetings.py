import pandas as pd
import requests
import streamlit as st

# Check if user is logged in
if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Please log in first.")
    st.stop()

BACKEND_URL = "http://localhost:8000"


# Helper to get auth header with JWT token
def get_auth_header():
    token = st.session_state.token
    return {"Authorization": f"Bearer {token}"}


def format_duration(minutes):
    """Convert minutes to hours and minutes format"""
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}h {mins}m"
    else:
        return f"{mins}m"


def format_time(time_obj):
    """Format time object to string"""
    if hasattr(time_obj, "strftime"):
        return time_obj.strftime("%H:%M")
    return str(time_obj)


def meetings_dashboard():
    st.title("📅 Meetings & Attendance")
    st.markdown("---")

    try:
        # Get all meetings for dropdown
        response = requests.get(
            f"{BACKEND_URL}/meetings/", headers=get_auth_header()
        )
        if response.status_code == 200:
            meetings = response.json()

            if not meetings:
                st.warning("No meetings found.")
                return

            # Create meeting selection dropdown
            meeting_options = {
                f"{meeting['title']} ({meeting['datetime'][:10]})": meeting[
                    "meeting_id"
                ]
                for meeting in meetings
            }

            selected_meeting_label = st.selectbox(
                "Select a meeting:",
                options=list(meeting_options.keys()),
                index=0,
            )

            selected_meeting_id = meeting_options[selected_meeting_label]

            # Get selected meeting details
            meeting_response = requests.get(
                f"{BACKEND_URL}/meetings/{selected_meeting_id}",
                headers=get_auth_header(),
            )
            if meeting_response.status_code == 200:
                meeting = meeting_response.json()

                # Display meeting details
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Meeting Title", meeting["title"])
                with col2:
                    st.metric(
                        "Date & Time",
                        meeting["datetime"][:19].replace("T", " "),
                    )
                with col3:
                    st.metric(
                        "Duration",
                        format_duration(meeting["duration_minutes"]),
                    )

                st.markdown("---")

                # Pagination controls
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    page_size = st.selectbox(
                        "Items per page:", [10, 25, 50], index=0
                    )
                with col2:
                    st.markdown("### Attendance Records")
                with col3:
                    if "current_page" not in st.session_state:
                        st.session_state.current_page = 1

                    if st.button("Reset to Page 1"):
                        st.session_state.current_page = 1

                # Get attendance data
                attendance_response = requests.get(
                    f"{BACKEND_URL}/meetings/{selected_meeting_id}/attendance",
                    params={
                        "page": st.session_state.current_page,
                        "page_size": page_size,
                    },
                    headers=get_auth_header(),
                )

                if attendance_response.status_code == 200:
                    attendance_data = attendance_response.json()

                    if attendance_data["attendances"]:
                        # Create DataFrame for display
                        df_data = []
                        for attendance in attendance_data["attendances"]:
                            df_data.append(
                                {
                                    "Name": attendance["user_name"],
                                    "Email": attendance["user_email"],
                                    "Date": attendance["day"],
                                    "Check In": format_time(
                                        attendance["check_in"]
                                    ),
                                    "Check Out": format_time(
                                        attendance["check_out"]
                                    ),
                                    "Time Spent": format_duration(
                                        attendance["time_spent"]
                                    ),
                                }
                            )

                        df = pd.DataFrame(df_data)

                        # Display attendance table
                        st.dataframe(
                            df, use_container_width=True, hide_index=True
                        )

                        # Pagination controls
                        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

                        with col1:
                            if attendance_data["has_previous"]:
                                if st.button("← Previous"):
                                    st.session_state.current_page -= 1
                                    st.rerun()

                        with col2:
                            st.markdown(
                                f"**Page {attendance_data['page']} of {
                                    attendance_data['total_pages']
                                }**"
                            )

                        with col3:
                            if attendance_data["has_next"]:
                                if st.button("Next →"):
                                    st.session_state.current_page += 1
                                    st.rerun()

                        with col4:
                            st.markdown(
                                f"**Total: {attendance_data['total_count']}"
                                f" records**"
                            )

                        # Summary statistics
                        st.markdown("---")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                "Total Attendees",
                                attendance_data["total_count"],
                            )
                        with col2:
                            st.metric(
                                "Current Page",
                                f"{attendance_data['page']}/{
                                    attendance_data['total_pages']
                                }",
                            )
                        with col3:
                            st.metric("Records per Page", page_size)

                    else:
                        st.info(
                            "No attendance records found for this meeting."
                        )

                else:
                    st.error(
                        f"Error fetching attendance data: {
                            attendance_response.status_code
                        }"
                    )

            else:
                st.error(
                    f"Error fetching meeting details: {
                        meeting_response.status_code
                    }"
                )

        else:
            st.error(f"Error fetching meetings: {response.status_code}")

    except requests.exceptions.ConnectionError:
        st.error(
            "❌ Cannot connect to the API server"
        )
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
