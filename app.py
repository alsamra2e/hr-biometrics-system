import streamlit as st
import pandas as pd
import re
import requests
import plotly.express as px
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from io import BytesIO
from datetime import datetime, date

# --- 1. GLOBAL UTILITIES ---

def set_rtl(paragraph):
    p = paragraph._element
    pPr = p.get_or_add_pPr()
    bidi = pPr.find(qn('w:bidi'))
    if bidi is None:
        bidi = OxmlElement('w:bidi')
        pPr.append(bidi)

def set_table_rtl(table):
    tbl_pr = table._element.xpath('w:tblPr')
    if tbl_pr:
        bidi = OxmlElement('w:bidiVisual')
        tbl_pr[0].append(bidi)

def extract_date_from_filename(filename):
    match = re.search(r'\d{4}-\d{2}-\d{2}', filename)
    return match.group(0) if match else str(date.today())

# --- 2. NEW AUDIT MODULE (Word Generation) ---

def create_word_doc(df):
    doc = Document()
    section = doc.sections[0]
    header = section.header
    htable = header.add_table(1, 3, width=Inches(6.5))
    
    # Right: Arabic
    r = htable.rows[0].cells[0].paragraphs[0]
    r.text = "جامعة التراث\nقسم الشؤون الإدارية والمالية\nشعبة الموارد البشرية"
    r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_rtl(r)
    
    # Middle: Logo
    m = htable.rows[0].cells[1].paragraphs[0]
    m.alignment = WD_ALIGN_PARAGRAPH.CENTER
    try:
        img_url = "https://uoturath.edu.iq/wp-content/uploads/2025/03/shield-1.png"
        img_data = BytesIO(requests.get(img_url).content)
        m.add_run().add_picture(img_data, width=Inches(0.8))
    except: pass
    
    # Left: English
    l = htable.rows[0].cells[2].paragraphs[0]
    l.text = "University Of Alturath\nDept. Of Admin & Financial Affairs\nHR Department"
    l.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # Separator
    p_line = doc.add_paragraph()
    run_line = p_line.add_run("______________________________________________________________________")
    run_line.font.color.rgb = RGBColor(0x8F, 0x0B, 0x0B) 
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Body
    body = doc.add_paragraph("\nنرفق لسيادتكم في ادناه الكشف الخاص بموقف الحضور والغياب لكادر العمل الخاص بجامعة التراث وحسب كشف البصمة المرفق طيا نسخة منه ... راجين التفضل بالاطلاع واعلامنا توجيهات سيادتكم حول ذلك ... مع التقدير..")
    body.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_rtl(body)

    # Table
    table = doc.add_table(rows=1, cols=5)
    table.style = 'Table Grid'
    set_table_rtl(table) 
    
    hdr = table.rows[0].cells
    labels = ['ت', 'الاسم', 'الحالة', 'العدد', 'التواريخ']
    for i, txt in enumerate(labels):
        hdr[i].text = txt
        hdr[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_rtl(hdr[i].paragraphs[0])

    for idx, row in df.iterrows():
        cells = table.add_row().cells
        cells[0].text = str(idx + 1)
        cells[1].text = str(row['Name'])
        cells[2].text = "تأخير" if "Late" in str(row['Status']) else "غياب"
        cells[3].text = str(row['Count'])
        d_para = cells[4].paragraphs[0]
        d_run = d_para.add_run(row['Dates_Str'])
        d_run.font.size = Pt(8)
        for cell in cells:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_rtl(cell.paragraphs[0])

    # Signature
    doc.add_paragraph("\n\n")
    sig = doc.add_paragraph("م.م محمد زهير طالب النقيب\nمدير قسم الشؤون الادارية والموارد البشرية")
    sig.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_rtl(sig)

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

def run_exceptions_module():
    st.subheader("📋 Multi-Day Exceptions Audit")
    uploaded_files = st.file_uploader("Upload Exported Excels (Row 2 Header)", accept_multiple_files=True, type=['xlsx', 'xls'])
    
    if uploaded_files:
        all_data = []
        for f in uploaded_files:
            file_date = extract_date_from_filename(f.name)
            try:
                engine = 'xlrd' if f.name.endswith('.xls') else 'openpyxl'
                # header=1 looks at Row 2 for 'Name' and 'Status'
                df = pd.read_excel(f, engine=engine, header=1)
                df.columns = [str(c).strip() for c in df.columns]
                
                if 'Status' in df.columns and 'Name' in df.columns:
                    mask = df['Status'].str.contains('Late|Absence', case=False, na=False)
                    day_data = df[mask].copy()
                    day_data['Report_Date'] = file_date
                    all_data.append(day_data[['Name', 'Status', 'Report_Date']])
            except: pass
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            summary = combined.groupby(['Name', 'Status'])['Report_Date'].unique().reset_index()
            summary['Count'] = summary['Report_Date'].apply(len)
            summary['Dates_Str'] = summary['Report_Date'].apply(lambda x: ", ".join(sorted(x)))
            st.dataframe(summary[['Name', 'Status', 'Count', 'Dates_Str']], use_container_width=True)
            
            if st.button("Download Official Word Report"):
                report_file = create_word_doc(summary)
                st.download_button("📥 Download .docx", report_file, "Alturath_Exceptions_Report.docx")

# --- 3. THE OLD DAILY APP MODULE ---

def run_daily_report_module():
    st.title("Daily Biometric Attendance")
    
    # Sidebar Filters for Daily
    use_today = st.sidebar.toggle("Show Today Only", value=False)
    target_date = date.today() if use_today else st.sidebar.date_input("Audit Date", value=date.today())
    
    weekdays_ar = {"Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الاربعاء", "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الاحد"}
    current_weekday_ar = weekdays_ar.get(target_date.strftime("%A"), "")
    st.sidebar.info(f"Audit Day: **{current_weekday_ar}**")

    f_zaqura = st.sidebar.file_uploader("Zaqura Gate", type=['xlsx', 'xls'])
    f_mhmd = st.sidebar.file_uploader("Mhmd Bn Ali Gate", type=['xlsx', 'xls'])
    f_app = st.sidebar.file_uploader("Mawjood App", type=['xlsx', 'xls'])
    f_weekly = st.sidebar.file_uploader("📅 Weekly Day-Off List", type=['xlsx', 'xls'])

    # --- YOUR ORIGINAL PROCESSING LOGIC (REINSTATED) ---
    def process_gate(file, g_name):
        try:
            engine = 'xlrd' if file.name.endswith('.xls') else 'openpyxl'
            df = pd.read_excel(file, engine=engine)
            df.columns = [str(c).strip() for c in df.columns]
            df['dt'] = pd.to_datetime(df['الوقت'], errors='coerce')
            df = df[df['dt'].dt.date == target_date]
            df['Time'] = df['dt'].dt.strftime('%H:%M')
            df = df.rename(columns={'الاسم': 'Name', 'الإسم': 'Name'})
            return df[['Name', 'Time']].assign(Source=g_name)
        except: return pd.DataFrame()

    def process_app(file):
        try:
            df = pd.read_excel(file, header=3)
            df = df[df['الحالة'].isin(['حاضر', 'Present'])]
            df['Time'] = pd.to_datetime(df['دخول'], errors='coerce').dt.strftime('%H:%M')
            return pd.DataFrame({'Name': df['الاسم'], 'Time': df['Time'], 'Source': 'App'})
        except: return pd.DataFrame()

    all_logs = []
    if f_zaqura: all_logs.append(process_gate(f_zaqura, "Zaqura Gate"))
    if f_mhmd: all_logs.append(process_gate(f_mhmd, "Mhmd Bn Ali Gate"))
    if f_app: all_logs.append(process_app(f_app))

    if all_logs or f_weekly:
        df_present = pd.concat(all_logs, ignore_index=True) if all_logs else pd.DataFrame(columns=['Name','Time','Source'])
        df_present = df_present.sort_values('Time').drop_duplicates(subset=['Name'], keep='first')
        
        # Load Weekly Off
        df_off = pd.DataFrame(columns=['Name', 'OffDay'])
        if f_weekly:
            df_off = pd.read_excel(f_weekly).rename(columns={'الاسم الثلاثي': 'Name', 'الاجازة الاسبوعية': 'OffDay'})
        
        master_names = list(set(df_present['Name'].tolist() + df_off['Name'].tolist()))
        final_data = []
        for name in master_names:
            punch = df_present[df_present['Name'] == name]
            off_info = df_off[df_off['Name'] == name]
            is_off = (off_info['OffDay'].iloc[0] == current_weekday_ar) if not off_info.empty else False
            
            row = {"Name": name, "Check-In": "-", "Source": "-", "Status": ""}
            if not punch.empty:
                row["Check-In"] = punch['Time'].iloc[0]
                row["Source"] = punch['Source'].iloc[0]
                row["Status"] = "🔴 Late" if row["Check-In"] > "08:35" else "✅ On Time"
            elif is_off: row["Status"] = "🟡 Weekly Off"
            else: row["Status"] = "❌ Absence"
            final_data.append(row)

        df_final = pd.DataFrame(final_data)
        st.dataframe(df_final, use_container_width=True)
        
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, index=False, sheet_name='Audit', startrow=1) # Row 2 header
        st.download_button("📥 Export Daily Excel", buf.getvalue(), f"HR_Report_{target_date}.xlsx")

# --- 4. MAIN NAVIGATION ---

st.set_page_config(page_title="Alturath HR System", layout="wide")
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRfTMmtmrsxGUBnlEb0xB0ClMbFZmj_L5Ap5Q&s")
app_mode = st.sidebar.selectbox("Choose App Mode", ["Daily Report Tool", "Multi-Day Audit Tool"])

if app_mode == "Daily Report Tool":
    run_daily_report_module()
else:
    run_exceptions_module()
