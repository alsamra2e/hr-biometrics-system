import os
import re
from io import BytesIO
from datetime import date, time, timedelta

import pandas as pd
import streamlit as st

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


# ============================================================
# ALTURATH HR BIOMETRICS SYSTEM V2
# ============================================================
# Daily HR rule:
#
# Selected date = TODAY / CHECK-IN
# Previous date = CHECK-OUT
#
# Example:
# Report Date: 07 Oct
# Check-In:    07 Oct
# Check-Out:   06 Oct
#
# Biometric:
# دخول(1)                  -> Check-In
# خروج(2) before 12:00     -> Check-In
# خروج(2) at/after 12:00  -> Check-Out
# ============================================================


# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Alturath HR • Biometric Attendance",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. CONSTANTS
# ============================================================

UNIVERSITY_NAME = "University Of Alturath"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_LOGO = os.path.join(BASE_DIR, "logo(1).png")


# ============================================================
# 3. GLOBAL THEME
# ============================================================

def apply_theme():
    st.markdown(
        """
        <style>

        /* ====================================================
           BASE
        ==================================================== */

        @import url(
            'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
        );

        html,
        body,
        [class*="css"] {
            font-family: "Inter", sans-serif;
        }

        .stApp {
            background:
                linear-gradient(
                    180deg,
                    #f8fafc 0%,
                    #f1f5f9 100%
                );
            color: #0f172a;
        }

        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1450px;
        }

        /* ====================================================
           SIDEBAR
        ==================================================== */

        section[data-testid="stSidebar"] {
            background: #071426;
            border-right: 1px solid #172b46;
        }

        section[data-testid="stSidebar"] > div {
            background: #071426;
        }

        section[data-testid="stSidebar"] * {
            color: #e2e8f0;
        }

        section[data-testid="stSidebar"] label {
            color: #94a3b8 !important;
            font-size: 12px !important;
            font-weight: 600 !important;
        }

        section[data-testid="stSidebar"] .stSelectbox > div > div,
        section[data-testid="stSidebar"] .stDateInput > div > div {
            background: #0d1d31 !important;
            border: 1px solid #223957 !important;
            border-radius: 10px !important;
        }

        section[data-testid="stSidebar"] input {
            color: #e2e8f0 !important;
        }

        section[data-testid="stSidebar"] .stFileUploader {
            background: #0b1a2d;
            border: 1px solid #1d334f;
            border-radius: 12px;
            padding: 7px;
            margin-bottom: 10px;
        }

        section[data-testid="stSidebar"] .stFileUploader section {
            border: none !important;
            background: transparent !important;
        }

        section[data-testid="stSidebar"] .stFileUploader small {
            color: #64748b !important;
        }

        section[data-testid="stSidebar"] .stButton button {
            background: #2563eb !important;
            border: 1px solid #3b82f6 !important;
        }

        /* ====================================================
           BRAND
        ==================================================== */

        .brand-box {
            padding: 8px 4px 22px 4px;
        }

        .brand-logo-wrap {
            width: 62px;
            height: 62px;
            background: #ffffff;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 7px;
            margin-bottom: 13px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.20);
        }

        .brand-logo {
            width: 100%;
            height: 100%;
            object-fit: contain;
            border-radius: 9px;
        }

        .brand-title {
            color: #f8fafc;
            font-size: 19px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }

        .brand-subtitle {
            color: #64748b;
            font-size: 9px;
            letter-spacing: 1.5px;
            margin-top: 4px;
            text-transform: uppercase;
        }

        .sidebar-section {
            color: #60a5fa;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin: 20px 0 8px 2px;
        }

        /* ====================================================
           HERO
        ==================================================== */

        .hero-card {
            position: relative;
            overflow: hidden;
            background:
                linear-gradient(
                    135deg,
                    #08172b 0%,
                    #0c203b 60%,
                    #102b4c 100%
                );
            border: 1px solid #17304e;
            border-radius: 22px;
            padding: 30px 32px;
            margin-bottom: 18px;
            box-shadow:
                0 18px 45px rgba(15, 23, 42, 0.12);
        }

        .hero-card:before {
            content: "";
            position: absolute;
            width: 360px;
            height: 360px;
            right: -170px;
            top: -220px;
            border-radius: 50%;
            background: rgba(37, 99, 235, 0.24);
        }

        .hero-card:after {
            content: "";
            position: absolute;
            width: 170px;
            height: 170px;
            right: 60px;
            bottom: -130px;
            border-radius: 50%;
            background: rgba(14, 165, 233, 0.10);
        }

        .hero-content {
            position: relative;
            z-index: 2;
        }

        .hero-kicker {
            color: #60a5fa;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 9px;
        }

        .hero-title {
            color: #ffffff;
            font-size: 29px;
            line-height: 1.15;
            font-weight: 800;
            letter-spacing: -0.9px;
            margin: 0;
        }

        .hero-arabic {
            color: #cbd5e1;
            font-size: 13px;
            margin-top: 9px;
            direction: rtl;
            text-align: left;
        }

        .hero-description {
            color: #94a3b8;
            font-size: 12px;
            line-height: 1.6;
            margin-top: 9px;
            max-width: 750px;
        }

        /* ====================================================
           DATE CARD
        ==================================================== */

        .date-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 15px;
            padding: 15px 18px;
            margin-bottom: 17px;
            box-shadow:
                0 5px 18px rgba(15, 23, 42, 0.04);
        }

        .date-label {
            color: #64748b;
            font-size: 9px;
            font-weight: 800;
            letter-spacing: 1.4px;
            text-transform: uppercase;
        }

        .date-main {
            color: #0f172a;
            font-size: 16px;
            font-weight: 800;
            margin-top: 3px;
        }

        .date-ar {
            color: #64748b;
            font-size: 11px;
            margin-top: 2px;
        }

        .date-pill {
            background: #eff6ff;
            color: #2563eb;
            border: 1px solid #dbeafe;
            border-radius: 999px;
            padding: 8px 13px;
            font-size: 11px;
            font-weight: 700;
            text-align: center;
        }

        .date-pill-small {
            color: #64748b;
            font-size: 9px;
            margin-top: 2px;
            text-align: center;
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
                0 5px 18px rgba(15, 23, 42, 0.035);
        }

        div[data-testid="stMetricLabel"] {
            color: #64748b !important;
            font-size: 10px !important;
            font-weight: 600 !important;
        }

        div[data-testid="stMetricValue"] {
            color: #0f172a !important;
            font-weight: 800 !important;
        }

        /* ====================================================
           SECTION TITLES
        ==================================================== */

        .section-heading {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 25px;
            margin-bottom: 10px;
        }

        .section-line {
            width: 4px;
            height: 22px;
            border-radius: 5px;
            background: #2563eb;
        }

        .section-text {
            color: #0f172a;
            font-size: 15px;
            font-weight: 800;
        }

        .section-en {
            color: #94a3b8;
            font-size: 9px;
            font-weight: 600;
            margin-left: 2px;
            letter-spacing: 0.5px;
        }

        /* ====================================================
           INFO CARD
        ==================================================== */

        .info-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #2563eb;
            border-radius: 12px;
            padding: 13px 16px;
            margin-top: 14px;
            color: #475569;
            font-size: 11px;
            line-height: 1.8;
            box-shadow:
                0 4px 16px rgba(15, 23, 42, 0.03);
        }

        .info-card strong {
            color: #0f172a;
        }

        /* ====================================================
           TABLE
        ==================================================== */

        div[data-testid="stDataFrame"] {
            border: 1px solid #dbe3ed;
            border-radius: 14px;
            overflow: hidden;
            box-shadow:
                0 7px 24px rgba(15, 23, 42, 0.05);
            background: #ffffff;
        }

        /* ====================================================
           BUTTONS
        ==================================================== */

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 10px !important;
            border: 1px solid #2563eb !important;
            background: #2563eb !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            min-height: 40px !important;
            transition: 0.18s ease !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background: #1d4ed8 !important;
            border-color: #1d4ed8 !important;
            transform: translateY(-1px);
            box-shadow:
                0 8px 20px rgba(37, 99, 235, 0.18);
        }

        /* ====================================================
           FOOTER
        ==================================================== */

        .footer {
            text-align: center;
            color: #94a3b8;
            font-size: 9px;
            letter-spacing: 1px;
            padding: 28px 0 8px 0;
        }

        /* ====================================================
           FILE UPLOADER
        ==================================================== */

        [data-testid="stFileUploaderDropzone"] {
            background: #f8fafc !important;
            border: 1px dashed #cbd5e1 !important;
            border-radius: 10px !important;
        }

        /* ====================================================
           MOBILE
        ==================================================== */

        @media (max-width: 800px) {

            .hero-card {
                padding: 23px;
                border-radius: 17px;
            }

            .hero-title {
                font-size: 24px;
            }

            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


apply_theme()


# ============================================================
# 4. SAFE HTML RENDER HELPER
# ============================================================

def render_html(html):
    """
    Central HTML renderer.

    Keeping HTML in one place prevents accidental
    markdown/code-block rendering problems.
    """
    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# ============================================================
# 5. LOCAL LOGO
# ============================================================

@st.cache_data(show_spinner=False)
def get_logo_bytes():
    try:
        if os.path.exists(LOCAL_LOGO):
            with open(LOCAL_LOGO, "rb") as f:
                return f.read()

        return None

    except Exception:
        return None


def show_sidebar_brand():
    logo_bytes = get_logo_bytes()

    if logo_bytes:
        import base64

        encoded = base64.b64encode(
            logo_bytes
        ).decode("utf-8")

        render_html(
            f"""
            <div class="brand-box">

                <div class="brand-logo-wrap">
                    <img
                        class="brand-logo"
                        src="data:image/png;base64,{encoded}"
                    />
                </div>

                <div class="brand-title">
                    ALTURATH HR
                </div>

                <div class="brand-subtitle">
                    BIOMETRIC ATTENDANCE • V2
                </div>

            </div>
            """
        )

    else:
        render_html(
            """
            <div class="brand-box">

                <div
                    class="brand-logo-wrap"
                    style="
                        color:#2563eb;
                        font-size:25px;
                        font-weight:800;
                    "
                >
                    ◈
                </div>

                <div class="brand-title">
                    ALTURATH HR
                </div>

                <div class="brand-subtitle">
                    BIOMETRIC ATTENDANCE • V2
                </div>

            </div>
            """
        )


# ============================================================
# 6. WORD RTL UTILITIES
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
    tbl_pr = table._element.tblPr

    bidi = OxmlElement("w:bidiVisual")
    tbl_pr.append(bidi)


def shade_cell(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()

    shd = tc_pr.find(
        qn("w:shd")
    )

    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)

    shd.set(
        qn("w:fill"),
        fill
    )


def set_cell_text(
    cell,
    text_value,
    bold=False,
    size=9,
    color="000000",
    rtl=True,
):
    cell.text = ""

    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if rtl:
        set_rtl(paragraph)

    run = paragraph.add_run(
        str(text_value)
    )

    run.bold = bold
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(
        color
    )

    cell.vertical_alignment = (
        WD_CELL_VERTICAL_ALIGNMENT.CENTER
    )


# ============================================================
# 7. FILE DATE
# ============================================================

def extract_date_from_filename(filename):
    match = re.search(
        r"\d{4}-\d{2}-\d{2}",
        filename,
    )

    if match:
        return match.group(0)

    return str(date.today())


# ============================================================
# 8. BIOMETRIC EVENT CLASSIFICATION
# ============================================================

def classify_gate_event(
    event_value,
    punch_datetime,
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

    if "دخول" in event:
        return "Check-In"

    if "خروج" in event:

        if punch_time < time(12, 0):
            return "Check-In"

        return "Check-Out"

    return None


# ============================================================
# 9. PROCESS GATE FILE
# ============================================================

def process_gate(
    file,
    gate_name,
):
    try:

        engine = (
            "xlrd"
            if file.name.lower().endswith(".xls")
            else "openpyxl"
        )

        df = pd.read_excel(
            file,
            engine=engine,
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

        elif "Name" in df.columns:
            name_col = "Name"

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

            possible_time = [
                "Time",
                "وقت",
                "التاريخ والوقت",
                "DateTime",
            ]

            time_col = None

            for col in possible_time:
                if col in df.columns:
                    time_col = col
                    break

            if time_col is None:
                st.warning(
                    f"{gate_name}: "
                    "الوقت column was not found."
                )
                return pd.DataFrame()

        else:
            time_col = "الوقت"

        # ----------------------------------------------------
        # EVENT
        # ----------------------------------------------------

        if "Event" in df.columns:
            event_col = "Event"

        elif "event" in df.columns:
            event_col = "event"

        elif "الحدث" in df.columns:
            event_col = "الحدث"

        else:
            st.warning(
                f"{gate_name}: "
                "Event column was not found."
            )
            return pd.DataFrame()

        # ----------------------------------------------------
        # NORMALIZE
        # ----------------------------------------------------

        df["Name"] = (
            df[name_col]
            .astype(str)
            .str.strip()
        )

        df["dt"] = pd.to_datetime(
            df[time_col],
            errors="coerce",
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
                row[event_col],
                row["dt"],
            ),
            axis=1,
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

        # Gate is source/reference ONLY.
        df["Source"] = gate_name

        return df[
            [
                "Name",
                "dt",
                "Date",
                "Time",
                "Event_Type",
                "Source",
            ]
        ].sort_values("dt")

    except Exception as e:

        st.error(
            f"Error processing "
            f"{gate_name}: {e}"
        )

        return pd.DataFrame()


# ============================================================
# 10. PROCESS MAWJOOD APP
# ============================================================

def process_app(file):

    try:

        df = pd.read_excel(
            file,
            header=3,
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
                    errors="coerce",
                )

                if pd.notna(dt):

                    result.append(
                        {
                            "Name": str(
                                row["الاسم"]
                            ).strip(),

                            "dt": dt,

                            "Date": dt.date(),

                            "Time": dt.strftime(
                                "%H:%M"
                            ),

                            "Event_Type":
                                "Check-In",

                            "Source":
                                "Mawjood App",
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
            "Checkout",
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
                    errors="coerce",
                )

                if pd.notna(dt):

                    result.append(
                        {
                            "Name": str(
                                row["الاسم"]
                            ).strip(),

                            "dt": dt,

                            "Date": dt.date(),

                            "Time": dt.strftime(
                                "%H:%M"
                            ),

                            "Event_Type":
                                "Check-Out",

                            "Source":
                                "Mawjood App",
                        }
                    )

        return pd.DataFrame(result)

    except Exception as e:

        st.error(
            f"Error processing "
            f"Mawjood App: {e}"
        )

        return pd.DataFrame()


# ============================================================
# 11. BUILD DAILY REPORT
# ============================================================

def build_daily_attendance(
    df_logs,
    target_date,
    current_weekday_ar,
    df_off,
):
    """
    IMPORTANT HR RULE

    Selected date:
        Check-In

    Previous date:
        Check-Out
    """

    master_names = set()

    # --------------------------------------------------------
    # NAMES FROM BIOMETRIC LOGS
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
    # NAMES FROM WEEKLY OFF
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

    # --------------------------------------------------------
    # EACH EMPLOYEE
    # --------------------------------------------------------

    for name in sorted(master_names):

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

            check_in = str(
                first_checkin["Time"]
            )

            check_in_source = str(
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

            check_out = str(
                last_checkout["Time"]
            )

            check_out_source = str(
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
                "Status": status,
            }
        )

    return pd.DataFrame(
        final_data
    )


# ============================================================
# 12. EXCEL EXPORT
# ============================================================

def create_daily_excel(
    df_final,
    target_date,
):
    """
    Compact modern LTR Excel.

    Main headings are Arabic.
    English is kept small where useful.

    NO RTL Excel setting.
    NO set_print_area().
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
            "Status",
        ]
    ].copy()

    with pd.ExcelWriter(
        buffer,
        engine="xlsxwriter",
        engine_kwargs={
            "options": {
                "strings_to_urls": False
            }
        },
    ) as writer:

        workbook = writer.book

        worksheet = workbook.add_worksheet(
            "Attendance"
        )

        writer.sheets[
            "Attendance"
        ] = worksheet

        # ====================================================
        # FORMATS
        # ====================================================

        title_format = workbook.add_format(
            {
                "bold": True,
                "font_size": 13,
                "font_color": "#FFFFFF",
                "bg_color": "#0B1D35",
                "align": "center",
                "valign": "vcenter",
            }
        )

        subtitle_format = workbook.add_format(
            {
                "font_size": 8,
                "font_color": "#64748B",
                "bg_color": "#F8FAFC",
                "align": "center",
                "valign": "vcenter",
            }
        )

        header_format = workbook.add_format(
            {
                "bold": True,
                "font_size": 10,
                "font_color": "#FFFFFF",
                "bg_color": "#2563EB",
                "align": "center",
                "valign": "vcenter",
                "border": 1,
                "border_color": "#CBD5E1",
                "text_wrap": True,
            }
        )

        cell_format = workbook.add_format(
            {
                "font_size": 9,
                "align": "center",
                "valign": "vcenter",
                "border": 1,
                "border_color": "#E2E8F0",
            }
        )

        name_format = workbook.add_format(
            {
                "font_size": 9,
                "align": "left",
                "valign": "vcenter",
                "border": 1,
                "border_color": "#E2E8F0",
            }
        )

        # ====================================================
        # TITLE
        # ====================================================

        worksheet.merge_range(
            "A1:F1",
            "جامعة التراث — سجل الحضور اليومي",
            title_format,
        )

        worksheet.merge_range(
            "A2:F2",
            (
                f"DAILY ATTENDANCE • HR SUBMISSION    |    "
                f"Check-In: {target_date.strftime('%d %b %Y')}    |    "
                f"Check-Out: {previous_date.strftime('%d %b %Y')}"
            ),
            subtitle_format,
        )

        worksheet.set_row(
            0,
            27,
        )

        worksheet.set_row(
            1,
            20,
        )

        # ====================================================
        # HEADERS
        # ====================================================

        headers = [
            "ت\nNo.",
            "الاسم\nName",
            (
                "الحضور\n"
                f"Check-In ({target_date.strftime('%d %b')})"
            ),
            (
                "الانصراف\n"
                f"Check-Out ({previous_date.strftime('%d %b')})"
            ),
            "المصدر\nSource",
            "الحالة\nStatus",
        ]

        for col, header in enumerate(headers):

            worksheet.write(
                2,
                col,
                header,
                header_format,
            )

        worksheet.set_row(
            2,
            38,
        )

        # ====================================================
        # DATA
        # ====================================================

        for i, (_, row) in enumerate(
            export_df.iterrows()
        ):

            excel_row = i + 3

            worksheet.write(
                excel_row,
                0,
                i + 1,
                cell_format,
            )

            worksheet.write(
                excel_row,
                1,
                str(row["Name"]),
                name_format,
            )

            worksheet.write(
                excel_row,
                2,
                str(row["Check-In"]),
                cell_format,
            )

            worksheet.write(
                excel_row,
                3,
                str(row["Check-Out"]),
                cell_format,
            )

            worksheet.write(
                excel_row,
                4,
                str(row["Source"]),
                cell_format,
            )

            worksheet.write(
                excel_row,
                5,
                str(row["Status"]),
                cell_format,
            )

        # ====================================================
        # WIDTHS
        # ====================================================

        worksheet.set_column(
            "A:A",
            6,
        )

        worksheet.set_column(
            "B:B",
            31,
        )

        worksheet.set_column(
            "C:D",
            19,
        )

        worksheet.set_column(
            "E:E",
            23,
        )

        worksheet.set_column(
            "F:F",
            19,
        )

        # ====================================================
        # SETTINGS
        # ====================================================

        worksheet.freeze_panes(
            3,
            0,
        )

        worksheet.hide_gridlines(
            2,
        )

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# 13. WORD REPORT
# ============================================================

def create_word_doc(df):

    doc = Document()

    section = doc.sections[0]

    # ========================================================
    # PAGE MARGINS
    # ========================================================

    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.65)
    section.right_margin = Inches(0.65)

    # ========================================================
    # HEADER
    # ========================================================

    header = section.header

    htable = header.add_table(
        1,
        3,
        width=Inches(6.7),
    )

    htable.alignment = (
        WD_TABLE_ALIGNMENT.CENTER
    )

    # --------------------------------------------------------
    # ARABIC
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

    for run in arabic.runs:
        run.font.size = Pt(9)

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
                width=Inches(0.72),
            )

        except Exception:

            run = logo_cell.add_run(
                "ALTURATH"
            )

            run.font.size = Pt(8)

    else:

        run = logo_cell.add_run(
            "ALTURATH"
        )

        run.font.size = Pt(8)

    # --------------------------------------------------------
    # ENGLISH
    # --------------------------------------------------------

    english = (
        htable.rows[0]
        .cells[2]
        .paragraphs[0]
    )

    english.text = (
        "University Of Alturath\n"
        "Administrative & Financial Affairs\n"
        "Human Resources"
    )

    english.alignment = (
        WD_ALIGN_PARAGRAPH.LEFT
    )

    for run in english.runs:
        run.font.size = Pt(7)

    # ========================================================
    # TITLE
    # ========================================================

    title = doc.add_paragraph()

    title.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )

    run = title.add_run(
        "تقرير استثناءات الحضور والانصراف"
    )

    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(
        15,
        23,
        42,
    )

    set_rtl(title)

    subtitle = doc.add_paragraph()

    subtitle.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )

    run = subtitle.add_run(
        "HR ATTENDANCE EXCEPTIONS REPORT"
    )

    run.font.size = Pt(7)
    run.font.color.rgb = RGBColor(
        100,
        116,
        139,
    )

    # ========================================================
    # SEPARATOR
    # ========================================================

    p_line = doc.add_paragraph()

    line = p_line.add_run(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    line.font.size = Pt(8)
    line.font.color.rgb = RGBColor(
        37,
        99,
        235,
    )

    p_line.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )

    # ========================================================
    # BODY
    # ========================================================

    body = doc.add_paragraph()

    body.alignment = (
        WD_ALIGN_PARAGRAPH.RIGHT
    )

    set_rtl(body)

    body_run = body.add_run(
        "نرفق لسيادتكم أدناه الكشف الخاص "
        "بموقف الحضور والغياب لكادر العمل "
        "في جامعة التراث، وحسب سجلات البصمة "
        "المعتمدة، راجين التفضل بالاطلاع "
        "واتخاذ ما ترونه مناسباً."
    )

    body_run.font.size = Pt(10)

    # ========================================================
    # TABLE
    # ========================================================

    table = doc.add_table(
        rows=1,
        cols=5,
    )

    table.style = "Table Grid"
    table.alignment = (
        WD_TABLE_ALIGNMENT.CENTER
    )

    set_table_rtl(table)

    headers = [
        "ت",
        "الاسم",
        "الحالة",
        "العدد",
        "التواريخ",
    ]

    for i, text_value in enumerate(headers):

        cell = (
            table.rows[0]
            .cells[i]
        )

        set_cell_text(
            cell,
            text_value,
            bold=True,
            size=8,
            color="FFFFFF",
            rtl=True,
        )

        shade_cell(
            cell,
            "0F2A4A",
        )

    # ========================================================
    # ROWS
    # ========================================================

    for idx, row in df.iterrows():

        cells = (
            table.add_row()
            .cells
        )

        set_cell_text(
            cells[0],
            idx + 1,
            size=8,
        )

        set_cell_text(
            cells[1],
            row["Name"],
            size=8,
        )

        status_text = str(
            row["Status"]
        )

        if "Late" in status_text:
            arabic_status = "تأخير"
        else:
            arabic_status = "غياب"

        set_cell_text(
            cells[2],
            arabic_status,
            size=8,
        )

        set_cell_text(
            cells[3],
            row["Count"],
            size=8,
        )

        set_cell_text(
            cells[4],
            row["Dates_Str"],
            size=7,
        )

    # ========================================================
    # SIGNATURE
    # ========================================================

    doc.add_paragraph()

    signature = doc.add_paragraph()

    signature.alignment = (
        WD_ALIGN_PARAGRAPH.LEFT
    )

    set_rtl(signature)

    run = signature.add_run(
        "م.م محمد زهير طالب النقيب\n"
        "مدير قسم الشؤون الإدارية والموارد البشرية"
    )

    run.font.size = Pt(9)

    # ========================================================
    # SAVE
    # ========================================================

    buffer = BytesIO()

    doc.save(buffer)

    buffer.seek(0)

    return buffer


# ============================================================
# 14. HERO
# ============================================================

def show_daily_hero():

    render_html(
        """
        <div class="hero-card">
            <div class="hero-content">

                <div class="hero-kicker">
                    ALTURATH UNIVERSITY • HUMAN RESOURCES
                </div>

                <div class="hero-title">
                    Daily Biometric Attendance
                </div>

                <div class="hero-arabic">
                    سجل الحضور اليومي — قسم الموارد البشرية
                </div>

                <div class="hero-description">
                    Current-day check-in and previous-day
                    check-out prepared for HR submission.
                </div>

            </div>
        </div>
        """
    )


def show_exceptions_hero():

    render_html(
        """
        <div class="hero-card">
            <div class="hero-content">

                <div class="hero-kicker">
                    ALTURATH UNIVERSITY • HUMAN RESOURCES
                </div>

                <div class="hero-title">
                    Multi-Day Exceptions
                </div>

                <div class="hero-arabic">
                    تقرير الاستثناءات متعددة الأيام
                </div>

                <div class="hero-description">
                    Review late arrivals and absences across
                    multiple HR attendance exports.
                </div>

            </div>
        </div>
        """
    )


# ============================================================
# 15. SECTION HEADER
# ============================================================

def section_header(
    arabic_title,
    english_title,
):
    render_html(
        f"""
        <div class="section-heading">
            <div class="section-line"></div>
            <div class="section-text">
                {arabic_title}
            </div>
            <div class="section-en">
                {english_title}
            </div>
        </div>
        """
    )


# ============================================================
# 16. DAILY REPORT MODULE
# ============================================================

def run_daily_report_module():

    show_daily_hero()

    show_sidebar_brand()

    # ========================================================
    # SIDEBAR SETTINGS
    # ========================================================

    render_html(
        """
        <div class="sidebar-section">
            Report Settings
        </div>
        """
    )

    use_today = st.sidebar.toggle(
        "Use Today",
        value=False,
    )

    target_date = (
        date.today()
        if use_today
        else st.sidebar.date_input(
            "Submission Date",
            value=date.today(),
        )
    )

    weekdays_ar = {
        "Monday": "الاثنين",
        "Tuesday": "الثلاثاء",
        "Wednesday": "الأربعاء",
        "Thursday": "الخميس",
        "Friday": "الجمعة",
        "Saturday": "السبت",
        "Sunday": "الأحد",
    }

    current_weekday_ar = weekdays_ar.get(
        target_date.strftime("%A"),
        "",
    )

    previous_date = (
        target_date
        -
        timedelta(days=1)
    )

    # ========================================================
    # DATE CARD
    # ========================================================

    col1, col2 = st.columns(
        [3.3, 1.2]
    )

    with col1:

        render_html(
            f"""
            <div class="date-card">

                <div class="date-label">
                    HR SUBMISSION DATE
                </div>

                <div class="date-main">
                    {target_date.strftime('%A, %d %B %Y')}
                </div>

                <div class="date-ar">
                    {current_weekday_ar}
                </div>

            </div>
            """
        )

    with col2:

        render_html(
            f"""
            <div class="date-card">

                <div class="date-pill">
                    Check-Out
                    {previous_date.strftime('%d %b %Y')}
                </div>

                <div class="date-pill-small">
                    previous working date source
                </div>

            </div>
            """
        )

    # ========================================================
    # SIDEBAR FILES
    # ========================================================

    render_html(
        """
        <div class="sidebar-section">
            Attendance Sources
        </div>
        """
    )

    f_zaqura = st.sidebar.file_uploader(
        "Zaqura Gate",
        type=[
            "xlsx",
            "xls",
        ],
        key="zaqura",
    )

    f_mhmd = st.sidebar.file_uploader(
        "Mhmd Bn Ali Gate",
        type=[
            "xlsx",
            "xls",
        ],
        key="mhmd",
    )

    f_app = st.sidebar.file_uploader(
        "Mawjood App",
        type=[
            "xlsx",
            "xls",
        ],
        key="maw",
    )

    render_html(
        """
        <div class="sidebar-section">
            HR Data
        </div>
        """
    )

    f_weekly = st.sidebar.file_uploader(
        "Weekly Day-Off List",
        type=[
            "xlsx",
            "xls",
        ],
        key="weekly",
    )

    # ========================================================
    # PROCESS GATES
    # ========================================================

    all_logs = []

    if f_zaqura:

        data = process_gate(
            f_zaqura,
            "Zaqura Gate",
        )

        if not data.empty:
            all_logs.append(data)

    if f_mhmd:

        data = process_gate(
            f_mhmd,
            "Mhmd Bn Ali Gate",
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
            "OffDay",
        ]
    )

    if f_weekly:

        try:

            df_off = pd.read_excel(
                f_weekly
            )

            df_off.columns = [
                str(c).strip()
                for c in df_off.columns
            ]

            rename_map = {
                "الاسم الثلاثي": "Name",
                "الاسم": "Name",
                "الإسم": "Name",
                "الاجازة الاسبوعية": "OffDay",
                "الإجازة الاسبوعية": "OffDay",
                "يوم العطلة": "OffDay",
            }

            df_off = df_off.rename(
                columns=rename_map
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
    # EMPTY STATE
    # ========================================================

    if not all_logs and not f_weekly:

        render_html(
            """
            <div class="info-card">

                <strong>Ready for HR submission.</strong><br>

                Upload the biometric gate files
                from the left panel to generate
                the daily attendance register.

            </div>
            """
        )

        return

    # ========================================================
    # COMBINE LOGS
    # ========================================================

    if all_logs:

        df_logs = pd.concat(
            all_logs,
            ignore_index=True,
        )

    else:

        df_logs = pd.DataFrame(
            columns=[
                "Name",
                "dt",
                "Date",
                "Time",
                "Event_Type",
                "Source",
            ]
        )

    # ========================================================
    # BUILD FINAL
    # ========================================================

    df_final = build_daily_attendance(
        df_logs,
        target_date,
        current_weekday_ar,
        df_off,
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

    total = len(df_final)

    on_time = len(
        df_final[
            df_final["Status"]
            .str.contains(
                "On Time",
                na=False,
            )
        ]
    )

    late = len(
        df_final[
            df_final["Status"]
            .str.contains(
                "Late",
                na=False,
            )
        ]
    )

    absent = len(
        df_final[
            df_final["Status"]
            .str.contains(
                "Absence",
                na=False,
            )
        ]
    )

    checkout_count = len(
        df_final[
            df_final["Check-Out"] != "-"
        ]
    )

    weekly_off_count = len(
        df_final[
            df_final["Status"]
            .str.contains(
                "Weekly Off",
                na=False,
            )
        ]
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "Employees",
            total,
        )

    with c2:
        st.metric(
            "On Time",
            on_time,
        )

    with c3:
        st.metric(
            "Late",
            late,
        )

    with c4:
        st.metric(
            "Absence",
            absent,
        )

    with c5:
        st.metric(
            "Check-Outs",
            checkout_count,
        )

    # ========================================================
    # HR RULE INFO
    # ========================================================

    render_html(
        f"""
        <div class="info-card">

            <strong>HR submission rule:</strong>

            Check-In →
            <strong>{target_date.strftime('%d %b %Y')}</strong>

            &nbsp;&nbsp;•&nbsp;&nbsp;

            Check-Out →
            <strong>{previous_date.strftime('%d %b %Y')}</strong>

            <br>

            <strong>دخول(1)</strong> = Check-In
            &nbsp; • &nbsp;

            <strong>خروج(2)</strong> before 12:00 = Check-In
            &nbsp; • &nbsp;

            <strong>خروج(2)</strong> at/after 12:00 = Check-Out

            <br>

            First valid Check-In is used for today.
            Last valid Check-Out is used from yesterday.
            Today's Check-Out is never used for today's HR report.

        </div>
        """
    )

    # ========================================================
    # ATTENDANCE TABLE
    # ========================================================

    section_header(
        "سجل الحضور",
        "ATTENDANCE REGISTER",
    )

    display_df = df_final.copy()

    display_df.insert(
        0,
        "No.",
        range(
            1,
            len(display_df) + 1,
        ),
    )

    display_df = display_df.rename(
        columns={
            "Name":
                "الاسم",

            "Check-In":
                f"الحضور ({target_date.strftime('%d %b')})",

            "Check-Out":
                f"الانصراف ({previous_date.strftime('%d %b')})",

            "Source":
                "المصدر",

            "Status":
                "الحالة",
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    # ========================================================
    # EXPORT
    # ========================================================

    section_header(
        "تصدير التقرير",
        "HR EXPORT",
    )

    excel_file = create_daily_excel(
        df_final,
        target_date,
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
        ),
    )

    st.caption(
        "Compact LTR Excel • "
        f"Check-In = {target_date.strftime('%d %b %Y')} • "
        f"Check-Out = {previous_date.strftime('%d %b %Y')}"
    )


# ============================================================
# 17. MULTI-DAY EXCEPTIONS MODULE
# ============================================================

def run_exceptions_module():

    show_exceptions_hero()

    show_sidebar_brand()

    uploaded_files = st.file_uploader(
        "Upload Exported Excel Files",
        accept_multiple_files=True,
        type=[
            "xlsx",
            "xls",
        ],
    )

    if not uploaded_files:

        render_html(
            """
            <div class="info-card">

                <strong>Multi-Day Audit</strong><br>

                Upload exported HR attendance Excel files.
                The system will combine Late and Absence
                records into a single exceptions report.

            </div>
            """
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

            df = pd.read_excel(
                file,
                engine=engine,
                header=2,
            )

            df.columns = [
                str(c).strip()
                for c in df.columns
            ]

            # ------------------------------------------------
            # Support current English/Arabic Excel headers
            # ------------------------------------------------

            name_col = None
            status_col = None

            for col in [
                "Name",
                "الاسم",
            ]:
                if col in df.columns:
                    name_col = col
                    break

            for col in [
                "Status",
                "الحالة",
            ]:
                if col in df.columns:
                    status_col = col
                    break

            if (
                name_col
                and
                status_col
            ):

                mask = (
                    df[status_col]
                    .astype(str)
                    .str.contains(
                        "Late|Absence|تأخير|غياب",
                        case=False,
                        na=False,
                    )
                )

                day_data = df[
                    mask
                ].copy()

                day_data[
                    "Report_Date"
                ] = file_date

                day_data[
                    "Name"
                ] = day_data[
                    name_col
                ]

                day_data[
                    "Status"
                ] = day_data[
                    status_col
                ]

                all_data.append(
                    day_data[
                        [
                            "Name",
                            "Status",
                            "Report_Date",
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
        ignore_index=True,
    )

    summary = (
        combined
        .groupby(
            [
                "Name",
                "Status",
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
                    [str(v) for v in x]
                )
            )
        )
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    section_header(
        "الاستثناءات",
        "EXCEPTIONS",
    )

    display_summary = summary.rename(
        columns={
            "Name": "الاسم",
            "Status": "الحالة",
            "Count": "العدد",
            "Dates_Str": "التواريخ",
        }
    )

    st.dataframe(
        display_summary[
            [
                "الاسم",
                "الحالة",
                "العدد",
                "التواريخ",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    # ========================================================
    # WORD REPORT
    # ========================================================

    section_header(
        "التقرير الرسمي",
        "OFFICIAL WORD REPORT",
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
            ),
        )


# ============================================================
# 18. SIDEBAR NAVIGATION
# ============================================================

show_sidebar_brand()

render_html(
    """
    <div class="sidebar-section">
        System Module
    </div>
    """
)

app_mode = st.sidebar.selectbox(
    "System Module",
    [
        "Daily Report Tool",
        "Multi-Day Audit Tool",
    ],
    label_visibility="collapsed",
)


# ============================================================
# 19. RUN
# ============================================================

if app_mode == "Daily Report Tool":

    run_daily_report_module()

else:

    run_exceptions_module()


# ============================================================
# 20. FOOTER
# ============================================================

render_html(
    """
    <div class="footer">
        ALTURATH HR BIOMETRICS SYSTEM • V2
        &nbsp;•&nbsp;
        HUMAN RESOURCES
    </div>
    """
)
