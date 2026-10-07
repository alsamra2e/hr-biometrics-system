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
    page_title="Alturath HR • Biometric Attendance",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. CONSTANTS
# ============================================================

UNIVERSITY_NAME = "University Of Alturath"

LOCAL_LOGO = "logo(1).png"


# ============================================================
# 3. THEME
# ============================================================

def apply_theme():

    st.markdown(
        """
<style>

/* ==========================================================
   BASE
   ========================================================== */

:root {
    --navy: #071426;
    --navy-2: #0b1d33;
    --blue: #2563eb;
    --blue-2: #3b82f6;
    --cyan: #06b6d4;
    --text: #0f172a;
    --muted: #64748b;
    --border: #e2e8f0;
    --surface: #ffffff;
    --surface-2: #f8fafc;
    --green: #16a34a;
    --red: #dc2626;
    --orange: #ea580c;
    --yellow: #ca8a04;
}

html,
body,
[data-testid="stAppViewContainer"] {
    background: #f4f7fb;
}

html,
body,
.stApp,
.stApp * {
    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

/* ==========================================================
   MAIN CONTAINER
   ========================================================== */

.block-container {
    max-width: 1500px !important;
    padding-top: 1.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 3rem !important;
}

/* ==========================================================
   SIDEBAR
   ========================================================== */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #061221 0%,
            #09182a 55%,
            #0b1d33 100%
        ) !important;

    border-right: 1px solid #1e293b;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1rem;
}

section[data-testid="stSidebar"] * {
    color: #e5edf7;
}

section[data-testid="stSidebar"] label {
    color: #9fb0c4 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}

/* Sidebar selectbox */

section[data-testid="stSidebar"]
div[data-baseweb="select"] > div {
    background: #101f34 !important;
    border: 1px solid #263852 !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}

/* Sidebar date */

section[data-testid="stSidebar"]
div[data-baseweb="input"] {
    background: #101f34 !important;
    border: 1px solid #263852 !important;
    border-radius: 10px !important;
}

section[data-testid="stSidebar"]
input {
    color: #ffffff !important;
}

/* Sidebar uploader */

section[data-testid="stSidebar"]
[data-testid="stFileUploader"] {
    margin-bottom: 0.7rem;
}

section[data-testid="stSidebar"]
[data-testid="stFileUploaderDropzone"] {
    background: #0d1c30 !important;
    border: 1px dashed #334966 !important;
    border-radius: 10px !important;
}

section[data-testid="stSidebar"]
[data-testid="stFileUploaderDropzoneInstructions"] {
    color: #a8b8cb !important;
}

/* ==========================================================
   BRAND
   ========================================================== */

.sidebar-brand {
    padding: 0.3rem 0.2rem 1.5rem 0.2rem;
}

.sidebar-logo {
    width: 62px;
    height: 62px;
    object-fit: contain;
    background: #ffffff;
    border-radius: 15px;
    padding: 7px;
    margin-bottom: 0.8rem;
    box-shadow:
        0 12px 30px rgba(0, 0, 0, 0.22);
}

.sidebar-brand-name {
    color: #ffffff;
    font-size: 1.05rem;
    font-weight: 800;
    letter-spacing: 0.3px;
}

.sidebar-brand-sub {
    color: #6f849c;
    font-size: 0.66rem;
    font-weight: 600;
    letter-spacing: 1.1px;
    margin-top: 0.25rem;
}

/* ==========================================================
   TOP BRAND
   ========================================================== */

.top-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1rem;
}

.top-brand-logo {
    width: 48px;
    height: 48px;
    object-fit: contain;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 5px;
}

.top-brand-title {
    color: #0f172a;
    font-size: 0.9rem;
    font-weight: 800;
}

.top-brand-subtitle {
    color: #64748b;
    font-size: 0.68rem;
    margin-top: 2px;
}

/* ==========================================================
   HERO
   ========================================================== */

.hero-card {
    position: relative;
    overflow: hidden;

    background:
        linear-gradient(
            135deg,
            #071426 0%,
            #0c1d34 60%,
            #102b4a 100%
        );

    border: 1px solid #1d3552;
    border-radius: 20px;

    padding: 2rem 2.2rem;
    margin-bottom: 1rem;

    box-shadow:
        0 18px 45px rgba(15, 23, 42, 0.12);
}

.hero-card::after {
    content: "";
    position: absolute;
    width: 260px;
    height: 260px;
    right: -110px;
    top: -140px;
    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(59, 130, 246, 0.30),
            rgba(59, 130, 246, 0) 70%
        );

    pointer-events: none;
}

.hero-kicker {
    color: #60a5fa;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.45rem;
}

.hero-title {
    color: #ffffff;
    font-size: clamp(1.45rem, 3vw, 2rem);
    font-weight: 800;
    line-height: 1.15;
    margin: 0;
}

.hero-text {
    color: #a9b8ca;
    font-size: 0.82rem;
    line-height: 1.6;
    margin-top: 0.65rem;
    max-width: 760px;
}

/* ==========================================================
   DATE CARD
   ========================================================== */

.date-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;

    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;

    padding: 0.9rem 1.1rem;
    margin-bottom: 1rem;

    box-shadow:
        0 5px 18px rgba(15, 23, 42, 0.04);
}

.date-main {
    color: #0f172a;
    font-size: 0.95rem;
    font-weight: 800;
}

.date-sub {
    color: #64748b;
    font-size: 0.72rem;
    margin-top: 0.2rem;
}

.checkout-pill {
    white-space: nowrap;

    color: #1d4ed8;
    background: #eff6ff;
    border: 1px solid #dbeafe;

    border-radius: 999px;

    padding: 0.45rem 0.75rem;

    font-size: 0.7rem;
    font-weight: 800;
}

/* ==========================================================
   METRICS
   ========================================================== */

div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;

    padding: 0.8rem 0.9rem !important;

    box-shadow:
        0 5px 18px rgba(15, 23, 42, 0.035);
}

div[data-testid="stMetricLabel"] {
    color: #64748b !important;
    font-size: 0.7rem !important;
}

div[data-testid="stMetricValue"] {
    color: #0f172a !important;
    font-size: 1.35rem !important;
    font-weight: 800 !important;
}

/* ==========================================================
   SECTION TITLES
   ========================================================== */

.section-heading {
    display: flex;
    align-items: center;
    gap: 9px;

    color: #0f172a;

    font-size: 1rem;
    font-weight: 800;

    margin-top: 1.4rem;
    margin-bottom: 0.65rem;
}

.section-heading::before {
    content: "";
    width: 4px;
    height: 18px;

    border-radius: 10px;

    background: #2563eb;
}

/* ==========================================================
   INFO CARD
   ========================================================== */

.info-card {
    background: #ffffff;

    border: 1px solid #e2e8f0;
    border-left: 4px solid #2563eb;

    border-radius: 12px;

    padding: 0.85rem 1rem;

    color: #475569;
    font-size: 0.76rem;
    line-height: 1.8;

    margin: 0.8rem 0;
}

.info-card strong {
    color: #0f172a;
}

/* ==========================================================
   TABLE
   ========================================================== */

div[data-testid="stDataFrame"] {
    width: 100%;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    overflow: hidden;
    box-shadow:
        0 6px 20px rgba(15, 23, 42, 0.04);
}

/* ==========================================================
   BUTTONS
   ========================================================== */

.stButton > button,
.stDownloadButton > button {
    min-height: 42px;

    border-radius: 10px !important;

    background: #2563eb !important;
    color: #ffffff !important;

    border: 1px solid #2563eb !important;

    font-weight: 700 !important;

    box-shadow:
        0 5px 14px rgba(37, 99, 235, 0.14);

    transition:
        transform 0.15s ease,
        background 0.15s ease,
        box-shadow 0.15s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #1d4ed8 !important;
    border-color: #1d4ed8 !important;

    transform: translateY(-1px);

    box-shadow:
        0 8px 20px rgba(37, 99, 235, 0.20);
}

/* ==========================================================
   FILE UPLOAD MAIN AREA
   ========================================================== */

[data-testid="stFileUploaderDropzone"] {
    border-radius: 12px !important;
}

/* ==========================================================
   FOOTER
   ========================================================== */

.footer {
    text-align: center;
    color: #94a3b8;
    font-size: 0.66rem;
    padding: 2rem 0 0.5rem 0;
}

/* ==========================================================
   MOBILE / RESPONSIVE
   ========================================================== */

@media (max-width: 900px) {

    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1rem !important;
    }

    .hero-card {
        padding: 1.35rem 1.25rem;
        border-radius: 16px;
    }

    .hero-title {
        font-size: 1.45rem;
    }

    .date-card {
        align-items: flex-start;
        flex-direction: column;
    }

    .checkout-pill {
        white-space: normal;
    }
}

@media (max-width: 600px) {

    .block-container {
        padding-left: 0.7rem !important;
        padding-right: 0.7rem !important;
    }

    .hero-card {
        padding: 1.15rem;
        margin-bottom: 0.75rem;
    }

    .hero-kicker {
        font-size: 0.58rem;
        letter-spacing: 1.3px;
    }

    .hero-title {
        font-size: 1.3rem;
    }

    .hero-text {
        font-size: 0.72rem;
    }

    .date-card {
        padding: 0.8rem;
    }

    div[data-testid="stMetric"] {
        padding: 0.65rem !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
    }

    .section-heading {
        font-size: 0.9rem;
    }

    .info-card {
        font-size: 0.7rem;
    }
}

</style>
        """,
        unsafe_allow_html=True
    )


apply_theme()


# ============================================================
# 4. LOGO
# ============================================================

def get_logo_path():

    candidates = [
        LOCAL_LOGO,
        os.path.join(
            os.path.dirname(__file__),
            LOCAL_LOGO
        )
    ]

    for path in candidates:

        if os.path.exists(path):

            return path

    return None


def show_sidebar_brand():

    logo_path = get_logo_path()

    if logo_path:

        st.sidebar.markdown(
            f"""
<div class="sidebar-brand">
    <img
        class="sidebar-logo"
        src="data:image/png;base64,{__import__('base64').b64encode(open(logo_path, 'rb').read()).decode()}"
    />

    <div class="sidebar-brand-name">
        ALTURATH HR
    </div>

    <div class="sidebar-brand-sub">
        BIOMETRIC ATTENDANCE SYSTEM
    </div>
</div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.sidebar.markdown(
            """
<div class="sidebar-brand">
    <div class="sidebar-brand-name">
        ALTURATH HR
    </div>

    <div class="sidebar-brand-sub">
        BIOMETRIC ATTENDANCE SYSTEM
    </div>
</div>
            """,
            unsafe_allow_html=True
        )


def show_top_brand():

    logo_path = get_logo_path()

    if logo_path:

        encoded = __import__("base64").b64encode(
            open(logo_path, "rb").read()
        ).decode()

        st.markdown(
            f"""
<div class="top-brand">
    <img
        class="top-brand-logo"
        src="data:image/png;base64,{encoded}"
    />

    <div>
        <div class="top-brand-title">
            ALTURATH UNIVERSITY
        </div>

        <div class="top-brand-subtitle">
            Human Resources • Biometric Attendance
        </div>
    </div>
</div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# 5. WORD RTL HELPERS
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


# ============================================================
# 6. FILE DATE
# ============================================================

def extract_date_from_filename(filename):

    match = re.search(
        r"\d{4}-\d{2}-\d{2}",
        filename
    )

    if match:
        return match.group(0)

    return str(date.today())


# ============================================================
# 7. BIOMETRIC CLASSIFICATION
# ============================================================

def classify_gate_event(
    event_value,
    punch_datetime
):

    event = str(event_value).strip()

    punch_time = punch_datetime.time()

    # دخول(1) = Check-In
    if "دخول" in event:
        return "Check-In"

    # خروج(2)
    if "خروج" in event:

        # Before 12:00 = Check-In
        if punch_time < time(12, 0):
            return "Check-In"

        # 12:00 and after = Check-Out
        return "Check-Out"

    return None


# ============================================================
# 8. PROCESS GATE
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

        # NAME
        if "الاسم" in df.columns:
            name_col = "الاسم"

        elif "الإسم" in df.columns:
            name_col = "الإسم"

        else:

            st.warning(
                f"{gate_name}: الاسم column was not found."
            )

            return pd.DataFrame()

        # TIME
        if "الوقت" not in df.columns:

            st.warning(
                f"{gate_name}: الوقت column was not found."
            )

            return pd.DataFrame()

        # EVENT
        if "Event" not in df.columns:

            st.warning(
                f"{gate_name}: Event column was not found."
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

        df = df[df["dt"].notna()].copy()

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

        df["Date"] = df["dt"].dt.date

        df["Time"] = df["dt"].dt.strftime(
            "%H:%M"
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

        # CHECK-IN
        if "دخول" in df.columns:

            for _, row in df.iterrows():

                dt = pd.to_datetime(
                    row["دخول"],
                    errors="coerce"
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

                            "Event_Type": "Check-In",

                            "Source": "Mawjood App"
                        }
                    )

        # CHECK-OUT
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
                            "Name": str(
                                row["الاسم"]
                            ).strip(),

                            "dt": dt,

                            "Date": dt.date(),

                            "Time": dt.strftime(
                                "%H:%M"
                            ),

                            "Event_Type": "Check-Out",

                            "Source": "Mawjood App"
                        }
                    )

        return pd.DataFrame(result)

    except Exception as e:

        st.error(
            f"Error processing Mawjood App: {e}"
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

    master_names = set()

    if not df_logs.empty:

        master_names.update(
            df_logs["Name"]
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

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

    for name in sorted(master_names):

        person = df_logs[
            df_logs["Name"]
            .astype(str)
            .str.strip()
            ==
            str(name).strip()
        ].copy()

        person = person.sort_values("dt")

        # ----------------------------------------------------
        # TODAY CHECK-IN
        # ----------------------------------------------------

        today_checkins = person[
            (person["Date"] == target_date)
            &
            (
                person["Event_Type"]
                == "Check-In"
            )
        ].copy()

        # ----------------------------------------------------
        # YESTERDAY CHECK-OUT
        # ----------------------------------------------------

        yesterday_checkouts = person[
            (person["Date"] == previous_date)
            &
            (
                person["Event_Type"]
                == "Check-Out"
            )
        ].copy()

        # ----------------------------------------------------
        # FIRST CHECK-IN
        # ----------------------------------------------------

        check_in = "-"
        check_in_source = "-"

        if not today_checkins.empty:

            first_checkin = (
                today_checkins
                .sort_values("dt")
                .iloc[0]
            )

            check_in = first_checkin["Time"]
            check_in_source = first_checkin["Source"]

        # ----------------------------------------------------
        # LAST CHECK-OUT
        # ----------------------------------------------------

        check_out = "-"
        check_out_source = "-"

        if not yesterday_checkouts.empty:

            last_checkout = (
                yesterday_checkouts
                .sort_values("dt")
                .iloc[-1]
            )

            check_out = last_checkout["Time"]
            check_out_source = last_checkout["Source"]

        # ----------------------------------------------------
        # WEEKLY OFF
        # ----------------------------------------------------

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
                str(
                    current_weekday_ar
                ).strip()
            )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if check_in != "-":

            # Time comparison
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

        # ----------------------------------------------------
        # SOURCE
        # ----------------------------------------------------

        source_parts = []

        if check_in_source != "-":
            source_parts.append(check_in_source)

        if (
            check_out_source != "-"
            and
            check_out_source not in source_parts
        ):
            source_parts.append(check_out_source)

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

    return pd.DataFrame(final_data)


# ============================================================
# 11. EXCEL EXPORT
# ============================================================

def create_daily_excel(
    df_final,
    target_date
):

    """
    Compact LTR Excel.

    IMPORTANT:
    - No RTL
    - No right_to_left()
    - No set_print_area()
    - No unnecessary images
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
                "strings_to_urls": False,
                "constant_memory": True
            }
        }
    ) as writer:

        workbook = writer.book

        worksheet = workbook.add_worksheet(
            "Attendance"
        )

        writer.sheets["Attendance"] = worksheet

        # ====================================================
        # FORMATS
        # ====================================================

        title_format = workbook.add_format(
            {
                "bold": True,
                "font_size": 13,
                "font_color": "#FFFFFF",
                "bg_color": "#071426",
                "align": "center",
                "valign": "vcenter"
            }
        )

        subtitle_format = workbook.add_format(
            {
                "font_size": 9,
                "font_color": "#475569",
                "bg_color": "#F8FAFC",
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
                "border_color": "#CBD5E1",
                "text_wrap": True,
                "font_size": 10
            }
        )

        cell_format = workbook.add_format(
            {
                "align": "center",
                "valign": "vcenter",
                "border": 1,
                "border_color": "#E2E8F0",
                "font_size": 9
            }
        )

        # ====================================================
        # TITLE
        # ====================================================

        worksheet.merge_range(
            "A1:F1",
            "كشف الحضور اليومي — ALTURATH HR",
            title_format
        )

        worksheet.merge_range(
            "A2:F2",
            (
                f"تاريخ الحضور: "
                f"{target_date.strftime('%d %b %Y')}"
                f"    |    "
                f"تاريخ الانصراف: "
                f"{previous_date.strftime('%d %b %Y')}"
            ),
            subtitle_format
        )

        worksheet.set_row(0, 25)
        worksheet.set_row(1, 20)

        # ====================================================
        # HEADERS
        # ====================================================

        headers = [
            "ت\nNo.",
            "الاسم\nName",
            (
                "وقت الدخول\n"
                f"Check-In ({target_date.strftime('%d %b')})"
            ),
            (
                "وقت الانصراف\n"
                f"Check-Out ({previous_date.strftime('%d %b')})"
            ),
            "المصدر\nSource",
            "الحالة\nStatus"
        ]

        for col, header in enumerate(headers):

            worksheet.write(
                2,
                col,
                header,
                header_format
            )

        worksheet.set_row(2, 36)

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

        # ====================================================
        # WIDTHS
        # ====================================================

        worksheet.set_column("A:A", 6)
        worksheet.set_column("B:B", 30)
        worksheet.set_column("C:D", 19)
        worksheet.set_column("E:E", 23)
        worksheet.set_column("F:F", 18)

        # ====================================================
        # VIEW
        # ====================================================

        worksheet.freeze_panes(3, 0)

        worksheet.hide_gridlines(2)

        # Explicitly LTR / normal Excel direction.
        # DO NOT call worksheet.right_to_left()

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

    arabic.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    set_rtl(arabic)

    # ========================================================
    # LOGO
    # ========================================================

    logo_cell = (
        htable.rows[0]
        .cells[1]
        .paragraphs[0]
    )

    logo_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER

    logo_path = get_logo_path()

    if logo_path:

        try:

            with open(
                logo_path,
                "rb"
            ) as logo_file:

                logo_stream = BytesIO(
                    logo_file.read()
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

    english.alignment = WD_ALIGN_PARAGRAPH.LEFT

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

    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER

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

    body.alignment = WD_ALIGN_PARAGRAPH.RIGHT

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

    for i, text_value in enumerate(headers):

        cell = table.rows[0].cells[i]

        cell.text = text_value

        paragraph = cell.paragraphs[0]

        paragraph.alignment = (
            WD_ALIGN_PARAGRAPH.CENTER
        )

        set_rtl(paragraph)

    # ========================================================
    # ROWS
    # ========================================================

    for idx, row in df.iterrows():

        cells = table.add_row().cells

        cells[0].text = str(idx + 1)

        cells[1].text = str(
            row["Name"]
        )

        status_text = str(
            row["Status"]
        )

        if "Late" in status_text:

            cells[2].text = "تأخير"

        else:

            cells[2].text = "غياب"

        cells[3].text = str(
            row["Count"]
        )

        d_para = (
            cells[4]
            .paragraphs[0]
        )

        d_para.text = str(
            row["Dates_Str"]
        )

        d_para.runs[0].font.size = Pt(8)

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

    doc.add_paragraph("\n\n")

    signature = doc.add_paragraph(
        "م.م محمد زهير طالب النقيب\n"
        "مدير قسم الشؤون الادارية والموارد البشرية"
    )

    signature.alignment = WD_ALIGN_PARAGRAPH.LEFT

    set_rtl(signature)

    buffer = BytesIO()

    doc.save(buffer)

    buffer.seek(0)

    return buffer


# ============================================================
# 13. HERO
# ============================================================

def daily_hero():

    st.markdown(
        """
<div class="hero-card">

    <div class="hero-kicker">
        ALTURATH UNIVERSITY • HUMAN RESOURCES
    </div>

    <div class="hero-title">
        Daily Biometric Attendance
    </div>

    <div class="hero-text">
        سجل الحضور اليومي للموارد البشرية —
        دخول اليوم وخروج اليوم السابق وفق آلية
        التسليم المعتمدة لدى قسم الموارد البشرية.
    </div>

</div>
        """,
        unsafe_allow_html=True
    )


def exceptions_hero():

    st.markdown(
        """
<div class="hero-card">

    <div class="hero-kicker">
        ALTURATH UNIVERSITY • HUMAN RESOURCES
    </div>

    <div class="hero-title">
        Multi-Day Attendance Audit
    </div>

    <div class="hero-text">
        مراجعة حالات التأخير والغياب عبر تقارير
        الحضور اليومية.
    </div>

</div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 14. DAILY REPORT
# ============================================================

def run_daily_report_module():

    show_top_brand()

    daily_hero()

    show_sidebar_brand()

    # ========================================================
    # DATE
    # ========================================================

    use_today = st.sidebar.toggle(
        "Use Today",
        value=True
    )

    if use_today:

        target_date = date.today()

    else:

        target_date = st.sidebar.date_input(
            "Submission Date",
            value=date.today()
        )

    weekdays_ar = {
        "Monday": "الاثنين",
        "Tuesday": "الثلاثاء",
        "Wednesday": "الأربعاء",
        "Thursday": "الخميس",
        "Friday": "الجمعة",
        "Saturday": "السبت",
        "Sunday": "الأحد"
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
    # DATE CARD
    # ========================================================

    st.markdown(
        f"""
<div class="date-card">

    <div>
        <div class="date-main">
            {target_date.strftime('%A, %d %B %Y')}
        </div>

        <div class="date-sub">
            {current_weekday_ar}
        </div>
    </div>

    <div class="checkout-pill">
        Check-Out:
        {previous_date.strftime('%d %b %Y')}
    </div>

</div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # SIDEBAR FILES
    # ========================================================

    st.sidebar.markdown("### Attendance Sources")

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

    st.sidebar.markdown("### HR Data")

    f_weekly = st.sidebar.file_uploader(
        "Weekly Day-Off List",
        type=["xlsx", "xls"],
        key="weekly"
    )

    # ========================================================
    # PROCESS LOGS
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

        data = process_app(f_app)

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
    # NOTHING UPLOADED
    # ========================================================

    if not all_logs and not f_weekly:

        st.markdown(
            """
<div class="info-card">

<strong>Ready for attendance data.</strong><br>

Upload the biometric gate files from the
sidebar to generate the HR submission report.

</div>
            """,
            unsafe_allow_html=True
        )

        return

    # ========================================================
    # LOG DATA
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
    # BUILD
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

    c1, c2, c3, c4, c5 = st.columns(
        5,
        gap="small"
    )

    with c1:
        st.metric("Employees", total)

    with c2:
        st.metric("On Time", on_time)

    with c3:
        st.metric("Late", late)

    with c4:
        st.metric("Absence", absent)

    with c5:
        st.metric("Check-Outs", checkout_count)

    # ========================================================
    # LOGIC NOTE
    # ========================================================

    st.markdown(
        f"""
<div class="info-card">

<strong>HR Submission Logic</strong><br>

Check-In → <strong>{target_date.strftime('%d %b %Y')}</strong>
&nbsp;&nbsp; | &nbsp;&nbsp;

Check-Out → <strong>{previous_date.strftime('%d %b %Y')}</strong>
<br>

<strong>دخول(1)</strong> = Check-In
&nbsp;&nbsp; • &nbsp;&nbsp;

<strong>خروج(2)</strong> before 12:00 = Check-In
&nbsp;&nbsp; • &nbsp;&nbsp;

<strong>خروج(2)</strong> at/after 12:00 = Check-Out

</div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # TABLE
    # ========================================================

    st.markdown(
        """
<div class="section-heading">
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
        hide_index=True,
        height=min(
            600,
            max(
                260,
                55 + len(display_df) * 35
            )
        )
    )

    # ========================================================
    # EXPORT
    # ========================================================

    st.markdown(
        """
<div class="section-heading">
    HR Export
</div>
        """,
        unsafe_allow_html=True
    )

    excel_file = create_daily_excel(
        df_final,
        target_date
    )

    col1, col2 = st.columns(
        [1, 3],
        gap="small"
    )

    with col1:

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
            use_container_width=True
        )

    with col2:

        st.caption(
            "LTR Excel • "
            f"Check-In = {target_date.strftime('%d %b %Y')} • "
            f"Check-Out = {previous_date.strftime('%d %b %Y')}"
        )


# ============================================================
# 15. MULTI-DAY EXCEPTIONS
# ============================================================

def run_exceptions_module():

    show_top_brand()

    exceptions_hero()

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
<div class="info-card">

<strong>Multi-Day Audit</strong><br>

Upload the daily HR Excel reports.
The system will combine late and absence
records into one audit report.

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

                day_data["Report_Date"] = file_date

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
                f"Could not process {file.name}: {e}"
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
        """
<div class="section-heading">
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

    if st.button(
        "Generate Official Word Report",
        use_container_width=True
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
            use_container_width=True
        )


# ============================================================
# 16. SIDEBAR NAVIGATION
# ============================================================

st.sidebar.markdown(
    "### System Module"
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
# 17. RUN
# ============================================================

if app_mode == "Daily Report Tool":

    run_daily_report_module()

else:

    run_exceptions_module()


# ============================================================
# 18. FOOTER
# ============================================================

st.markdown(
    """
<div class="footer">
    ALTURATH HR BIOMETRICS SYSTEM • V2
</div>
    """,
    unsafe_allow_html=True
)
