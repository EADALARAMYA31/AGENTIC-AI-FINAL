import streamlit as st
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
from groq import Groq
from datetime import date, datetime, timedelta
import pickle
from googleapiclient.discovery import build
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

from calender_connection import (
    get_calendar_auth_url,
    handle_oauth_callback,
    load_creds,
    get_google_profile_info,
    get_calendar_service
)

from database import (
    register_user,
    login_user,
    get_events,
    get_assignments,
    get_goals,
    insert_event,
    insert_assignment,
    delete_assignment,
    insert_goal,
    delete_event,
    delete_goal,
    check_conflict,
    update_goal_progress,
    get_user_by_email  # <-- add this
)


# =========================
# CONFIG
# =========================
# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="AI Scheduler Pro MAX",
    page_icon="📅",
    layout="wide"
)

# =========================
# SESSION STATE INIT
# =========================
defaults = {
    "app_stage": "auth",
    "oauth_done": False,
    "user_id": None,
    "username": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value
# =========================
# OAUTH CALLBACK
code = st.query_params.get("code")

# IMPORTANT: prevent double execution
if code and not st.session_state.get("oauth_done"):

    st.session_state["oauth_done"] = True

    creds = handle_oauth_callback(code)

    if creds:

        profile = get_google_profile_info(creds)

        st.session_state.update({
            "user_id": 1,
            "username": profile["name"],
            "app_stage": "dashboard"
        })

        st.query_params.clear()
        st.rerun()
# =========================
# AUTH PAGE
# =========================
def auth_page():
    st.title("🔐 Smart Timetable AI")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab2:
        u = st.text_input("Username", key="su")
        p = st.text_input("Password", type="password", key="sp")

        if st.button("Signup"):
            if register_user(u, p):
                st.success("Account Created")
            else:
                st.error("User already exists")

    with tab1:
        u = st.text_input("Username", key="lu")
        p = st.text_input("Password", type="password", key="lp")

        if st.button("Login"):
            user = login_user(u, p)

            if user:
                st.session_state["user_id"] = user[0]
                st.session_state["username"] = user[1]
                st.session_state["app_stage"] = "google"
                st.session_state["oauth_processed"] = False
                st.rerun()
            else:
                st.error("Invalid login")


# =========================
# GOOGLE PAGE
# =========================
def google_page():
    handle_login_callback()   # 🔥 ADD THIS LINE

    if not st.session_state.get("user_id"):
        st.session_state["app_stage"] = "auth"
        st.rerun()

    st.title("Google Connect")

    auth_url = get_calendar_auth_url()
    st.link_button("Continue with Google", auth_url)


# =========================
# DASHBOARD
# =========================
def dashboard():
    # Clear query params once we’re safely in dashboard
    if st.session_state.get("navigation") == "🚪 Logout":
        keys_to_clear = [
            "user_id",
            "username",
            "auth_url",
            "oauth_processed",
            "google_connected",
            "app_stage"
        ]

        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

        st.session_state["app_stage"] = "auth"
        st.rerun()

    st.title("🚀 AI Scheduler Pro MAX Dashboard")
    st.markdown(f"👋 Welcome **{st.session_state['username']}**")

    # ... rest of your dashboard logic ...


    pages = [
        "🏠 Dashboard",
        "📅 Create Event",
        "📋 View Events",
        "📚 Assignments",
        "🗓️ Weekly Timetable",
        "📖 Study Planner",
        "🕒 Free Time Slots",
        "🤖 Smart Assistant",
        "🤖 AI Scheduler",
        "📈 Analytics",
        "🎯 Goals",
        "🔔 Smart Notifications",
        "🌤️ Daily Motivation",
        "⚙️ Settings",
        "❓ FAQ",
        "ℹ️ About",
        "🚪 Logout"
    ]

    # Default to Dashboard if no page set
    # Default to Dashboard if no page set
    if st.session_state.get("redirect_dashboard"):
        st.session_state["navigation"] = "🏠 Dashboard"
        st.session_state["redirect_dashboard"] = False

    page = st.sidebar.radio(
        "Navigation",
        pages,
        key="navigation"
    )


    # 🔥 ALWAYS FRESH DATA
    events = get_events(st.session_state["user_id"])
    assignments = get_assignments(st.session_state["user_id"])
    goals = get_goals(st.session_state["user_id"])

    # =========================
    # DASHBOARD HOME
    # =========================
    if page == "🏠 Dashboard":
        st.markdown("""
        <h1 style='text-align:center;color:#4CAF50;'>
            🚀 AI Scheduler Pro MAX
        </h1>
        <h4 style='text-align:center;'>
            Your Personal Productivity Command Center
        </h4>
        """, unsafe_allow_html=True)

        st.info(random.choice([
            "🚀 Success starts with today's schedule.",
            "📚 Small progress every day adds up.",
            "🔥 Discipline beats motivation.",
            "⭐ Stay consistent and trust the process.",
            "💪 Focus on one task at a time.",
            "🎯 Every completed task is a step closer to your goal."
        ]))

        # LIVE STATS
        total_events = len(events)
        total_assignments = len(assignments)
        total_goals = len(goals)
        completed_goals = len([g for g in goals if int(g[2]) >= 100])

        productivity = min(
            100,
            (total_events * 5) +
            (completed_goals * 15) +
            (total_assignments * 3)
        )

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("📅 Events", total_events)
        c2.metric("📚 Assignments", total_assignments)
        c3.metric("🎯 Goals", total_goals)
        c4.metric("✅ Completed", completed_goals)
        c5.metric("⚡ Productivity", f"{productivity}%")

        st.divider()

        # TODAY EVENTS
        st.subheader("📅 Today's Schedule")
        today = str(date.today())
        today_events = [e for e in events if str(e[2]) == today]

        if today_events:
            for e in today_events:
                st.success(f"📌 {e[1]} | ⏰ {e[3]} → {e[4]} | 🏷 {e[5]} | 🔥 {e[6]}")
        else:
            st.info("🎉 No events scheduled today")

        # UPCOMING ASSIGNMENTS
        st.divider()
        st.subheader("📚 Upcoming Assignments")

        if assignments:
            assignments = sorted(assignments, key=lambda x: str(x[3]))
            for a in assignments[:5]:
                if a[4] == "High":
                    st.error(f"🔴 {a[1]} | {a[2]} | Due: {a[3]}")
                elif a[4] == "Medium":
                    st.warning(f"🟡 {a[1]} | {a[2]} | Due: {a[3]}")
                else:
                    st.success(f"🟢 {a[1]} | {a[2]} | Due: {a[3]}")
        else:
            st.info("No assignments available")

        # GOAL PROGRESS
        st.divider()
        st.subheader("🎯 Goal Progress")

        if goals:
            for g in goals:
                st.write(f"**{g[1]}**")
                st.progress(int(g[2]))
                st.caption(f"{g[2]}% Completed")
        else:
            st.info("No goals added yet")

        # QUICK SUMMARY
        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⚡ Quick Insights")
            st.success(f"📅 You have {total_events} total events scheduled.")
            st.warning(f"📚 You have {total_assignments} assignments.")
            st.info(f"🎯 You are tracking {total_goals} goals.")

        with col2:
            st.subheader("🏆 Achievement Status")
            if productivity >= 80:
                st.success("🔥 Excellent Productivity!")
            elif productivity >= 50:
                st.warning("🚀 Good Progress! Keep Going.")
            else:
                st.error("⚠ Time to focus and complete pending tasks.")

        st.divider()

        # RECENT ACTIVITY
        st.subheader("📈 Live Activity Feed")
        if events:
            st.write(f"✅ Latest Event: {events[-1][1]}")
        if assignments:
            st.write(f"📚 Latest Assignment: {assignments[-1][1]}")
        if goals:
            st.write(f"🎯 Latest Goal: {goals[-1][1]}")

    # =========================
    # CREATE EVENT (AUTO UPDATE)
    # =========================
    elif page == "📅 Create Event":
        st.markdown("""
        <h2 style='text-align:center;color:#4CAF50;'>
            📅 Create New Event
        </h2>
        <p style='text-align:center;'>
            Schedule tasks, meetings, study sessions and sync with Google Calendar
        </p>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("📝 Event Title", placeholder="e.g. DBMS Study Session")
            d = st.date_input("📅 Event Date")
            cat = st.selectbox("🏷 Category", ["Study", "Work", "Personal", "Meeting", "Exam", "Project", "Fitness"])

        with col2:
            start = st.time_input("⏰ Start Time")
            end = st.time_input("⏰ End Time")
            pr = st.selectbox("🔥 Priority", ["High", "Medium", "Low"])

        st.divider()

        if st.button("🚀 Create Event", use_container_width=True):
            if not title.strip():
                st.error("Please enter an event title")
                st.stop()

            if start >= end:
                st.error("End time must be greater than start time")
                st.stop()
            # 🔎 Check for conflicts before saving
            conflict = check_conflict(
                st.session_state["user_id"],
                str(d),
                str(start),
                str(end)
            )


            st.write("CONFLICT RESULT:", conflict)
            if conflict:
                st.error(
                    f"⚠ Conflict detected with existing event: "
                    f"{conflict[1]} ({conflict[3]} → {conflict[4]})"
                )
                st.stop()
            if not st.session_state.get("user_id"):
                st.error("User session lost. Please login again.")
                st.stop()
            # Save to database
            insert_event(
                st.session_state["user_id"],
                title,
                str(d),
                str(start),
                str(end),
                cat,
                pr
            )
            events_after_insert = get_events(
                st.session_state["user_id"]
            )

            st.write("USER ID:", st.session_state["user_id"])
            st.write("EVENTS AFTER INSERT:", events_after_insert)
            # Google Calendar Sync
            service = get_calendar_service()
            if service:
                try:
                    service.events().insert(
                        calendarId="primary",
                        body={
                            "summary": title,
                            "description": f"Category: {cat} | Priority: {pr}",
                            "start": {
                                "dateTime": datetime.combine(d, start).isoformat(),
                                "timeZone": "Asia/Kolkata"
                            },
                            "end": {
                                "dateTime": datetime.combine(d, end).isoformat(),
                                "timeZone": "Asia/Kolkata"
                            }
                        }
                    ).execute()
                    st.success("✅ Event Created & Synced with Google Calendar")
                except Exception as e:
                    st.warning(f"Event saved locally but Google sync failed: {e}")
            else:
                st.success("✅ Event Created Successfully")

            st.markdown(f"""
            <div style="padding:12px;border-radius:8px;background:#e6f7ff;margin-top:10px;">
            🎉 <b>{title}</b> scheduled on <b>{d}</b><br>
            ⏰ {start} → {end}<br>
            🏷 {cat} | 🔥 {pr}
            </div>
            """, unsafe_allow_html=True)

            #st.balloons()

            # Force DB refresh before redirect
            _ = get_events(st.session_state["user_id"])

            # Redirect to Dashboard
            st.session_state["redirect_dashboard"] = True
            st.rerun()



    # =========================
    # VIEW EVENTS (LIVE FIX)
    # =========================
    elif page == "📋 View Events":

        st.markdown("""
        <h2 style='text-align:center;color:#4CAF50;'>
            📋 Event Manager
        </h2>
        <p style='text-align:center;'>
            View, Search, Filter and Manage all your scheduled events
        </p>
        """, unsafe_allow_html=True)

        events = get_events(st.session_state["user_id"])

        if not events:
            st.info("📭 No events available.")
            st.stop()

    # =====================================
    # SUMMARY
    # =====================================
        st.metric("📅 Total Events", len(events))

    # =====================================
    # CONVERT TO DATAFRAME
    # =====================================
        df = pd.DataFrame(
            events,
            columns=[
                "ID",
                "Title",
                "Date",
                "Start Time",
                "End Time",
                "Category",
                "Priority"
            ]
        )

    # =====================================
    # SEARCH + FILTERS
    # =====================================
        st.divider()

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            search = st.text_input(
                "🔍 Search Event",
                placeholder="Enter title..."
            )

        with c2:
            category_filter = st.selectbox(
                "🏷 Category",
                ["All"] + sorted(df["Category"].unique().tolist())
            )

        with c3:
            priority_filter = st.selectbox(
                "🔥 Priority",
                ["All", "High", "Medium", "Low"]
            )

        with c4:
            date_filter = st.date_input(
                "📅 Filter Date",
                value=None
            )

    # =====================================
    # APPLY FILTERS
    # =====================================
        filtered_df = df.copy()

        if search:
            filtered_df = filtered_df[
                filtered_df["Title"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        if category_filter != "All":
            filtered_df = filtered_df[
                filtered_df["Category"] == category_filter
            ]

        if priority_filter != "All":
            filtered_df = filtered_df[
                filtered_df["Priority"] == priority_filter
            ]

        if date_filter:
            filtered_df = filtered_df[
                filtered_df["Date"].astype(str) ==
                str(date_filter)
            ]

    # =====================================
    # TODAY EVENTS
    # =====================================
        st.divider()
        st.subheader("📌 Today's Events")

        today_events = filtered_df[
            filtered_df["Date"].astype(str) ==
            str(date.today())
        ]

        if len(today_events):
            for _, row in today_events.iterrows():
                st.success(
                    f"{row['Title']} | "
                    f"{row['Start Time']} → {row['End Time']}"
                )
        else:
            st.info("No events today")

    # =====================================
    # EVENT TABLE
    # =====================================
        st.divider()
        st.subheader("📊 All Events")

        filtered_df = filtered_df.sort_values(
            by=["Date", "Start Time"]
        )

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

    # =====================================
    # DOWNLOAD CSV
    # =====================================
        csv = filtered_df.to_csv(index=False)

        st.download_button(
            "📥 Download Events CSV",
            csv,
            file_name="events.csv",
            mime="text/csv"
        )

    # =====================================
    # EVENT ANALYTICS
    # =====================================
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏷 Category Distribution")

            cat_counts = (
                filtered_df["Category"]
                .value_counts()
                .reset_index()
            )

            cat_counts.columns = [
                "Category",
                "Count"
            ]

            fig = px.pie(
                cat_counts,
                names="Category",
                values="Count",
                title="Events by Category"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:
            st.subheader("🔥 Priority Distribution")

            pri_counts = (
                filtered_df["Priority"]
                .value_counts()
                .reset_index()
            )

            pri_counts.columns = [
                "Priority",
                "Count"
            ]

            fig2 = px.bar(
                pri_counts,
                x="Priority",
                y="Count",
                title="Events by Priority"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

    # =====================================
    # DELETE EVENT
    # =====================================
        st.divider()
        st.subheader("🗑 Delete Event")

        event_options = {
            f"{row['ID']} - {row['Title']} ({row['Date']})":
            row["ID"]
            for _, row in filtered_df.iterrows()
        }

        if event_options:

            selected_event = st.selectbox(
                "Choose Event",
                list(event_options.keys())
            )

            if st.button(
                "❌ Delete Selected Event",
                use_container_width=True
            ):

                delete_event(
                    event_options[selected_event],
                    st.session_state["user_id"]
                )

                st.success(
                    "✅ Event deleted successfully"
                )

                st.rerun()


    # =========================
    # ASSIGNMENTS (FIX)
    # =========================
    elif page == "📚 Assignments":

        st.markdown("""
        <h2 style='text-align:center;color:#4CAF50;'>
            📚 Assignment Manager
        </h2>
        <p style='text-align:center;'>
            Track assignments, deadlines and priorities
        </p>
        """, unsafe_allow_html=True)

    # =====================================
    # ADD ASSIGNMENT
    # =====================================

        st.subheader("➕ Add Assignment")

        c1, c2 = st.columns(2)

        with c1:
            name = st.text_input(
                "📝 Assignment Name",
                placeholder="DBMS Record"
            )

            subject = st.text_input(
                "📖 Subject",
                placeholder="Database Management System"
            )

        with c2:
            deadline = st.date_input(
                "📅 Deadline"
            )

            priority = st.selectbox(
                "🔥 Priority",
                ["High", "Medium", "Low"]
            )

        if st.button(
            "➕ Add Assignment",
            use_container_width=True
        ):

            if not name.strip():
                st.error("Please enter assignment name")
                st.stop()

            insert_assignment(
                st.session_state["user_id"],
                name,
                subject,
                str(deadline),
                priority
            )

            st.success("✅ Assignment Added Successfully")
            #st.balloons()

            st.rerun()

        st.divider()

    # =====================================
    # LOAD ASSIGNMENTS
    # =====================================

        assignments = get_assignments(
            st.session_state["user_id"]
        )

        if not assignments:
            st.info("📭 No assignments available")
            st.stop()

    # =====================================
    # DATAFRAME
    # =====================================

        df = pd.DataFrame(
            assignments,
            columns=[
                "ID",
                "Assignment",
                "Subject",
                "Deadline",
                "Priority"
            ]
        )

    # =====================================
    # SUMMARY METRICS
    # =====================================

        total_assignments = len(df)

        high_priority = len(
            df[df["Priority"] == "High"]
        )

        medium_priority = len(
            df[df["Priority"] == "Medium"]
        )

        low_priority = len(
            df[df["Priority"] == "Low"]
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "📚 Total",
            total_assignments
        )

        c2.metric(
            "🔴 High",
            high_priority
        )

        c3.metric(
            "🟡 Medium",
            medium_priority
        )

        c4.metric(
            "🟢 Low",
            low_priority
        )

        st.divider()

    # =====================================
    # SEARCH + FILTERS
    # =====================================

        col1, col2, col3 = st.columns(3)

        with col1:
            search = st.text_input(
                "🔍 Search Assignment"
            )

        with col2:
            priority_filter = st.selectbox(
                "Priority Filter",
                ["All", "High", "Medium", "Low"]
            )

        with col3:
            subject_filter = st.selectbox(
                "Subject Filter",
                ["All"] +
                sorted(
                    df["Subject"]
                    .dropna()
                    .unique()
                    .tolist()
                )
            )

        filtered_df = df.copy()

        if search:
            filtered_df = filtered_df[
                filtered_df["Assignment"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        if priority_filter != "All":
            filtered_df = filtered_df[
                filtered_df["Priority"]
                == priority_filter
            ]

        if subject_filter != "All":
            filtered_df = filtered_df[
                filtered_df["Subject"]
                == subject_filter
            ]

    # =====================================
    # UPCOMING + OVERDUE ALERTS
    # =====================================

        st.divider()

        st.subheader("⏳ Deadline Alerts")

        today = date.today()

        overdue_count = 0

        for _, row in filtered_df.iterrows():

            due_date = pd.to_datetime(
                row["Deadline"]
            ).date()

            days_left = (
                due_date - today
            ).days

            if days_left < 0:

                overdue_count += 1

                st.error(
                    f"🚨 OVERDUE: "
                    f"{row['Assignment']} "
                    f"({abs(days_left)} days late)"
                )

            elif days_left <= 2:

                st.error(
                    f"⚠ {row['Assignment']} "
                    f"({days_left} days left)"
                )

            elif days_left <= 7:

                st.warning(
                    f"📅 {row['Assignment']} "
                    f"({days_left} days left)"
                )

        if overdue_count == 0:
            st.success("✅ No overdue assignments")

    # =====================================
    # ASSIGNMENT CARDS
    # =====================================

        st.divider()

        st.subheader("📚 Assignment Cards")

        for _, row in filtered_df.iterrows():

            with st.container():

                st.markdown(f"""
                ### 📘 {row['Assignment']}

                📖 Subject: **{row['Subject']}**

                📅 Deadline: **{row['Deadline']}**

                🔥 Priority: **{row['Priority']}**
                """)

                st.divider()

    # =====================================
    # TABLE VIEW
    # =====================================

        st.subheader("📋 Assignment Table")

        filtered_df = filtered_df.sort_values(
            by="Deadline"
        )

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

    # =====================================
    # DOWNLOAD CSV
    # =====================================

        csv = filtered_df.to_csv(
            index=False
        )

        st.download_button(
            "📥 Download CSV",
            csv,
            file_name="assignments.csv",
            mime="text/csv"
        )

    # =====================================
    # ANALYTICS
    # =====================================

        st.divider()

        st.subheader(
            "📊 Assignment Analytics"
        )

        if not filtered_df.empty:

            priority_counts = (
                filtered_df["Priority"]
                .value_counts()
                .reset_index()
            )

            priority_counts.columns = [
                "Priority",
                "Count"
            ]

            fig = px.pie(
                priority_counts,
                names="Priority",
                values="Count",
                title="Assignments By Priority"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # =====================================
    # DELETE ASSIGNMENT
    # =====================================

        st.divider()

        st.subheader(
            "🗑 Delete Assignment"
        )

        options = {
            f"{row['ID']} - {row['Assignment']}":
            row["ID"]
            for _, row in filtered_df.iterrows()
        }

        if options:

            selected = st.selectbox(
                "Select Assignment",
                list(options.keys())
            )

            if st.button(
                "❌ Delete Assignment",
                use_container_width=True
            ):

                delete_assignment(
                    options[selected],
                    st.session_state["user_id"]
                )

                st.success(
                    "✅ Assignment Deleted"
                )

                st.rerun()

        else:
            st.info(
                "No assignments available for deletion"
            )


    # =========================
    # WEEKLY TIMETABLE (FIX)
    # =========================
    elif page == "🗓️ Weekly Timetable":

        st.markdown("""
        <h2 style='text-align:center;color:#4CAF50;'>
            🗓️ Weekly Timetable
        </h2>
        <p style='text-align:center;'>
            Automatically generated from your Events & Assignments
        </p>
        """, unsafe_allow_html=True)

    # ===================================
    # LOAD DATA
    # ===================================

        events = get_events(
            st.session_state["user_id"]
        )

        assignments = get_assignments(
            st.session_state["user_id"]
        )

    # ===================================
    # WEEK RANGE
    # ===================================

        today = date.today()

        start_week = today - timedelta(
            days=today.weekday()
        )

        end_week = start_week + timedelta(
            days=6
        )

        st.success(
            f"📅 Week: {start_week} → {end_week}"
        )

    # ===================================
    # CREATE WEEK DAYS
    # ===================================

        week_days = [
            start_week + timedelta(days=i)
            for i in range(7)
        ]

        timetable = []

    # ===================================
    # EVENTS
    # ===================================

        for e in events:

            event_date = pd.to_datetime(
                e[2]
            ).date()

            if start_week <= event_date <= end_week:

                timetable.append({
                    "Date": event_date,
                    "Type": "📅 Event",
                    "Title": e[1],
                    "Time": f"{e[3]} - {e[4]}",
                    "Priority": e[6]
                })

    # ===================================
    # ASSIGNMENTS
    # ===================================

        for a in assignments:

            due_date = pd.to_datetime(
                a[3]
            ).date()

            if start_week <= due_date <= end_week:

                timetable.append({
                    "Date": due_date,
                    "Type": "📚 Assignment",
                    "Title": a[1],
                    "Time": "Deadline",
                    "Priority": a[4]
                })

    # ===================================
    # EMPTY WEEK
    # ===================================

        if not timetable:

            st.info(
                "No activities scheduled this week."
            )

            st.stop()

    # ===================================
    # DATAFRAME
    # ===================================

        df = pd.DataFrame(
            timetable
        )

        df = df.sort_values(
            by=["Date"]
        )

    # ===================================
    # STATS
    # ===================================

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "📅 Events",
            len(
                df[df["Type"] == "📅 Event"]
            )
        )

        c2.metric(
            "📚 Assignments",
            len(
                df[df["Type"] == "📚 Assignment"]
            )
        )

        c3.metric(
            "📝 Total Activities",
            len(df)
        )

        st.divider()

    # ===================================
    # TODAY'S PLAN
    # ===================================

        st.subheader(
            "📌 Today's Schedule"
        )

        today_df = df[
            df["Date"] == today
        ]

        if not today_df.empty:

            for _, row in today_df.iterrows():

                st.success(
                    f"{row['Type']} | "
                    f"{row['Title']} | "
                    f"{row['Time']}"
                )

        else:

            st.info(
                "🎉 No activities today"
            )

    # ===================================
    # WEEKLY TIMETABLE
    # ===================================

        st.divider()

        st.subheader(
            "🗓 Weekly Timetable"
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    # ===================================
    # DAY WISE VIEW
    # ===================================

        st.divider()

        st.subheader(
            "📖 Day Wise Planner"
        )

        for day in week_days:

            st.markdown(
                f"### 📅 {day.strftime('%A')} ({day})"
            )

            day_data = df[
                df["Date"] == day
            ]

            if day_data.empty:

                st.info(
                    "Free Day 🎉"
                )

            else:

                for _, row in day_data.iterrows():

                    if row["Priority"] == "High":

                        st.error(
                            f"{row['Type']} | "
                            f"{row['Title']} | "
                            f"{row['Time']}"
                        )

                    elif row["Priority"] == "Medium":

                        st.warning(
                            f"{row['Type']} | "
                            f"{row['Title']} | "
                            f"{row['Time']}"
                        )

                    else:

                        st.success(
                            f"{row['Type']} | "
                            f"{row['Title']} | "
                            f"{row['Time']}"
                        )

    # ===================================
    # UPCOMING DEADLINES
    # ===================================

        st.divider()

        st.subheader(
            "🚨 Upcoming Deadlines"
        )

        for a in assignments:

            due = pd.to_datetime(
                a[3]
            ).date()

            days_left = (
                due - today
            ).days

            if 0 <= days_left <= 7:

                st.warning(
                    f"📚 {a[1]} "
                    f"due in {days_left} days"
                )

    # ===================================
    # WORKLOAD CHART
    # ===================================

        st.divider()

        st.subheader(
            "📊 Weekly Workload"
        )

        chart_df = (
            df.groupby("Date")
            .size()
            .reset_index(name="Tasks")
        )

        fig = px.bar(
            chart_df,
            x="Date",
            y="Tasks",
            title="Tasks Per Day"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ===================================
    # DOWNLOAD
    # ===================================

        csv = df.to_csv(
            index=False
        )

        st.download_button(
            "📥 Download Weekly Timetable",
            csv,
            file_name="weekly_timetable.csv",
            mime="text/csv"
        )


    # =========================
    # STUDY PLANNER
    # =========================
    elif page == "📖 Study Planner":

        st.markdown("""
        <h2 style='text-align:center;color:#4CAF50;'>
            📖 Smart Study Planner
        </h2>
        <p style='text-align:center;'>
            AI-powered study recommendations based on assignments and deadlines
        </p>
        """, unsafe_allow_html=True)

        assignments = get_assignments(
            st.session_state["user_id"]
        )

        events = get_events(
            st.session_state["user_id"]
        )

        today = date.today()

        if not assignments:
            st.info(
                "📭 No assignments available. Add assignments to generate study plans."
            )
            st.stop()

    # ==========================
    # BUILD STUDY TASKS
    # ==========================

        planner = []

        for a in assignments:

            due_date = pd.to_datetime(
                a[3]
            ).date()

            days_left = (
                due_date - today
            ).days

            if days_left < 0:
                urgency = "Overdue"
            elif days_left <= 2:
                urgency = "Critical"
            elif days_left <= 7:
                urgency = "High"
            else:
                urgency = "Normal"

            planner.append({
                "Assignment": a[1],
                "Subject": a[2],
                "Deadline": due_date,
                "Days Left": days_left,
                "Priority": a[4],
                "Urgency": urgency
            })

        df = pd.DataFrame(planner)

    # ==========================
    # SORT BY URGENCY
    # ==========================

        urgency_order = {
            "Overdue": 0,
            "Critical": 1,
            "High": 2,
            "Normal": 3
        }

        df["Sort"] = df["Urgency"].map(
            urgency_order
        )

        df = df.sort_values(
            by=["Sort", "Days Left"]
        )

    # ==========================
    # METRICS
    # ==========================

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "📚 Assignments",
            len(df)
        )

        c2.metric(
            "🚨 Critical",
            len(
                df[df["Urgency"] == "Critical"]
            )
        )

        c3.metric(
            "⚠ High",
            len(
                df[df["Urgency"] == "High"]
            )
        )

        c4.metric(
            "❌ Overdue",
            len(
                df[df["Urgency"] == "Overdue"]
            )
        )

        st.divider()

    # ==========================
    # TODAY'S STUDY PLAN
    # ==========================

        st.subheader(
            "📌 Today's Recommended Study Plan"
        )

        top_tasks = df.head(5)

        for _, row in top_tasks.iterrows():

            if row["Urgency"] == "Overdue":

                st.error(
                    f"🚨 {row['Assignment']} "
                    f"({row['Subject']})"
                )

            elif row["Urgency"] == "Critical":

                st.error(
                    f"🔥 {row['Assignment']} "
                    f"({row['Days Left']} days left)"
                )

            elif row["Urgency"] == "High":

                st.warning(
                    f"⚠ {row['Assignment']} "
                    f"({row['Days Left']} days left)"
                )

            else:

                st.success(
                    f"✅ {row['Assignment']}"
                )

        st.divider()

    # ==========================
    # STUDY TABLE
    # ==========================

        st.subheader(
            "📋 Complete Study Planner"
        )

        st.dataframe(
            df[
                [
                    "Assignment",
                    "Subject",
                    "Deadline",
                    "Days Left",
                    "Priority",
                    "Urgency"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

    # ==========================
    # SUBJECT ANALYSIS
    # ==========================

        st.subheader(
            "📊 Subject Workload"
        )

        subject_df = (
            df["Subject"]
            .value_counts()
            .reset_index()
        )

        subject_df.columns = [
            "Subject",
            "Count"
        ]

        fig = px.bar(
            subject_df,
            x="Subject",
            y="Count",
            title="Assignments by Subject"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.divider()

    # ==========================
    # AI RECOMMENDATION
    # ==========================

        st.subheader(
            "🤖 AI Study Recommendation"
        )

        critical = len(
            df[df["Urgency"] == "Critical"]
        )

        overdue = len(
            df[df["Urgency"] == "Overdue"]
        )

        if overdue > 0:

            st.error(
                "🚨 Finish overdue assignments immediately."
            )

        elif critical > 0:

            st.warning(
                "🔥 Focus on critical assignments first."
            )

        else:

            st.success(
                "✅ You're on track. Continue studying consistently."
            )

        st.divider()

    # ==========================
    # UPCOMING EXAMS / EVENTS
    # ==========================

        st.subheader(
            "📅 Upcoming Study Events"
        )

        future_events = []

        for e in events:

            event_date = pd.to_datetime(
                e[2]
            ).date()

            days_left = (
                event_date - today
            ).days

            if 0 <= days_left <= 7:

                future_events.append(e)

        if future_events:

            for e in future_events:

                st.info(
                    f"📌 {e[1]} | "
                    f"{e[2]} | "
                    f"{e[3]}"
                )

        else:

            st.success(
                "No upcoming study events this week."
            )

        st.divider()

    # ==========================
    # DOWNLOAD STUDY PLAN
    # ==========================

        csv = df.to_csv(
            index=False
        )

        st.download_button(
            "📥 Download Study Plan",
            csv,
            file_name="study_plan.csv",
            mime="text/csv"
        )


    # =========================
    # FREE TIME
    # =========================
    elif page == "🕒 Free Time Slots":

        st.markdown("""
        <h2 style='text-align:center;color:#4CAF50;'>
            🕒 Smart Free Time Finder
        </h2>
        <p style='text-align:center;'>
            Automatically discover available time slots in your schedule
        </p>
        """, unsafe_allow_html=True)

        selected_date = st.date_input(
            "📅 Select Date",
            value=date.today()
        )

        events = get_events(
            st.session_state["user_id"]
        )

        day_events = [
            e for e in events
            if str(e[2]) == str(selected_date)
        ]

        st.divider()

        st.subheader("📅 Scheduled Events")

        if day_events:

            day_events = sorted(
                day_events,
                key=lambda x: str(x[3])
            )

            for e in day_events:
                st.success(
                    f"📌 {e[1]} | {e[3]} → {e[4]}"
                )

        else:
            st.info(
                "No events scheduled for this day."
            )

        st.divider()

        st.subheader("🕒 Available Free Slots")

        start_day = datetime.combine(
            selected_date,
            datetime.strptime(
                "06:00",
                "%H:%M"
            ).time()
        )

        end_day = datetime.combine(
            selected_date,
            datetime.strptime(
                "23:00",
                "%H:%M"
            ).time()
        )

        free_slots = []

        current = start_day

        for event in sorted(
            day_events,
            key=lambda x: str(x[3])
        ):

            event_start = datetime.combine(
                selected_date,
                event[3]
            )

            event_end = datetime.combine(
                selected_date,
                event[4]
            )

            if current < event_start:
                free_slots.append(
                    (
                        current.time(),
                        event_start.time()
                    )
                )

            current = max(
                current,
                event_end
            )

        if current < end_day:
            free_slots.append(
                (
                    current.time(),
                    end_day.time()
                )
            )

        if free_slots:

            total_free = 0

            for start, end in free_slots:

                mins = (
                    datetime.combine(selected_date, end)
                    -
                    datetime.combine(selected_date, start)
                ).seconds / 60

                total_free += mins

                if mins >= 180:
                    st.success(
                        f"🟢 {start} → {end} "
                        f"({int(mins/60)} hrs)"
                    )

                elif mins >= 60:
                    st.warning(
                        f"🟡 {start} → {end} "
                        f"({int(mins/60)} hrs)"
                    )

                else:
                    st.info(
                        f"🔵 {start} → {end} "
                        f"({int(mins)} mins)"
                    )

            st.divider()

            c1, c2 = st.columns(2)

            c1.metric(
                "⏳ Total Free Hours",
                round(total_free/60, 1)
            )

            c2.metric(
                "🕒 Free Slots",
                len(free_slots)
            )

        else:
            st.error(
                "🚫 No free time available."
            )

        st.divider()

        st.subheader(
            "🤖 Smart Suggestions"
        )

        if free_slots:

            longest = max(
                free_slots,
                key=lambda x:
                (
                    datetime.combine(selected_date, x[1])
                    -
                    datetime.combine(selected_date, x[0])
                ).seconds
            )

            duration = (
                datetime.combine(selected_date, longest[1])
                -
                datetime.combine(selected_date, longest[0])
            ).seconds / 3600

            if duration >= 3:
                st.success(
                    "📚 Perfect time for deep study session."
                )
            elif duration >= 1:
                st.warning(
                    "📝 Good slot for assignments and revision."
                )
            else:
                st.info(
                    "☕ Ideal for a short break or quick task."
                )

        st.divider()

        st.subheader("⚡ Quick Actions")

        if st.button(
            "📖 Find Best Study Time",
            use_container_width=True
        ):
            if free_slots:
                best = max(
                    free_slots,
                    key=lambda x:
                    (
                        datetime.combine(selected_date, x[1])
                        -
                        datetime.combine(selected_date, x[0])
                    ).seconds
                )

                st.success(
                    f"""
                    Best Study Slot:

                    🕒 {best[0]} → {best[1]}
                    """
                )


    # =========================
    # AI ASSISTANT
    # =========================
    elif page == "🤖 Smart Assistant":

        st.markdown("""
        <h2 style='text-align:center;color:#4CAF50;'>
            🤖 AI Smart Assistant
        </h2>
        <p style='text-align:center;'>
            Your personal productivity coach
        </p>
        """, unsafe_allow_html=True)

    # Load user data
        events = get_events(
            st.session_state["user_id"]
        )

        assignments = get_assignments(
            st.session_state["user_id"]
        )

        goals = get_goals(
            st.session_state["user_id"]
        )

        st.info(
            "Ask me anything about your schedule, studies, assignments, goals, or productivity."
        )

    # Chat History
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_prompt = st.chat_input(
            "Ask your AI assistant..."
        )

    # Display previous messages
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if user_prompt:

            st.session_state.chat_history.append(
                {
                    "role": "user",
                    "content": user_prompt
                }
            )

            with st.chat_message("user"):
                st.write(user_prompt)

        # Build context
            context = f"""

            Student Name:
            {st.session_state['username']}

            Events:
            {events}

            Assignments:
            {assignments}

            Goals:
            {goals}

            You are a Smart Timetable AI assistant.

            Help students with:

            - Time management
            - Study plans
            - Assignments
            - Productivity
            - Scheduling
            - Goal achievement

            Be concise and helpful.

            """

            try:

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": context
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=800
                )

                answer = (
                    response
                    .choices[0]
                    .message.content
                )

            except Exception as e:

                answer = f"Error: {e}"

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

            with st.chat_message("assistant"):
                st.write(answer)


    # =========================
    # AI SCHEDULER
    # =========================
    elif page == "🤖 AI Scheduler":

        st.markdown("""
        <h2 style='text-align:center;color:#4CAF50;'>
            🤖 AI Scheduler
        </h2>
        <p style='text-align:center;'>
            Generate a personalized study timetable using AI
        </p>
        """, unsafe_allow_html=True)

        events = get_events(
            st.session_state["user_id"]
        )

        assignments = get_assignments(
            st.session_state["user_id"]
        )

        goals = get_goals(
            st.session_state["user_id"]
        )

        st.subheader("⚙ Scheduler Settings")

        col1, col2 = st.columns(2)

        with col1:
            days = st.slider(
                "Schedule Duration (Days)",
                1,
                30,
                7
            )

            study_hours = st.slider(
                "Daily Study Hours",
                1,
                12,
                4
            )

        with col2:
            schedule_type = st.selectbox(
                "Schedule Type",
                [
                    "Balanced Study Plan",
                    "Exam Preparation",
                    "Assignment Focus",
                    "Productivity Boost",
                    "Weekend Planner"
                ]
            )

            difficulty = st.selectbox(
                "Intensity",
                [
                    "Light",
                    "Moderate",
                    "Intensive"
                ]
            )

        st.divider()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "📅 Events",
            len(events)
        )

        c2.metric(
            "📚 Assignments",
            len(assignments)
        )

        c3.metric(
            "🎯 Goals",
            len(goals)
        )

        c4.metric(
            "⏳ Study Hours",
            study_hours
        )

        st.divider()

        if st.button(
            "🚀 Generate AI Schedule",
            use_container_width=True
        ):

            if not assignments and not goals:
                st.warning(
                    "Please add assignments or goals first."
                )
                st.stop()

            with st.spinner(
                "Creating your personalized timetable..."
            ):

                try:

                    prompt = f"""
                    Student Name:
                    {st.session_state['username']}

                    Existing Events:
                    {events}

                    Assignments:
                    {assignments}

                    Goals:
                    {goals}

                    Schedule Type:
                    {schedule_type}

                    Intensity:
                    {difficulty}

                    Duration:
                    {days} days

                    Daily Study Hours:
                    {study_hours}

                    Create a professional study timetable.

                    Rules:

                    1. Prioritize high priority assignments.
                    2. Respect existing calendar events.
                    3. Include revision sessions.
                    4. Include breaks.
                    5. Suggest best study times.
                    6. Avoid burnout.
                    7. Return schedule day-by-day.
                    8. Use neat formatting.
                    """

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {
                                "role": "system",
                                "content":
                                "You are an expert academic planner."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.5,
                        max_tokens=2500
                    )

                    plan = (
                        response
                        .choices[0]
                        .message.content
                    )

                    st.success(
                        "✅ AI Timetable Generated Successfully"
                    )

                    st.markdown(plan)

                    st.download_button(
                        "📥 Download Schedule",
                        data=plan,
                        file_name="AI_Schedule.txt",
                        mime="text/plain"
                    )

                except Exception as e:

                    st.error(
                        f"AI Scheduler Error: {e}"
                    )

        st.divider()

        st.subheader("⚡ Quick Schedule Generators")

        q1, q2, q3 = st.columns(3)

        with q1:
            if st.button("📚 Exam Planner"):
                st.info(
                    "Generate a focused exam preparation timetable."
                )

        with q2:
            if st.button("📝 Assignment Planner"):
                st.info(
                    "Generate assignment completion schedule."
                )

        with q3:
            if st.button("🎯 Goal Planner"):
                st.info(
                    "Generate goal achievement roadmap."
                )

        st.divider()

        st.subheader("💡 AI Scheduling Tips")

        tips = [
            "Study difficult subjects during high-energy hours.",
            "Take a 5–10 minute break every hour.",
            "Finish assignments before the deadline week.",
            "Reserve weekends for revision and projects.",
            "Track goal progress regularly."
        ]

        st.info(random.choice(tips))


    # =========================
    # ANALYTICS
    # =========================
    elif page == "📈 Analytics":

        st.markdown("""
        <h2 style='text-align:center;color:#4CAF50;'>
            📈 Productivity Analytics
        </h2>
        <p style='text-align:center;'>
            Real-time insights from your timetable
        </p>
        """, unsafe_allow_html=True)

        events = get_events(
            st.session_state["user_id"]
        )

        assignments = get_assignments(
            st.session_state["user_id"]
        )

        goals = get_goals(
            st.session_state["user_id"]
        )

    # ==========================
    # TOP METRICS
    # ==========================

        total_events = len(events)
        total_assignments = len(assignments)
        total_goals = len(goals)

        completed_goals = len([
            g for g in goals
            if int(g[2]) >= 100
        ])

        productivity = min(
            100,
            total_events * 5 +
            total_assignments * 3 +
            completed_goals * 15
        )

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "📅 Events",
            total_events
        )

        c2.metric(
            "📚 Assignments",
            total_assignments
        )

        c3.metric(
            "🎯 Goals",
            total_goals
        )

        c4.metric(
            "✅ Completed",
            completed_goals
        )

        c5.metric(
            "⚡ Productivity",
            f"{productivity}%"
        )

        st.divider()

    # ==========================
    # EVENT CATEGORY ANALYSIS
    # ==========================

        if events:

            event_df = pd.DataFrame(
                events,
                columns=[
                    "ID",
                    "Title",
                    "Date",
                    "Start",
                    "End",
                    "Category",
                    "Priority"
                ]
            )

            st.subheader(
                "📅 Event Categories"
            )

            cat_counts = (
                event_df["Category"]
                .value_counts()
                .reset_index()
            )

            cat_counts.columns = [
                "Category",
                "Count"
            ]

            fig = px.pie(
                cat_counts,
                names="Category",
                values="Count",
                title="Events by Category"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.divider()

    # ==========================
    # EVENT PRIORITY ANALYSIS
    # ==========================

        if events:

            st.subheader(
                "🔥 Event Priority"
            )

            priority_counts = (
                event_df["Priority"]
                .value_counts()
                .reset_index()
            )

            priority_counts.columns = [
                "Priority",
                "Count"
            ]

            fig = px.bar(
                priority_counts,
                x="Priority",
                y="Count",
                title="Priority Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.divider()

    # ==========================
    # ASSIGNMENT ANALYTICS
    # ==========================

        if assignments:

            assignment_df = pd.DataFrame(
                assignments,
                columns=[
                    "ID",
                    "Assignment",
                    "Subject",
                    "Deadline",
                    "Priority"
                ]
            )

            st.subheader(
                "📚 Assignment Priority"
            )

            ass_counts = (
                assignment_df["Priority"]
                .value_counts()
                .reset_index()
            )

            ass_counts.columns = [
                "Priority",
                "Count"
            ]

            fig = px.pie(
                ass_counts,
                names="Priority",
                values="Count",
                title="Assignments by Priority"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.divider()

    # ==========================
    # GOAL PROGRESS
    # ==========================

        if goals:

            st.subheader(
                "🎯 Goal Progress"
            )

            goal_df = pd.DataFrame(
                goals,
                columns=[
                    "ID",
                    "Goal",
                    "Progress"
                ]
            )

            fig = px.bar(
                goal_df,
                x="Goal",
                y="Progress",
                title="Goal Completion"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.divider()

    # ==========================
    # UPCOMING DEADLINES
    # ==========================

        st.subheader(
            "⏳ Upcoming Deadlines"
        )

        today = date.today()

        if assignments:

            for a in assignments:

                due = pd.to_datetime(
                    a[3]
                ).date()

                days_left = (
                    due - today
                ).days

                if days_left <= 2:

                    st.error(
                        f"🚨 {a[1]} due in {days_left} day(s)"
                    )

                elif days_left <= 7:

                    st.warning(
                        f"⚠ {a[1]} due in {days_left} day(s)"
                    )

        st.divider()

    # ==========================
    # WEEKLY EVENT TREND
    # ==========================

        if events:

            st.subheader(
                "📊 Weekly Activity"
            )

            event_df["Date"] = pd.to_datetime(
                event_df["Date"]
            )

            trend = (
                event_df.groupby("Date")
                .size()
                .reset_index(name="Count")
            )

            fig = px.line(
                trend,
                x="Date",
                y="Count",
                markers=True,
                title="Events Per Day"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.divider()

    # ==========================
    # AI INSIGHTS
    # ==========================

        st.subheader(
            "🤖 Smart Insights"
        )

        if productivity >= 80:

            st.success(
                "🔥 Excellent productivity level."
            )

        elif productivity >= 50:

            st.warning(
                "🚀 Good progress. Complete remaining goals."
            )

        else:

            st.error(
                "⚠ Add more study sessions and goals."
            )

        if total_assignments > 5:

            st.warning(
                "📚 You have many pending assignments."
            )

        if completed_goals == total_goals and total_goals > 0:

            st.success(
                "🏆 All goals completed!"
            )


    # =========================
    # GOALS
    # =========================
    elif page == "🎯 Goals":

        st.markdown("""
        <h2 style='text-align:center;color:#4CAF50;'>
            🎯 Goal Tracker
        </h2>
        <p style='text-align:center;'>
            Set goals and track your progress
        </p>
        """, unsafe_allow_html=True)

    # =========================
    # ADD GOAL
    # =========================

        st.subheader("➕ Add New Goal")

        goal_name = st.text_input(
            "Goal Name",
            placeholder="Complete DBMS Project"
        )

        if st.button(
            "🎯 Add Goal",
            use_container_width=True
        ):

            if not goal_name.strip():
                st.error("Enter goal name")
                st.stop()

            insert_goal(
                st.session_state["user_id"],
                goal_name,
                0
            )

            st.success("Goal Added Successfully")
            #st.balloons()
            st.rerun()

        st.divider()

    # =========================
    # LOAD GOALS
    # =========================

        goals = get_goals(
            st.session_state["user_id"]
        )

        if not goals:
            st.info("No goals available")
            st.stop()

    # =========================
    # SUMMARY
    # =========================

        total_goals = len(goals)

        completed_goals = len([
            g for g in goals
            if int(g[2]) >= 100
        ])

        progress_avg = round(
            sum(int(g[2]) for g in goals)
            /
            total_goals,
            1
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "🎯 Total Goals",
            total_goals
        )

        c2.metric(
            "✅ Completed",
            completed_goals
        )

        c3.metric(
            "📈 Avg Progress",
            f"{progress_avg}%"
        )

        st.divider()

    # =========================
    # GOAL LIST
    # =========================

        st.subheader("📋 Goal Progress")

        for g in goals:

            goal_id = g[0]
            goal_name = g[1]
            progress = int(g[2])

            with st.container():

                st.write(
                    f"### 🎯 {goal_name}"
                )

                st.progress(progress)

                st.caption(
                    f"{progress}% Completed"
                )

                new_progress = st.slider(
                    f"Update Progress - {goal_name}",
                    0,
                    100,
                    progress,
                    key=f"goal_{goal_id}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        f"💾 Save {goal_id}"
                    ):

                        update_goal_progress(
                            goal_id,
                            new_progress,
                            st.session_state["user_id"]
                        )

                        st.success(
                            "Progress Updated"
                        )

                        st.rerun()

                with col2:

                    if st.button(
                        f"🗑 Delete {goal_id}"
                    ):

                        delete_goal(
                            goal_id,
                            st.session_state["user_id"]
                        )

                        st.success(
                            "Goal Deleted"
                        )

                        st.rerun()

                if progress >= 100:

                    st.success(
                        "🏆 Goal Completed!"
                    )

                st.divider()

    # =========================
    # CHART
    # =========================

        st.subheader(
            "📊 Goal Analytics"
        )

        goal_df = pd.DataFrame(
            goals,
            columns=[
                "ID",
                "Goal",
                "Progress"
            ]
        )

        fig = px.bar(
            goal_df,
            x="Goal",
            y="Progress",
            title="Goal Completion"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =========================
    # AI INSIGHTS
    # =========================

        st.subheader(
            "🤖 Goal Insights"
        )

        highest = max(
            goals,
            key=lambda x: int(x[2])
        )

        st.info(
            f"🏅 Most Progress: {highest[1]} ({highest[2]}%)"
        )

        remaining = [
            g for g in goals
            if int(g[2]) < 100
        ]

        st.warning(
            f"📌 {len(remaining)} goals still in progress"
        )

    elif page == "🔔 Smart Notifications":

        st.markdown("""
        <h2 style='text-align:center;color:#4CAF50;'>
            🔔 Smart Notifications Center
        </h2>
        <p style='text-align:center;'>
            AI-powered reminders and productivity alerts
        </p>
        """, unsafe_allow_html=True)

        events = get_events(st.session_state["user_id"])
        assignments = get_assignments(st.session_state["user_id"])
        goals = get_goals(st.session_state["user_id"])

        today = date.today()

        notifications = []

    # ====================================
    # EVENT REMINDERS
    # ====================================

        for e in events:

            event_date = e[2]

            if isinstance(event_date, str):
                event_date = datetime.strptime(
                    event_date,
                    "%Y-%m-%d"
                ).date()

            days_left = (event_date - today).days

            if days_left == 0:
                notifications.append(
                    (
                        "today",
                        f"📅 Event Today: {e[1]}"
                    )
                )

            elif days_left == 1:
                notifications.append(
                    (
                        "warning",
                        f"⏰ Event Tomorrow: {e[1]}"
                    )
                )

    # ====================================
    # ASSIGNMENT ALERTS
    # ====================================

        for a in assignments:

            due = a[3]

            if isinstance(due, str):
                due = datetime.strptime(
                    due,
                    "%Y-%m-%d"
                ).date()

            days_left = (due - today).days

            if days_left < 0:

                notifications.append(
                    (
                        "danger",
                        f"🚨 Overdue Assignment: {a[1]}"
                    )
                )

            elif days_left <= 2:

                notifications.append(
                    (
                        "danger",
                        f"🔥 Assignment Due Soon: {a[1]}"
                    )
                )

            elif days_left <= 7:

                notifications.append(
                    (
                        "warning",
                        f"⚠ Upcoming Assignment: {a[1]}"
                    )
                )

    # ====================================
    # GOAL ALERTS
    # ====================================

        for g in goals:

            progress = int(g[2])

            if progress >= 100:

                notifications.append(
                    (
                        "success",
                        f"🏆 Goal Completed: {g[1]}"
                    )
                )

            elif progress < 30:

                notifications.append(
                    (
                        "warning",
                        f"🎯 Goal Needs Attention: {g[1]}"
                    )
                )

    # ====================================
    # SUMMARY CARDS
    # ====================================

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "📅 Events",
            len(events)
        )

        c2.metric(
            "📚 Assignments",
            len(assignments)
        )

        c3.metric(
            "🎯 Goals",
            len(goals)
        )

        st.divider()

    # ====================================
    # SHOW NOTIFICATIONS
    # ====================================

        if not notifications:

            st.success(
                "🎉 No pending notifications. Everything is on track!"
            )

        else:

            st.subheader(
                f"🔔 {len(notifications)} Notifications"
            )

            for level, msg in notifications:

                if level == "danger":
                    st.error(msg)

                elif level == "warning":
                    st.warning(msg)

                elif level == "success":
                    st.success(msg)

                else:
                    st.info(msg)

    # ====================================
    # DAILY SUMMARY
    # ====================================

        st.divider()

        st.subheader("📋 Daily Summary")

        today_events = [
            e for e in events
            if str(e[2]) == str(today)
        ]

        st.write(
            f"📅 Events Today: {len(today_events)}"
        )

        st.write(
            f"📚 Total Assignments: {len(assignments)}"
        )

        completed_goals = len(
            [
                g for g in goals
                if int(g[2]) >= 100
            ]
        )

        st.write(
            f"🏆 Completed Goals: {completed_goals}"
        )

        productivity = min(
            100,
            (len(events) * 5) +
            (len(assignments) * 3) +
            (completed_goals * 15)
        )

        st.progress(productivity)

        st.caption(
            f"⚡ Productivity Score: {productivity}%"
        )

    # ====================================
    # QUICK ACTIONS
    # ====================================

        st.divider()

        st.subheader("⚡ Quick Actions")

        q1, q2, q3 = st.columns(3)

        with q1:
            if st.button(
                "📅 Create Event",
                use_container_width=True
            ):
                st.session_state["navigation"] = "📅 Create Event"
                st.rerun()

        with q2:
            if st.button(
                "📚 Add Assignment",
                use_container_width=True
            ):
                st.session_state["navigation"] = "📚 Assignments"
                st.rerun()

        with q3:
            if st.button(
                "🎯 Update Goals",
                use_container_width=True
            ):
                st.session_state["navigation"] = "🎯 Goals"
                st.rerun()
    
    elif page == "🌤️ Daily Motivation":

        st.markdown("""
        <h2 style='text-align:center;color:#4CAF50;'>
            🌤️ Daily Motivation Center
        </h2>
        <p style='text-align:center;'>
            Stay focused, productive and inspired every day
        </p>
        """, unsafe_allow_html=True)

        events = get_events(st.session_state["user_id"])
        assignments = get_assignments(st.session_state["user_id"])
        goals = get_goals(st.session_state["user_id"])

        completed_goals = len(
            [g for g in goals if int(g[2]) >= 100]
        )

        productivity = min(
            100,
            (len(events) * 5)
            + (len(assignments) * 3)
            + (completed_goals * 15)
        )

        st.divider()

    # ==========================
    # MOTIVATION SCORE
    # ==========================

        st.subheader("⚡ Your Productivity Score")

        st.progress(productivity)

        st.metric(
            "Productivity",
            f"{productivity}%"
        )

        st.divider()

    # ==========================
    # MOTIVATION MESSAGE
    # ==========================

        if productivity >= 80:

            st.success("""
            🔥 Outstanding Work!

            You are building momentum every day.
            Keep executing your plans and stay consistent.
            """)

        elif productivity >= 50:

            st.warning("""
            🚀 Good Progress!

            You are moving forward.
            Finish pending tasks and push a little harder today.
            """)

        else:

            st.error("""
            ⚠ Time To Refocus!

            Every small task completed today moves you closer to success.
            Start with one important task now.
            """)

        st.divider()

    # ==========================
    # DAILY QUOTE
    # ==========================

        quotes = [

            "Success is the sum of small efforts repeated daily.",

            "Discipline is choosing what you want most over what you want now.",

            "Focus on progress, not perfection.",

            "Dream big. Start small. Act now.",

            "The secret of getting ahead is getting started.",

            "Consistency beats motivation.",

            "One hour of focused study can change your future.",

            "Your future self is watching your decisions today.",

            "Small daily improvements create massive results.",

            "Work hard in silence and let success make the noise."
        ]

        st.subheader("🌟 Quote of the Day")

        day_index = datetime.now().day % len(quotes)

        st.info(quotes[day_index])

        st.divider()

    # ==========================
    # GOAL STATUS
    # ==========================

        st.subheader("🎯 Goal Tracker")

        if goals:

            for g in goals:

                st.write(f"**{g[1]}**")

                progress = int(g[2])

                st.progress(progress)

                st.caption(
                    f"{progress}% Complete"
                )

        else:

            st.info(
                "No goals added yet."
            )

        st.divider()

    # ==========================
    # TODAY'S FOCUS
    # ==========================

        st.subheader("📅 Today's Focus")

        today = str(date.today())

        today_events = [
            e for e in events
            if str(e[2]) == today
        ]

        if today_events:

            for e in today_events:

                st.success(
                    f"📌 {e[1]} | {e[3]} → {e[4]}"
                )

        else:

            st.info(
                "No events scheduled today."
            )

        st.divider()

    # ==========================
    # AI MOTIVATION
    # ==========================

        st.subheader("🤖 AI Motivation")

        if st.button(
            "Generate AI Motivation",
            use_container_width=True
        ):

            try:

                prompt = f"""
                Give a motivational message for a student.

                Productivity Score: {productivity}
                Total Events: {len(events)}
                Assignments: {len(assignments)}
                Goals: {len(goals)}

                Keep it under 100 words.
                """

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                msg = response.choices[0].message.content

                st.success(msg)

            except Exception as e:

                st.error(f"AI Error: {e}")

        st.divider()

    # ==========================
    # ACHIEVEMENTS
    # ==========================

        st.subheader("🏆 Achievement Badges")

        if productivity >= 90:
            st.success("🥇 Productivity Master")

        elif productivity >= 70:
            st.success("🥈 Consistency Champion")

        elif productivity >= 50:
            st.success("🥉 Rising Achiever")

        else:
            st.info("🌱 Getting Started")

        if completed_goals >= 3:
            st.success("🎯 Goal Crusher")

        if len(events) >= 10:
            st.success("📅 Scheduling Expert")

        if len(assignments) >= 5:
            st.success("📚 Academic Warrior")

        st.divider()

        #st.balloons()

    elif page == "⚙️ Settings":

        st.markdown("""
        <h2 style='text-align:center;color:#4CAF50;'>
            ⚙️ Settings
        </h2>
        <p style='text-align:center;'>
            Manage your account and application preferences
        </p>
        """, unsafe_allow_html=True)

        st.divider()

    # ====================================
    # ACCOUNT INFO
    # ====================================

        st.subheader("👤 Account Information")

        c1, c2 = st.columns(2)

        with c1:
            st.text_input(
                "Username",
                value=st.session_state.get("username", ""),
                disabled=True
            )

        with c2:
            st.text_input(
                "User ID",
                value=str(
                    st.session_state.get("user_id", "")
                ),
                disabled=True
            )

        st.divider()

    # ====================================
    # GOOGLE STATUS
    # ====================================

        st.subheader("🔗 Google Calendar")

        if st.session_state.get("google_connected"):

            st.success(
                "✅ Connected to Google Calendar"
            )

        else:

            st.error(
                "❌ Google Calendar Not Connected"
            )

        st.divider()

    # ====================================
    # APP STATISTICS
    # ====================================

        st.subheader("📊 Account Statistics")

        events = get_events(
            st.session_state["user_id"]
        )

        assignments = get_assignments(
        st.session_state["user_id"]
        )

        goals = get_goals(
            st.session_state["user_id"]
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "📅 Events",
            len(events)
        )

        c2.metric(
            "📚 Assignments",
            len(assignments)
        )

        c3.metric(
            "🎯 Goals",
            len(goals)
        )

        st.divider()

    # ====================================
    # NOTIFICATION SETTINGS
    # ====================================

        st.subheader("🔔 Notification Preferences")

        event_notify = st.toggle(
            "Event Reminders",
            value=True
        )

        assignment_notify = st.toggle(
            "Assignment Alerts",
            value=True
        )

        goal_notify = st.toggle(
            "Goal Progress Notifications",
            value=True
        )

        st.divider()

    # ====================================
    # THEME SETTINGS
    # ====================================

        st.subheader("🎨 Dashboard Preferences")

        theme = st.selectbox(
            "Theme",
            [
                "Light",
                "Dark",
                "System Default"
            ]
        )

        start_page = st.selectbox(
            "Default Startup Page",
            [
                "🏠 Dashboard",
                "📅 Create Event",
                "📋 View Events",
                "📚 Assignments"
            ]
        )

        st.divider()

    # ====================================
    # AI SETTINGS
    # ====================================

        st.subheader("🤖 AI Settings")

        ai_model = st.selectbox(
            "AI Model",
            [
                "llama-3.3-70b-versatile",
                "llama3-8b-8192"
            ]
        )

        enable_ai_scheduler = st.toggle(
            "Enable AI Scheduler",
            value=True
        )

        st.divider()

    # ====================================
    # EXPORT DATA
    # ====================================

        st.subheader("📥 Export Data")

        if st.button(
            "Export Events CSV",
            use_container_width=True
        ):

            df = pd.DataFrame(
                events,
                columns=[
                    "ID",
                    "Title",
                    "Date",
                    "Start",
                    "End",
                    "Category",
                    "Priority"
                ]
            )

            csv = df.to_csv(
                index=False
            )

            st.download_button(
                "Download Events",
                csv,
                file_name="events.csv",
                mime="text/csv"
            )

        st.divider()

    # ====================================
    # PRODUCTIVITY SCORE
    # ====================================

        completed_goals = len(
            [
                g for g in goals
                if int(g[2]) >= 100
            ]
        )

        productivity = min(
            100,
            len(events) * 5 +
            len(assignments) * 3 +
            completed_goals * 15
        )

        st.subheader(
            "⚡ Productivity Overview"
        )

        st.progress(productivity)

        st.caption(
            f"Productivity Score: {productivity}%"
        )

        st.divider()

    # ====================================
    # SAVE SETTINGS
    # ====================================

        if st.button(
            "💾 Save Settings",
            use_container_width=True
        ):

            st.success(
                "✅ Settings Saved Successfully"
            )

        st.divider()

    # ====================================
    # LOGOUT
    # ====================================

        st.subheader("🚪 Logout")

        if st.button(
            "Logout",
            use_container_width=True
        ):

            for key in list(
                st.session_state.keys()
            ):
                del st.session_state[key]

            st.success(
                "Logged Out Successfully"
            )

            st.rerun()

    elif page == "❓ FAQ":

        st.markdown("""
        <h2 style='text-align:center;color:#4CAF50;'>
            ❓ Frequently Asked Questions
        </h2>
        <p style='text-align:center;'>
            Find answers to common questions about Smart Timetable AI
        </p>
        """, unsafe_allow_html=True)

        st.divider()

        with st.expander("📅 How do I create an event?"):
            st.write("""
            Go to **Create Event** page,
            fill in title, date, time, category and priority,
            then click **Create Event**.
        
            The event will be saved in the database and optionally synced with Google Calendar.
            """)

        with st.expander("📋 Why can't I see my events?"):
            st.write("""
            Make sure you are logged into the correct account.

            Events are linked to your User ID.

            If you logged in with a different account,
            events from another account will not appear.
            """)

        with st.expander("🔗 How does Google Calendar integration work?"):
            st.write("""
            After login, connect your Google account.

            Events created in Smart Timetable AI can automatically sync to your Google Calendar.
            """)

        with st.expander("📚 How do assignments work?"):
            st.write("""
            Assignments help you track:

            • Subject
            • Deadline
            • Priority

            Upcoming deadlines automatically appear in:
            - Dashboard
            - Notifications
            - Analytics
            """)

        with st.expander("🎯 How do goals work?"):
            st.write("""
            Create personal or academic goals.

            Update progress from 0% to 100%.

            Goal completion automatically updates:
            - Dashboard
            - Analytics
            - Motivation Page
            - Notifications
            """)

        with st.expander("🕒 How are free time slots calculated?"):
            st.write("""
            The system analyzes all your scheduled events.

            Empty periods between events are shown as available free time slots.
            """)

        with st.expander("🤖 What does Smart Assistant do?"):
            st.write("""
            Smart Assistant uses AI (Groq + Llama models).

            It can:
            - Answer study questions
            - Suggest schedules
            - Improve productivity
            - Help manage assignments
            """)

        with st.expander("🤖 What does AI Scheduler do?"):
            st.write("""
            AI Scheduler automatically generates study plans
            based on:

            • Available hours
            • Assignments
            • Priorities
            • Deadlines

            It creates an optimized timetable.
            """)

        with st.expander("📊 How is productivity calculated?"):
            st.write("""
            Productivity Score is calculated using:

            • Events completed
            • Assignments managed
            • Goals completed

            Higher activity results in a higher score.
            """)

        with st.expander("🔔 How do notifications work?"):
            st.write("""
            Notifications are generated automatically.

            Examples:
            - Event reminders
            - Assignment deadlines
            - Goal achievements
            - Daily productivity updates
            """)

        with st.expander("📥 Can I export my data?"):
            st.write("""
            Yes.

            Go to Settings and export your data as CSV files.
            """)

        with st.expander("🔒 Is my data secure?"):
            st.write("""
            Yes.

            User data is stored separately in the database.

            Each user can only access their own events,
            assignments and goals.
            """)

        with st.expander("🚪 How do I logout?"):
            st.write("""
            Open the Settings page and click Logout.

            Your session will be cleared and you will be redirected to the login page.
            """)

        st.divider()

        st.subheader("📞 Need More Help?")

        st.info("""
        If your issue is not listed here:

        • Check Settings
        • Reconnect Google Calendar
        • Verify your login account
        • Contact the project administrator
        """)

        st.success("🎉 Smart Timetable AI is designed to make academic planning easier and smarter.")


    elif page == "ℹ️ About":

        st.markdown("""
        <h1 style='text-align:center;color:#4CAF50;'>
            🚀 Smart Timetable AI
        </h1>

        <h4 style='text-align:center;'>
            AI-Powered Academic Planning & Productivity System
        </h4>
        """, unsafe_allow_html=True)

        st.divider()

        st.image(
            "https://images.unsplash.com/photo-1509062522246-3755977927d7",
            use_container_width=True
        )

        st.divider()

        st.subheader("📖 Project Overview")

        st.write("""
        Smart Timetable AI is an intelligent academic productivity platform
        designed to help students organize their schedules, assignments,
        goals, study plans and daily activities efficiently.

        The system combines traditional timetable management with Artificial
        Intelligence to create a smart productivity ecosystem that helps
        students stay organized and achieve their academic goals.
        """)

        st.divider()

        st.subheader("✨ Key Features")

        features = [
            "📅 Event Scheduling & Calendar Management",
            "🔗 Google Calendar Integration",
            "📚 Assignment Tracking System",
            "🎯 Goal Management",
            "📖 Smart Study Planner",
            "🕒 Free Time Slot Detection",
            "🤖 AI Study Assistant",
            "🤖 AI Scheduler",
            "📈 Productivity Analytics",
            "🔔 Smart Notifications",
            "🌤️ Daily Motivation System",
            "📊 Performance Dashboard"
        ]

        for feature in features:
            st.success(feature)

        st.divider()

        st.subheader("🛠️ Technologies Used")

        tech1, tech2, tech3 = st.columns(3)

        with tech1:
            st.info("""
            ### Frontend
            - Streamlit
            - HTML
            - CSS
            """)

        with tech2:
            st.info("""
            ### Backend
            - Python
            - PostgreSQL
            - Google APIs
            """)

        with tech3:
            st.info("""
            ### AI & Analytics
            - Groq API
            - Llama Models
            - Plotly
            - Pandas
            """)

        st.divider()

        st.subheader("🎯 Project Objectives")

        st.write("""
        • Improve student productivity

        • Automate schedule planning

        • Reduce missed deadlines

        • Improve time management

        • Increase academic performance

        • Provide AI-powered guidance
        """)

        st.divider()

        st.subheader("📊 Live System Statistics")

        events = get_events(st.session_state["user_id"])
        assignments = get_assignments(st.session_state["user_id"])
        goals = get_goals(st.session_state["user_id"])

        completed_goals = len(
            [g for g in goals if int(g[2]) >= 100]
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "📅 Events",
            len(events)
        )

        c2.metric(
            "📚 Assignments",
            len(assignments)
        )

        c3.metric(
            "🎯 Goals",
            len(goals)
        )

        c4.metric(
            "🏆 Completed Goals",
            completed_goals
        )

        st.divider()

        st.subheader("👨‍💻 Developer Information")

        st.success("""
        Name: Ramya

        Role: Full Stack Developer

        Project: Smart Timetable AI

        Domain:
        Artificial Intelligence +
        Productivity Management +
        Education Technology
        """)

        st.divider()

        st.subheader("🌟 Why Smart Timetable AI?")

        st.write("""
        Unlike traditional timetable applications,
        Smart Timetable AI combines scheduling,
        assignment tracking, goal management,
        AI assistance and productivity analytics
        into a single integrated platform.

        This helps students make smarter decisions,
        manage time effectively and stay focused
        on long-term academic success.
        """)

        st.divider()

        st.subheader("🚀 Future Enhancements")

        future_features = [
            "📱 Mobile Application",
            "🔊 Voice Assistant",
            "🧠 Advanced AI Recommendations",
            "📧 Email Notifications",
            "📲 WhatsApp Reminders",
            "👥 Group Study Planning",
            "☁️ Cloud Synchronization",
            "🏫 College ERP Integration"
        ]

        for item in future_features:
            st.write(item)

        st.divider()

        st.success(
            "🎉 Thank you for using Smart Timetable AI!"
        )

        st.caption(
            "Built with ❤️ using Streamlit, PostgreSQL, Google Calendar API and Groq AI."
        )

    elif page == "🚪 Logout":

        st.title("🚪 Logout")

        st.warning("Are you sure you want to logout?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Yes, Logout", use_container_width=True):

            # remove saved token (Google login etc.)
                if os.path.exists("token.pkl"):
                    os.remove("token.pkl")

                if os.path.exists("verifier.txt"):
                    os.remove("verifier.txt")

            # clear session completely
                for key in list(st.session_state.keys()):
                    del st.session_state[key]

            # reset app stage
                st.session_state["app_stage"] = "auth"

                st.success("Logged out successfully")
                st.rerun()

        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.rerun()



if st.session_state["app_stage"] == "auth":
    auth_page()
elif st.session_state["app_stage"] == "google":
    google_page()
elif st.session_state["app_stage"] == "dashboard":
    dashboard()
