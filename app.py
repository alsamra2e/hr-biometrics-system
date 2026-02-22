import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime
import re

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Alturath University | HR Audit", layout="wide")

# 2. SIDEBAR LOGO & NAV
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRfTMmtmrsxGUBnlEb0xB0ClMbFZmj_L5Ap5Q&s", use_container_width=True)
st.sidebar.title("HR Audit Portal")
nav = st.sidebar.radio("Navigation", ["📊 Executive Summary", "🕵️ Detailed Audit Report"])

with st.sidebar:
    st.divider()
    st.subheader("Upload Center")
    # Supports both modern .xlsx and legacy .xls
    file_zaqura = st.file_uploader("Upload Zaqura Gate Log", type=['xlsx', 'xls'])
    file_mhmd = st.file_uploader("Upload Mhmd Bn Ali Gate Log", type=['xlsx', 'xls'])
    file_app = st.file_uploader("Upload Mawjood App Log", type=['xlsx', 'xls'])

# 3. PROCESSING ENGINES
def process_gate_logs(file, gate_name):
    """Processes vertical logs with ID, Name, Time, and Event."""
    try:
        engine = 'xlrd' if file.name.endswith('.xls') else 'openpyxl'
        df = pd.read_excel(file, engine=engine)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Parse the 'الوقت' column (Format: 2026/02/22 07:53:07)
        df['dt'] = pd.to_datetime(df['الوقت'], errors='coerce')
        df['Date'] = df['dt'].dt.date
        df['Time_Only'] = df['dt'].dt.strftime('%H:%M')
        
        # Mapping Arabic headers
        df = df.rename(columns={'رقم هوية': 'ID', 'الإسم': 'Name'})
        
        # Grouping to find daily Check-In (min) and Check-Out (max)
        summary = df.groupby(['ID', 'Name', 'Date']).agg(
            Check_In=('Time_Only', 'min'),
            Check_Out=('Time_Only', 'max')
        ).reset_index()
        
        summary['Source'] = gate_name
        return summary
    except Exception as e:
        st.error(f"Error processing {gate_name}: {e}")
        return pd.DataFrame()

def process_mawjood_app(file):
    """Processes the Mawjood App format."""
    try:
        engine = 'xlrd' if file.name.endswith('.xls') else 'openpyxl'
        # Skip institution headers (first 3 rows)
        df = pd.read_excel(file, header=3, engine=engine)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Filter for 'Present' (حاضر)
        df = df[df['الحالة'] == 'حاضر']
        
        res = pd.DataFrame({
            'ID': 'App-User',
            'Name': df['الاسم'],
            'Date': datetime.now().date(),
            'Check_In': df['دخول'],
            'Check_Out': df['خروج'],
            'Source': 'Mawjood App'
        })
        return res
    except Exception as e:
        st.error(f"Error processing App file: {e}")
        return pd.DataFrame()

# 4. DATA MERGING
all_data = []
if file_zaqura: all_data.append(process_gate_logs(file_zaqura, "Zaqura Gate"))
if file_mhmd: all_data.append(process_gate_logs(file_mhmd, "Mhmd Bn Ali Gate"))
if file_app: all_data.append(process_mawjood_app(file_app))

if all_data:
    master_df = pd.concat(all_data, ignore_index=True)
    
    # Timing Alert Logic (8:30 AM Cutoff)
    def check_compliance(time_val):
        if pd.isna(time_val) or str(time_val) == '-': return "N/A"
        try:
            t = pd.to_datetime(time_val).time()
            limit = datetime.strptime("08:30", "%H:%M").time()
            return "🔴 Late" if t > limit else "✅ On Time"
        except: return "On Time"

    master_df['Status'] = master_df['Check_In'].apply(check_compliance)

    # PAGE 1: SUMMARY
    if nav == "📊 Executive Summary":
        st.header("Institutional Attendance Summary")
        m1, m2, m3 = st.columns(3)
        m1.metric("Staff Detected", master_df['Name'].nunique())
        m2.metric("Total Log Entries", len(master_df))
        late_pct = (len(master_df[master_df['Status'] == "🔴 Late"]) / len(master_df)) * 100
        m3.metric("Lateness Rate", f"{late_pct:.1f}%")

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.pie(master_df, names='Source', title="Log Source Share", hole=0.5), use_container_width=True)
        with c2:
            st.plotly_chart(px.histogram(master_df, x="Source", color="Status", barmode="group",
                                       color_discrete_map={"🔴 Late": "#d73a49", "✅ On Time": "#22863a"},
                                       title="Punctuality by Device"), use_container_width=True)

    # PAGE 2: DETAILED AUDIT
    elif nav == "🕵️ Detailed Audit Report":
        st.header("Comprehensive Audit Log")
        search = st.text_input("🔍 Search Name or ID")
        filtered = master_df[master_df['Name'].str.contains(search, na=False, case=False)] if search else master_df
        
        # Color Coding Rows
        def style_rows(val):
            if val == "✅ On Time": return 'background-color: #e6ffed; color: #22863a; font-weight: bold;'
            if val == "🔴 Late": return 'background-color: #ffeef0; color: #d73a49; font-weight: bold;'
            return ''

        st.dataframe(filtered.style.applymap(style_rows, subset=['Status']), use_container_width=True, hide_index=True)

        # Excel Export
        st.divider()
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered.to_excel(writer, index=False, sheet_name='Audit')
        st.download_button("📥 Export Detailed Audit (Excel)", output.getvalue(), "Alturath_Audit_Report.xlsx")
else:
    st.info("Awaiting data upload. Please use the sidebar to upload Zaqura, Mhmd Bn Ali, or Mawjood App files.")
