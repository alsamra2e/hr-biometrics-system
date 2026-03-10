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

# --- 1. CORE HELPER FUNCTIONS ---

def set_rtl(paragraph):
    """Sets Right-to-Left direction for Arabic text in Word."""
    p = paragraph._element
    pPr = p.get_or_add_pPr()
    bidi = pPr.find(qn('w:bidi'))
    if bidi is None:
        bidi = OxmlElement('w:bidi')
        pPr.append(bidi)

def extract_date_from_filename(filename):
    """Extracts YYYY-MM-DD from filenames like HR_Report_2026-03-10."""
    match = re.search(r'\d{4}-\d{2}-\d{2}', filename)
    return match.group(0) if match else str(date.today())

def create_word_doc(df):
    """Generates the official Arabic Word report with Header/Footer/Table."""
    doc = Document()
    
    # 1. HEADER (3 Columns)
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
    except: 
        pass
    
    # Left: English
    l = htable.rows[0].cells[2].paragraphs[0]
    l.text = "University Of Alturath\nDept. Of Admin & Financial Affairs\nHR Department"
    l.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # 2. SEPARATOR LINE (Maroon #8F0B0B)
    p_line = doc.add_paragraph()
    run_line = p_line.add_run("______________________________________________________________________")
    run_line.font.color.rgb = RGBColor(0x8F, 0x0B, 0x0B) 
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 3. BODY TEXT
    body = doc.add_paragraph("\nنرفق لسيادتكم في ادناه الكشف الخاص بموقف الحضور والغياب لكادر العمل الخاص بجامعة التراث وحسب كشف البصمة المرفق طيا نسخة منه ... راجين التفضل بالاطلاع واعلامنا توجيهات سيادتكم حول ذلك ... مع التقدير..")
    body.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_rtl(body)

    # 4. DATA TABLE
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    hdr = table.rows[0].cells
    labels = ['الاسم', 'الحالة', 'العدد', 'التواريخ']
    for i, txt in enumerate(labels):
        hdr[i].text = txt
        set_rtl(hdr[i].paragraphs[0])

    for _, row in df.iterrows():
        cells = table.add_row().cells
        cells[0].text = str(row['Name'])
        cells[1].text = "تأخير" if "Late" in row['Status'] else "غياب"
        cells[2].text = str(row['Count'])
        
        # Small font for dates to fit 30 days if needed
        d_para = cells[3].paragraphs[0]
        d_run = d_para.add_run(row['Dates_Str'])
        d_run.font.size = Pt(8)
        
        # Apply RTL to all cells in the row
        for cell in cells:
            for paragraph in cell.paragraphs:
                set_rtl(paragraph)

    # 5. SIGNATURE
    doc.add_paragraph("\n\n")
    sig = doc.add_paragraph("م.م محمد زهير طالب النقيب\nمدير قسم الشؤون الادارية والموارد البشرية")
    sig.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_rtl(sig)

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

def run_exceptions_module():
    """Logic for the 'Exceptions Audit' mode."""
    st.subheader("📋 Exceptions & Attendance Audit")
    uploaded_files = st.file_uploader("Upload Daily Excels (Multiple)", accept_multiple_files=True, type=['xlsx', 'xls'])
    
    if uploaded_files:
        all_data = []
        for f in uploaded_files:
            file_date = extract_date_from_filename(f.name)
            try:
                engine = 'xlrd' if f.name.endswith('.xls') else 'openpyxl'
                df = pd.read_excel(f, engine=engine)
                df.columns = [str(c).strip() for c in df.columns]
                df['Report_Date'] = file_date
                all_data.append(df)
            except Exception as e:
                st.error(f"Error in {f.name}: {e}")
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            mask = combined_df['Status'].str.contains('Late|Absence', case=False, na=False)
            exceptions = combined_df[mask].copy()
            
            if not exceptions.empty:
                # Aggregate unique dates per employee and status
                summary = exceptions.groupby(['Name', 'Status'])['Report_Date'].unique().reset_index()
                summary['Count'] = summary['Report_Date'].apply(len)
                summary['Dates_Str'] = summary['Report_Date'].apply(lambda x: ", ".join(sorted(x)))

                st.info(f"Summary: Found {len(summary)} records of violations.")
                st.dataframe(summary[['Name', 'Status', 'Count', 'Dates_Str']], use_container_width=True)
                
                if st.button("Generate Official Alturath Word Report"):
                    with st.spinner("Processing..."):
                        report_bytes = create_word_doc(summary)
                        st.download_button("📥 Download Official Report", report_bytes, "Alturath_Exceptions_Report.docx")
            else:
                st.success("Perfect! No Lates or Absences detected.")

# --- 3. MAIN APP STRUCTURE ---

st.set_page_config(page_title="Alturath University | HR Audit Pro", layout="wide")

# Sidebar
st.sidebar.title("HR Management System")
mode = st.sidebar.radio("Navigation:", ["Daily Report (Old)", "Exceptions Audit (New)"])

if mode == "Daily Report (Old)":
    st.title("Biometric Attendance Report")
    
    # Old Logic Sidebar Elements
    st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRfTMmtmrsxGUBnlEb0xB0ClMbFZmj_L5Ap5Q&s")
    with st.sidebar:
        st.divider()
        st.subheader("📅 Audit Parameters")
        target_date = st.date_input("Audit Date", value=date.today())
        
        weekdays_ar = {"Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الاربعاء", "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الاحد"}
        st.info(f"Audit Day: **{weekdays_ar.get(target_date.strftime('%A'), '')}**")

        f_zaqura = st.file_uploader("Zaqura Gate", type=['xlsx', 'xls'])
        f_mhmd = st.file_uploader("Mhmd Bn Ali Gate", type=['xlsx', 'xls'])
        f_app = st.file_uploader("Mawjood App", type=['xlsx', 'xls'])
        f_weekly = st.file_uploader("📅 Weekly Day-Off List", type=['xlsx', 'xls'])

    # Paste your existing processing logic for Daily Report here if it differs significantly
    st.info("Upload your individual gate logs above to generate the daily summary.")

else:
    run_exceptions_module()
