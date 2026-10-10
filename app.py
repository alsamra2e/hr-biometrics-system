from datetime import date, datetime, time, timedelta
from io import BytesIO
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
import pandas as pd
import requests
import streamlit as st

# ============================================================
# 1. GLOBAL UTILITIES & ARABIC NAME NORMALIZATION
# ============================================================


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


def clean_arabic_name(name):
  """Normalizes Arabic names by removing department tags, diacritics,

  unifying Alef variants, and standardizing Taa Marbuta/Haa for accurate
  matching.
  """
  if not isinstance(name, str):
    return ''
  # Strip department suffixes like '/الصيدلة', ' - IT', etc.
  base = re.split(r'[/\\-\(\)]', name)[0].strip()
  # Remove Arabic tashkeel (diacritics)
  base = re.sub(r'[\u064b-\u0652]', '', base)
  # Unify Alef variants
  base = re.sub(r'[إأآٱ]', 'ا', base)
  # Standardize Taa Marbuta and Haa for matching (رقيه / رقية)
  base = base.replace('ة', 'ه')
  # Normalize whitespace
  base = ' '.join(base.split())
  return base


# ============================================================
# 2. OFFICIAL WORD REPORT GENERATION (BILINGUAL)
# ============================================================


def create_word_doc(df):
  doc = Document()
  section = doc.sections[0]
  header = section.header
  htable = header.add_table(1, 3, width=Inches(6.5))

  # Right: Arabic Header
  r = htable.rows[0].cells[0].paragraphs[0]
  r.text = (
      'جامعة التراث\nقسم الشؤون الإدارية والمالية\nشعبة الموارد البشرية'
  )
  r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
  set_rtl(r)

  # Middle: University Shield Logo
  m = htable.rows[0].cells[1].paragraphs[0]
  m.alignment = WD_ALIGN_PARAGRAPH.CENTER
  try:
    img_url = (
        'https://uoturath.edu.iq/wp-content/uploads/2025/03/shield-1.png'
    )
    img_data = BytesIO(requests.get(img_url).content)
    m.add_run().add_picture(img_data, width=Inches(0.8))
  except Exception:
    pass

  # Left: English Header
  l = htable.rows[0].cells[2].paragraphs[0]
  l.text = (
      'University Of Alturath\nDept. Of Admin & Financial Affairs\nHR'
      ' Department'
  )
  l.alignment = WD_ALIGN_PARAGRAPH.LEFT

  # Separator line
  p_line = doc.add_paragraph()
  run_line = p_line.add_run(
      '______________________________________________________________________'
  )
  run_line.font.color.rgb = RGBColor(0x8F, 0x0B, 0x0B)
  p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER

  # Official Body Text
  body = doc.add_paragraph(
      '\nنرفق لسيادتكم في ادناه الكشف الخاص بموقف الحضور والغياب لكادر العمل'
      ' الخاص بجامعة التراث وحسب كشف البصمة المرفق طيا نسخة منه ... راجين التفضل'
      ' بالاطلاع واعلامنا توجيهات سيادتكم حول ذلك ... مع التقدير..'
  )
  body.alignment = WD_ALIGN_PARAGRAPH.RIGHT
  set_rtl(body)

  # Data Table
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
    cells[2].text = 'تأخير' if 'Late' in str(row['Status']) else 'غياب'
    cells[3].text = str(row['Count'])
    d_para = cells[4].paragraphs[0]
    d_run = d_para.add_run(row['Dates_Str'])
    d_run.font.size = Pt(8)
    for cell in cells:
      cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
      set_rtl(cell.paragraphs[0])

  # Official Signature Block
  doc.add_paragraph('\n\n')
  sig = doc.add_paragraph(
      'م.م محمد زهير طالب النقيب\nمدير قسم الشؤون الادارية والموارد البشرية'
  )
  sig.alignment = WD_ALIGN_PARAGRAPH.LEFT
  set_rtl(sig)

  buf = BytesIO()
  doc.save(buf)
  buf.seek(0)
  return buf


def run_exceptions_module():
  st.markdown(
      '<div class="main-header">📋 Multi-Day Exceptions Audit Report</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<p style="color:#64748b; font-size:0.9rem;">Aggregate attendance'
      ' exceptions, lateness, and absence logs across multiple exported'
      ' files.</p>',
      unsafe_allow_html=True,
  )

  uploaded_files = st.file_uploader(
      'Upload Exported Excel Reports',
      accept_multiple_files=True,
      type=['xlsx', 'xls'],
  )

  if uploaded_files:
    all_data = []
    for f in uploaded_files:
      file_date = extract_date_from_filename(f.name)
      try:
        engine = 'xlrd' if f.name.endswith('.xls') else 'openpyxl'
        df = pd.read_excel(f, engine=engine, header=1)
        df.columns = [str(c).strip() for c in df.columns]

        if 'Status' in df.columns and 'Name' in df.columns:
          mask = df['Status'].str.contains('Late|Absence', case=False, na=False)
          day_data = df[mask].copy()
          day_data['Report_Date'] = file_date
          all_data.append(day_data[['Name', 'Status', 'Report_Date']])
      except Exception:
        pass

    if all_data:
      combined = pd.concat(all_data, ignore_index=True)
      summary = (
          combined.groupby(['Name', 'Status'])['Report_Date']
          .unique()
          .reset_index()
      )
      summary['Count'] = summary['Report_Date'].apply(len)
      summary['Dates_Str'] = summary['Report_Date'].apply(
          lambda x: ', '.join(sorted(x))
      )

      st.dataframe(
          summary[['Name', 'Status', 'Count', 'Dates_Str']],
          use_container_width=True,
      )

      if st.button('Generate Official Word Report (.docx)'):
        report_file = create_word_doc(summary)
        st.download_button(
            '📥 Download Official Word Document',
            report_file,
            'Alturath_Exceptions_Report.docx',
        )


# ============================================================
# 3. DAILY REPORT MODULE
# ============================================================


def classify_gate_event(event_value, punch_datetime):
  event = str(event_value).strip()
  punch_time = punch_datetime.time()
  if 'دخول' in event:
    return 'Check-In'
  if 'خروج' in event:
    if punch_time < time(12, 0):
      return 'Check-In'
    return 'Check-Out'
  return None


def run_daily_report_module():
  st.markdown(
      '<div class="main-header">Daily Biometric Attendance Audit</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<p style="color:#64748b; font-size:0.9rem;">Consolidate physical gate'
      ' logs (Zaqura & Mhmd Bn Ali) and Mawjood App records against official'
      ' weekly off schedules.</p>',
      unsafe_allow_html=True,
  )

  use_today = st.sidebar.toggle('Show Today Only', value=False)
  target_date = (
      date.today()
      if use_today
      else st.sidebar.date_input('Audit Date', value=date.today())
  )

  # Interactive Lateness Threshold Selector
  threshold_time = st.sidebar.time_input(
      '⏱️ Lateness Threshold', value=time(8, 35)
  )
  threshold_str = threshold_time.strftime('%H:%M')

  weekdays_ar = {
      'Monday': 'الاثنين',
      'Tuesday': 'الثلاثاء',
      'Wednesday': 'الاربعاء',
      'Thursday': 'الخميس',
      'Friday': 'الجمعة',
      'Saturday': 'السبت',
      'Sunday': 'الاحد',
  }
  current_weekday_ar = weekdays_ar.get(target_date.strftime('%A'), '')
  st.sidebar.info(
      f'Audit Day: **{current_weekday_ar}**\n\nCutoff: **{threshold_str}**'
  )

  st.sidebar.markdown('---')
  st.sidebar.subheader('Data Sources')
  f_zaqura = st.sidebar.file_uploader('Zaqura Gate File', type=['xlsx', 'xls'])
  f_mhmd = st.sidebar.file_uploader(
      'Mhmd Bn Ali Gate File', type=['xlsx', 'xls']
  )
  f_app = st.sidebar.file_uploader('Mawjood App File', type=['xlsx', 'xls'])
  f_weekly = st.sidebar.file_uploader(
      '📅 Weekly Day-Off List File', type=['xlsx', 'xls']
  )

  def process_gate(file, gate_name):
    try:
      engine = 'xlrd' if file.name.lower().endswith('.xls') else 'openpyxl'
      df = pd.read_excel(file, engine=engine)
      df.columns = [str(c).strip() for c in df.columns]

      name_col = (
          'الاسم'
          if 'الاسم' in df.columns
          else ('الإسم' if 'الإسم' in df.columns else None)
      )
      if not name_col or 'الوقت' not in df.columns:
        return pd.DataFrame()

      df['Raw_Name'] = df[name_col].astype(str).str.strip()
      df['Name'] = df['Raw_Name'].apply(clean_arabic_name)
      df['dt'] = pd.to_datetime(df['الوقت'], errors='coerce')
      df = df[df['dt'].notna()].copy()

      if 'Event' in df.columns:
        df['Event_Type'] = df.apply(
            lambda row: classify_gate_event(row['Event'], row['dt']), axis=1
        )
      else:
        df['Event_Type'] = 'Check-In'

      df = df[df['Event_Type'].notna()].copy()
      df['Date'] = df['dt'].dt.date
      df['Time'] = df['dt'].dt.strftime('%H:%M')
      df['Source'] = gate_name
      return df[
          ['Name', 'Raw_Name', 'dt', 'Date', 'Time', 'Event_Type', 'Source']
      ].sort_values('dt')
    except Exception:
      return pd.DataFrame()

  def process_app(file):
    try:
      df = pd.read_excel(file, header=3)
      df.columns = [str(c).strip() for c in df.columns]
      if 'الاسم' not in df.columns:
        return pd.DataFrame()

      result = []
      if 'دخول' in df.columns:
        for _, row in df.iterrows():
          dt = pd.to_datetime(row['دخول'], errors='coerce')
          if pd.notna(dt):
            raw_n = str(row['الاسم']).strip()
            result.append({
                'Name': clean_arabic_name(raw_n),
                'Raw_Name': raw_n,
                'dt': dt,
                'Date': dt.date(),
                'Time': dt.strftime('%H:%M'),
                'Event_Type': 'Check-In',
                'Source': 'Mawjood App',
            })

      checkout_columns = [
          'خروج',
          'الانصراف',
          'وقت الخروج',
          'Check-Out',
          'Checkout',
      ]
      chk_col = next((c for c in checkout_columns if c in df.columns), None)
      if chk_col:
        for _, row in df.iterrows():
          dt = pd.to_datetime(row[chk_col], errors='coerce')
          if pd.notna(dt):
            raw_n = str(row['الاسم']).strip()
            result.append({
                'Name': clean_arabic_name(raw_n),
                'Raw_Name': raw_n,
                'dt': dt,
                'Date': dt.date(),
                'Time': dt.strftime('%H:%M'),
                'Event_Type': 'Check-Out',
                'Source': 'Mawjood App',
            })
      return pd.DataFrame(result)
    except Exception:
      return pd.DataFrame()

  all_logs = []
  if f_zaqura:
    all_logs.append(process_gate(f_zaqura, 'Zaqura Gate'))
  if f_mhmd:
    all_logs.append(process_gate(f_mhmd, 'Mhmd Bn Ali Gate'))
  if f_app:
    all_logs.append(process_app(f_app))

  if all_logs or f_weekly:
    df_logs = (
        pd.concat(all_logs, ignore_index=True)
        if all_logs
        else pd.DataFrame(
            columns=[
                'Name',
                'Raw_Name',
                'dt',
                'Date',
                'Time',
                'Event_Type',
                'Source',
            ]
        )
    )

    df_off = pd.DataFrame(columns=['Name', 'Raw_Name', 'OffDay'])
    if f_weekly:
      off_raw = pd.read_excel(f_weekly).rename(
          columns={'الاسم الثلاثي': 'Raw_Name', 'الاجازة الاسبوعية': 'OffDay'}
      )
      off_raw['Name'] = off_raw['Raw_Name'].apply(clean_arabic_name)
      df_off = off_raw

    # Build mapping from normalized clean name to preferred raw display name
    name_display_map = {}
    if not df_logs.empty:
      for _, row in df_logs[['Name', 'Raw_Name']].drop_duplicates().iterrows():
        name_display_map[row['Name']] = row['Raw_Name']
    if not df_off.empty:
      for _, row in df_off[['Name', 'Raw_Name']].drop_duplicates().iterrows():
        if row['Name'] not in name_display_map:
          name_display_map[row['Name']] = row['Raw_Name']

    master_names = set()
    if not df_logs.empty:
      master_names.update(df_logs['Name'].dropna().unique())
    if not df_off.empty:
      master_names.update(df_off['Name'].dropna().unique())

    final_data = []
    previous_date = target_date - timedelta(days=1)

    for clean_name in sorted(master_names):
      display_name = name_display_map.get(clean_name, clean_name)
      person = (
          df_logs[df_logs['Name'] == clean_name].copy().sort_values('dt')
      )

      today_checkins = person[
          (person['Date'] == target_date)
          & (person['Event_Type'] == 'Check-In')
      ]
      yesterday_checkouts = person[
          (person['Date'] == previous_date)
          & (person['Event_Type'] == 'Check-Out')
      ]

      check_in = '-'
      check_in_source = '-'
      if not today_checkins.empty:
        first_in = today_checkins.iloc[0]
        check_in = first_in['Time']
        check_in_source = first_in['Source']

      check_out = '-'
      check_out_source = '-'
      if not yesterday_checkouts.empty:
        last_out = yesterday_checkouts.iloc[-1]
        check_out = last_out['Time']
        check_out_source = last_out['Source']

      off_info = df_off[df_off['Name'] == clean_name]
      is_off = False
      if not off_info.empty:
        off_val = str(off_info['OffDay'].iloc[0])
        # Support multiple off days separated by comma, slash, or spaces
        off_days = [
            d.strip() for d in re.split(r'[,،/\\-\s]+', off_val) if d.strip()
        ]
        is_off = current_weekday_ar in off_days

      if check_in != '-':
        status = '🔴 Late' if check_in > threshold_str else '🟢 On Time'
      elif is_off:
        status = '🟡 Weekly Off'
      elif check_out != '-':
        status = '🟠 Check-Out Only'
      else:
        status = '🔴 Absence'

      sources = [s for s in [check_in_source, check_out_source] if s != '-']
      source_str = ' + '.join(dict.fromkeys(sources)) if sources else '-'

      final_data.append({
          'Name': display_name,
          'Check-In': check_in,
          'Check-Out': check_out,
          'Source': source_str,
          'Status': status,
      })

    df_final = pd.DataFrame(final_data)

    col1, col2, col3 = st.columns(3)
    col1.metric('Total Employees', len(df_final))
    col2.metric(
        'On-Time', len(df_final[df_final['Status'].str.contains('On Time')])
    )
    col3.metric(
        'Violations / Absences',
        len(
            df_final[
                df_final['Status'].str.contains('Late|Absence', na=False)
            ]
        ),
    )

    st.markdown('---')
    st.dataframe(df_final, use_container_width=True)

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
      df_final.to_excel(writer, index=False, sheet_name='Audit', startrow=1)

    st.download_button(
        '📥 Export Daily Excel Report',
        buf.getvalue(),
        f'HR_Report_{target_date}.xlsx',
    )


# ============================================================
# 4. MAIN PAGE CONFIG & MODERN MINIMAL THEME
# ============================================================

st.set_page_config(
    page_title='Alturath HR System', page_icon='◈', layout='wide'
)

st.markdown(
    """
<style>
    .main-header {
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.2rem;
    }
    div[data-testid="stMetric"] {
        border-radius: 12px;
        padding: 0.8rem 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar Branding Logo Integration
try:
  st.sidebar.image(
      'https://uoturath.edu.iq/wp-content/uploads/2025/03/shield-1.png',
      width=90,
  )
except Exception:
  st.sidebar.title('ALTURATH HR')

st.sidebar.markdown(
    '**ALTURATH UNIVERSITY**\nHuman Resources & Biometric System'
)
st.sidebar.markdown('---')

app_mode = st.sidebar.selectbox(
    'Choose App Mode', ['Daily Report Tool', 'Multi-Day Audit Tool']
)

if app_mode == 'Daily Report Tool':
  run_daily_report_module()
else:
  run_exceptions_module()
