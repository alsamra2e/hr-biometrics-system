import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime, date
import re

# 1. PAGE SETUP
st.set_page_config(page_title="Alturath University | HR Audit Pro", layout="wide")

# 2. SIDEBAR LOGO & FILTERS
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRfTMmtmrsxGUBnlEb0xB0ClMbFZmj_L5Ap5Q&s")
st.sidebar.title("HR Control Center")

with st.sidebar:
    st.divider()
    use_today = st.toggle("Show Today Only", value=False)
    target_date = date.today() if use_today else st.date_input("Audit Date", value=date.today())
    
    st.subheader("📥 Upload Center")
    file_zaqura = st.file_uploader("Zaqura Gate", type=['xlsx', 'xls'])
    file_mhmd = st.file_uploader("Mhmd Bn Ali Gate", type=['xlsx', 'xls'])
    file_app = st.file_uploader("Mawjood App", type=['xlsx', 'xls'])
    file_off = st.file_uploader("📅 Official Day-Off/Leaves List", type=['xlsx', 'xls'])

# 3. PROCESSING FUNCTIONS
def process_gate(file, gate_name):
    try:
        engine = 'xlrd' if file.name.endswith('.xls') else 'openpyxl'
        df = pd.read_excel(file, engine=engine)
        df.columns = [str(c).strip() for c in df.columns]
        df['dt'] = pd.to_datetime(df['الوقت'], errors='coerce')
        df['Date'] = df['dt'].dt.date
        df['Time'] = df['dt'].dt.strftime('%H:%M')
        df = df.rename(columns={'رقم هوية': 'ID', 'الإسم': 'Name'})
        summary = df.groupby(['ID', 'Name', 'Date']).agg(Check_In=('Time', 'min'), Check_Out=('Time', 'max')).reset_index()
        summary['Source'] = gate_name
        return summary
    except: return pd.DataFrame()

def process_app(file):
    try:
        engine = 'xlrd' if file.name.endswith('.xls') else 'openpyxl'
        df = pd.read_excel(file, header=3, engine=engine)
        df.columns = [str(c).strip() for c in df.columns]
        df = df[df['الحالة'] == 'حاضر']
        return pd.DataFrame({'ID': 'App', 'Name': df['الاسم'], 'Date': target_date, 'Check_In': df['دخول'], 'Check_Out': df['خروج'], 'Source': 'App'})
    except: return pd.DataFrame()

def process_leaves(file):
    try:
        engine = 'xlrd' if file.name.endswith('.xls') else 'openpyxl'
        df = pd.read_excel(file, engine=engine)
        df.columns = [str(c).strip() for c in df.columns]
        # Expecting columns: 'Name' and 'Date'
        df['Date'] = pd.to_datetime(df.get('Date', target_date)).dt.date
        return df
    except: return pd.DataFrame()

# 4. CORE AUDIT LOGIC
all_logs = []
if file_zaqura: all_logs.append(process_gate(file_zaqura, "Zaqura"))
if file_mhmd: all_logs.append(process_gate(file_mhmd, "Mhmd Bn Ali"))
if file_app: all_logs.append(process_app(file_app))

if all_logs:
    master_present = pd.concat(all_logs, ignore_index=True)
    master_present = master_present[master_present['Date'] == target_date]
    
    # Load Day-Offs
    df_leaves = process_leaves(file_off) if file_off else pd.DataFrame(columns=['Name', 'Date'])
    
    # 5. GENERATE ABSENCE REPORT (The "Ghost Hunter")
    # We assume the 'Master List' of employees is everyone found in any of the uploads
    total_staff = master_present['Name'].unique().tolist()
    if file_off: total_staff = list(set(total_staff + df_leaves['Name'].unique().tolist()))
    
    absent_list = []
    for person in total_staff:
        is_present = person in master_present['Name'].values
        is_on_leave = person in df_leaves['Name'].values if not df_leaves.empty else False
        
        if not is_present and not is_on_leave:
            absent_list.append({"Name": person, "Status": "Unexplained Absence (Forgot Biometric)"})
        elif not is_present and is_on_leave:
            reason = df_leaves[df_leaves['Name'] == person]['Reason'].iloc[0] if 'Reason' in df_leaves.columns else "Official Leave"
            absent_list.append({"Name": person, "Status": f"Authorized Day-Off: {reason}"})

    df_absence_report = pd.DataFrame(absent_list)

    # 6. UI TABS
    tab1, tab2, tab3 = st.tabs(["📊 Progress Analysis", "🕵️ Attendance Audit", "🚨 Absence & Ghost Report"])

    with tab1:
        st.header(f"Lateness Progress Analysis - {target_date}")
        # Chart: Lateness by source
        master_present['Compliance'] = master_present['Check_In'].apply(lambda x: "Late" if str(x) > "08:30" else "On Time")
        fig = px.histogram(master_present, x="Source", color="Compliance", barmode="group",
                           color_discrete_map={"Late": "#d73a49", "On Time": "#22863a"},
                           title="Gate vs App Discipline")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("Present Staff Audit")
        st.dataframe(master_present, use_container_width=True)

    with tab3:
        st.header("Absence Investigation")
        st.info("This report excludes people who are officially on 'Day-Off'.")
        
        # Color code the absences
        def color_absent(val):
            if "Unexplained" in str(val): return 'background-color: #ffeef0; color: #d73a49; font-weight: bold;'
            return 'background-color: #fffbdd; color: #735c0f;'

        if not df_absence_report.empty:
            st.dataframe(df_absence_report.style.applymap(color_absent, subset=['Status']), use_container_width=True)
            
            # Export Absence Report
            buf = BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                df_absence_report.to_excel(writer, index=False)
            st.download_button("📥 Download Absence Report", buf.getvalue(), "Absence_Investigation.xlsx")
        else:
            st.success("No absences detected for this date.")

else:
    st.info("Please upload logs to begin the audit.")
