import streamlit as st
import pandas as pd
import re
import requests

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from io import BytesIO
from datetime import date, time, timedelta


# ============================================================
# ALTURATH HR BIOMETRICS SYSTEM V2
# ============================================================


# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Alturath HR • Biometric System",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. FUTURISTIC MINIMAL THEME
# ============================================================

def apply_v2_theme():

    st.markdown(
        """
        <style>

        /* ====================================================
           GLOBAL
        ==================================================== */

        @import url(
            'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
        );

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 80% 0%,
                    rgba(59,130,246,0.08),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 0% 100%,
                    rgba(16,185,129,0.05),
                    transparent 25%
                ),
                #f7f8fa;
        }

        /* ====================================================
           SIDEBAR
        ==================================================== */

        section[data-testid="stSidebar"] {
            background: #0b1120;
            border-right: 1px solid #1e293b;
        }

        section[data-testid="stSidebar"] * {
            color: #e2e8f0;
        }

        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stFileUploader label,
        section[data-testid="stSidebar"] .stDateInput label {
            color: #94a3b8 !important;
            font-size: 12px;
            font-weight: 600;
        }

        section[data-testid="stSidebar"] .stFileUploader {
            margin-bottom: 8px;
        }

        /* ====================================================
           BRAND
        ==================================================== */

        .brand {
            padding: 8px 4px 24px 4px;
        }

        .brand-mark {
            width: 42px;
            height: 42px;
            border-radius: 12px;

            display: flex;
            align-items: center;
            justify-content: center;

            background:
                linear-gradient(
                    135deg,
                    #2563eb,
                    #06b6d4
                );

            color: white;
            font-size: 20px;
            font-weight: 800;

            box-shadow:
                0 8px 24px rgba(37,99,235,0.25);

            margin-bottom: 12px;
        }

        .brand-name {
            color: #f8fafc;
            font-size: 18px;
            font-weight: 800;
            letter-spacing: -0.4px;
        }

        .brand-sub {
            color: #64748b;
            font-size: 11px;
            margin-top: 3px;
        }

        /* ====================================================
           HEADER
        ==================================================== */

        .hero {
            position: relative;
            overflow: hidden;

            background: #0f172a;

            border: 1px solid #1e293b;
            border-radius: 20px;

            padding: 26px 30px;
            margin-bottom: 22px;

            box-shadow:
                0 15px 40px rgba(15,23,42,0.08);
        }

        .hero:after {
            content: "";

            position: absolute;

            width: 240px;
            height: 240px;

            right: -100px;
            top: -120px;

            border-radius: 50%;

            background:
                radial-gradient(
                    circle,
                    rgba(37,99,235,0.35),
                    transparent 68%
                );
        }

        .hero-label {
            color: #60a5fa;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.8px;
            text-transform: uppercase;
            margin-bottom: 7px;
        }

        .hero-title {
            color: #f8fafc;
            font-size: 30px;
            font-weight: 800;
            letter-spacing: -1px;
            margin: 0;
        }

        .hero-description {
            color: #94a3b8;
            font-size: 13px;
            margin-top: 7px;
        }

        /* ====================================================
           INFO BAR
        ==================================================== */

        .date-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;

            background: #ffffff;

            border: 1px solid #e2e8f0;
            border-radius: 14px;

            padding: 13px 17px;

            margin-bottom: 18px;

            box-shadow:
                0 5px 18px rgba(15,23,42,0.04);
        }

        .date-main {
            color: #0f172a;
            font-size: 14px;
            font-weight: 700;
        }

        .date-sub {
            color: #64748b;
            font-size: 11px;
            margin-top: 2px;
        }

        .checkout-badge {
            background: #eff6ff;
            color: #2563eb;

            border: 1px solid #dbeafe;

            padding: 6px 10px;
            border-radius: 999px;

            font-size: 11px;
            font-weight: 700;
        }

        /* ====================================================
           METRICS
        ==================================================== */

        div[data-testid="stMetric"] {
            background: #ffffff;

            border: 1px solid #e2e8f0;
            border-radius: 14px;

            padding: 12px 15px;

            box-shadow:
                0 5px 18px rgba(15,23,42,0.035);
        }

        div[data-testid="stMetricLabel"] {
            color: #64748b;
            font-size: 11px;
        }

        div[data-testid="stMetricValue"] {
            color: #0f172a;
            font-weight: 800;
        }

        /* ====================================================
           BUTTONS
        ==================================================== */

        .stButton > button,
        .stDownloadButton > button {

            border-radius: 9px;

            border: 1px solid #2563eb;

            background: #2563eb;

            color: white;

            font-weight: 700;

            transition: all 0.18s ease;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {

            background: #1d4ed8;

            border-color: #1d4ed8;

            transform: translateY(-1px);

            box-shadow:
                0 7px 18px rgba(37,99,235,0.18);
        }

        /* ====================================================
           DATAFRAME
        ==================================================== */

        div[data-testid="stDataFrame"] {

            border: 1px solid #e2e8f0;

            border-radius: 14px;

            overflow: hidden;

            box-shadow:
                0 7px 25px rgba(15,23,42,0.05);
        }

        /* ====================================================
           SECTION TITLE
        ==================================================== */

        .section-title {
            color: #0f172a;
            font-size: 16px;
            font-weight: 800;

            margin-top: 24px;
            margin-bottom: 10px;
        }

        /* ====================================================
           STATUS CARDS
        ==================================================== */

        .status-note {
            border-radius: 12px;

            padding: 12px 15px;

            background: #ffffff;

            border: 1px solid #e2e8f0;

            color: #475569;

            font-size: 12px;
        }

        /* ====================================================
           FOOTER
        ==================================================== */

        .footer {
            color: #94a3b8;
            text-align: center;

            font-size: 10px;

            padding: 25px 0 10px 0;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


apply_v2_theme()


# ============================================================
# 3. GLOBAL UTILITIES
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

    match = re.search(
        r"\d{4}-\d{2}-\d{2}",
        filename
    )

    if match:

        return match.group(0)

    return str(date.today())


# ============================================================
# 4. EVENT CLASSIFICATION
# ============================================================

def classify_gate_event(event_value, punch_datetime):

    """
    Actual biometric rules:

        دخول(1)             -> Check-In

        خروج(2) before 12   -> Check-In
                              (wrong button / morning punch)

        خروج(2) 12:00+      -> Check-Out
    """

    event = str(
        event_value
    ).strip()

    punch_time = punch_datetime.time()

    # دخول(1)
    if "دخول" in event:

        return "Check-In"

    # خروج(2)
    if "خروج" in event:

        if punch_time < time(12, 0):

            return "Check-In"

        return "Check-Out"

    return None


# ============================================================
# 5. PROCESS GATE
# ============================================================

def process_gate(file, gate_name):

    try:

        engine = (
            "xlrd"
            if file.name.lower().endswith(".xls")
            else "openpyxl"
        )

        df = pd.read_excel(
            file,
            engine=engine
        )

        df.columns = [
            str(c).strip()
            for c in df.columns
        ]

        # ----------------------------------------------------
        # Name
        # ----------------------------------------------------

        if "الاسم" in df.columns:

            name_col = "الاسم"

        elif "الإسم" in df.columns:

            name_col = "الإسم"

        else:

            st.warning(
                f"{gate_name}: الاسم column not found."
            )

            return pd.DataFrame()

        # ----------------------------------------------------
        # Time
        # ----------------------------------------------------

        if "الوقت" not in df.columns:

            st.warning(
                f"{gate_name}: الوقت column not found."
            )

            return pd.DataFrame()

        # ----------------------------------------------------
        # Event
        # ----------------------------------------------------

        if "Event" not in df.columns:

            st.warning(
                f"{gate_name}: Event column not found."
            )

            return pd.DataFrame()

        df["Name"] = (
            df[name_col]
            .astype(str)
            .str.strip()
        )

        df["dt"] = pd.to_datetime(
            df["الوقت"],
            errors="coerce"
        )

        df = df[
            df["dt"].notna()
            &
            (df["Name"] != "")
            &
            (df["Name"] != "nan")
        ].copy()

        df["Event_Type"] = df.apply(
            lambda row:
                classify_gate_event(
                    row["Event"],
                    row["dt"]
                ),
            axis=1
        )

        df = df[
            df["Event_Type"].notna()
        ].copy()

        df["Date"] = (
            df["dt"].dt.date
        )

        df["Time"] = (
            df["dt"].dt.strftime("%H:%M")
        )

        df["Source"] = gate_name

        return df[
            [
                "Name",
                "dt",
                "Date",
                "Time",
                "Event_Type",
                "Source"
            ]
        ].sort_values("dt")

    except Exception as e:

        st.error(
            f"Error processing {gate_name}: {e}"
        )

        return pd.DataFrame()


# ============================================================
# 6. PROCESS MAWJOOD APP
# ============================================================

def process_app(file):

    try:

        df = pd.read_excel(
            file,
            header=3
        )

        df.columns = [
            str(c).strip()
            for c in df.columns
        ]

        if "الاسم" not in df.columns:

            return pd.DataFrame()

        result = []

        # ----------------------------------------------------
        # Check-In
        # ----------------------------------------------------

        if "دخول" in df.columns:

            for _, row in df.iterrows():

                dt = pd.to_datetime(
                    row["دخول"],
                    errors="coerce"
                )

                if pd.notna(dt):

                    result.append(
                        {
                            "Name": row["الاسم"],
                            "dt": dt,
                            "Date": dt.date(),
                            "Time": dt.strftime("%H:%M"),
                            "Event_Type": "Check-In",
                            "Source": "Mawjood App"
                        }
                    )

        # ----------------------------------------------------
        # Check-Out
        # ----------------------------------------------------

        checkout_columns = [
            "خروج",
            "الانصراف",
            "وقت الخروج",
            "Check-Out",
            "Checkout"
        ]

        checkout_col = None

        for col in checkout_columns:

            if col in df.columns:

                checkout_col = col

                break

        if checkout_col:

            for _, row in df.iterrows():

                dt = pd.to_datetime(
                    row[checkout_col],
                    errors="coerce"
                )

                if pd.notna(dt):

                    result.append(
                        {
                            "Name": row["الاسم"],
                            "dt": dt,
                            "Date": dt.date(),
                            "Time": dt.strftime("%H:%M"),
                            "Event_Type": "Check-Out",
                            "Source": "Mawjood App"
                        }
                    )

        return pd.DataFrame(
            result
        )

    except Exception as e:

        st.error(
            f"Error processing Mawjood App: {e}"
        )

        return pd.DataFrame()


# ============================================================
# 7. BUILD DAILY HR REPORT
# ============================================================

def build_daily_attendance(
    df_logs,
    target_date,
    current_weekday_ar,
    df_off
):

    """
    IMPORTANT HR SUBMISSION RULE:

    If report date = 7 Oct:

        Check-In  -> 7 Oct
        Check-Out -> 6 Oct

    This is intentional because HR receives the current day's
    check-in report while the checkout belongs to the previous
    working day.
    """

    master_names = set()

    # --------------------------------------------------------
    # Names from logs
    # --------------------------------------------------------

    if not df_logs.empty:

        master_names.update(
            df_logs["Name"]
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

    # --------------------------------------------------------
    # Names from weekly off
    # --------------------------------------------------------

    if not df_off.empty:

        master_names.update(
            df_off["Name"]
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

    final_data = []

    previous_date = (
        target_date
        - timedelta(days=1)
    )

    for name in sorted(
        master_names
    ):

        person = df_logs[
            df_logs["Name"]
            .astype(str)
            .str.strip()
            ==
            str(name).strip()
        ].copy()

        person = person.sort_values(
            "dt"
        )

        # ====================================================
        # TODAY = CHECK-IN
        # ====================================================

        today_checkins = person[
            (person["Date"] == target_date)
            &
            (person["Event_Type"] == "Check-In")
        ].copy()

        # ====================================================
        # YESTERDAY = CHECK-OUT
        # ====================================================

        yesterday_checkouts = person[
            (person["Date"] == previous_date)
            &
            (person["Event_Type"] == "Check-Out")
        ].copy()

        # ====================================================
        # CHECK-IN
        # ====================================================

        check_in = "-"
        check_in_source = "-"

        if not today_checkins.empty:

            first_checkin = (
                today_checkins
                .sort_values("dt")
                .iloc[0]
            )

            check_in = (
                first_checkin["Time"]
            )

            check_in_source = (
                first_checkin["Source"]
            )

        # ====================================================
        # CHECK-OUT
        # ====================================================

        check_out = "-"
        check_out_source = "-"

        if not yesterday_checkouts.empty:

            last_checkout = (
                yesterday_checkouts
                .sort_values("dt")
                .iloc[-1]
            )

            check_out = (
                last_checkout["Time"]
            )

            check_out_source = (
                last_checkout["Source"]
            )

        # ====================================================
        # WEEKLY OFF
        # ====================================================

        off_info = df_off[
            df_off["Name"]
            .astype(str)
            .str.strip()
            ==
            str(name).strip()
        ]

        is_off = False

        if not off_info.empty:

            is_off = (
                str(
                    off_info["OffDay"].iloc[0]
                ).strip()
                ==
                str(current_weekday_ar).strip()
            )

        # ====================================================
        # STATUS
        # ====================================================

        if check_in != "-":

            if check_in > "08:35":

                status = "🔴 Late"

            else:

                status = "🟢 On Time"

        elif is_off:

            status = "🟡 Weekly Off"

        elif check_out != "-":

            status = "🟠 Check-Out Only"

        else:

            status = "🔴 Absence"

        # ====================================================
        # SOURCE
        # ====================================================

        source_parts = []

        if check_in_source != "-":

            source_parts.append(
                check_in_source
            )

        if check_out_source != "-":

            if check_out_source not in source_parts:

                source_parts.append(
                    check_out_source
                )

        source = " + ".join(
            source_parts
        )

        if not source:

            source = "-"

        final_data.append(
            {
                "Name": name,
                "Check-In": check_in,
                "Check-Out": check_out,
                "Source": source,
                "Status": status
            }
        )

    return pd.DataFrame(
        final_data
    )


# ============================================================
# 8. SMALL / CLEAN EXCEL EXPORT
# ============================================================

def create_daily_excel(
    df_final,
    target_date
):

    """
    Lightweight LTR Excel export.

    No RTL.
    No unnecessary images.
    No huge formatting.
    No print-area configuration.
    """

    buf = BytesIO()

    # Keep only the fields needed by HR.
    export_df = df_final[
        [
            "Name",
            "Check-In",
            "Check-Out",
            "Source",
            "Status"
        ]
    ].copy()

    with pd.ExcelWriter(
        buf,
        engine="xlsxwriter",
        engine_kwargs={
            "options": {
                "strings_to_urls": False
            }
        }
    ) as writer:

        workbook = writer.book

        worksheet = workbook.add_worksheet(
            "Attendance"
        )

        writer.sheets[
            "Attendance"
        ] = worksheet

        # ----------------------------------------------------
        # Minimal formats
        # ----------------------------------------------------

        title_format = workbook.add_format(
            {
                "bold": True,
                "font_size": 14,
                "font_color": "#FFFFFF",
                "bg_color": "#0F172A",
                "align": "center",
                "valign": "vcenter"
            }
        )

        subtitle_format = workbook.add_format(
            {
                "font_size": 9,
                "font_color": "#64748B",
                "align": "center",
                "valign": "vcenter"
            }
        )

        header_format = workbook.add_format(
            {
                "bold": True,
                "font_color": "#FFFFFF",
                "bg_color": "#2563EB",
                "align": "center",
                "valign": "vcenter",
                "border": 1,
                "border_color": "#CBD5E1"
            }
        )

        cell_format = workbook.add_format(
            {
                "align": "center",
                "valign": "vcenter",
                "border": 1,
                "border_color": "#E2E8F0"
            }
        )

        # ----------------------------------------------------
        # IMPORTANT:
        # LTR export. Do NOT use right_to_left().
        # ----------------------------------------------------

        # Title
        worksheet.merge_range(
            "A1:F1",
            (
                "ALTURATH UNIVERSITY • "
                "DAILY ATTENDANCE"
            ),
            title_format
        )

        worksheet.merge_range(
            "A2:F2",
            (
                f"Check-In: "
                f"{target_date.strftime('%d %b %Y')}"
                f"   |   "
                f"Check-Out: "
                f"{(target_date - timedelta(days=1)).strftime('%d %b %Y')}"
            ),
            subtitle_format
        )

        worksheet.set_row(
            0,
            25
        )

        worksheet.set_row(
            1,
            20
        )

        # ----------------------------------------------------
        # Headers
        # ----------------------------------------------------

        headers = [
            "No.",
            "Name",
            f"Check-In\n({target_date.strftime('%d %b')})",
            (
                "Check-Out\n"
                f"({(target_date - timedelta(days=1)).strftime('%d %b')})"
            ),
            "Source",
            "Status"
        ]

        for col, header in enumerate(
            headers
        ):

            worksheet.write(
                2,
                col,
                header,
                header_format
            )

        worksheet.set_row(
            2,
            32
        )

        # ----------------------------------------------------
        # Data
        # ----------------------------------------------------

        for i, (_, row) in enumerate(
            export_df.iterrows()
        ):

            excel_row = i + 3

            worksheet.write(
                excel_row,
                0,
                i + 1,
                cell_format
            )

            worksheet.write(
                excel_row,
                1,
                str(row["Name"]),
                cell_format
            )

            worksheet.write(
                excel_row,
                2,
                str(row["Check-In"]),
                cell_format
            )

            worksheet.write(
                excel_row,
                3,
                str(row["Check-Out"]),
                cell_format
            )

            worksheet.write(
                excel_row,
                4,
                str(row["Source"]),
                cell_format
            )

            worksheet.write(
                excel_row,
                5,
                str(row["Status"]),
                cell_format
            )

        # ----------------------------------------------------
        # Compact widths
        # ----------------------------------------------------

        worksheet.set_column(
            "A:A",
            6
        )

        worksheet.set_column(
            "B:B",
            30
        )

        worksheet.set_column(
            "C:D",
            14
        )

        worksheet.set_column(
            "E:E",
            20
        )

        worksheet.set_column(
            "F:F",
            17
        )

        # ----------------------------------------------------
        # Lightweight worksheet settings
        # ----------------------------------------------------

        worksheet.freeze_panes(
            3,
            0
        )

        worksheet.hide_gridlines(
            2
        )

    buf.seek(0)

    return buf.getvalue()


# ============================================================
# 9. WORD REPORT
# ============================================================

def create_word_doc(df):

    doc = Document()

    section = doc.sections[0]

    header = section.header

    htable = header.add_table(
        1,
        3,
        width=Inches(6.5)
    )

    # --------------------------------------------------------
    # Arabic
    # --------------------------------------------------------

    r = (
        htable.rows[0]
        .cells[0]
        .paragraphs[0]
    )

    r.text = (
        "جامعة التراث\n"
        "قسم الشؤون الإدارية والمالية\n"
        "شعبة الموارد البشرية"
    )

    r.alignment = (
        WD_ALIGN_PARAGRAPH.RIGHT
    )

    set_rtl(r)

    # --------------------------------------------------------
    # Logo
    # --------------------------------------------------------

    m = (
        htable.rows[0]
        .cells[1]
        .paragraphs[0]
    )

    m.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )

    try:

        img_url = (
            "https://uoturath.edu.iq/"
            "wp-content/uploads/2025/03/"
            "shield-1.png"
        )

        response = requests.get(
            img_url,
            timeout=10
        )

        img_data = BytesIO(
            response.content
        )

        m.add_run().add_picture(
            img_data,
            width=Inches(0.8)
        )

    except Exception:

        pass

    # --------------------------------------------------------
    # English
    # --------------------------------------------------------

    l = (
        htable.rows[0]
        .cells[2]
        .paragraphs[0]
    )

    l.text = (
        "University Of Alturath\n"
        "Dept. Of Admin & Financial Affairs\n"
        "HR Department"
    )

    l.alignment = (
        WD_ALIGN_PARAGRAPH.LEFT
    )

    # --------------------------------------------------------
    # Separator
    # --------------------------------------------------------

    p_line = doc.add_paragraph()

    run_line = p_line.add_run(
        "______________________________________________________________________"
    )

    run_line.font.color.rgb = RGBColor(
        0x8F,
        0x0B,
        0x0B
    )

    p_line.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )

    # --------------------------------------------------------
    # Body
    # --------------------------------------------------------

    body = doc.add_paragraph(
        "\nنرفق لسيادتكم في ادناه الكشف الخاص بموقف "
        "الحضور والغياب لكادر العمل الخاص بجامعة التراث "
        "وحسب كشف البصمة المرفق طيا نسخة منه ... "
        "راجين التفضل بالاطلاع واعلامنا توجيهات سيادتكم "
        "حول ذلك ... مع التقدير.."
    )

    body.alignment = (
        WD_ALIGN_PARAGRAPH.RIGHT
    )

    set_rtl(body)

    # --------------------------------------------------------
    # Table
    # --------------------------------------------------------

    table = doc.add_table(
        rows=1,
        cols=5
    )

    table.style = "Table Grid"

    set_table_rtl(table)

    hdr = table.rows[0].cells

    labels = [
        "ت",
        "الاسم",
        "الحالة",
        "العدد",
        "التواريخ"
    ]

    for i, txt in enumerate(
        labels
    ):

        hdr[i].text = txt

        hdr[i].paragraphs[0].alignment = (
            WD_ALIGN_PARAGRAPH.CENTER
        )

        set_rtl(
            hdr[i].paragraphs[0]
        )

    # --------------------------------------------------------
    # Data
    # --------------------------------------------------------

    for idx, row in df.iterrows():

        cells = table.add_row().cells

        cells[0].text = str(
            idx + 1
        )

        cells[1].text = str(
            row["Name"]
        )

        cells[2].text = (
            "تأخير"
            if "Late" in str(row["Status"])
            else "غياب"
        )

        cells[3].text = str(
            row["Count"]
        )

        d_para = (
            cells[4]
            .paragraphs[0]
        )

        d_run = d_para.add_run(
            row["Dates_Str"]
        )

        d_run.font.size = Pt(8)

        for cell in cells:

            cell.paragraphs[0].alignment = (
                WD_ALIGN_PARAGRAPH.CENTER
            )

            set_rtl(
                cell.paragraphs[0]
            )

    # --------------------------------------------------------
    # Signature
    # --------------------------------------------------------

    doc.add_paragraph(
        "\n\n"
    )

    sig = doc.add_paragraph(
        "م.م محمد زهير طالب النقيب\n"
        "مدير قسم الشؤون الادارية والموارد البشرية"
    )

    sig.alignment = (
        WD_ALIGN_PARAGRAPH.LEFT
    )

    set_rtl(sig)

    buf = BytesIO()

    doc.save(buf)

    buf.seek(0)

    return buf


# ============================================================
# 10. DAILY REPORT UI
# ============================================================

def run_daily_report_module():

    st.markdown(
        """
        <div class="hero">

            <div class="hero-label">
                ALTURATH UNIVERSITY • HR
            </div>

            <div class="hero-title">
                Daily Biometric Attendance
            </div>

            <div class="hero-description">
                Current-day check-in & previous-day check-out
                prepared for HR submission.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # DATE
    # ========================================================

    use_today = st.sidebar.toggle(
        "Use Today",
        value=False
    )

    target_date = (
        date.today()
        if use_today
        else st.sidebar.date_input(
            "Submission Date",
            value=date.today()
        )
    )

    weekdays_ar = {
        "Monday": "الاثنين",
        "Tuesday": "الثلاثاء",
        "Wednesday": "الاربعاء",
        "Thursday": "الخميس",
        "Friday": "الجمعة",
        "Saturday": "السبت",
        "Sunday": "الاحد"
    }

    current_weekday_ar = weekdays_ar.get(
        target_date.strftime("%A"),
        ""
    )

    previous_date = (
        target_date
        - timedelta(days=1)
    )

    # ========================================================
    # DATE BAR
    # ========================================================

    st.markdown(
        f"""
        <div class="date-bar">

            <div>
                <div class="date-main">
                    {target_date.strftime('%A, %d %B %Y')}
                </div>

                <div class="date-sub">
                    {current_weekday_ar}
                </div>
            </div>

            <div class="checkout-badge">
                Check-Out is from
                {previous_date.strftime('%d %b %Y')}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # SIDEBAR
    # ========================================================

    st.sidebar.markdown(
        """
        <div class="brand">

            <div class="brand-mark">
                ◈
            </div>

            <div class="brand-name">
                ALTURATH HR
            </div>

            <div class="brand-sub">
                BIOMETRIC ATTENDANCE • V2
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        "### Attendance Sources"
    )

    f_zaqura = st.sidebar.file_uploader(
        "Zaqura Gate",
        type=["xlsx", "xls"],
        key="zaqura"
    )

    f_mhmd = st.sidebar.file_uploader(
        "Mhmd Bn Ali Gate",
        type=["xlsx", "xls"],
        key="mhmd"
    )

    f_app = st.sidebar.file_uploader(
        "Mawjood App",
        type=["xlsx", "xls"],
        key="maw"
    )

    st.sidebar.markdown(
        "### HR Data"
    )

    f_weekly = st.sidebar.file_uploader(
        "Weekly Day-Off List",
        type=["xlsx", "xls"],
        key="weekly"
    )

    # ========================================================
    # PROCESS
    # ========================================================

    all_logs = []

    if f_zaqura:

        data = process_gate(
            f_zaqura,
            "Zaqura Gate"
        )

        if not data.empty:

            all_logs.append(data)

    if f_mhmd:

        data = process_gate(
            f_mhmd,
            "Mhmd Bn Ali Gate"
        )

        if not data.empty:

            all_logs.append(data)

    if f_app:

        data = process_app(
            f_app
        )

        if not data.empty:

            all_logs.append(data)

    # ========================================================
    # WEEKLY OFF
    # ========================================================

    df_off = pd.DataFrame(
        columns=[
            "Name",
            "OffDay"
        ]
    )

    if f_weekly:

        try:

            df_off = pd.read_excel(
                f_weekly
            )

            df_off = df_off.rename(
                columns={
                    "الاسم الثلاثي": "Name",
                    "الاجازة الاسبوعية": "OffDay"
                }
            )

            if "Name" in df_off.columns:

                df_off["Name"] = (
                    df_off["Name"]
                    .astype(str)
                    .str.strip()
                )

            if "OffDay" in df_off.columns:

                df_off["OffDay"] = (
                    df_off["OffDay"]
                    .astype(str)
                    .str.strip()
                )

        except Exception as e:

            st.warning(
                f"Weekly file error: {e}"
            )

    # ========================================================
    # BUILD
    # ========================================================

    if all_logs or f_weekly:

        if all_logs:

            df_logs = pd.concat(
                all_logs,
                ignore_index=True
            )

        else:

            df_logs = pd.DataFrame(
                columns=[
                    "Name",
                    "dt",
                    "Date",
                    "Time",
                    "Event_Type",
                    "Source"
                ]
            )

        df_final = build_daily_attendance(
            df_logs,
            target_date,
            current_weekday_ar,
            df_off
        )

        if df_final.empty:

            st.info(
                "No employees found."
            )

            return

        df_final = (
            df_final
            .sort_values("Name")
            .reset_index(drop=True)
        )

        # ====================================================
        # METRICS
        # ====================================================

        total = len(df_final)

        on_time = len(
            df_final[
                df_final["Status"]
                .str.contains(
                    "On Time",
                    na=False
                )
            ]
        )

        late = len(
            df_final[
                df_final["Status"]
                .str.contains(
                    "Late",
                    na=False
                )
            ]
        )

        absent = len(
            df_final[
                df_final["Status"]
                .str.contains(
                    "Absence",
                    na=False
                )
            ]
        )

        checkout_count = len(
            df_final[
                df_final["Check-Out"] != "-"
            ]
        )

        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:

            st.metric(
                "Employees",
                total
            )

        with c2:

            st.metric(
                "On Time",
                on_time
            )

        with c3:

            st.metric(
                "Late",
                late
            )

        with c4:

            st.metric(
                "Absence",
                absent
            )

        with c5:

            st.metric(
                "Previous Check-Outs",
                checkout_count
            )

        # ====================================================
        # REPORT EXPLANATION
        # ====================================================

        st.markdown(
            f"""
            <div class="status-note">

                <b>HR submission logic:</b>

                Check-In is taken from
                <b>{target_date.strftime('%d %b %Y')}</b>.

                &nbsp; • &nbsp;

                Check-Out is taken from
                <b>{previous_date.strftime('%d %b %Y')}</b>.

                &nbsp; • &nbsp;

                This means today's HR sheet can be submitted
                while still carrying yesterday's completed
                checkout.

            </div>
            """,
            unsafe_allow_html=True
        )

        # ====================================================
        # TABLE
        # ====================================================

        st.markdown(
            '<div class="section-title">Attendance Register</div>',
            unsafe_allow_html=True
        )

        display_df = df_final.copy()

        display_df.insert(
            0,
            "No.",
            range(
                1,
                len(display_df) + 1
            )
        )

        display_df = display_df.rename(
            columns={
                "Name": "Name",
                "Check-In":
                    f"Check-In ({target_date.strftime('%d %b')})",
                "Check-Out":
                    f"Check-Out ({previous_date.strftime('%d %b')})",
                "Source": "Source",
                "Status": "Status"
            }
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        # ====================================================
        # EXPORT
        # ====================================================

        st.markdown(
            '<div class="section-title">HR Export</div>',
            unsafe_allow_html=True
        )

        excel_file = create_daily_excel(
            df_final,
            target_date
        )

        st.download_button(
            label="Download HR Excel",
            data=excel_file,
            file_name=(
                f"HR_Attendance_"
                f"{target_date.strftime('%Y-%m-%d')}.xlsx"
            ),
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )

        st.caption(
            "Compact LTR Excel • "
            "Check-In = selected date • "
            "Check-Out = previous date"
        )

    else:

        st.markdown(
            """
            <div class="status-note">

                <b>Ready.</b>

                Upload a gate export to begin.
                The system will automatically separate
                Check-In and Check-Out according to the
                biometric event and date rules.

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# 11. MULTI-DAY AUDIT
# ============================================================

def run_exceptions_module():

    st.markdown(
        """
        <div class="hero">

            <div class="hero-label">
                ALTURATH UNIVERSITY • HR
            </div>

            <div class="hero-title">
                Multi-Day Exceptions
            </div>

            <div class="hero-description">
                Review late arrivals and absences across
                multiple biometric exports.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_files = st.file_uploader(
        "Upload Exported Excel Files",
        accept_multiple_files=True,
        type=["xlsx", "xls"]
    )

    if not uploaded_files:

        st.markdown(
            """
            <div class="status-note">

                Upload your daily HR Excel files.
                The system will combine them into a
                multi-day exceptions report.

            </div>
            """,
            unsafe_allow_html=True
        )

        return

    all_data = []

    for f in uploaded_files:

        file_date = extract_date_from_filename(
            f.name
        )

        try:

            engine = (
                "xlrd"
                if f.name.lower().endswith(".xls")
                else "openpyxl"
            )

            df = pd.read_excel(
                f,
                engine=engine,
                header=2
            )

            df.columns = [
                str(c).strip()
                for c in df.columns
            ]

            # Compatibility with old files
            if (
                "Status" in df.columns
                and
                "Name" in df.columns
            ):

                mask = df["Status"].astype(str).str.contains(
                    "Late|Absence",
                    case=False,
                    na=False
                )

                day_data = df[
                    mask
                ].copy()

                day_data["Report_Date"] = (
                    file_date
                )

                all_data.append(
                    day_data[
                        [
                            "Name",
                            "Status",
                            "Report_Date"
                        ]
                    ]
                )

        except Exception as e:

            st.warning(
                f"Could not process {f.name}: {e}"
            )

    if not all_data:

        st.info(
            "No Late or Absence records found."
        )

        return

    combined = pd.concat(
        all_data,
        ignore_index=True
    )

    summary = (
        combined
        .groupby(
            [
                "Name",
                "Status"
            ]
        )["Report_Date"]
        .unique()
        .reset_index()
    )

    summary["Count"] = (
        summary["Report_Date"]
        .apply(len)
    )

    summary["Dates_Str"] = (
        summary["Report_Date"]
        .apply(
            lambda x:
            ", ".join(
                sorted(x)
            )
        )
    )

    st.dataframe(
        summary[
            [
                "Name",
                "Status",
                "Count",
                "Dates_Str"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    if st.button(
        "Generate Official Word Report"
    ):

        report_file = create_word_doc(
            summary
        )

        st.download_button(
            "Download Word Report",
            report_file,
            "Alturath_Exceptions_Report.docx"
        )


# ============================================================
# 12. SIDEBAR NAVIGATION
# ============================================================

app_mode = st.sidebar.selectbox(
    "System Module",
    [
        "Daily Report Tool",
        "Multi-Day Audit Tool"
    ]
)


# ============================================================
# 13. RUN APPLICATION
# ============================================================

if app_mode == "Daily Report Tool":

    run_daily_report_module()

else:

    run_exceptions_module()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        ALTURATH HR BIOMETRICS SYSTEM • V2
    </div>
    """,
    unsafe_allow_html=True
)
