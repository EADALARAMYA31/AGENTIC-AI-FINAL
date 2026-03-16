import streamlit as st
from calender_connection import authenticate_google
from datetime import datetime, timedelta
import pytz

# -----------------------------------
# APP TITLE
# -----------------------------------
st.set_page_config(page_title="Smart Timetable AI", layout="wide")
st.title("📅 Smart Timetable AI")

# -----------------------------------
# GOOGLE AUTH
# -----------------------------------
service = authenticate_google()
st.success("✅ Connected to Google Calendar!")

TIMEZONE = pytz.timezone("Asia/Kolkata")

# -----------------------------------
# SESSION STORAGE
# -----------------------------------
if "assignments" not in st.session_state:
    st.session_state.assignments = []

# -----------------------------------
# DATE DETECTOR (NLP)
# -----------------------------------
def detect_date(query):

    today = datetime.today().date()

    if "tomorrow" in query:
        return today + timedelta(days=1)

    if "yesterday" in query:
        return today - timedelta(days=1)

    return today


# -----------------------------------
# GET EVENTS FOR DATE
# -----------------------------------
def get_events_for_date(selected_date):

    start_of_day = TIMEZONE.localize(
        datetime.combine(selected_date, datetime.min.time())
    )

    end_of_day = TIMEZONE.localize(
        datetime.combine(selected_date, datetime.max.time())
    )

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return events_result.get("items", [])


# -----------------------------------
# CONFLICT DETECTION
# -----------------------------------
def has_conflict(new_start, new_end, events):

    for event in events:

        if "dateTime" not in event["start"]:
            continue

        existing_start = datetime.fromisoformat(
            event["start"]["dateTime"]
        )

        existing_end = datetime.fromisoformat(
            event["end"]["dateTime"]
        )

        if new_start < existing_end and new_end > existing_start:
            return True

    return False


# -----------------------------------
# ACCURATE FREE TIME
# -----------------------------------
def find_free_time(events):

    if len(events) == 0:
        return ["🎉 You are free all day!"]

    free_slots = []

    work_start = TIMEZONE.localize(
        datetime.combine(datetime.today(), datetime.strptime("09:00","%H:%M").time())
    )

    work_end = TIMEZONE.localize(
        datetime.combine(datetime.today(), datetime.strptime("18:00","%H:%M").time())
    )

    current = work_start

    for event in events:

        if "dateTime" not in event["start"]:
            continue

        start = datetime.fromisoformat(event["start"]["dateTime"])
        end = datetime.fromisoformat(event["end"]["dateTime"])

        if current < start:
            free_slots.append(
                f"{current.strftime('%H:%M')} - {start.strftime('%H:%M')}"
            )

        current = max(current, end)

    if current < work_end:
        free_slots.append(
            f"{current.strftime('%H:%M')} - {work_end.strftime('%H:%M')}"
        )

    return free_slots


# -----------------------------------
# ASSIGNMENT FUNCTIONS
# -----------------------------------
def add_assignment(name, subject, deadline):

    st.session_state.assignments.append({
        "name": name,
        "subject": subject,
        "deadline": deadline
    })


def get_assignments_by_date(date):

    result = [
        a for a in st.session_state.assignments
        if a["deadline"] == date
    ]

    return result


# -----------------------------------
# REMINDER SYSTEM
# -----------------------------------
def check_deadlines():

    today = datetime.today().date()

    for a in st.session_state.assignments:
        if a["deadline"] == today:
            st.warning(f"⚠ Assignment due today: {a['name']}")

check_deadlines()

# -----------------------------------
# UPCOMING EVENTS
# -----------------------------------
st.subheader("📌 Upcoming Events")

if st.button("Show Upcoming Events"):

    now = datetime.utcnow().isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = events_result.get("items", [])

    if not events:
        st.info("No upcoming events.")
    else:
        for event in events:
            st.write("•", event.get("summary", "No title"))

# -----------------------------------
# CREATE EVENT
# -----------------------------------
st.subheader("➕ Create New Event")

col1, col2 = st.columns(2)

with col1:
    title = st.text_input("Event Title")
    date = st.date_input("Select Date")

with col2:
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    priority = st.selectbox("Priority", ["High","Medium","Low"])

if st.button("Create Event"):

    if not title:
        st.error("Enter event title")

    elif start_time >= end_time:
        st.error("End time must be after start time")

    else:

        new_start = TIMEZONE.localize(
            datetime.combine(date, start_time)
        )

        new_end = TIMEZONE.localize(
            datetime.combine(date, end_time)
        )

        events = get_events_for_date(date)

        if has_conflict(new_start, new_end, events):
            st.error("⚠️ Time conflict detected!")
        else:

            event = {
                "summary": title,
                "description": f"Priority: {priority}",
                "start": {
                    "dateTime": new_start.isoformat(),
                    "timeZone": "Asia/Kolkata",
                },
                "end": {
                    "dateTime": new_end.isoformat(),
                    "timeZone": "Asia/Kolkata",
                },
            }

            service.events().insert(
                calendarId="primary",
                body=event
            ).execute()

            st.success("✅ Event Created Successfully!")

# -----------------------------------
# ASSIGNMENT TRACKER
# -----------------------------------
st.subheader("📚 Assignment Tracker")

a_name = st.text_input("Assignment Name")
a_subject = st.text_input("Subject")
a_deadline = st.date_input("Deadline")

if st.button("Add Assignment"):

    if a_name and a_subject:
        add_assignment(a_name, a_subject, a_deadline)
        st.success("Assignment added!")
    else:
        st.error("Fill all fields")

if st.button("Show Assignments"):

    if not st.session_state.assignments:
        st.info("No assignments yet.")
    else:
        for a in st.session_state.assignments:
            st.write(
                f"📘 {a['name']} | {a['subject']} | {a['deadline']}"
            )

# -----------------------------------
# SMART ASSISTANT (FINAL)
# -----------------------------------
st.subheader("🤖 Smart Assistant")

query = st.text_input("Ask about your schedule")

if st.button("Ask Assistant"):

    q = query.lower()
    selected_date = detect_date(q)

    events = get_events_for_date(selected_date)

    # EVENTS
    if "event" in q or "meeting" in q:
        if not events:
            st.write("No events found.")
        else:
            for e in events:
                st.write("📅", e.get("summary", "No title"))

    # FREE TIME
    elif "free" in q:
        slots = find_free_time(events)
        for s in slots:
            st.write("🟢 Free:", s)

    # ASSIGNMENTS
    elif "assignment" in q:
        assignments = get_assignments_by_date(selected_date)

        if not assignments:
            st.write("No assignments.")
        else:
            for a in assignments:
                st.write(f"📘 {a['name']} - {a['deadline']}")

    else:
        st.write(
            "Try asking: 'free time tomorrow', 'today events', or 'tomorrow assignments'"
        )