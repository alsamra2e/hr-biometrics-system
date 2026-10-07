import streamlit as st
import pandas as pd
import re
import os

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
# 2. CONSTANTS / LOCAL BRANDING
# ============================================================

UNIVERSITY_NAME = "University Of Alturath"

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

LOGO_PATH = os.path.join(
    BASE_DIR,
    "logo(1).png"
)

# ============================================================
# 3. FUTURISTIC MINIMAL THEME
# ============================================================

def apply_v2_theme():

    st.markdown(
        """
        <style>

        @import url(
            'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
        );

        /* ====================================================
           GLOBAL
        ==================================================== */

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: #f4f7fb;
            color: #0f172a;
        }

        .main .block-container {
            max-width: 1500px;
            padding-top: 1.8rem;
            padding-bottom: 2rem;
        }

        /* ====================================================
           SIDEBAR
        ==================================================== */

        section[data-testid="stSidebar"] {
            background: #07111f;
            border-right: 1px solid #172338;
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1.2rem;
        }

        section[data-testid="stSidebar"] * {
            color: #dbe7f5;
        }

        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stFileUploader label,
        section[data-testid="stSidebar"] .stDateInput label {
            color: #8ea3bd !important;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: .2px;
        }

        section[data-testid="stSidebar"] .stToggle label {
            color: #dbe7f5 !important;
            font-size: 12px;
            font-weight: 600;
        }

        /* ====================================================
           BRAND
        ==================================================== */

        .brand {
            padding: 4px 5px 28px 5px;
        }

        .brand-logo {
            width: 62px;
            height: 62px;
            object-fit: contain;
            background: #ffffff;
            border-radius: 15px;
            padding: 6px;
            margin-bottom: 13px;

            box-shadow:
                0 8px 24px rgba(0,0,0,.25);
        }

        .brand-name {
            color: #f8fafc;
            font-size: 19px;
            font-weight: 800;
            letter-spacing: -.5px;
        }

        .brand-sub {
            color: #6f86a1;
            font-size: 9px;
            margin-top: 5px;
            letter-spacing: 1.1px;
            font-weight: 600;
        }

        /* ====================================================
           SIDEBAR HEADINGS
        ==================================================== */

        section[data-testid="stSidebar"] h3 {
            color: #e8f0fa;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: .4px;
            margin-top: 22px;
            margin-bottom: 9px;
        }

        /* ====================================================
           HERO
        ==================================================== */

        .hero {
            position: relative;
            overflow: hidden;

            background:
                linear-gradient(
                    135deg,
                    #081525 0%,
                    #0d1c31 100%
                );

            border: 1px solid #1b2d46;
            border-radius: 18px;

            padding: 26px 29px;
            margin-bottom: 18px;

            box-shadow:
                0 12px 30px rgba(15,23,42,.08);
        }

        .hero:before {
            content: "";

            position: absolute;
            right: 28px;
            top: 25px;

            width: 7px;
            height: 7px;

            border-radius: 50%;

            background: #38bdf8;

            box-shadow:
                0 0 0 6px rgba(56,189,248,.08),
                0 0 24px rgba(56,189,248,.35);
        }

        .hero-label {
            color: #38bdf8;
            font-size: 9px;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 7px;
        }

        .hero-title {
            color: #f8fafc;
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -.8px;
            margin: 0;
        }

        .hero-description {
            color: #91a4bb;
            font-size: 12px;
            margin-top: 7px;
            max-width: 760px;
            line-height: 1.6;
        }

        /* ====================================================
           DATE BAR
        ==================================================== */

        .date-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;

            background: #ffffff;

            border: 1px solid #dce5ef;
            border-radius: 13px;

            padding: 12px 16px;

            margin-bottom: 17px;

            box-shadow:
                0 4px 16px rgba(15,23,42,.035);
        }

        .date-main {
            color: #0f172a;
            font-size: 13px;
            font-weight: 800;
        }

        .date-sub {
            color: #718198;
            font-size: 10px;
            margin-top: 3px;
        }

        .checkout-badge {
            background: #f0f7ff;
            color: #1769c2;

            border: 1px solid #d7eaff;

            padding: 6px 11px;
            border-radius: 999px;

            font-size: 10px;
            font-weight: 700;
        }

        /* ====================================================
           METRICS
        ==================================================== */

        div[data-testid="stMetric"] {
            background: #ffffff;

            border: 1px solid #dce5ef;
            border-radius: 13px;

            padding: 12px 14px;

            box-shadow:
                0 4px 16px rgba(15,23,42,.035);
        }

        div[data-testid="stMetricLabel"] {
            color: #718198;
            font-size: 10px;
            font-weight: 600;
        }

        div[data-testid="stMetricValue"] {
            color: #0f172a;
            font-size: 22px;
            font-weight: 800;
        }

        /* ====================================================
           BUTTONS
        ==================================================== */

        .stButton > button,
        .stDownloadButton > button {

            border-radius: 9px;

            border: 1px solid #1769e0;

            background: #1769e0;

            color: white;

            font-weight: 700;

            min-height: 40px;

            box-shadow:
                0 4px 12px rgba(23,105,224,.12);

            transition:
                background .15s ease,
                box-shadow .15s ease,
                transform .15s ease;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {

            background: #1258bd;

            border-color: #1258bd;

            transform: translateY(-1px);

            box-shadow:
                0 7px 18px rgba(23,105,224,.18);
        }

        /* ====================================================
           FILE UPLOADER
        ==================================================== */

        section[data-testid="stSidebar"]
        [data-testid="stFileUploader"] {

            background: #0c1829;

            border: 1px solid #1d3049;

            border-radius: 10px;

            padding: 5px;

            margin-bottom: 7px;
        }

        section[data-testid="stSidebar"]
        [data-testid="stFileUploaderDropzone"] {

            background: #0b1727;

            border: 1px dashed #29415e;

            border-radius: 8px;
        }

        section[data-testid="stSidebar"]
        [data-testid="stFileUploaderDropzoneInstructions"] {

            color: #91a4bb;
        }

        /* ====================================================
           INPUTS
        ==================================================== */

        .stSelectbox > div > div,
        .stDateInput > div > div {

            border-radius: 9px !important;
        }

        /* ====================================================
           DATAFRAME
        ==================================================== */

        div[data-testid="stDataFrame"] {

            border: 1px solid #dce5ef;

            border-radius: 13px;

            overflow: hidden;

            box-shadow:
                0 5px 20px rgba(15,23,42,.045);
        }

        /* ====================================================
           SECTION TITLE
        ==================================================== */

        .section-title {

            display: flex;

            align-items: center;

            color: #0f172a;

            font-size: 14px;

            font-weight: 800;

            margin-top: 23px;

            margin-bottom: 9px;

            letter-spacing: -.2px;
        }

        .section-title:before {

            content: "";

            display: inline-block;

            width: 3px;

            height: 16px;

            background: #1769e0;

            border-radius: 4px;

            margin-right: 8px;
        }

        /* ====================================================
           STATUS NOTE
        ==================================================== */

        .status-note {

            border-radius: 11px;

            padding: 11px 14px;

            background: #ffffff;

            border: 1px solid #dce5ef;

            color: #53657b;

            font-size: 11px;

            line-height: 1.65;

            margin-top: 14px;

            box-shadow:
                0 3px 12px rgba(15,23,42,.025);
        }

        .status-note b {
            color: #172a42;
        }

        /* ====================================================
           ALERTS
        ==================================================== */

        div[data-testid="stAlert"] {
            border-radius: 10px;
        }

        /* ====================================================
           FOOTER
        ==================================================== */

        .footer {

            color: #91a0b3;

            text-align: center;

            font-size: 9px;

            padding: 28px 0 8px 0;

            letter-spacing: .5px;
        }

        /* ====================================================
           MOBILE
        ==================================================== */

        @media (max-width: 768px) {

            .main .block-container {
                padding: 1rem;
            }

            .hero {
                padding: 21px;
            }

            .hero-title {
                font-size: 23px;
            }

            .date-bar {
                gap: 10px;
                align-items: flex-start;
                flex-direction: column;
            }

        }

        </style>
        """,
        unsafe_allow_html=True
    )

apply_v2_theme()

# ============================================================
# 4. LOGO HELPERS
# ============================================================

@st.cache_data(show_spinner=False)
def get_logo_bytes():

    try:

        if not os.path.exists(LOGO_PATH):
            return None

        with open(
            LOGO_PATH,
            "rb"
        ) as file:

            return file.read()

    except Exception:

        return None

def show_sidebar_brand():

    logo = get_logo_bytes()

    if logo:

        import base64

        encoded = base64.b64encode(
            logo
        ).decode("utf-8")

        st.sidebar.markdown(
            f"""
            <div class="brand">

                <img
                    class="brand-logo"
                    src="data:image/png;base64,{encoded}"
                />

                <div class="brand-name">
                    ALTURATH HR
                </div>

                <div class="brand-sub">
                    HUMAN RESOURCES • BIOMETRIC SYSTEM V2
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    else:

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
                    HUMAN RESOURCES • BIOMETRIC SYSTEM V2
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

# ============================================================
# 5. RTL UTILITIES FOR WORD ONLY
# ============================================================

def set_rtl(paragraph):

    p = paragraph._element

    pPr = p.get_or_add_pPr()

    bidi = pPr.find(
        qn("w:bidi")
    )

    if bidi is None:

        bidi = OxmlElement("w:bidi")

        pPr.append(bidi)

def set_table_rtl(table):

    tbl_pr = table._element.xpath(
        "w:tblPr"
    )

    if tbl_pr:

        bidi = OxmlElement(
            "w:bidiVisual"
        )

        tbl_pr[0].append(bidi)

# ============================================================
# 6. FILE DATE
# ============================================================

def extract_date_from_filename(
    filename
):

    match = re.search(
        r"\d{4}-\d{2}-\d{2}",
        filename
    )

    if match:

        return match.group(0)

    return str(date.today())

# ============================================================
# 7. BIOMETRIC EVENT CLASSIFICATION
# ============================================================

def classify_gate_event(
    event_value,
    punch_datetime
):

    """
    Biometric logic:

    دخول(1)
        -> Check-In

    خروج(2) before 12:00
        -> Check-In

    خروج(2) at/after 12:00
        -> Check-Out
    """

    event = str(
        event_value
    ).strip()

    punch_time = (
        punch_datetime.time()
    )

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
# 8. PROCESS GATE FILE
# ============================================================

def process_gate(
    file,
    gate_name
):

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
        # NAME
        # ----------------------------------------------------

        if "الاسم" in df.columns:

            name_col = "الاسم"

        elif "الإسم" in df.columns:

            name_col = "الإسم"

        else:

            st.warning(
                f"{gate_name}: "
                "الاسم column was not found."
            )

            return pd.DataFrame()

        # ----------------------------------------------------
        # TIME
        # ----------------------------------------------------

        if "الوقت" not in df.columns:

            st.warning(
                f"{gate_name}: "
                "الوقت column was not found."
            )

            return pd.DataFrame()

        # ----------------------------------------------------
        # EVENT
        # ----------------------------------------------------

        if "Event" not in df.columns:

            st.warning(
                f"{gate_name}: "
                "Event column was not found."
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
        ].copy()

        df = df[
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
            df["dt"].dt.strftime(
                "%H:%M"
            )
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
            f"Error processing "
            f"{gate_name}: {e}"
        )

        return pd.DataFrame()

# ============================================================
# 9. PROCESS MAWJOOD APP
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
        # APP CHECK-IN
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
                            "Time": dt.strftime(
                                "%H:%M"
                            ),
                            "Event_Type": "Check-In",
                            "Source": "Mawjood App"
                        }
                    )

        # ----------------------------------------------------
        # APP CHECK-OUT
        # ----------------------------------------------------

        possible_checkout = [
            "خروج",
            "الانصراف",
            "وقت الخروج",
            "Check-Out",
            "Checkout"
        ]

        checkout_col = None

        for col in possible_checkout:

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
                            "Time": dt.strftime(
                                "%H:%M"
                            ),
                            "Event_Type": "Check-Out",
                            "Source": "Mawjood App"
                        }
                    )

        return pd.DataFrame(
            result
        )

    except Exception as e:

        st.error(
            f"Error processing "
            f"Mawjood App: {e}"
        )

        return pd.DataFrame()

# ============================================================
# 10. BUILD DAILY REPORT
# ============================================================

def build_daily_attendance(
    df_logs,
    target_date,
    current_weekday_ar,
    df_off
):

    """
    HR SUBMISSION RULE

    Selected date = 7 Oct

    Check-In = 7 Oct
    Check-Out = 6 Oct
    """

    master_names = set()

    # --------------------------------------------------------
    # Names from biometric logs
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
    # Names from weekly off list
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
        -
        timedelta(days=1)
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
        # TODAY CHECK-IN
        # ====================================================

        today_checkins = person[
            (person["Date"] == target_date)
            &
            (
                person["Event_Type"]
                == "Check-In"
            )
        ].copy()

        # ====================================================
        # YESTERDAY CHECK-OUT
        # ====================================================

        yesterday_checkouts = person[
            (person["Date"] == previous_date)
            &
            (
                person["Event_Type"]
                == "Check-Out"
            )
        ].copy()

        # ====================================================
        # FIRST CHECK-IN
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
        # LAST CHECK-OUT
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
                    off_info["OffDay"]
                    .iloc[0]
                ).strip()
                ==
                str(
                    current_weekday_ar
                ).strip()
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
        # SOURCES
        # ====================================================

        source_parts = []

        if check_in_source != "-":

            source_parts.append(
                check_in_source
            )

        if (
            check_out_source != "-"
            and
            check_out_source
            not in source_parts
        ):

            source_parts.append(
                check_out_source
            )

        source = (
            " + ".join(source_parts)
            if source_parts
            else "-"
        )

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
# 11. EXCEL EXPORT
# ============================================================

def create_daily_excel(
    df_final,
    target_date
):

    """
    Compact, modern, Arabic-first Excel.

    IMPORTANT:
    - Workbook remains LTR.
    - No RTL Excel setting.
    - No worksheet.right_to_left().
    - No set_print_area().
    - No large images.
    """

    buffer = BytesIO()

    previous_date = (
        target_date
        -
        timedelta(days=1)
    )

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
        buffer,
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
        # FORMATS
        # ----------------------------------------------------

        title_format = workbook.add_format(
            {
                "bold": True,
                "font_size": 15,
                "font_color": "#FFFFFF",
                "bg_color": "#0B1727",
                "align": "center",
                "valign": "vcenter"
            }
        )

        arabic_title_format = workbook.add_format(
            {
                "bold": True,
                "font_size": 13,
                "font_color": "#FFFFFF",
                "bg_color": "#0B1727",
                "align": "center",
                "valign": "vcenter"
            }
        )

        english_small_format = workbook.add_format(
            {
                "font_size": 8,
                "font_color": "#8FA4BD",
                "bg_color": "#0B1727",
                "align": "center",
                "valign": "vcenter"
            }
        )

        date_format = workbook.add_format(
            {
                "font_size": 9,
                "font_color": "#334155",
                "bg_color": "#F1F5F9",
                "align": "center",
                "valign": "vcenter"
            }
        )

        header_format = workbook.add_format(
            {
                "bold": True,
                "font_color": "#FFFFFF",
                "bg_color": "#1769E0",
                "align": "center",
                "valign": "vcenter",
                "border": 1,
                "border_color": "#CBD5E1",
                "text_wrap": True
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
        # ARABIC / ENGLISH TITLE
        # ----------------------------------------------------

        worksheet.merge_range(
            "A1:F1",
            "جامعة التراث",
            title_format
        )

        worksheet.merge_range(
            "A2:F2",
            "كشف الحضور والانصراف اليومي",
            arabic_title_format
        )

        worksheet.merge_range(
            "A3:F3",
            "University Of Alturath • Daily Attendance",
            english_small_format
        )

        worksheet.merge_range(
            "A4:F4",
            (
                f"تاريخ الحضور: "
                f"{target_date.strftime('%d %b %Y')}"
                f"    |    "
                f"تاريخ الانصراف: "
                f"{previous_date.strftime('%d %b %Y')}"
            ),
            date_format
        )

        worksheet.merge_range(
            "A5:F5",
            (
                f"Check-In: "
                f"{target_date.strftime('%d %b %Y')}"
                f"    •    "
                f"Check-Out: "
                f"{previous_date.strftime('%d %b %Y')}"
            ),
            english_small_format
        )

        worksheet.set_row(
            0,
            24
        )

        worksheet.set_row(
            1,
            22
        )

        worksheet.set_row(
            2,
            17
        )

        worksheet.set_row(
            3,
            20
        )

        worksheet.set_row(
            4,
            17
        )

        # ----------------------------------------------------
        # HEADERS
        # ----------------------------------------------------

        headers = [
            "ت",
            "الاسم\nName",
            (
                "الحضور\n"
                "Check-In\n"
                f"({target_date.strftime('%d %b')})"
            ),
            (
                "الانصراف\n"
                "Check-Out\n"
                f"({previous_date.strftime('%d %b')})"
            ),
            "المصدر\nSource",
            "الحالة\nStatus"
        ]

        for col, header in enumerate(
            headers
        ):

            worksheet.write(
                5,
                col,
                header,
                header_format
            )

        worksheet.set_row(
            5,
            34
        )

        # ----------------------------------------------------
        # DATA
        # ----------------------------------------------------

        for i, (_, row) in enumerate(
            export_df.iterrows()
        ):

            excel_row = i + 6

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
        # COLUMN WIDTHS
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
            16
        )

        worksheet.set_column(
            "E:E",
            22
        )

        worksheet.set_column(
            "F:F",
            18
        )

        # ----------------------------------------------------
        # LIGHTWEIGHT SETTINGS
        # ----------------------------------------------------

        worksheet.freeze_panes(
            6,
            0
        )

        worksheet.hide_gridlines(
            2
        )

    buffer.seek(0)

    return buffer.getvalue()

# ============================================================
# 12. WORD REPORT
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
    # ARABIC HEADER
    # --------------------------------------------------------

    arabic = (
        htable.rows[0]
        .cells[0]
        .paragraphs[0]
    )

    arabic.text = (
        "جامعة التراث\n"
        "قسم الشؤون الإدارية والمالية\n"
        "شعبة الموارد البشرية"
    )

    arabic.alignment = (
        WD_ALIGN_PARAGRAPH.RIGHT
    )

    set_rtl(arabic)

    # --------------------------------------------------------
    # LOGO
    # --------------------------------------------------------

    logo_cell = (
        htable.rows[0]
        .cells[1]
        .paragraphs[0]
    )

    logo_cell.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )

    logo_bytes = get_logo_bytes()

    if logo_bytes:

        try:

            logo_stream = BytesIO(
                logo_bytes
            )

            logo_cell.add_run().add_picture(
                logo_stream,
                width=Inches(0.85)
            )

        except Exception:

            logo_cell.add_run(
                "ALTURATH"
            )

    else:

        logo_cell.add_run(
            "ALTURATH"
        )

    # --------------------------------------------------------
    # ENGLISH HEADER
    # --------------------------------------------------------

    english = (
        htable.rows[0]
        .cells[2]
        .paragraphs[0]
    )

    english.text = (
        "University Of Alturath\n"
        "Dept. Of Admin & Financial Affairs\n"
        "HR Department"
    )

    english.alignment = (
        WD_ALIGN_PARAGRAPH.LEFT
    )

    # --------------------------------------------------------
    # SEPARATOR
    # --------------------------------------------------------

    p_line = doc.add_paragraph()

    line = p_line.add_run(
        "______________________________________________________________________"
    )

    line.font.color.rgb = RGBColor(
        0x8F,
        0x0B,
        0x0B
    )

    p_line.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )

    # --------------------------------------------------------
    # BODY
    # --------------------------------------------------------

    body = doc.add_paragraph(
        "\nنرفق لسيادتكم في ادناه الكشف الخاص "
        "بموقف الحضور والغياب لكادر العمل الخاص "
        "بجامعة التراث وحسب كشف البصمة المرفق "
        "طيا نسخة منه ... راجين التفضل بالاطلاع "
        "واعلامنا توجيهات سيادتكم حول ذلك ... "
        "مع التقدير.."
    )

    body.alignment = (
        WD_ALIGN_PARAGRAPH.RIGHT
    )

    set_rtl(body)

    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    table = doc.add_table(
        rows=1,
        cols=5
    )

    table.style = "Table Grid"

    set_table_rtl(table)

    headers = [
        "ت",
        "الاسم",
        "الحالة",
        "العدد",
        "التواريخ"
    ]

    for i, text_value in enumerate(
        headers
    ):

        cell = table.rows[0].cells[i]

        cell.text = text_value

        paragraph = (
            cell.paragraphs[0]
        )

        paragraph.alignment = (
            WD_ALIGN_PARAGRAPH.CENTER
        )

        set_rtl(paragraph)

    # --------------------------------------------------------
    # ROWS
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
            if "Late"
            in str(row["Status"])
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
            str(row["Dates_Str"])
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
    # SIGNATURE
    # --------------------------------------------------------

    doc.add_paragraph(
        "\n\n"
    )

    signature = doc.add_paragraph(
        "م.م محمد زهير طالب النقيب\n"
        "مدير قسم الشؤون الادارية والموارد البشرية"
    )

    signature.alignment = (
        WD_ALIGN_PARAGRAPH.LEFT
    )

    set_rtl(signature)

    buffer = BytesIO()

    doc.save(buffer)

    buffer.seek(0)

    return buffer

# ============================================================
# 13. DAILY REPORT MODULE
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
                Current-day check-in and previous-day
                check-out prepared for HR submission.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # SIDEBAR BRAND
    # ========================================================

    show_sidebar_brand()

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
        -
        timedelta(days=1)
    )

    # ========================================================
    # DATE DISPLAY
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
                Check-Out:
                {previous_date.strftime('%d %b %Y')}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # FILE UPLOADERS
    # ========================================================

    st.sidebar.markdown(
        "### Attendance Sources"
    )

    f_zaqura = st.sidebar.file_uploader(
        "Zaqura Gate",
        type=[
            "xlsx",
            "xls"
        ],
        key="zaqura"
    )

    f_mhmd = st.sidebar.file_uploader(
        "Mhmd Bn Ali Gate",
        type=[
            "xlsx",
            "xls"
        ],
        key="mhmd"
    )

    f_app = st.sidebar.file_uploader(
        "Mawjood App",
        type=[
            "xlsx",
            "xls"
        ],
        key="maw"
    )

    st.sidebar.markdown(
        "### HR Data"
    )

    f_weekly = st.sidebar.file_uploader(
        "Weekly Day-Off List",
        type=[
            "xlsx",
            "xls"
        ],
        key="weekly"
    )

    # ========================================================
    # PROCESS GATES
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

    # ========================================================
    # PROCESS APP
    # ========================================================

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
    # BUILD REPORT
    # ========================================================

    if not all_logs and not f_weekly:

        st.markdown(
            """
            <div class="status-note">

                <b>Ready.</b><br><br>

                Upload your biometric gate exports
                from the sidebar to generate the
                HR attendance report.

            </div>
            """,
            unsafe_allow_html=True
        )

        return

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

    # ========================================================
    # FINAL DATA
    # ========================================================

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

    # ========================================================
    # METRICS
    # ========================================================

    total = len(
        df_final
    )

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
            "Check-Outs",
            checkout_count
        )

    # ========================================================
    # HR LOGIC NOTE
    # ========================================================

    st.markdown(
        f"""
        <div class="status-note">

            <b>HR submission:</b>

            Check-In is taken from
            <b>{target_date.strftime('%d %b %Y')}</b>.

            &nbsp; • &nbsp;

            Check-Out is taken from
            <b>{previous_date.strftime('%d %b %Y')}</b>.

            &nbsp; • &nbsp;

            <b>دخول(1)</b> = Check-In

            &nbsp; • &nbsp;

            <b>خروج(2)</b> before 12:00 =
            Check-In

            &nbsp; • &nbsp;

            <b>خروج(2)</b> at/after 12:00 =
            Check-Out

        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # ATTENDANCE TABLE
    # ========================================================

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
            "Check-In":
                f"Check-In ({target_date.strftime('%d %b')})",

            "Check-Out":
                f"Check-Out ({previous_date.strftime('%d %b')})"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # EXPORT
    # ========================================================

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
            "HR_Attendance_"
            f"{target_date.strftime('%Y-%m-%d')}"
            ".xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    st.caption(
        "Compact LTR Excel • "
        f"Check-In = {target_date.strftime('%d %b %Y')} • "
        f"Check-Out = {previous_date.strftime('%d %b %Y')}"
    )

# ============================================================
# 14. MULTI-DAY EXCEPTIONS MODULE
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

    show_sidebar_brand()

    uploaded_files = st.file_uploader(
        "Upload Exported Excel Files",
        accept_multiple_files=True,
        type=[
            "xlsx",
            "xls"
        ]
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

    for file in uploaded_files:

        file_date = extract_date_from_filename(
            file.name
        )

        try:

            engine = (
                "xlrd"
                if file.name.lower().endswith(".xls")
                else "openpyxl"
            )

            # V2 Excel structure:
            # row 1 = Arabic university title
            # row 2 = Arabic report title
            # row 3 = English title
            # row 4 = Arabic dates
            # row 5 = English dates
            # row 6 = table headers
            df = pd.read_excel(
                file,
                engine=engine,
                header=5
            )

            df.columns = [
                str(c).strip()
                for c in df.columns
            ]

            if (
                "الحالة\nStatus" in df.columns
                and
                "الاسم\nName" in df.columns
            ):

                status_col = "الحالة\nStatus"
                name_col = "الاسم\nName"

                mask = (
                    df[status_col]
                    .astype(str)
                    .str.contains(
                        "Late|Absence|تأخير|غياب",
                        case=False,
                        na=False
                    )
                )

                day_data = df[
                    mask
                ].copy()

                day_data[
                    "Report_Date"
                ] = file_date

                all_data.append(
                    day_data[
                        [
                            name_col,
                            status_col,
                            "Report_Date"
                        ]
                    ].rename(
                        columns={
                            name_col: "Name",
                            status_col: "Status"
                        }
                    )
                )

            elif (
                "Status" in df.columns
                and
                "Name" in df.columns
            ):

                mask = (
                    df["Status"]
                    .astype(str)
                    .str.contains(
                        "Late|Absence",
                        case=False,
                        na=False
                    )
                )

                day_data = df[
                    mask
                ].copy()

                day_data[
                    "Report_Date"
                ] = file_date

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
                f"Could not process "
                f"{file.name}: {e}"
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
                sorted(
                    x
                )
            )
        )
    )

    st.markdown(
        '<div class="section-title">Exceptions</div>',
        unsafe_allow_html=True
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
            label="Download Word Report",
            data=report_file,
            file_name=(
                "Alturath_Exceptions_Report.docx"
            ),
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )
        )

# ============================================================
# 15. NAVIGATION
# ============================================================

app_mode = st.sidebar.selectbox(
    "System Module",
    [
        "Daily Report Tool",
        "Multi-Day Audit Tool"
    ]
)

# ============================================================
# 16. RUN
# ============================================================

if app_mode == "Daily Report Tool":

    run_daily_report_module()

else:

    run_exceptions_module()

# ============================================================
# 17. FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        ALTURATH HR BIOMETRICS SYSTEM • V2
    </div>
    """,
    unsafe_allow_html=True
)

Also, the local logo is now used in both the **sidebar** and the **Word report**, with no dependency on the university website for the logo.
