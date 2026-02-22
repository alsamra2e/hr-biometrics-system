import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime, date
import re

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Alturath University | HR Audit", layout="wide")

# 2. SIDEBAR LOGO & NAV
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRfTMmtmrsxGUBnlEb0xB0ClMbFZmj_L5Ap5Q&s", use_container_width=True)
st.sidebar.title("HR Audit Portal")

# 3. DATE FILTERING SECTION
with st.sidebar:
    st.divider()
    st.subheader("📅 Filter & Timeline")
    use_today = st.toggle("Show Today Only", value=False)
    
    if not use_today:
        # Range selection for 500+ employees historical audit
        date_range = st.date_input("Select Audit Period", value=[date.today(), date.today()])
    else:
        date_range = [date.today(), date.today()]

    st.divider()
    st.subheader("📥 Data Migration Center")
    file_zaqura = st.file_uploader("Upload Zaqura Gate Log (.xls/.xlsx)", type=['xlsx', 'xls'])
    file_mhmd = st.file_uploader("Upload Mhmd Bn Ali Gate Log (.xls/.xlsx)", type=['xlsx', 'xls'])
    file_app = st.file_uploader("Upload Mawjood App Log (.xls/.xlsx)", type=['xlsx', 'xls'])

# 4. PROCESSING ENGINES
def process_gate_logs(file, gate_name):
    try:
        # Supports Excel 97 (.xls) and modern (.xlsx)
        engine = 'xlrd' if file.name.endswith('.xls') else 'openpyxl'
        df = pd.read_excel(file, engine=engine)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Parse the 'الوقت' column (Format: 2026/02/22 07:53:07)
        df['dt'] = pd.to_datetime(df['الوقت'], errors='coerce')
        df['Date'] = df['dt'].dt.date
        df['Time_Only'] = df['dt'].dt.strftime('%H:%M')
        
        # Map Arabic Headers from your sample
        df = df.rename(columns={'رقم هوية': 'ID', 'الإسم': 'Name'})
        
        # Grouping: Vertical logs -> Daily In/Out Summary
        summary = df.groupby(['ID', 'Name', 'Date']).agg(
            Check_In=('Time_Only', 'min'),
            Check_Out=('Time_Only', 'max')
        ).reset_index()
        
        summary['Source'] = gate_name
        return summary
    except Exception as e:
        st.error(f"Error in {gate_name} file: {e}")
        return pd.DataFrame()

def process_mawjood_app(file):
    try:
        engine = 'xlrd' if file.name.endswith('.xls') else 'openpyxl'
        # Extract report date from Row 3 of the Mawjood export
        header_date_df = pd.read_excel(file, header=None, nrows=3, engine=engine)
        try:
            raw_date = str(header_date_df.iloc[2, 0]).strip()
            report_date = pd.to_datetime(raw_date, dayfirst=True).date()
        except:
            report_date = date.today()

        df = pd.read_excel(file, header=3, engine=engine)
        df.columns = [str(c).strip() for c in df.columns]
        df = df[df['الحالة'] == 'حاضر']
        
        res = pd.DataFrame({
            'ID': 'App-User',
            'Name': df['الاسم'],
            'Date': report_date,
            'Check_In': df['دخول'],
            'Check_Out': df['خروج'],
            'Source': 'Mawjood App'
        })
        return res
    except Exception as e:
        st.error(f"Error in Mawjood App file: {e}")
        return pd.DataFrame()

# 5. DATA MERGING & TIMING ANALYSIS
all_data = []
if file_zaqura: all_data.append(process_gate_logs(file_zaqura, "Zaqura Gate"))
if file_mhmd: all_data.append(process_gate_logs(file_mhmd, "Mhmd Bn Ali Gate"))
if file_app: all_data.append(process_mawjood_app(file_app))

if all_data:
    master_df = pd.concat(all_data, ignore_index=True)
    
    # Filter by Date
    if use_today:
        master_df = master_df[master_df['Date'] == date.today()]
    elif isinstance(date_range, list) and len(date_range) == 2:
        start_date, end_date = date_range
        master_df = master_df[(master_df['Date'] >= start_date) & (master_df['Date'] <= end_date)]

    # Compliance Logic (> 08:30)
    def check_compliance(time_val):
        if pd.isna(time_val) or str(time_val) in ['-', '', 'nan']: return "N/A"
        try:
            t = pd.to_datetime(time_val).time()
            limit = datetime.strptime("08:30", "%H:%M").time()
            return "🔴 Late" if t > limit else "✅ On Time"
        except: return "On Time"

    master_df['Status'] = master_df['Check_In'].apply(check_compliance)

    # 6. UI TABS
    tab_dashboard, tab_audit = st.tabs(["📊 Performance Analysis", "🕵️ Detailed Audit Report"])

    with tab_dashboard:
        st.header("App Migration & Lateness Analysis")
        
        # Top Metrics
        m1, m2, m3, m4 = st.columns(4)
        total_logs = len(master_df)
        late_logs = len(master_df[master_df['Status'] == "🔴 Late"])
        late_pct = (late_logs/total_logs*100) if total_logs > 0 else 0
        
        m1.metric("Total Attendance", total_logs)
        m2.metric("Lateness Rate", f"{late_pct:.1f}%")
        m3.metric("Staff Active", master_df['Name'].nunique())
        m4.metric("System Health", "Operational", delta="Migration Active")

        st.divider()
        
        # Professional Analysis Charts
        c1, c2 = st.columns(2)
        
        with c1:
            # Punctuality Progress Analysis
            source_perf = master_df.groupby(['Source', 'Status']).size().unstack(fill_value=0)
            # Calculate Late Percentage for comparison
            if "🔴 Late" in source_perf.columns:
                source_perf['Late_Rate'] = (source_perf['🔴 Late'] / (source_perf['🔴 Late'] + source_perf['✅ On Time'])) * 100
            else:
                source_perf['Late_Rate'] = 0
                
            fig_perf = px.bar(source_perf.reset_index(), x='Source', y='Late_Rate', 
                             title="Lateness Percentage by Source (Lower is Better)",
                             labels={'Late_Rate': 'Lateness %'},
                             color_discrete_sequence=['#d73a49'])
            fig_perf.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig_perf, use_container_width=True)

        with c2:
            # Adoption Analysis
            fig_pie = px.pie(master_df, names='Source', title="System Usage Distribution",
                            hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig_pie, use_container_width=True)

        # Comparative Trend (If multi-day)
        if len(master_df['Date'].unique()) > 1:
            st.subheader("Punctuality Trend (App vs Gates)")
            trend_df = master_df.groupby(['Date', 'Source', 'Status']).size().unstack(fill_value=0).reset_index()
            trend_df['Late_Rate'] = (trend_df['🔴 Late'] / (trend_df['🔴 Late'] + trend_df['✅ On Time'])) * 100
            fig_trend = px.line(trend_df, x='Date', y='Late_Rate', color='Source', 
                               title="Daily Lateness Trend Line", markers=True)
            st.plotly_chart(fig_trend, use_container_width=True)

    with tab_audit:
        st.header("Comprehensive Audit Log")
        search = st.text_input("🔍 Filter by Name or ID", placeholder="Search 500+ employees...")
        filtered = master_df[master_df['Name'].str.contains(search, na=False, case=False)] if search else master_df
        
        # Professional Red/Green Coloring
        def style_rows(val):
            if val == "✅ On Time": return 'background-color: #e6ffed; color: #22863a; font-weight: bold;'
            if val == "🔴 Late": return 'background-color: #ffeef0; color: #d73a49; font-weight: bold;'
            return ''

        st.dataframe(
            filtered.sort_values(by='Date', ascending=False).style.applymap(style_rows, subset=['Status']),
            use_container_width=True, hide_index=True
        )

        # Export for HR Printing
        st.divider()
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            filtered.to_excel(writer, index=False, sheet_name='Audit_Report')
        st.download_button("📥 Download PDF-Ready Excel Report", buf.getvalue(), "Alturath_Audit_Report.xlsx")

else:
    st.info("👋 System Ready. Please upload Gate (Zaqura/Mhmd) and App logs in the sidebar to begin the audit.")
