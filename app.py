import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime, date
import re

# 1. PAGE SETUP
st.set_page_config(page_title="Alturath University | HR Audit Pro", layout="wide")

# 2. SIDEBAR & LOGO
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRfTMmtmrsxGUBnlEb0xB0ClMbFZmj_L5Ap5Q&s", use_container_width=True)
st.sidebar.title("HR Audit Control")

with st.sidebar:
    st.divider()
    st.subheader("📅 Audit Parameters")
    use_today = st.toggle("Show Today Only", value=False)
    target_date = date.today() if use_today else st.date_input("Audit Date", value=date.today())
    
    st.divider()
    st.subheader("📥 Upload Data")
    file_zaqura = st.file_uploader("Zaqura Gate (.xls/.xlsx)", type=['xlsx', 'xls'])
    file_mhmd = st.file_uploader("Mhmd Bn Ali Gate (.xls/.xlsx)", type=['xlsx', 'xls'])
    file_app = st.file_uploader("Mawjood App (.xls/.xlsx)", type=['xlsx', 'xls'])
    file_off = st.file_uploader("📅 Official Day-Off List (.xls/.xlsx)", type=['xlsx', 'xls'])

# 3. PROCESSING ENGINES
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
        return pd.DataFrame({'ID': 'App', 'Name': df['الاسم'], 'Date': target_date, 'Check_In': df['دخول'], 'Check_Out': df['خروج'], 'Source': 'Mawjood App'})
    except: return pd.DataFrame()

def process_leaves(file):
    try:
        engine = 'xlrd' if file.name.endswith('.xls') else 'openpyxl'
        df = pd.read_excel(file, engine=engine)
        df.columns = [str(c).strip() for c in df.columns]
        return df # Needs columns 'Name'
    except: return pd.DataFrame()

# 4. CONSOLIDATION & AUDIT
all_logs = []
if file_zaqura: all_logs.append(process_gate(file_zaqura, "Zaqura"))
if file_mhmd: all_logs.append(process_gate(file_mhmd, "Mhmd Bn Ali"))
if file_app: all_logs.append(process_app(file_app))

if all_logs:
    master_present = pd.concat(all_logs, ignore_index=True)
    master_present = master_present[master_present['Date'] == target_date]
    
    # 8:30 Compliance
    master_present['Compliance'] = master_present['Check_In'].apply(
        lambda x: "🔴 Late" if str(x) > "08:30" else "✅ On Time"
    )
    
    df_leaves = process_leaves(file_off) if file_off else pd.DataFrame(columns=['Name'])

    # 5. ABSENCE LOGIC (GHOST HUNTER)
    all_names = master_present['Name'].unique().tolist()
    if not df_leaves.empty:
        all_names = list(set(all_names + df_leaves['Name'].unique().tolist()))
    
    absence_data = []
    for name in all_names:
        present = name in master_present['Name'].values
        on_leave = name in df_leaves['Name'].values if not df_leaves.empty else False
        
        if not present and not on_leave:
            absence_data.append({"Name": name, "Status": "Unexplained Absence (Forgot Biometric)", "Type": "Warning"})
        elif not present and on_leave:
            absence_data.append({"Name": name, "Status": "Official Day-Off", "Type": "Authorized"})
    
    df_absence = pd.DataFrame(absence_data)

    # 6. UI TABS
    tab1, tab2, tab3 = st.tabs(["📊 Performance Analysis", "🕵️ Presence Audit", "🚨 Absence Investigation"])

    with tab1:
        st.header(f"Lateness Progress - {target_date}")
        c1, c2 = st.columns(2)
        with c1:
            fig = px.histogram(master_present, x="Source", color="Compliance", barmode="group",
                               color_discrete_map={"🔴 Late": "#d73a49", "✅ On Time": "#22863a"},
                               title="Punctuality Check by Source")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            late_rate = (len(master_present[master_present['Compliance'] == "🔴 Late"]) / len(master_present)) * 100
            st.metric("Overall Lateness Rate", f"{late_rate:.1f}%", delta_color="inverse")

    with tab2:
        st.header("Detailed Presence Log")
        def style_present(val):
            if val == "✅ On Time": return 'background-color: #e6ffed; color: #22863a;'
            if val == "🔴 Late": return 'background-color: #ffeef0; color: #d73a49;'
            return ''
        
        st.dataframe(master_present.style.applymap(style_present, subset=['Compliance']), use_container_width=True)
        
        # Export Colored Excel
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            master_present.to_excel(writer, index=False, sheet_name='Presence')
            workbook  = writer.book
            worksheet = writer.sheets['Presence']
            # Simple column formatting
            worksheet.set_column('A:Z', 15)
        st.download_button("📥 Export Presence Report", buf.getvalue(), "Alturath_Audit_Report.xlsx")

    with tab3:
        st.header("Absence & Leave Report")
        def style_absence(val):
            if "Unexplained" in str(val): return 'background-color: #ffeef0; color: #d73a49;'
            if "Official" in str(val): return 'background-color: #fffbdd; color: #735c0f;'
            return ''

        if not df_absence.empty:
            st.dataframe(df_absence.style.applymap(style_absence, subset=['Status']), use_container_width=True)
            
            buf_abs = BytesIO()
            with pd.ExcelWriter(buf_abs, engine='xlsxwriter') as writer:
                df_absence.to_excel(writer, index=False, sheet_name='Absences')
            st.download_button("📥 Export Absence Report", buf_abs.getvalue(), "Absence_Report.xlsx")
        else:
            st.success("No absences or leaves recorded.")

else:
    st.info("Please upload logs to generate the report.")
