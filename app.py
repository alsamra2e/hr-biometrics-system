import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime

# 1. PAGE SETUP
st.set_page_config(page_title="Alturath University | HR Audit Pro", layout="wide")

# 2. STYLING & UI
def apply_color_logic(val):
    if "Late" in str(val):
        return 'background-color: #ffeef0; color: #d73a49; font-weight: bold;'
    elif "On Time" in str(val):
        return 'background-color: #e6ffed; color: #22863a; font-weight: bold;'
    return ''

# 3. DATA PROCESSING ENGINES
def process_gate_logs(file, source_name):
    """Processes the new Gate format with Date/Time in one column."""
    try:
        # engine='xlrd' handles .xls, engine='openpyxl' handles .xlsx
        engine = 'xlrd' if file.name.endswith('.xls') else 'openpyxl'
        df = pd.read_excel(file, engine=engine)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Convert 'الوقت' to datetime
        df['dt'] = pd.to_datetime(df['الوقت'], errors='coerce')
        df['Date'] = df['dt'].dt.date
        df['Time'] = df['dt'].dt.strftime('%H:%M')
        
        # Rename columns to standard English
        df = df.rename(columns={
            'رقم هوية': 'ID',
            'الإسم': 'Name',
            'Event': 'Action'
        })
        
        # Identify Check-In (min time) and Check-Out (max time) per person per day
        # Usually, (1)دخول is the first and (2)خروج is the last
        summary = df.groupby(['ID', 'Name', 'Date']).agg(
            Check_In=('Time', 'min'),
            Check_Out=('Time', 'max')
        ).reset_index()
        
        summary['Source'] = source_name
        return summary
    except Exception as e:
        st.error(f"Error processing Gate file: {e}")
        return pd.DataFrame()

def process_app_logs(file):
    """Processes the new Mawjood App format."""
    try:
        engine = 'xlrd' if file.name.endswith('.xls') else 'openpyxl'
        # Skip the institution headers (first 3 rows)
        df = pd.read_excel(file, header=3, engine=engine)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Filter only Present (حاضر)
        df = df[df['الحالة'] == 'حاضر']
        
        res = pd.DataFrame({
            'ID': 'App',
            'Name': df['الاسم'],
            'Date': datetime.now().date(), # Usually current day for this report
            'Check_In': df['دخول'],
            'Check_Out': df['خروج'],
            'Source': 'Mawjood App'
        })
        return res
    except Exception as e:
        st.error(f"Error processing App file: {e}")
        return pd.DataFrame()

# 4. NAVIGATION
st.sidebar.title("🏛️ Alturath HR Audit")
page = st.sidebar.radio("Go to:", ["📊 Summary", "🕵️ Detailed Audit"])

with st.sidebar:
    st.divider()
    st.subheader("Upload Logs (.xls or .xlsx)")
    gate_files = st.file_uploader("Upload Gate Logs", type=['xlsx', 'xls'], accept_multiple_files=True)
    app_file = st.file_uploader("Upload Mawjood App Log", type=['xlsx', 'xls'])

# 5. DATA MERGING
all_data = []
for f in gate_files:
    all_data.append(process_gate_logs(f, f.name))
if app_file:
    all_data.append(process_app_logs(app_file))

if all_data:
    master_df = pd.concat(all_data, ignore_index=True)
    
    # Apply Compliance Rule (> 08:30)
    def determine_status(time_str):
        if pd.isna(time_str) or time_str == '-': return "N/A"
        # Convert HH:MM AM/PM if from app, or HH:MM if from device
        try:
            t = pd.to_datetime(time_str).time()
            cutoff = datetime.strptime("08:30", "%H:%M").time()
            return "🔴 Late" if t > cutoff else "✅ On Time"
        except:
            return "On Time"

    master_df['Status'] = master_df['Check_In'].apply(determine_status)

    if page == "📊 Summary":
        st.header("Institutional Overview")
        col1, col2, col3 = st.columns(3)
        total = len(master_df)
        late = len(master_df[master_df['Status'] == "🔴 Late"])
        
        col1.metric("Total Records", total)
        col2.metric("Late Arrivals", late, delta=f"{late/total*100:.1f}%", delta_color="inverse")
        col3.metric("Staff Count", master_df['Name'].nunique())

        st.divider()
        fig = px.histogram(master_df, x="Source", color="Status", barmode="group",
                           color_discrete_map={"🔴 Late": "#d73a49", "✅ On Time": "#22863a"},
                           title="Punctuality per Device Source")
        st.plotly_chart(fig, use_container_width=True)

    elif page == "🕵️ Detailed Audit":
        st.header("Employee Detail Report")
        
        # Search Filter
        search = st.text_input("🔍 Search by Name or ID")
        if search:
            display_df = master_df[master_df['Name'].str.contains(search, na=False, case=False)]
        else:
            display_df = master_df

        # Display Styled Table
        st.dataframe(
            display_df.style.applymap(apply_color_logic, subset=['Status']),
            use_container_width=True,
            hide_index=True
        )

        # Export Report
        st.divider()
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            display_df.to_excel(writer, index=False, sheet_name='Audit_Report')
        st.download_button("📥 Download Full Audit (Excel)", output.getvalue(), "Alturath_Detailed_Audit.xlsx")

else:
    st.info("👋 Welcome! Please upload your .xls or .xlsx log files in the sidebar to generate the report.")
