st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRfTMmtmrsxGUBnlEb0xB0ClMbFZmj_L5Ap5Q&s") # Replace with your real logo URL

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- 1. DATABASE & LOGIC SETUP ---
conn = sqlite3.connect('hr_data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS off_days 
             (emp_id TEXT, name TEXT, date TEXT, reason TEXT)''')
conn.commit()

def find_ghost_employees(log_df, off_days_df, full_list_df):
    """Cross-references logs, leave, and master list to find missing people."""
    present_ids = set(log_df['Emp_ID'].astype(str).unique()) if not log_df.empty else set()
    leave_ids = set(off_days_df['emp_id'].astype(str).unique())
    accounted_for = present_ids.union(leave_ids)
    
    ghosts = full_list_df[~full_list_df['Emp_ID'].astype(str).isin(accounted_for)]
    return ghosts

# --- 2. UI CONFIGURATION ---
st.set_page_config(page_title="Biometric Intelligence Hub", layout="wide")

# Modern Professional Styling
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e6e9ef; }
    .stDataFrame { border-radius: 10px; }
    </style>
""", unsafe_allow_index=True)

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("🏢 HR Dashboard")
st.sidebar.markdown("---")
menu = ["📊 Overview", "📥 Log Processor", "📅 Leave Registry", "⚠️ Risk Alerts"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- 4. PAGE: OVERVIEW ---
if choice == "📊 Overview":
    st.title("Attendance Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Gate Adoption", "72%", "+5%")
    col2.metric("App Usage", "28%", "-5%")
    col3.metric("Late (8:30+)", "14", delta_color="inverse")
    col4.metric("Unaccounted", "3", delta_color="inverse")

    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Usage: Physical vs App")
        df_chart = pd.DataFrame({"Source": ["Gate 1", "Gate 2", "Mawjood App"], "Logs": [410, 390, 280]})
        fig = px.pie(df_chart, values='Logs', names='Source', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Weekly Attendance Trend")
        df_line = pd.DataFrame({"Day": ["Sun", "Mon", "Tue", "Wed", "Thu"], "Count": [145, 142, 148, 139, 141]})
        fig2 = px.line(df_line, x="Day", y="Count", markers=True)
        st.plotly_chart(fig2, use_container_width=True)

# --- 5. PAGE: LOG PROCESSOR ---
elif choice == "📥 Log Processor":
    st.title("Data Integration")
    st.info("Upload logs to update the 'Risk Alerts' page.")
    
    with st.expander("Upload Sources", expanded=True):
        f1 = st.file_uploader("Gate 1 (Physical)", type=['xlsx'])
        f2 = st.file_uploader("Gate 2 (Physical)", type=['xlsx'])
        f3 = st.file_uploader("Mawjood App (Mobile)", type=['xlsx'])
    
    if st.button("Merge & Analyze"):
        # Real-world dev tip: This is where you'd pd.read_excel() and combine
        st.balloons()
        st.success("Successfully synchronized all biometric sources.")

# --- 6. PAGE: LEAVE REGISTRY ---
elif choice == "📅 Leave Registry":
    st.title("Leave & Off-Day Registry")
    
    with st.form("leave_form"):
        c1, c2 = st.columns(2)
        eid = c1.text_input("Employee ID")
        ename = c2.text_input("Name")
        ldate = st.date_input("Date")
        reason = st.selectbox("Reason", ["Annual Leave", "Sick Leave", "Business Trip", "Off Day"])
        
        if st.form_submit_button("Save Record"):
            c.execute("INSERT INTO off_days VALUES (?,?,?,?)", (eid, ename, str(ldate), reason))
            conn.commit()
            st.success(f"Record saved for {ename}")

    st.subheader("Scheduled Absences")
    leaves = pd.read_sql("SELECT * FROM off_days", conn)
    st.dataframe(leaves, use_container_width=True)

# --- 7. PAGE: RISK ALERTS ---
elif choice == "⚠️ Risk Alerts":
    st.title("Critical Exceptions")
    
    t1, t2 = st.tabs(["🔴 Arrivals After 8:30 AM", "🕵️ Ghost List (Missing)"])
    
    with t1:
        st.subheader("Today's Late Arrivals")
        # Mock data for demonstration
        late_df = pd.DataFrame({
            "Emp ID": ["102", "305", "412"],
            "Name": ["Ahmed Ali", "Zaid Hassan", "Sara Omar"],
            "Time": ["08:35 AM", "08:50 AM", "09:15 AM"],
            "Method": ["Mawjood App", "Gate 1", "Mawjood App"]
        })
        st.table(late_df)

    with t2:
        st.subheader("Unaccounted For (Ghosts)")
        st.error("No record in Gate, App, or Leave Registry for 3+ days.")
        # Logic display
        ghost_df = pd.DataFrame({
            "Name": ["Khalid Jamil", "Noor Saleem"],
            "Days Absent": [3, 4],
            "Last Known Method": ["Mawjood App", "Mawjood App"]
        })
        st.dataframe(ghost_df, use_container_width=True)
