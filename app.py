import streamlit as st
import pandas as pd
import re
import sqlite3
from io import BytesIO
from datetime import datetime
import plotly.express as px

# 1. PAGE CONFIGURATION (Using Default Theme)
st.set_page_config(page_title="Alturath University | HR Audit", layout="wide")

# 2. DATABASE FOR DAY-OFFS (Keeps records between sessions)
def init_db():
    conn = sqlite3.connect('hr_portal.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS leaves 
                 (emp_id TEXT, name TEXT, date TEXT, reason TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# 3. ROBUST PARSING ENGINE (Handles your specific Excel layout)
def clean_time(val):
    if pd.isna(val) or str(val).strip() in ["", "-"]: return None, None
    val_clean = str(val).replace('\n', ' ').strip()
    parts = val_clean.split()
    return (parts[0], parts[-1]) if len(parts) >= 2 else (parts[0], None)

def process_device(file, source_name):
    df_raw = pd.read_excel(file, header=None)
    meta = str(df_raw.iloc[3, 0])
    eid = re.search(r'رقم هوية:(\d+)', meta).group(1) if re.search(r'رقم هوية:(\d+)', meta) else "0"
    ename = re.search(r'الإسم:(.*?)القسم:', meta).group(1).strip() if re.search(r'الإسم:(.*?)القسم:', meta) else "Unknown"
    
    data = []
    # Row 6 (Days 1-16) and Row 8 (Days 17-31)
    for r, c_lim in [(6, 16), (8, 15)]:
        for c_idx in range(c_lim):
            day, log = df_raw.iloc[r-1, c_idx], df_raw.iloc[r, c_idx]
            cin, cout = clean_time(log)
            if cin:
                data.append({"ID": eid, "Name": ename, "Day": str(day), "In": cin, "Out": cout, "Source": source_name})
    return pd.DataFrame(data)

def process_app(file):
    df = pd.read_excel(file, header=3)
    df.columns = [str(c).strip() for c in df.columns]
    df = df[df['الحالة'] != 'غياب']
    return pd.DataFrame({"Name": df['الاسم'], "In": df['دخول'], "Out": df['خروج'], "Source": "Mawjood App", "Day": "Current", "ID": "App"})

# 4. SIDEBAR & NAVIGATION
st.sidebar.title("🏛️ HR Audit Portal")
page = st.sidebar.radio("Navigation", ["📊 Summary Dashboard", "🕵️ Detailed Employee Audit", "📅 Day-Off Registry"])

with st.sidebar:
    st.divider()
    st.subheader("Upload Excel Files")
    g1 = st.file_uploader("Gate 1 Log", type=['xlsx'])
    g2 = st.file_uploader("Gate 2 Log", type=['xlsx'])
    app = st.file_uploader("Mawjood App Log", type=['xlsx'])

# 5. DATA CONSOLIDATION
all_data = []
if g1: all_data.append(process_device(g1, "Gate 1"))
if g2: all_data.append(process_device(g2, "Gate 2"))
if app: all_data.append(process_app(app))

if all_data:
    df = pd.concat(all_data, ignore_index=True)
    
    # APPLY TIMING ALERTS (Logic for Coloring)
    def check_compliance(time_val):
        if not time_val: return "Unknown"
        return "🔴 LATE" if str(time_val) > "08:30" else "✅ ON TIME"

    df['Compliance'] = df['In'].apply(check_compliance)

    # --- PAGE 1: EXECUTIVE SUMMARY ---
    if page == "📊 Summary Dashboard":
        st.header("Institutional Attendance Performance")
        
        c1, c2, c3 = st.columns(3)
        late_count = len(df[df['Compliance'] == "🔴 LATE"])
        c1.metric("General Compliance", f"{((len(df)-late_count)/len(df))*100:.1f}%")
        c2.metric("Mawjood App Dependency", f"{(len(df[df['Source']=='Mawjood App'])/len(df))*100:.1f}%")
        c3.metric("Employees Processed", df['Name'].nunique())

        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            fig1 = px.pie(df, names='Source', title="Verification Source Split", hole=0.5)
            st.plotly_chart(fig1, use_container_width=True)
        with col_b:
            # Color map for the charts
            fig2 = px.histogram(df, x="Source", color="Compliance", barmode="group", 
                                title="Punctuality by Device",
                                color_discrete_map={"🔴 LATE": "#d73a49", "✅ ON TIME": "#22863a"})
            st.plotly_chart(fig2, use_container_width=True)

    # --- PAGE 2: DETAILED AUDIT ---
    elif page == "🕵️ Detailed Employee Audit":
        st.header("Detailed Performance Audit")
        
        # SEARCH AND FILTER
        search = st.selectbox("Search for Employee Name", ["View All Records"] + list(df['Name'].unique()))
        final_df = df if search == "View All Records" else df[df['Name'] == search]
        
        # THE COLOR-CODING MAGIC (Conditional Styling)
        def color_compliance_rows(val):
            # Applying colors directly to the 'Compliance' column cell
            if val == "✅ ON TIME":
                return 'background-color: #e6ffed; color: #22863a; font-weight: bold;'
            elif val == "🔴 LATE":
                return 'background-color: #ffeef0; color: #d73a49; font-weight: bold;'
            return ''

        # Display Styled Dataframe
        st.dataframe(
            final_df.style.applymap(color_compliance_rows, subset=['Compliance']), 
            use_container_width=True, 
            hide_index=True
        )

        # EXPORT FOR PRINTING
        st.divider()
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            final_df.to_excel(writer, index=False, sheet_name='HR_Report')
        st.download_button("📥 Export Report to Excel (Print-Ready)", output.getvalue(), "Alturath_University_Audit.xlsx")

    # --- PAGE 3: LEAVE REGISTRY ---
    elif page == "📅 Day-Off Registry":
        st.header("Day-Off & Leave Management")
        with st.form("leave_form"):
            col1, col2 = st.columns(2)
            l_name = col1.text_input("Full Name")
            l_reason = col2.selectbox("Type of Leave", ["Official Off-Day", "Sick Leave", "Annual Vacation", "Mission"])
            l_date = st.date_input("Date of Absence")
            if st.form_submit_button("Save to Database"):
                conn.execute("INSERT INTO leaves VALUES (?,?,?,?)", ("-", l_name, str(l_date), l_reason))
                conn.commit()
                st.success(f"Registered {l_reason} for {l_name}")

        st.subheader("Official Absence Records")
        st.dataframe(pd.read_sql("SELECT * FROM leaves", conn), use_container_width=True, hide_index=True)

else:
    st.info("Awaiting Data Upload. Please select Gate 1, Gate 2, or Mawjood App Excel files in the sidebar.")
