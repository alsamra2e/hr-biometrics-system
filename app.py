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
# 1. GLOBAL UTILITIES & ADVANCED ARABIC NAME NORMALIZATION
# ============================================================


def set_rtl(paragraph):
  p = paragraph._element
  pPr = p.get_or_add_pPr()
  bidi = pPr.find(qn("w:bidi"))
  if bidi is None:
    bidi = OxmlElement("w:bidi")
    pPr.append(bidi)


def set_table_rtl(table):
  tbl_pr = table._element.xpath("w:tblPr")
  if tbl_pr:
    bidi = OxmlElement("w:bidiVisual")
    tbl_pr[0].append(bidi)


def extract_date_from_filename(filename):
  match = re.search(r"\d{4}-\d{2}-\d{2}", filename)
  return match.group(0) if match else str(date.today())


def clean_arabic_name(name):
  """Normalizes Arabic names by removing department tags, diacritics,

  unifying Alef/Hamza variants, standardizing Taa Marbuta/Haa, and unifying
  confusable letters like ظ/ض.
  """
  if not isinstance(name, str):
    return ""
  for sep in ["/", "\\", "-", "(", ")"]:
    name = name.split(sep)[0]
  base = name.strip()
  base = re.sub(r"[\u064b-\u0652]", "", base)
  base = re.sub(r"[إأآٱؤئءإ]", "ا", base)
  base = base.replace("ة", "ه")
  base = base.replace("ظ", "ض")
  base = " ".join(base.split())
  return base


# ============================================================
# 2. OFFICIAL WORD REPORT GENERATION (BILINGUAL)
# ============================================================


def create_word_doc(df):
  doc = Document()
  section = doc.sections[0]
  header = section.header
  htable = header.add_table(1, 3, width=Inches(6.5))

  r = htable.rows[0].cells[0].paragraphs[0]
  r.text = (
      "جامعة التراث\nقسم الشؤون الإدارية والمالية\nشعبة الموارد البشرية"
  )
  r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
  set_rtl(r)

  m = htable.rows[0].cells[1].paragraphs[0]
  m.alignment = WD_ALIGN_PARAGRAPH.CENTER
  m.add_run("ALTURATH UNIVERSITY")

  l = htable.rows[0].cells[2].paragraphs[0]
  l.text = (
      "University Of Alturath\nDept. Of Admin & Financial Affairs\nHR"
      " Department"
  )
  l.alignment = WD_ALIGN_PARAGRAPH.LEFT

  p_line = doc.add_paragraph()
  run_line = p_line.add_run(
      "______________________________________________________________________"
  )
  run_line.font.color.rgb = RGBColor(0x8F, 0x0B, 0x0B)
  p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER

  body = doc.add_paragraph(
      "\nنرفق لسيادتكم في ادناه الكشف الخاص بموقف الحضور والغياب لكادر العمل"
      " الخاص بجامعة التراث وحسب كشف البصمة المرفق طيا نسخة منه ... راجين التفضل"
      " بالاطلاع واعلامنا توجيهات سيادتكم حول ذلك ... مع التقدير.."
  )
  body.alignment = WD_ALIGN_PARAGRAPH.RIGHT
  set_rtl(body)

  table = doc.add_table(rows=1, cols=5)
  table.style = "Table Grid"
  set_table_rtl(table)

  hdr = table.rows[0].cells
  labels = ["ت", "الاسم", "الحالة", "العدد", "التواريخ"]
  for i, txt in enumerate(labels):
    hdr[i].text = txt
    hdr[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_rtl(hdr[i].paragraphs[0])

  for idx, row in df.iterrows():
    cells = table.add_row().cells
    cells[0].text = str(idx + 1)
    cells[1].text = str(row["Name"])
    cells[2].text = "تأخير" if "Late" in str(row["Status"]) else "غياب"
    cells[3].text = str(row["Count"])
    d_para = cells[4].paragraphs[0]
    d_run = d_para.add_run(row["Dates_Str"])
    d_run.font.size = Pt(8)
    for cell in cells:
      cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
      set_rtl(cell.paragraphs[0])

  doc.add_paragraph("\n\n")
  sig = doc.add_paragraph(
      "م.م محمد زهير طالب النقيب\nمدير قسم الشؤون الادارية والموارد البشرية"
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
      " exceptions, lateness, and absence logs across multiple exported"
      " files.</p>",
      unsafe_allow_html=True,
  )

  uploaded_files = st.file_uploader(
      "Upload Exported Excel Reports",
      accept_multiple_files=True,
      type=["xlsx", "xls"],
  )

  if uploaded_files:
    all_data = []
    for f in uploaded_files:
      file_date = extract_date_from_filename(f.name)
      try:
        engine = "xlrd" if f.name.endswith(".xls") else "openpyxl"
        df = pd.read_excel(f, engine=engine, header=1)
        df.columns = [str(c).strip() for c in df.columns]

        if "Status" in df.columns and "Name" in df.columns:
          mask = df["Status"].str.contains(
              "Late|Absence", case=False, na=False
          )
          day_data = df[mask].copy()
          day_data["Report_Date"] = file_date
          all_data.append(day_data[["Name", "Status", "Report_Date"]])
      except Exception:
        pass

    if all_data:
      combined = pd.concat(all_data, ignore_index=True)
      summary = (
          combined.groupby(["Name", "Status"])["Report_Date"]
          .unique()
          .reset_index()
      )
      summary["Count"] = summary["Report_Date"].apply(len)
      summary["Dates_Str"] = summary["Report_Date"].apply(
          lambda x: ", ".join(sorted(x))
      )

      st.dataframe(
          summary[["Name", "Status", "Count", "Dates_Str"]],
          use_container_width=True,
      )

      if st.button("Generate Official Word Report (.docx)"):
        report_file = create_word_doc(summary)
        st.download_button(
            "📥 Download Official Word Document",
            report_file,
            "Alturath_Exceptions_Report.docx",
        )


# ============================================================
# 3. DAILY REPORT MODULE & PROFESSIONAL EXCEL EXPORT
# ============================================================


def classify_gate_event(event_value, punch_datetime):
  event = str(event_value).strip()
  punch_time = punch_datetime.time()
  if "دخول" in event:
    return "Check-In"
  if "خروج" in event:
    if punch_time < time(12, 0):
      return "Check-In"
    return "Check-Out"
  return None


def create_daily_excel(df_final, target_date, current_weekday_ar):
  buffer = BytesIO()
  previous_date = target_date - timedelta(days=1)

  ar_map = {
      "Monday": "الاثنين",
      "Tuesday": "الثلاثاء",
      "Wednesday": "الاربعاء",
      "Thursday": "الخميس",
      "Friday": "الجمعة",
      "Saturday": "السبت",
      "Sunday": "الاحد",
  }
  prev_weekday_ar = ar_map.get(previous_date.strftime("%A"), "")

  export_df = df_final[
      ["Name", "Check-In", "Check-Out", "In_Source", "Out_Source", "Status"]
  ].copy()

  with pd.ExcelWriter(
      buffer,
      engine="xlsxwriter",
      engine_kwargs={
          "options": {
              "strings_to_urls": False,
              "constant_memory": True,
          }
      },
  ) as writer:
    workbook = writer.book
    worksheet = workbook.add_worksheet("Attendance")
    writer.sheets["Attendance"] = worksheet

    worksheet.set_paper(9)  # A4 size
    worksheet.set_portrait()
    worksheet.fit_to_pages(1, 0)
    worksheet.set_footer("&CPage &P of &N")

    title_format = workbook.add_format({
        "bold": True,
        "font_size": 13,
        "font_color": "#FFFFFF",
        "bg_color": "#071426",
        "align": "center",
        "valign": "vcenter",
    })
    subtitle_format = workbook.add_format({
        "font_size": 9,
        "font_color": "#334155",
        "bg_color": "#F1F5F9",
        "align": "center",
        "valign": "vcenter",
    })
    header_format = workbook.add_format({
        "bold": True,
        "font_color": "#FFFFFF",
        "bg_color": "#2563EB",
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "border_color": "#CBD5E1",
        "text_wrap": True,
        "font_size": 10,
    })
    cell_format = workbook.add_format({
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "border_color": "#E2E8F0",
        "font_size": 10,
    })

    fmt_base = workbook.add_format({"font_size": 10, "valign": "vcenter"})
    fmt_green = workbook.add_format(
        {"font_size": 10, "font_color": "#16A34A", "bold": True}
    )
    fmt_gray = workbook.add_format(
        {"font_size": 10, "font_color": "#64748B", "bold": True}
    )

    worksheet.merge_range(
        "A1:F1", "جامعة التراث - الموقف اليومي", title_format
    )

    date_subtitle = (
        f'تاريخ الحضور: {current_weekday_ar} ({target_date.strftime("%Y/%m/%d")})'
        f'    |    تاريخ الانصراف: {prev_weekday_ar}'
        f' ({previous_date.strftime("%Y/%m/%d")})'
    )
    worksheet.merge_range("A2:F2", date_subtitle, subtitle_format)

    worksheet.set_row(0, 26)
    worksheet.set_row(1, 22)

    headers = [
        "ت\nNo.",
        "الاسم\nName",
        f"وقت الدخول\nCheck-In ({target_date.strftime('%d %b')})",
        f"وقت الانصراف\nCheck-Out ({previous_date.strftime('%d %b')})",
        "المصدر\nSource",
        "الحالة\nStatus",
    ]

    for col, header in enumerate(headers):
      worksheet.write(2, col, header, header_format)

    worksheet.set_row(2, 34)

    for i, (_, row) in enumerate(export_df.iterrows()):
      excel_row = i + 3
      in_src = str(row["In_Source"])
      out_src = str(row["Out_Source"])

      worksheet.write(excel_row, 0, i + 1, cell_format)
      worksheet.write(excel_row, 1, str(row["Name"]), cell_format)
      worksheet.write(excel_row, 2, str(row["Check-In"]), cell_format)
      worksheet.write(excel_row, 3, str(row["Check-Out"]), cell_format)

      if in_src != "-" and out_src != "-" and in_src != out_src:
        worksheet.write_rich_string(
            excel_row,
            4,
            fmt_base,
            f"{in_src} ",
            fmt_green,
            "(In)",
            fmt_base,
            " + ",
            fmt_base,
            f"{out_src} ",
            fmt_gray,
            "(Out)",
            cell_format,
        )
      elif in_src != "-":
        worksheet.write_rich_string(
            excel_row,
            4,
            fmt_base,
            f"{in_src} ",
            fmt_green,
            "(In)",
            cell_format,
        )
      elif out_src != "-":
        worksheet.write_rich_string(
            excel_row,
            4,
            fmt_base,
            f"{out_src} ",
            fmt_gray,
            "(Out)",
            cell_format,
        )
      else:
        worksheet.write(excel_row, 4, "-", cell_format)

      worksheet.write(excel_row, 5, str(row["Status"]), cell_format)

    worksheet.set_column("A:A", 6)
    worksheet.set_column("B:B", 32)
    worksheet.set_column("C:D", 20)
    worksheet.set_column("E:E", 28)
    worksheet.set_column("F:F", 18)

    worksheet.freeze_panes(3, 0)
    worksheet.hide_gridlines(2)

  buffer.seek(0)
  return buffer.getvalue()


def run_daily_report_module():
  st.markdown(
      '<div class="main-header">Daily Biometric Attendance Audit</div>',
      unsafe_allow_html=True,
  )
  st.markdown(
      '<p style="color:#64748b; font-size:0.9rem;">Consolidate physical gate'
      " logs (Zaqura & Mhmd Bn Ali) against official weekly off schedules.</p>",
      unsafe_allow_html=True,
  )

  use_today = st.sidebar.toggle("Show Today Only", value=False)
  target_date = (
      date.today()
      if use_today
      else st.sidebar.date_input("Audit Date", value=date.today())
  )

  threshold_time = st.sidebar.time_input(
      "⏱️ Lateness Threshold", value=time(8, 35)
  )
  threshold_str = threshold_time.strftime("%H:%M")

  weekdays_ar = {
      "Monday": "الاثنين",
      "Tuesday": "الثلاثاء",
      "Wednesday": "الاربعاء",
      "Thursday": "الخميس",
      "Friday": "الجمعة",
      "Saturday": "السبت",
      "Sunday": "الاحد",
  }
  current_weekday_ar = weekdays_ar.get(target_date.strftime("%A"), "")
  previous_date = target_date - timedelta(days=1)
  previous_weekday_ar = weekdays_ar.get(previous_date.strftime("%A"), "")

  st.sidebar.info(
      f"Audit Day: **{current_weekday_ar}**\n\nCutoff: **{threshold_str}**"
  )

  st.sidebar.markdown("---")
  st.sidebar.subheader("Data Sources")
  f_zaqura = st.sidebar.file_uploader(
      "Zaqura Log File", type=["xlsx", "xls"]
  )
  f_mhmd = st.sidebar.file_uploader(
      "Mhmd Bn Ali Log File", type=["xlsx", "xls"]
  )
  f_weekly = st.sidebar.file_uploader(
      "📅 Weekly Day-Off List File (Optional)", type=["xlsx", "xls"]
  )

  def process_gate(file, gate_name):
    try:
      engine = "xlrd" if file.name.lower().endswith(".xls") else "openpyxl"
      df = pd.read_excel(file, engine=engine)
      df.columns = [str(c).strip() for c in df.columns]

      name_col = (
          "الاسم"
          if "الاسم" in df.columns
          else ("الإسم" if "الإسم" in df.columns else None)
      )
      if not name_col or "الوقت" not in df.columns:
        return pd.DataFrame()

      df["Raw_Name"] = df[name_col].astype(str).str.strip()
      df["Name"] = df["Raw_Name"].apply(clean_arabic_name)
      df["dt"] = pd.to_datetime(df["الوقت"], errors="coerce")
      df = df[df["dt"].notna()].copy()

      if "Event" in df.columns:
        df["Event_Type"] = df.apply(
            lambda row: classify_gate_event(row["Event"], row["dt"]), axis=1
        )
      else:
        df["Event_Type"] = "Check-In"

      df = df[df["Event_Type"].notna()].copy()
      df["Date"] = df["dt"].dt.date
      df["Time"] = df["dt"].dt.strftime("%H:%M")

      clean_gate_name = (
          gate_name.replace("Gate", "").replace("gate", "").strip()
      )
      df["Source"] = clean_gate_name

      prev_d = target_date - timedelta(days=1)
      df = df[(df["Date"] == target_date) | (df["Date"] == prev_d)]

      return df[
          ["Name", "Raw_Name", "dt", "Date", "Time", "Event_Type", "Source"]
      ].sort_values("dt")
    except Exception:
      return pd.DataFrame()

  all_logs = []
  if f_zaqura:
    all_logs.append(process_gate(f_zaqura, "Zaqura"))
  if f_mhmd:
    all_logs.append(process_gate(f_mhmd, "Mhmd Bn Ali"))

  if all_logs or f_weekly:
    df_logs = (
        pd.concat(all_logs, ignore_index=True)
        if all_logs
        else pd.DataFrame(
            columns=[
                "Name",
                "Raw_Name",
                "dt",
                "Date",
                "Time",
                "Event_Type",
                "Source",
            ]
        )
    )

    df_off = pd.DataFrame(columns=["Name", "Raw_Name", "OffDay"])
    if f_weekly:
      try:
        off_raw = pd.read_excel(f_weekly)
        off_raw.columns = [str(c).strip() for c in off_raw.columns]
        off_col = (
            "الاسم الثلاثي"
            if "الاسم الثلاثي" in off_raw.columns
            else (
                "الاسم"
                if "الاسم" in off_raw.columns
                else off_raw.columns[0]
            )
        )
        day_col = (
            "الاجازة الاسبوعية"
            if "الاجازة الاسبوعية" in off_raw.columns
            else off_raw.columns[1]
        )
        off_raw = off_raw.rename(
            columns={off_col: "Raw_Name", day_col: "OffDay"}
        )
        off_raw["Name"] = off_raw["Raw_Name"].apply(clean_arabic_name)
        df_off = off_raw
      except Exception:
        pass

    name_display_map = {}
    if not df_logs.empty:
      for _, row in df_logs[["Name", "Raw_Name"]].drop_duplicates().iterrows():
        name_display_map[row["Name"]] = row["Raw_Name"]
    if not df_off.empty:
      for _, row in df_off[["Name", "Raw_Name"]].drop_duplicates().iterrows():
        if row["Name"] not in name_display_map:
          name_display_map[row["Name"]] = row["Raw_Name"]

    master_names = set()
    if not df_logs.empty:
      master_names.update(df_logs["Name"].dropna().unique())
    if not df_off.empty:
      master_names.update(df_off["Name"].dropna().unique())

    final_data = []

    for clean_name in sorted(master_names):
      display_name = name_display_map.get(clean_name, clean_name)
      person = (
          df_logs[df_logs["Name"] == clean_name].copy().sort_values("dt")
      )

      today_checkins = person[
          (person["Date"] == target_date)
          & (person["Event_Type"] == "Check-In")
      ]
      yesterday_checkouts = person[
          (person["Date"] == previous_date)
          & (person["Event_Type"] == "Check-Out")
      ]

      check_in = "-"
      check_in_source = "-"
      if not today_checkins.empty:
        first_in = today_checkins.iloc[0]
        check_in = first_in["Time"]
        check_in_source = first_in["Source"]

      check_out = "-"
      check_out_source = "-"
      if not yesterday_checkouts.empty:
        last_out = yesterday_checkouts.iloc[-1]
        check_out = last_out["Time"]
        check_out_source = last_out["Source"]

      # Evaluate Weekly Off status for Check-In day vs. Check-Out day separately
      off_info = df_off[df_off["Name"] == clean_name]
      is_checkin_off = False
      is_checkout_off = False

      if not off_info.empty:
        off_val = str(off_info["OffDay"].iloc[0])
        for sep in [",", "،", "/", "\\", "-"]:
          off_val = off_val.replace(sep, " ")
        off_days = [d.strip() for d in off_val.split() if d.strip()]
        is_checkin_off = current_weekday_ar in off_days
        is_checkout_off = previous_weekday_ar in off_days

      # Handle Check-Out text if day off on previous day
      if check_out == "-" and is_checkout_off:
        check_out = "🟡 Day Off"

      # Determine status
      if check_in != "-":
        status = "🔴 Late" if check_in > threshold_str else "🟢 On Time"
      elif is_checkin_off:
        status = "🟡 Weekly Off"
      elif check_out != "-":
        status = "🟠 Check-Out Only"
      else:
        status = "🔴 Absence"

      final_data.append({
          "Name": display_name,
          "Check-In": check_in,
          "Check-Out": check_out,
          "In_Source": check_in_source,
          "Out_Source": check_out_source,
          "Status": status,
      })

    df_final = pd.DataFrame(final_data)

    if not df_final.empty:
      col1, col2, col3 = st.columns(3)
      col1.metric("Total Employees", len(df_final))
      col2.metric(
          "On-Time", len(df_final[df_final["Status"].str.contains("On Time")])
      )
      col3.metric(
          "Violations / Absences",
          len(
              df_final[
                  df_final["Status"].str.contains("Late|Absence", na=False)
              ]
          ),
      )

      st.markdown("---")
      st.dataframe(df_final, use_container_width=True)

      excel_bytes = create_daily_excel(
          df_final, target_date, current_weekday_ar
      )
      st.download_button(
          "📥 Export Daily Excel Report",
          excel_bytes,
          file_name=f"Attendance_{target_date}.xlsx",
          mime=(
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          ),
      )
  else:
    st.info(
        "👈 Please upload at least one gate log file (Zaqura or Mhmd Bn Ali) from"
        " the sidebar to start the daily audit."
    )


# ============================================================
# 4. MAIN PAGE CONFIG & MODERN MINIMAL THEME
# ============================================================

st.set_page_config(
    page_title="Alturath HR System", page_icon="◈", layout="wide"
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
    .sidebar-shield {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 0;
        margin-bottom: 12px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Inline SVG Shield Logo for 100% Guaranteed Sidebar Rendering
st.sidebar.markdown(
    """
<div class="sidebar-shield">
    <svg width="42" height="42" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2L3 5V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V5L12 2Z" fill="#2563EB" stroke="#1D4ED8" stroke-width="1.5" stroke-linejoin="round"/>
        <path d="M12 6V18M8 10L12 6L16 10" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <div>
        <div style="font-weight: 850; font-size: 1.05rem; color: #0F172A; line-height: 1.2;">ALTURATH HR</div>
        <div style="font-size: 0.68rem; color: #64748B; font-weight: 600;">Biometric Attendance System</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")

app_mode = st.sidebar.selectbox(
    "Choose App Mode", ["Daily Report Tool", "Multi-Day Audit Tool"]
)

if app_mode == "Daily Report Tool":
  run_daily_report_module()
else:
  run_exceptions_module()
