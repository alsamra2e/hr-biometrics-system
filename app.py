import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime, date

# 1. PAGE SETUP
st.set_page_config(page_title="Alturath University | HR Audit Pro", layout="wide")

# 2. SIDEBAR LOGO & FILTERS
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRfTMmtmrsxGUBnlEb0xB0ClMbFZmj_L5Ap5Q&s")
st.sidebar.title("HR Audit Control")

with st.sidebar:
    st.divider()
    use_today = st.toggle("Show Today Only", value=False)
    target_date = date.today() if use_today else st.date_input("Audit Date", value=date.today())
    
    # Map Python weekday to Arabic for your Excel matching
    weekdays_ar = {
        "Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الاربعاء", 
        "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الاحد"
    }
    current_weekday_ar = weekdays_ar[target_date.strftime("%A")]
    st.info(f"Audit Day: **{current_weekday_ar}**")

    st.subheader("📥 Upload Data")
    f_zaqura = st.file_uploader("Zaqura Gate", type=['xlsx', 'xls'])
    f_mhmd = st.file_uploader("Mhmd Bn Ali Gate", type=['xlsx', 'xls'])
    f_app = st.file_uploader("Mawjood App", type=['xlsx', 'xls'])
    f_weekly = st.file_uploader("📅 Weekly Day-Off List", type=['xlsx', 'xls'])

# 3. PROCESSING ENGINES
def process_gate(file, g_name):
    try:
        engine = 'xlrd' if file.name.endswith('.xls') else 'openpyxl'
        df = pd.read_excel(file, engine=engine)
        df.columns = [str(c).strip() for c in df.columns]
        df['dt'] = pd.to_datetime(df['الوقت'], errors='coerce')
        df = df[df['dt'].dt.date == target_date] # Filter for selected date
        df['Time'] = df['dt'].dt.strftime('%H:%M')
        df = df.rename(columns={'الاسم': 'Name', 'الإسم': 'Name', 'رقم هوية': 'ID'})
        return df[['ID', 'Name', 'Time', 'Date']].assign(Source=g_name)
    except: return pd.DataFrame()

def process_app(file):
    try:
        engine = 'xlrd' if file.name.endswith('.xls') else 'openpyxl'
        df = pd.read_excel(file, header=3, engine=engine)
        df.columns = [str(c).strip() for c in df.columns]
        df = df[df['الحالة'] == 'حاضر']
        return pd.DataFrame({'Name': df['الاسم'], 'Time': df['دخول'], 'Source': 'App', 'Date': target_date})
    except: return pd.DataFrame()

def process_weekly_off(file):
    try:
        engine = 'xlrd' if file.name.endswith('.xls') else 'openpyxl'
        df = pd.read_excel(file, engine=engine)
        df.columns = [str(c).strip() for c in df.columns]
        # Columns: الاسم الثلاثي, الاجازة الاسبوعية
        return df.rename(columns={'الاسم الثلاثي': 'Name', 'الاجازة الاسبوعية': 'OffDay'})
    except: return pd.DataFrame()

# 4. CONSOLIDATION LOGIC
all_logs = []
if f_zaqura: all_logs.append(process_gate(f_zaqura, "Zaqura"))
if f_mhmd: all_logs.append(process_gate(f_mhmd, "Mhmd Bn Ali"))
if f_app: all_logs.append(process_app(f_app))

if all_logs or f_weekly:
    # A. Get Logs and De-Duplicate (Keep First Punch)
    if all_logs:
        df_present = pd.concat(all_logs, ignore_index=True)
        # Keep only the earliest punch for each person
        df_present = df_present.sort_values('Time').drop_duplicates(subset=['Name'], keep='first')
    else:
        df_present = pd.DataFrame(columns=['Name', 'Time', 'Source'])

    # B. Get Staff List & Weekly Offs
    df_off = process_weekly_off(f_weekly) if f_weekly else pd.DataFrame(columns=['Name', 'OffDay'])
    
    # C. Master Reconciliation
    # Combine list of everyone who punched and everyone on the staff list
    master_list = list(set(df_present['Name'].tolist() + df_off['Name'].tolist()))
    
    final_report = []
    for name in master_list:
        row = {"Name": name, "Check-In": "-", "Source": "-", "Status": ""}
        
        # Check if they punched in
        punch = df_present[df_present['Name'] == name]
        is_present = not punch.empty
        
        # Check if today is their day off
        staff_info = df_off[df_off['Name'] == name]
        is_day_off_today = False
        if not staff_info.empty:
            is_day_off_today = (staff_info['OffDay'].iloc[0] == current_weekday_ar)

        if is_present:
            row["Check-In"] = punch['Time'].iloc[0]
            row["Source"] = punch['Source'].iloc[0]
            # Compliance Check
            try:
                t = row["Check-In"].replace(" AM", "").replace(" PM", "")
                row["Status"] = "🔴 Late" if t > "08:30" else "✅ On Time"
            except: row["Status"] = "✅ Present"
        elif is_day_off_today:
            row["Status"] = "🟡 Official Weekly Off"
        else:
            row["Status"] = "❌ Unexplained Absence"
        
        final_report.append(row)

    df_final = pd.DataFrame(final_report).sort_values("Status")

    # 5. UI TABS
    st.header(f"Detailed Presence Log - {target_date} ({current_weekday_ar})")
    
    # Search for 500+ employees
    search = st.text_input("🔍 Search Employee Name", placeholder="Type name to audit...")
    if search:
        df_final = df_final[df_final['Name'].str.contains(search, na=False)]

    def style_final(val):
        if "Late" in str(val) or "Absence" in str(val): return 'background-color: #ffeef0; color: #d73a49; font-weight: bold;'
        if "On Time" in str(val): return 'background-color: #e6ffed; color: #22863a; font-weight: bold;'
        if "Weekly Off" in str(val): return 'background-color: #fffbdd; color: #735c0f;'
        return ''

    st.dataframe(df_final.style.applymap(style_final, subset=['Status']), use_container_width=True, hide_index=True)

    # 6. EXCEL EXPORT
    st.divider()
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        df_final.to_excel(writer, index=False, sheet_name='Audit')
        workbook  = writer.book
        worksheet = writer.sheets['Audit']
        # Add a bit of width
        worksheet.set_column('A:D', 25)
    
    st.download_button("📥 Download Official Colored Report", buf.getvalue(), f"HR_Audit_{target_date}.xlsx")

else:
    st.info("Please upload Gate/App logs and the Weekly Day-Off Excel to generate the integrated report.")
