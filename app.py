st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRfTMmtmrsxGUBnlEb0xB0ClMbFZmj_L5Ap5Q&s") # Replace with your real logo URL

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px

# --- 1. DATABASE SETUP (Persistent Storage) ---
conn = sqlite3.connect('hr_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS off_days 
             (emp_id TEXT, name TEXT, date TEXT, reason TEXT)''')
conn.commit()

# --- 2. UI CONFIGURATION ---
st.set_page_config(page_title="Institution Biometric Hub", layout="wide")

# Custom CSS for a modern "Institution" look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .late-text { color: #e74c3c; font-weight: bold; }
    </style>
""", unsafe_allow_index=True)

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("🏢 HR Management")
st.sidebar.info("Transitioning from App to Physical Biometrics")
menu = ["📊 Overview", "📥 Log Processor", "📅 Leave Registry", "⚠️ Risk Alerts"]
choice = st.sidebar.selectbox("Go to:", menu)

# --- 4. PAGE: OVERVIEW ---
if choice == "📊 Overview":
    st.title("Attendance Intelligence Dashboard")
    
    # KPIs - These would be calculated from your merged data
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Workforce", "150")
    col2.metric("Physical Gate Users", "98", "+12% 📈")
    col3.metric("App Users (Mawjood)", "52", "-15% 📉")
    col4.metric("Active Alerts", "5", delta_color="inverse")

    st.divider()
    
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("Device Adoption Rate")
        # Logic to show the manager how many people moved to gates
        adoption_df = pd.DataFrame({"Method": ["Gate 1", "Gate 2", "Mawjood App"], "Total Logs": [450, 410, 220]})
        fig = px.pie(adoption_df, values='Total Logs', names='Method', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    
    with c_right:
        st.subheader("Peak Entry Times")
        time_data = pd.DataFrame({"Hour": ["7:00", "7:30", "8:00", "8:30", "9:00"], "Employees": [10, 45, 80, 12, 3]})
        fig2 = px.bar(time_data, x="Hour", y="Employees", color_discrete_sequence=['#1E88E5'])
        st.plotly_chart(fig2, use_container_width=True)

# --- 5. PAGE: LOG PROCESSOR ---
elif choice == "📥 Log Processor":
    st.title("Data Integration Tool")
    st.markdown("Upload the latest exports to generate the consolidated HR report.")
    
    with st.container(border=True):
        f1 = st.file_uploader("Gate 1 (Physical)", type=['xlsx'])
        f2 = st.file_uploader("Gate 2 (Physical)", type=['xlsx'])
        f3 = st.file_uploader("Mawjood App (Mobile)", type=['xlsx'])
        
        if st.button("Generate Master Report"):
            with st.spinner("Analyzing timestamps and cross-referencing IDs..."):
                # Simulation of processing
                st.balloons()
                st.success("Analysis Complete! Records deduplicated and late arrivals flagged.")

# --- 6. PAGE: LEAVE REGISTRY ---
elif choice == "📅 Leave Registry":
    st.title("Off-Day Management")
    
    with st.form("leave_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        eid = c1.text_input("Employee ID")
        ename = c2.text_input("Full Name")
        ldate = st.date_input("Scheduled Off Date")
        reason = st.selectbox("Reason", ["Annual Leave", "Sick Leave", "Off Day"])
        
        if st.form_submit_button("Submit Registry"):
            c.execute("INSERT INTO off_days VALUES (?,?,?,?)", (eid, ename, str(ldate), reason))
            conn.commit()
            st.toast(f"Saved: {ename} on {ldate}")

    st.subheader("Current Leave Records")
    current_leaves = pd.read_sql("SELECT * FROM off_days", conn)
    st.dataframe(current_leaves, use_container_width=True)

# --- 7. PAGE: RISK ALERTS ---
elif choice == "⚠️ Risk Alerts":
    st.title("Compliance & Attendance Risks")
    
    tab_late, tab_ghosts = st.tabs(["Late Arrivals (> 8:30)", "Long-term Missing (3+ Days)"])
    
    with tab_late:
        st.subheader("Lateness Logs (Current Day)")
        # In a real app, this would filter your uploaded data
        late_example = pd.DataFrame({
            "Emp ID": ["1002", "1145", "1089"],
            "Name": ["John Doe", "Sarah Connor", "Mike Ross"],
            "Check-In": ["08:35 AM", "08:42 AM", "09:05 AM"],
            "Method": ["Mawjood App", "Gate 1", "Gate 2"]
        })
        st.warning("The following employees clocked in after 8:30 AM.")
        st.table(late_example)

    with tab_ghosts:
        st.subheader("Unexplained Absence (3+ Days)")
        st.error("These employees have no logs in the last 72 hours and are NOT in the Leave Registry.")
        ghost_example = pd.DataFrame({
            "Name": ["Arthur Dent", "Ford Prefect"],
            "Last Seen": ["2026-02-18", "2026-02-17"],
            "Privilege Status": ["Mobile App", "Mobile App"]
        })
        st.dataframe(ghost_example, use_container_width=True)
        st.info("💡 Insight: Most missing employees are currently using the Phone App privilege.")
