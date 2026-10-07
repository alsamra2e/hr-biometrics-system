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
# 2. CONSTANTS
# ============================================================

UNIVERSITY_NAME = "University Of Alturath"

# Local logo.
# Put logo(1).png in the SAME folder as app.py.
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

LOGO_PATH = os.path.join(
    BASE_DIR,
    "logo(1).png"
)


# ============================================================
# 3. FUTURISTIC HR THEME
# ============================================================

def apply_v2_theme():

    st.markdown(
        """
        <style>

        /* ==================================================
           GLOBAL
           ================================================== */

        @import url(
            'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
        );

        html,
        body,
        [class*="css"] {
            font-family: 'Inter', sans-serif;
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
            max-width: 1500px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }


        /* ==================================================
           SIDEBAR
           ================================================== */

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #07111f 0%,
                    #0a1628 55%,
                    #0b1930 100%
                );

            border-right: 1px solid #17263c;
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1.3rem;
        }

        section[data-testid="stSidebar"] * {
            color: #e2e8f0;
        }

        section[data-testid="stSidebar"] label {
            color: #a9b8ca !important;
            font-size: 12px !important;
            font-weight: 600 !important;
        }

        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stFileUploader label,
        section[data-testid="stSidebar"] .stDateInput label {
            color: #a9b8ca !important;
        }

        section[data-testid="stSidebar"] .stSelectbox > div > div,
        section[data-testid="stSidebar"] .stDateInput > div > div {
            background: #101e31;
            border: 1px solid #263952;
            border-radius: 10px;
        }

        section[data-testid="stSidebar"] .stSelectbox svg {
            fill: #94a3b8;
        }

        section[data-testid="stSidebar"] .stFileUploader {
            margin-bottom: 8px;
        }

        section[data-testid="stSidebar"] .stFileUploader > div {
            background: #0d1a2c;
            border: 1px dashed #31445f;
            border-radius: 10px;
        }

        section[data-testid="stSidebar"] .stFileUploader > div:hover {
            border-color: #3b82f6;
        }

        section[data-testid="stSidebar"] hr {
            border-color: #1e3049;
        }


        /* ==================================================
           SIDEBAR BRAND
           ================================================== */

        .brand {
            padding: 4px 3px 24px 3px;
        }

        .brand-logo {
            width: 64px;
            height: 64px;
            object-fit: contain;

            background: #ffffff;

            border-radius: 15px;

            padding: 7px;

            margin-bottom: 13px;

            box-shadow:
                0 12px 30px rgba(0, 0, 0, 0.22);

            border: 1px solid rgba(255,255,255,0.10);
        }

        .brand-name {
            color: #f8fafc;

            font-size: 19px;
            font-weight: 800;

            letter-spacing: -0.5px;

            line-height: 1.1;
        }

        .brand-sub {
            color: #71839b;

            font-size: 9px;

            margin-top: 6px;

            letter-spacing: 1.2px;

            text-transform: uppercase;
        }


        /* ==================================================
           SIDEBAR SECTION LABEL
           ================================================== */

        .sidebar-section {
            color: #dbeafe;

            font-size: 11px;

            font-weight: 800;

            letter-spacing: 1.1px;

            text-transform: uppercase;

            margin-top: 20px;
            margin-bottom: 9px;

            padding-left: 2px;
        }


        /* ==================================================
           HERO
           ================================================== */

        .hero {
            position: relative;

            overflow: hidden;

            background:
                linear-gradient(
                    135deg,
                    #09172a 0%,
                    #0d1e36 58%,
                    #10284a 100%
                );

            border: 1px solid #1b3150;

            border-radius: 22px;

            padding: 30px 32px;

            margin-bottom: 20px;

            box-shadow:
                0 20px 50px rgba(15,23,42,0.10);
        }

        .hero:before {
            content: "";

            position: absolute;

            width: 420px;
            height: 420px;

            right: -190px;
            top: -220px;

            border-radius: 50%;

            background:
                radial-gradient(
                    circle,
                    rgba(59,130,246,0.24),
                    rgba(59,130,246,0.04) 50%,
                    transparent 70%
                );
        }

        .hero:after {
            content: "";

            position: absolute;

            width: 150px;
            height: 150px;

            right: 80px;
            bottom: -100px;

            border-radius: 50%;

            background:
                rgba(14,165,233,0.08);
        }

        .hero-content {
            position: relative;
            z-index: 2;
        }

        .hero-label {
            color: #60a5fa;

            font-size: 10px;

            font-weight: 800;

            letter-spacing: 2px;

            text-transform: uppercase;

            margin-bottom: 8px;
        }

        .hero-title {
            color: #f8fafc;

            font-size: 30px;

            font-weight: 800;

            letter-spacing: -1px;

            line-height: 1.1;

            margin: 0;
        }

        .hero-description {
            color: #a8b7ca;

            font-size: 13px;

            line-height: 1.7;

            max-width: 780px;

            margin-top: 10px;
        }


        /* ==================================================
           DATE BAR
           ================================================== */

        .date-bar {
            display: flex;

            align-items: center;

            justify-content: space-between;

            gap: 15px;

            background: #ffffff;

            border: 1px solid #dce4ee;

            border-radius: 15px;

            padding: 14px 18px;

            margin-bottom: 18px;

            box-shadow:
                0 7px 24px rgba(15,23,42,0.045);
        }

        .date-main {
            color: #0f172a;

            font-size: 14px;

            font-weight: 800;
        }

        .date-sub {
            color: #64748b;

            font-size: 11px;

            margin-top: 4px;
        }

        .date-flow {
            display: flex;

            align-items: center;

            gap: 8px;

            flex-wrap: wrap;

            justify-content: flex-end;
        }

        .date-badge {
            padding: 7px 11px;

            border-radius: 999px;

            font-size: 10px;

            font-weight: 800;

            white-space: nowrap;
        }

        .date-badge.in {
            background: #ecfdf5;

            color: #047857;

            border: 1px solid #bbf7d0;
        }

        .date-badge.out {
            background: #eff6ff;

            color: #1d4ed8;

            border: 1px solid #bfdbfe;
        }


        /* ==================================================
           METRICS
           ================================================== */

        div[data-testid="stMetric"] {
            background: #ffffff;

            border: 1px solid #dce4ee;

            border-radius: 14px;

            padding: 13px 15px;

            box-shadow:
                0 6px 20px rgba(15,23,42,0.035);
        }

        div[data-testid="stMetricLabel"] {
            color: #64748b;

            font-size: 10px;
        }

        div[data-testid="stMetricValue"] {
            color: #0f172a;

            font-weight: 800;

            font-size: 25px;
        }


        /* ==================================================
           BUTTONS
           ================================================== */

        .stButton > button,
        .stDownloadButton > button {

            border-radius: 9px;

            border: 1px solid #2563eb;

            background: #2563eb;

            color: #ffffff;

            font-weight: 700;

            min-height: 40px;

            transition:
                background 0.15s ease,
                transform 0.15s ease,
                box-shadow 0.15s ease;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {

            background: #1d4ed8;

            border-color: #1d4ed8;

            transform: translateY(-1px);

            box-shadow:
                0 8px 20px rgba(37,99,235,0.18);
        }


        /* ==================================================
           DATAFRAME
           ================================================== */

        div[data-testid="stDataFrame"] {

            border: 1px solid #dce4ee;

            border-radius: 14px;

            overflow: hidden;

            box-shadow:
                0 8px 28px rgba(15,23,42,0.045);
        }


        /* ==================================================
           SECTION TITLES
           ================================================== */

        .section-title {

            color: #0f172a;

            font-size: 15px;

            font-weight: 800;

            letter-spacing: -0.2px;

            margin-top: 25px;

            margin-bottom: 10px;

            padding-left: 1px;
        }


        /* ==================================================
           INFORMATION CARDS
           ================================================== */

        .status-note {

            border-radius: 13px;

            padding: 13px 16px;

            background: #ffffff;

            border: 1px solid #dce4ee;

            color: #475569;

            font-size: 12px;

            line-height: 1.7;

            margin-top: 15px;

            box-shadow:
                0 5px 18px rgba(15,23,42,0.025);
        }

        .status-note strong {
            color: #0f172a;
        }


        /* ==================================================
           EMPTY / READY CARD
           ================================================== */

        .ready-card {

            background: #ffffff;

            border: 1px solid #dce4ee;

            border-radius: 16px;

            padding: 25px;

            box-shadow:
                0 8px 28px rgba(15,23,42,0.035);
        }

        .ready-title {
            color: #0f172a;

            font-size: 16px;

            font-weight: 800;

            margin-bottom: 6px;
        }

        .ready-text {
            color: #64748b;

            font-size: 12px;

            line-height: 1.7;
        }


        /* ==================================================
           FOOTER
           ================================================== */

        .footer {

            color: #94a3b8;

            text-align: center;

            font-size: 10px;

            padding: 30px 0 8px 0;

            letter-spacing: 0.3px;
        }


        /* ==================================================
           FILE UPLOAD HELP
           ================================================== */

        [data-testid="stFileUploaderFile"] {
            background: #0f2035;
            border-radius: 8px;
        }


        /* ==================================================
           MOBILE
           ================================================== */

        @media (max-width: 800px) {

            .hero {
                padding: 24px 21px;
            }

            .hero-title {
                font-size: 24px;
            }

            .date-bar {
                align-items: flex-start;
                flex-direction: column;
            }

            .date-flow {
                justify-content: flex-start;
            }

        }

        </style>
        """,
        unsafe_allow_html=True
    )


apply_v2_theme()


# ============================================================
# 4. LOCAL LOGO
# ============================================================

@st.cache_data(show_spinner=False)
def get_logo_bytes():

    try:

        if not os.path.exists(LOGO_PATH):

            return None

        with open(
            LOGO_PATH,
            "rb"
        ) as f:

            return f.read()

    except Exception:

        return None


def get_logo_base64():

    logo = get_logo_bytes()

    if not logo:

        return None

    import base64

    return base64.b64encode(
        logo
    ).decode("utf-8")


def show_sidebar_brand():

    encoded = get_logo_base64()

    if encoded:

        st.sidebar.markdown(
            f"""
            <div class="brand">

                <img
                    class="brand-logo"
                    src="data:image/png;base64,{encoded}"
                    alt="Alturath University Logo"
                />

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

    else:

        st.sidebar.markdown(
            """
            <div class="brand">

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


# ============================================================
# 5. WORD RTL UTILITIES
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
    Biometric event rules:

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
# 8. PROCESS BIOMETRIC GATE
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

        elif "اسم" in df.columns:

            name_col = "اسم"

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

        # Gate name is ONLY the source.
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
        ].sort_values(
            "dt"
        )

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
                            "Time": dt.strftime("%H:%M"),
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
            f"Error processing "
            f"Mawjood App: {e}"
        )

        return pd.DataFrame()


# ============================================================
# 10. BUILD DAILY ATTENDANCE
# ============================================================

def build_daily_attendance(
    df_logs,
    target_date,
    current_weekday_ar,
    df_off
):

    """
    IMPORTANT HR SUBMISSION RULE

    Selected date = 7 Oct

    Check-In  = 7 Oct
    Check-Out = 6 Oct

    NEVER use today's Check-Out for today's report.
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

        if "Name" in df_off.columns:

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
        # FIRST VALID CHECK-IN
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
        # LAST VALID PREVIOUS-DAY CHECK-OUT
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

        off_info = pd.DataFrame()

        if not df_off.empty:

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

            # Compare HH:MM as actual time,
            # rather than relying on string comparison.
            try:

                check_in_time = (
                    datetime_from_hhmm(
                        check_in
                    )
                )

                if check_in_time > time(8, 35):

                    status = "🔴 Late"

                else:

                    status = "🟢 On Time"

            except Exception:

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


def datetime_from_hhmm(
    value
):

    hour, minute = (
        str(value)
        .split(":")
    )

    return time(
        int(hour),
        int(minute)
    )


# ============================================================
# 11. EXCEL EXPORT
# ============================================================

def create_daily_excel(
    df_final,
    target_date
):

    """
    Compact modern LTR Excel.

    IMPORTANT:
    - No RTL worksheet setting.
    - No worksheet.right_to_left().
    - No set_print_area().
    - No large images.
    - No unnecessary formatting.
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
            "الحضور"
        )

        writer.sheets[
            "الحضور"
        ] = worksheet

        # ====================================================
        # FORMATS
        # ====================================================

        title_format = workbook.add_format(
            {
                "bold": True,
                "font_size": 15,
                "font_name": "Arial",
                "font_color": "#FFFFFF",
                "bg_color": "#0B1930",
                "align": "center",
                "valign": "vcenter"
            }
        )

        subtitle_format = workbook.add_format(
            {
                "font_size": 9,
                "font_name": "Arial",
                "font_color": "#CBD5E1",
                "bg_color": "#0B1930",
                "align": "center",
                "valign": "vcenter"
            }
        )

        header_ar_format = workbook.add_format(
            {
                "bold": True,
                "font_size": 11,
                "font_name": "Arial",
                "font_color": "#FFFFFF",
                "bg_color": "#2563EB",
                "align": "center",
                "valign": "vcenter",
                "border": 1,
                "border_color": "#CBD5E1",
                "text_wrap": True
            }
        )

        header_en_format = workbook.add_format(
            {
                "font_size": 7,
                "font_name": "Arial",
                "font_color": "#DBEAFE",
                "bg_color": "#2563EB",
                "align": "center",
                "valign": "vcenter"
            }
        )

        cell_format = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 10,
                "align": "center",
                "valign": "vcenter",
                "border": 1,
                "border_color": "#E2E8F0"
            }
        )

        name_format = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 10,
                "align": "right",
                "valign": "vcenter",
                "border": 1,
                "border_color": "#E2E8F0"
            }
        )

        # ====================================================
        # TITLE
        # ====================================================

        worksheet.merge_range(
            "A1:F1",
            "جامعة التراث • كشف الحضور اليومي",
            title_format
        )

        worksheet.merge_range(
            "A2:F2",
            (
                f"University Of Alturath • "
                f"HR Daily Attendance | "
                f"Check-In: {target_date.strftime('%d %b %Y')} | "
                f"Check-Out: {previous_date.strftime('%d %b %Y')}"
            ),
            subtitle_format
        )

        worksheet.set_row(
            0,
            27
        )

        worksheet.set_row(
            1,
            20
        )

        # ====================================================
        # HEADERS
        # ====================================================

        headers = [
            ("ت", "No."),
            ("الاسم", "Name"),
            (
                f"الحضور\n({target_date.strftime('%d %b')})",
                "Check-In"
            ),
            (
                f"الانصراف\n({previous_date.strftime('%d %b')})",
                "Check-Out"
            ),
            ("المصدر", "Source"),
            ("الحالة", "Status")
        ]

        for col, (
            arabic_header,
            english_header
        ) in enumerate(headers):

            worksheet.write(
                2,
                col,
                arabic_header,
                header_ar_format
            )

            # Small English line underneath.
            worksheet.write_comment(
                2,
                col,
                english_header
            )

        worksheet.set_row(
            2,
            38
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
                cell_format
            )

            worksheet.write(
                excel_row,
                1,
                str(row["Name"]),
                name_format
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

        # ====================================================
        # COLUMN WIDTHS
        # ====================================================

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
            17
        )

        worksheet.set_column(
            "E:E",
            23
        )

        worksheet.set_column(
            "F:F",
            18
        )

        # ====================================================
        # LIGHTWEIGHT SETTINGS
        # ====================================================

        worksheet.freeze_panes(
            3,
            0
        )

        worksheet.hide_gridlines(
            2
        )

        # LTR by default.
        # DO NOT call right_to_left().

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

    # ========================================================
    # ARABIC HEADER
    # ========================================================

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

    # ========================================================
    # LOCAL LOGO
    # ========================================================

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

    # ========================================================
    # ENGLISH HEADER
    # ========================================================

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

    # ========================================================
    # SEPARATOR
    # ========================================================

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

    # ========================================================
    # BODY
    # ========================================================

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

    # ========================================================
    # TABLE
    # ========================================================

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

    # ========================================================
    # ROWS
    # ========================================================

    for idx, row in df.iterrows():

        cells = table.add_row().cells

        cells[0].text = str(
            idx + 1
        )

        cells[1].text = str(
            row["Name"]
        )

        if "Late" in str(
            row["Status"]
        ):

            cells[2].text = "تأخير"

        elif "Absence" in str(
            row["Status"]
        ):

            cells[2].text = "غياب"

        else:

            cells[2].text = str(
                row["Status"]
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

    # ========================================================
    # SIGNATURE
    # ========================================================

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

    # ========================================================
    # HERO
    # ========================================================

    st.markdown(
        """
        <div class="hero">

            <div class="hero-content">

                <div class="hero-label">
                    ALTURATH UNIVERSITY • HUMAN RESOURCES
                </div>

                <div class="hero-title">
                    Daily Biometric Attendance
                </div>

                <div class="hero-description">
                    سجل الحضور اليومي للموارد البشرية —
                    دخول اليوم وخروج اليوم السابق وفق آلية
                    التسليم المعتمدة لدى قسم الموارد البشرية.
                </div>

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
    # SYSTEM MODULE
    # ========================================================

    st.sidebar.markdown(
        """
        <div class="sidebar-section">
            System Module
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

            <div class="date-flow">

                <div class="date-badge in">
                    Check-In • {target_date.strftime('%d %b %Y')}
                </div>

                <div class="date-badge out">
                    Check-Out • {previous_date.strftime('%d %b %Y')}
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # FILE UPLOADERS
    # ========================================================

    st.sidebar.markdown(
        """
        <div class="sidebar-section">
            Attendance Sources
        </div>
        """,
        unsafe_allow_html=True
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

    # ========================================================
    # HR DATA
    # ========================================================

    st.sidebar.markdown(
        """
        <div class="sidebar-section">
            HR Data
        </div>
        """,
        unsafe_allow_html=True
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

            all_logs.append(
                data
            )

    if f_mhmd:

        data = process_gate(
            f_mhmd,
            "Mhmd Bn Ali Gate"
        )

        if not data.empty:

            all_logs.append(
                data
            )

    # ========================================================
    # PROCESS MAWJOOD APP
    # ========================================================

    if f_app:

        data = process_app(
            f_app
        )

        if not data.empty:

            all_logs.append(
                data
            )

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

            if "Name" not in df_off.columns:

                st.warning(
                    "Weekly file: Name column was not found."
                )

            if "OffDay" not in df_off.columns:

                st.warning(
                    "Weekly file: OffDay column was not found."
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
    # NO FILES
    # ========================================================

    if not all_logs and not f_weekly:

        st.markdown(
            """
            <div class="ready-card">

                <div class="ready-title">
                    System Ready
                </div>

                <div class="ready-text">
                    Upload the biometric gate exports
                    from the sidebar to generate the
                    HR attendance report.
                    <br><br>
                    <b>Today's Check-In</b> is paired with
                    <b>yesterday's Check-Out</b>.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        return

    # ========================================================
    # COMBINE LOGS
    # ========================================================

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
    # BUILD REPORT
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

            <strong>HR Submission Rule</strong><br>

            Check-In is taken from
            <b>{target_date.strftime('%d %b %Y')}</b>.

            &nbsp; • &nbsp;

            Check-Out is taken from
            <b>{previous_date.strftime('%d %b %Y')}</b>.

            <br>

            <b>دخول(1)</b> = Check-In
            &nbsp; • &nbsp;
            <b>خروج(2)</b> before 12:00 = Check-In
            &nbsp; • &nbsp;
            <b>خروج(2)</b> at/after 12:00 = Check-Out

        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # ATTENDANCE TABLE
    # ========================================================

    st.markdown(
        """
        <div class="section-title">
            Attendance Register
        </div>
        """,
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
        """
        <div class="section-title">
            HR Export
        </div>
        """,
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

    # ========================================================
    # HERO
    # ========================================================

    st.markdown(
        """
        <div class="hero">

            <div class="hero-content">

                <div class="hero-label">
                    ALTURATH UNIVERSITY • HUMAN RESOURCES
                </div>

                <div class="hero-title">
                    Multi-Day Exceptions
                </div>

                <div class="hero-description">
                    مراجعة حالات التأخير والغياب عبر
                    تقارير الحضور اليومية المصدّرة.
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # BRAND
    # ========================================================

    show_sidebar_brand()

    # ========================================================
    # UPLOAD
    # ========================================================

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
            <div class="ready-card">

                <div class="ready-title">
                    Multi-Day Audit Ready
                </div>

                <div class="ready-text">
                    Upload your daily HR Excel files.
                    The system will combine them into
                    a multi-day exceptions report.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        return

    all_data = []

    # ========================================================
    # PROCESS FILES
    # ========================================================

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
                header=2
            )

            df.columns = [
                str(c).strip()
                for c in df.columns
            ]

            if (
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

    # ========================================================
    # NO EXCEPTIONS
    # ========================================================

    if not all_data:

        st.info(
            "No Late or Absence records found."
        )

        return

    combined = pd.concat(
        all_data,
        ignore_index=True
    )

    # ========================================================
    # SUMMARY
    # ========================================================

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
                    [
                        str(v)
                        for v in x
                    ]
                )
            )
        )
    )

    # ========================================================
    # TABLE
    # ========================================================

    st.markdown(
        """
        <div class="section-title">
            Exceptions
        </div>
        """,
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

    # ========================================================
    # WORD REPORT
    # ========================================================

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

st.sidebar.markdown(
    """
    <div class="sidebar-section">
        System Module
    </div>
    """,
    unsafe_allow_html=True
)

app_mode = st.sidebar.selectbox(
    "System Module",
    [
        "Daily Report Tool",
        "Multi-Day Audit Tool"
    ],
    label_visibility="collapsed"
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
        &nbsp;•&nbsp;
        UNIVERSITY OF ALTURATH
    </div>
    """,
    unsafe_allow_html=True
)
