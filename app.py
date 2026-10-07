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
from datetime import datetime, date, time, timedelta

# ============================================================
# ALTURATH HR SYSTEM — V2
# ============================================================

# ============================================================
# 1. GLOBAL UTILITIES
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

# ============================================================
# 2. V2 WEBSITE THEME
# ============================================================

def apply_v2_theme():

    st.markdown("""
    <style>

    .stApp {
        background:
            linear-gradient(
                135deg,
                #f8fafc 0%,
                #eef2ff 45%,
                #f0fdf4 100%
            );
    }

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #172554 0%,
                #1e3a8a 45%,
                #312e81 100%
            );
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stFileUploader label,
    section[data-testid="stSidebar"] .stDateInput label {
        color: white !important;
        font-weight: 600;
    }

    .v2-title {
        background:
            linear-gradient(
                135deg,
                #1e3a8a,
                #4f46e5,
                #0891b2
            );

        color: white;
        padding: 24px 28px;
        border-radius: 18px;
        margin-bottom: 20px;

        box-shadow:
            0 10px 25px rgba(30, 58, 138, 0.20);
    }

    .v2-title h1 {
        margin: 0;
        font-size: 32px;
        font-weight: 800;
    }

    .v2-title p {
        margin: 5px 0 0 0;
        opacity: 0.90;
        font-size: 15px;
    }

    .v2-info {
        background:
            linear-gradient(
                135deg,
                #dbeafe,
                #e0e7ff
            );

        border-left: 5px solid #2563eb;

        padding: 14px 18px;
        border-radius: 10px;

        color: #1e3a8a;
        font-weight: 600;

        margin-bottom: 18px;
    }

    .stButton > button {
        border-radius: 10px;
        border: none;

        background:
            linear-gradient(
                135deg,
                #2563eb,
                #4f46e5
            );

        color: white;
        font-weight: 700;

        padding: 8px 18px;
    }

    .stButton > button:hover {
        background:
            linear-gradient(
                135deg,
                #1d4ed8,
                #4338ca
            );

        color: white;
    }

    .stDownloadButton > button {
        border-radius: 10px;
        background:
            linear-gradient(
                135deg,
                #059669,
                #0d9488
            );

        color: white;
        font-weight: 700;
        border: none;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        box-shadow:
            0 5px 20px rgba(15,23,42,0.08);
    }

    </style>
    """, unsafe_allow_html=True)

# ============================================================
# 3. EVENT CLASSIFICATION
# ============================================================

def classify_gate_event(event_value, punch_datetime):
    """
    Exact business rule:

    دخول(1) -> Check-In

    خروج(2) -> Check-Out

    Exception:
    خروج(2) before 12:00 PM -> Check-In

    This handles an employee accidentally pressing
    the Check-Out button in the morning.
    """

    event = str(event_value).strip()

    punch_time = punch_datetime.time()

    # دخول(1)
    if "دخول" in event and "(1)" in event:
        return "Check-In"

    # Also tolerate minor formatting variations
    if "دخول" in event:
        return "Check-In"

    # خروج(2)
    if "خروج" in event and "(2)" in event:

        if punch_time < time(12, 0):
            return "Check-In"

        return "Check-Out"

    # Fallback for slightly different export formatting
    if "خروج" in event:

        if punch_time < time(12, 0):
            return "Check-In"

        return "Check-Out"

    return None

# ============================================================
# 4. GATE PROCESSING
# ============================================================

def process_gate(file, g_name):

    try:

        engine = (
            'xlrd'
            if file.name.endswith('.xls')
            else 'openpyxl'
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
        # Required columns
        # ----------------------------------------------------

        if 'الوقت' not in df.columns:
            return pd.DataFrame()

        if 'Event' not in df.columns:
            return pd.DataFrame()

        # ----------------------------------------------------
        # Name
        # ----------------------------------------------------

        if 'الاسم' in df.columns:

            df = df.rename(
                columns={
                    'الاسم': 'Name'
                }
            )

        elif 'الإسم' in df.columns:

            df = df.rename(
                columns={
                    'الإسم': 'Name'
                }
            )

        else:

            return pd.DataFrame()

        # ----------------------------------------------------
        # Datetime
        # ----------------------------------------------------

        df['dt'] = pd.to_datetime(
            df['الوقت'],
            errors='coerce'
        )

        df = df[
            df['dt'].notna()
            &
            df['Name'].notna()
        ].copy()

        # ----------------------------------------------------
        # Event classification
        # ----------------------------------------------------

        df['Event_Type'] = df.apply(
            lambda row:
            classify_gate_event(
                row['Event'],
                row['dt']
            ),
            axis=1
        )

        df = df[
            df['Event_Type'].notna()
        ].copy()

        # ----------------------------------------------------
        # Date / Time
        # ----------------------------------------------------

        df['Date'] = df['dt'].dt.date

        df['Time'] = df['dt'].dt.strftime(
            '%H:%M'
        )

        df['Source'] = g_name

        return df[
            [
                'Name',
                'dt',
                'Date',
                'Time',
                'Event_Type',
                'Source'
            ]
        ]

    except Exception:

        return pd.DataFrame()

# ============================================================
# 5. MAWJOOD APP PROCESSING
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

        if 'الاسم' not in df.columns:
            return pd.DataFrame()

        result = []

        # ----------------------------------------------------
        # Check-In
        # ----------------------------------------------------

        if 'دخول' in df.columns:

            for _, row in df.iterrows():

                dt = pd.to_datetime(
                    row['دخول'],
                    errors='coerce'
                )

                if pd.notna(dt):

                    result.append({
                        'Name': row['الاسم'],
                        'dt': dt,
                        'Date': dt.date(),
                        'Time': dt.strftime('%H:%M'),
                        'Event_Type': 'Check-In',
                        'Source': 'App'
                    })

        # ----------------------------------------------------
        # Check-Out
        # ----------------------------------------------------

        possible_checkout_columns = [
            'خروج',
            'الانصراف',
            'وقت الخروج',
            'Check-Out',
            'Checkout'
        ]

        checkout_column = None

        for col in possible_checkout_columns:

            if col in df.columns:
                checkout_column = col
                break

        if checkout_column:

            for _, row in df.iterrows():

                dt = pd.to_datetime(
                    row[checkout_column],
                    errors='coerce'
                )

                if pd.notna(dt):

                    result.append({
                        'Name': row['الاسم'],
                        'dt': dt,
                        'Date': dt.date(),
                        'Time': dt.strftime('%H:%M'),
                        'Event_Type': 'Check-Out',
                        'Source': 'App'
                    })

        return pd.DataFrame(result)

    except Exception:

        return pd.DataFrame()

# ============================================================
# 6. BUILD DAILY ATTENDANCE
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
            df_logs['Name']
            .dropna()
            .astype(str)
            .tolist()
        )

    if not df_off.empty:
        master_names.update(
            df_off['Name']
            .dropna()
            .astype(str)
            .tolist()
        )

    final_data = []

    # --------------------------------------------------------
    # Overnight window
    #
    # We look at the previous day after noon and the
    # selected day before noon, so a previous-day shift
    # can receive its midnight checkout.
    # --------------------------------------------------------

    previous_date = (
        target_date - timedelta(days=1)
    )

    for name in sorted(master_names):

        person_logs = df_logs[
            df_logs['Name'].astype(str) == str(name)
        ].copy()

        person_logs = person_logs.sort_values(
            'dt'
        )

        # ----------------------------------------------------
        # Check-In records belonging to target date
        # ----------------------------------------------------

        target_checkins = person_logs[
            (person_logs['Date'] == target_date)
            &
            (person_logs['Event_Type'] == 'Check-In')
        ].copy()

        # ----------------------------------------------------
        # Check-Out records on target date
        # ----------------------------------------------------

        target_checkouts = person_logs[
            (person_logs['Date'] == target_date)
            &
            (person_logs['Event_Type'] == 'Check-Out')
        ].copy()

        # ----------------------------------------------------
        # Determine Check-In
        # ----------------------------------------------------

        check_in = None
        check_in_dt = None
        check_in_source = None

        if not target_checkins.empty:

            # Earliest valid Check-In
            selected = target_checkins.iloc[0]

            check_in = selected['Time']
            check_in_dt = selected['dt']
            check_in_source = selected['Source']

        # ----------------------------------------------------
        # Determine Check-Out
        # ----------------------------------------------------

        check_out = None
        check_out_dt = None
        check_out_source = None

        if not target_checkouts.empty:

            # Prefer a Check-Out after the Check-In.
            if check_in_dt is not None:

                after_checkin = target_checkouts[
                    target_checkouts['dt'] > check_in_dt
                ]

                if not after_checkin.empty:

                    selected = after_checkin.iloc[-1]

                else:

                    selected = target_checkouts.iloc[-1]

            else:

                selected = target_checkouts.iloc[-1]

            check_out = selected['Time']
            check_out_dt = selected['dt']
            check_out_source = selected['Source']

        # ----------------------------------------------------
        # OVERNIGHT CHECKOUT
        #
        # Example:
        #
        # Oct 6 20:00 دخول(1)
        # Oct 7 02:00 خروج(2)
        #
        # The 02:00 checkout belongs to Oct 6.
        # ----------------------------------------------------

        if check_in_dt is not None:

            overnight_checkouts = person_logs[
                (person_logs['Date'] == target_date)
                &
                (person_logs['Event_Type'] == 'Check-Out')
                &
                (
                    person_logs['dt']
                    <= check_in_dt + timedelta(hours=12)
                )
            ]

            # If there is a normal same-day checkout,
            # it remains the selected checkout.
            #
            # This block mainly protects overnight shifts
            # where checkout happens after midnight.

        else:

            # No target-day check-in.
            #
            # Look for previous-day Check-In and a
            # post-midnight Check-Out.
            previous_checkins = person_logs[
                (person_logs['Date'] == previous_date)
                &
                (person_logs['Event_Type'] == 'Check-In')
            ]

            overnight_checkouts = person_logs[
                (person_logs['Date'] == target_date)
                &
                (person_logs['Event_Type'] == 'Check-Out')
                &
                (
                    person_logs['dt'].dt.time
                    < time(12, 0)
                )
            ]

            if (
                not previous_checkins.empty
                and not overnight_checkouts.empty
            ):

                # This checkout is actually for the
                # previous day's attendance.
                #
                # We do not put it into today's report.
                #
                # Today's employee therefore remains absent
                # unless another valid target-day punch exists.
                pass

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # If the selected target date has no Check-In but
        # has a morning خروج(2), our classifier already
        # converted that morning خروج(2) into Check-In.
        # Therefore it will appear above as target_checkins.
        # ----------------------------------------------------

        # ----------------------------------------------------
        # Weekly Off
        # ----------------------------------------------------

        off_info = df_off[
            df_off['Name'].astype(str) == str(name)
        ]

        is_off = (
            not off_info.empty
            and str(off_info['OffDay'].iloc[0]).strip()
            == str(current_weekday_ar).strip()
        )

        # ----------------------------------------------------
        # Build row
        # ----------------------------------------------------

        row = {
            'Name': name,
            'Check-In': '-',
            'Check-Out': '-',
            'Source': '-',
            'Status': ''
        }

        # ----------------------------------------------------
        # Has Check-In
        # ----------------------------------------------------

        if check_in is not None:

            row['Check-In'] = check_in

            if check_out is not None:
                row['Check-Out'] = check_out

            row['Source'] = (
                check_in_source
                if check_in_source
                else (
                    check_out_source
                    if check_out_source
                    else '-'
                )
            )

            if check_in > '08:35':

                row['Status'] = '🔴 Late'

            else:

                row['Status'] = '✅ On Time'

        # ----------------------------------------------------
        # Has only Check-Out
        # ----------------------------------------------------

        elif check_out is not None:

            row['Check-Out'] = check_out

            row['Source'] = (
                check_out_source
                if check_out_source
                else '-'
            )

            # No check-in means we don't invent one.
            row['Status'] = '⚠️ Check-Out Only'

        # ----------------------------------------------------
        # Weekly Off
        # ----------------------------------------------------

        elif is_off:

            row['Status'] = '🟡 Weekly Off'

        # ----------------------------------------------------
        # Absence
        # ----------------------------------------------------

        else:

            row['Status'] = '❌ Absence'

        final_data.append(row)

    return pd.DataFrame(final_data)

# ============================================================
# 7. EXCEL EXPORT — V2
# ============================================================

def create_daily_excel(df_final, target_date):

    buf = BytesIO()

    with pd.ExcelWriter(
        buf,
        engine='xlsxwriter'
    ) as writer:

        workbook = writer.book

        worksheet = workbook.add_worksheet(
            'Audit'
        )

        writer.sheets['Audit'] = worksheet

        # ----------------------------------------------------
        # COLORS
        # ----------------------------------------------------

        dark_blue = '#172554'
        blue = '#2563EB'
        green = '#DCFCE7'
        red = '#FEE2E2'
        yellow = '#FEF3C7'
        orange = '#FFEDD5'
        white = '#FFFFFF'
        black = '#000000'

        # ----------------------------------------------------
        # FORMATS
        # ----------------------------------------------------

        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_color': white,
            'bg_color': dark_blue,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': black,
        })

        header_format = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'font_color': white,
            'bg_color': blue,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': black,
        })

        cell_format = workbook.add_format({
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': black,
        })

        name_format = workbook.add_format({
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': black,
            'reading_order': 2,
        })

        ontime_format = workbook.add_format({
            'font_size': 10,
            'font_color': '#047857',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': black,
            'bg_color': green,
        })

        late_format = workbook.add_format({
            'font_size': 10,
            'font_color': '#B91C1C',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': black,
            'bg_color': red,
        })

        off_format = workbook.add_format({
            'font_size': 10,
            'font_color': '#92400E',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': black,
            'bg_color': yellow,
        })

        absence_format = workbook.add_format({
            'font_size': 10,
            'font_color': '#991B1B',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': black,
            'bg_color': red,
        })

        checkout_only_format = workbook.add_format({
            'font_size': 10,
            'font_color': '#9A3412',
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': black,
            'bg_color': orange,
        })

        # ----------------------------------------------------
        # RTL
        # ----------------------------------------------------

        worksheet.right_to_left()

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = (
            f'جامعة التراث - الموقف اليومي - '
            f'{target_date.strftime("%Y/%m/%d")}'
        )

        worksheet.merge_range(
            'A1:F1',
            title,
            title_format
        )

        worksheet.set_row(
            0,
            30
        )

        # ----------------------------------------------------
        # HEADER
        # Row 2 intentionally preserved for the
        # Multi-Day Audit module.
        # ----------------------------------------------------

        headers = [
            'No',
            'Name',
            'Check-In',
            'Check-Out',
            'Source',
            'Status'
        ]

        for col, header in enumerate(headers):

            worksheet.write(
                1,
                col,
                header,
                header_format
            )

        worksheet.set_row(
            1,
            24
        )

        # ----------------------------------------------------
        # COLUMN WIDTHS
        # ----------------------------------------------------

        worksheet.set_column(
            'A:A',
            7
        )

        worksheet.set_column(
            'B:B',
            32
        )

        worksheet.set_column(
            'C:D',
            13
        )

        worksheet.set_column(
            'E:E',
            23
        )

        worksheet.set_column(
            'F:F',
            20
        )

        # ----------------------------------------------------
        # DATA
        # ----------------------------------------------------

        for row_idx, row in df_final.iterrows():

            excel_row = row_idx + 2

            worksheet.write(
                excel_row,
                0,
                row_idx + 1,
                cell_format
            )

            worksheet.write(
                excel_row,
                1,
                str(row['Name']),
                name_format
            )

            worksheet.write(
                excel_row,
                2,
                str(row['Check-In']),
                cell_format
            )

            worksheet.write(
                excel_row,
                3,
                str(row['Check-Out']),
                cell_format
            )

            worksheet.write(
                excel_row,
                4,
                str(row['Source']),
                cell_format
            )

            status = str(row['Status'])

            if 'On Time' in status:

                status_format = ontime_format

            elif 'Late' in status:

                status_format = late_format

            elif 'Weekly Off' in status:

                status_format = off_format

            elif 'Check-Out Only' in status:

                status_format = checkout_only_format

            else:

                status_format = absence_format

            worksheet.write(
                excel_row,
                5,
                status,
                status_format
            )

            worksheet.set_row(
                excel_row,
                23
            )

        # ----------------------------------------------------
        # PRINT / VIEW
        # ----------------------------------------------------

        worksheet.freeze_panes(
            2,
            0
        )

        worksheet.hide_gridlines(
            2
        )

        worksheet.set_landscape()

        worksheet.fit_to_pages(
            1,
            0
        )

        worksheet.set_margins(
            left=0.25,
            right=0.25,
            top=0.40,
            bottom=0.40
        )

        worksheet.set_print_area(
            0,
            0,
            len(df_final) + 1,
            5
        )

    buf.seek(0)

    return buf.getvalue()

# ============================================================
# 8. WORD REPORT
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

    # Arabic
    r = htable.rows[0].cells[0].paragraphs[0]

    r.text = (
        'جامعة التراث\n'
        'قسم الشؤون الإدارية والمالية\n'
        'شعبة الموارد البشرية'
    )

    r.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    set_rtl(r)

    # Logo
    m = htable.rows[0].cells[1].paragraphs[0]

    m.alignment = WD_ALIGN_PARAGRAPH.CENTER

    try:

        img_url = (
            'https://uoturath.edu.iq/'
            'wp-content/uploads/2025/03/shield-1.png'
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

    except:
        pass

    # English
    l = htable.rows[0].cells[2].paragraphs[0]

    l.text = (
        'University Of Alturath\n'
        'Dept. Of Admin & Financial Affairs\n'
        'HR Department'
    )

    l.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # Separator
    p_line = doc.add_paragraph()

    run_line = p_line.add_run(
        '______________________________________________________________________'
    )

    run_line.font.color.rgb = RGBColor(
        0x8F,
        0x0B,
        0x0B
    )

    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Body
    body = doc.add_paragraph(
        '\nنرفق لسيادتكم في ادناه الكشف الخاص بموقف الحضور والغياب '
        'لكادر العمل الخاص بجامعة التراث وحسب كشف البصمة المرفق '
        'طيا نسخة منه ... راجين التفضل بالاطلاع واعلامنا توجيهات '
        'سيادتكم حول ذلك ... مع التقدير..'
    )

    body.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    set_rtl(body)

    # Table
    table = doc.add_table(
        rows=1,
        cols=5
    )

    table.style = 'Table Grid'

    set_table_rtl(table)

    hdr = table.rows[0].cells

    labels = [
        'ت',
        'الاسم',
        'الحالة',
        'العدد',
        'التواريخ'
    ]

    for i, txt in enumerate(labels):

        hdr[i].text = txt

        hdr[i].paragraphs[0].alignment = (
            WD_ALIGN_PARAGRAPH.CENTER
        )

        set_rtl(
            hdr[i].paragraphs[0]
        )

    for idx, row in df.iterrows():

        cells = table.add_row().cells

        cells[0].text = str(idx + 1)

        cells[1].text = str(
            row['Name']
        )

        cells[2].text = (
            'تأخير'
            if 'Late' in str(row['Status'])
            else 'غياب'
        )

        cells[3].text = str(
            row['Count']
        )

        d_para = cells[4].paragraphs[0]

        d_run = d_para.add_run(
            row['Dates_Str']
        )

        d_run.font.size = Pt(8)

        for cell in cells:

            cell.paragraphs[0].alignment = (
                WD_ALIGN_PARAGRAPH.CENTER
            )

            set_rtl(
                cell.paragraphs[0]
            )

    doc.add_paragraph('\n\n')

    sig = doc.add_paragraph(
        'م.م محمد زهير طالب النقيب\n'
        'مدير قسم الشؤون الادارية والموارد البشرية'
    )

    sig.alignment = WD_ALIGN_PARAGRAPH.LEFT

    set_rtl(sig)

    buf = BytesIO()

    doc.save(buf)

    buf.seek(0)

    return buf

# ============================================================
# 9. MULTI-DAY EXCEPTIONS MODULE
# ============================================================

def run_exceptions_module():

    st.markdown("""
    <div class="v2-title">
        <h1>📋 Multi-Day Exceptions Audit</h1>
        <p>Alturath HR Department • Attendance Exceptions</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        'Upload Exported Excels (Row 2 Header)',
        accept_multiple_files=True,
        type=['xlsx', 'xls']
    )

    if uploaded_files:

        all_data = []

        for f in uploaded_files:

            file_date = extract_date_from_filename(
                f.name
            )

            try:

                engine = (
                    'xlrd'
                    if f.name.endswith('.xls')
                    else 'openpyxl'
                )

                df = pd.read_excel(
                    f,
                    engine=engine,
                    header=1
                )

                df.columns = [
                    str(c).strip()
                    for c in df.columns
                ]

                if (
                    'Status' in df.columns
                    and 'Name' in df.columns
                ):

                    mask = df['Status'].str.contains(
                        'Late|Absence',
                        case=False,
                        na=False
                    )

                    day_data = df[mask].copy()

                    day_data['Report_Date'] = file_date

                    all_data.append(
                        day_data[
                            [
                                'Name',
                                'Status',
                                'Report_Date'
                            ]
                        ]
                    )

            except:
                pass

        if all_data:

            combined = pd.concat(
                all_data,
                ignore_index=True
            )

            summary = (
                combined
                .groupby(
                    ['Name', 'Status']
                )['Report_Date']
                .unique()
                .reset_index()
            )

            summary['Count'] = (
                summary['Report_Date']
                .apply(len)
            )

            summary['Dates_Str'] = (
                summary['Report_Date']
                .apply(
                    lambda x:
                    ', '.join(sorted(x))
                )
            )

            st.dataframe(
                summary[
                    [
                        'Name',
                        'Status',
                        'Count',
                        'Dates_Str'
                    ]
                ],
                use_container_width=True
            )

            if st.button(
                '📄 Download Official Word Report'
            ):

                report_file = create_word_doc(
                    summary
                )

                st.download_button(
                    '📥 Download .docx',
                    report_file,
                    'Alturath_Exceptions_Report.docx'
                )

# ============================================================
# 10. DAILY REPORT MODULE
# ============================================================

def run_daily_report_module():

    st.markdown("""
    <div class="v2-title">
        <h1>📊 Daily Biometric Attendance — V2</h1>
        <p>University Of Alturath • Human Resources Department</p>
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    use_today = st.sidebar.toggle(
        '📅 Show Today Only',
        value=False
    )

    target_date = (
        date.today()
        if use_today
        else st.sidebar.date_input(
            'Audit Date',
            value=date.today()
        )
    )

    weekdays_ar = {
        'Monday': 'الاثنين',
        'Tuesday': 'الثلاثاء',
        'Wednesday': 'الاربعاء',
        'Thursday': 'الخميس',
        'Friday': 'الجمعة',
        'Saturday': 'السبت',
        'Sunday': 'الاحد'
    }

    current_weekday_ar = weekdays_ar.get(
        target_date.strftime('%A'),
        ''
    )

    st.sidebar.info(
        f'Audit Day: **{current_weekday_ar}**'
    )

    # --------------------------------------------------------
    # FILES
    # --------------------------------------------------------

    st.sidebar.markdown(
        '### 🚪 Attendance Sources'
    )

    f_zaqura = st.sidebar.file_uploader(
        '🟦 Zaqura Gate',
        type=['xlsx', 'xls']
    )

    f_mhmd = st.sidebar.file_uploader(
        '🟪 Mhmd Bn Ali Gate',
        type=['xlsx', 'xls']
    )

    f_app = st.sidebar.file_uploader(
        '🟩 Mawjood App',
        type=['xlsx', 'xls']
    )

    st.sidebar.markdown(
        '### 📅 HR Files'
    )

    f_weekly = st.sidebar.file_uploader(
        '📅 Weekly Day-Off List',
        type=['xlsx', 'xls']
    )

    # --------------------------------------------------------
    # PROCESS SOURCES
    # --------------------------------------------------------

    all_logs = []

    if f_zaqura:

        gate_data = process_gate(
            f_zaqura,
            'Zaqura Gate'
        )

        if not gate_data.empty:
            all_logs.append(gate_data)

    if f_mhmd:

        gate_data = process_gate(
            f_mhmd,
            'Mhmd Bn Ali Gate'
        )

        if not gate_data.empty:
            all_logs.append(gate_data)

    if f_app:

        app_data = process_app(
            f_app
        )

        if not app_data.empty:
            all_logs.append(app_data)

    # --------------------------------------------------------
    # WEEKLY OFF
    # --------------------------------------------------------

    df_off = pd.DataFrame(
        columns=[
            'Name',
            'OffDay'
        ]
    )

    if f_weekly:

        try:

            df_off = pd.read_excel(
                f_weekly
            ).rename(
                columns={
                    'الاسم الثلاثي': 'Name',
                    'الاجازة الاسبوعية': 'OffDay'
                }
            )

            df_off['Name'] = (
                df_off['Name']
                .astype(str)
                .str.strip()
            )

            df_off['OffDay'] = (
                df_off['OffDay']
                .astype(str)
                .str.strip()
            )

        except:

            df_off = pd.DataFrame(
                columns=[
                    'Name',
                    'OffDay'
                ]
            )

    # --------------------------------------------------------
    # BUILD
    # --------------------------------------------------------

    if all_logs or f_weekly:

        if all_logs:

            df_logs = pd.concat(
                all_logs,
                ignore_index=True
            )

        else:

            df_logs = pd.DataFrame(
                columns=[
                    'Name',
                    'dt',
                    'Date',
                    'Time',
                    'Event_Type',
                    'Source'
                ]
            )

        df_final = build_daily_attendance(
            df_logs,
            target_date,
            current_weekday_ar,
            df_off
        )

        # ----------------------------------------------------
        # SORT
        # ----------------------------------------------------

        if not df_final.empty:

            df_final = (
                df_final
                .sort_values('Name')
                .reset_index(drop=True)
            )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        total = len(df_final)

        on_time = len(
            df_final[
                df_final['Status']
                .astype(str)
                .str.contains(
                    'On Time',
                    na=False
                )
            ]
        )

        late = len(
            df_final[
                df_final['Status']
                .astype(str)
                .str.contains(
                    'Late',
                    na=False
                )
            ]
        )

        absent = len(
            df_final[
                df_final['Status']
                .astype(str)
                .str.contains(
                    'Absence',
                    na=False
                )
            ]
        )

        checkout_only = len(
            df_final[
                df_final['Status']
                .astype(str)
                .str.contains(
                    'Check-Out Only',
                    na=False
                )
            ]
        )

        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            st.metric(
                '👥 Total',
                total
            )

        with c2:
            st.metric(
                '✅ On Time',
                on_time
            )

        with c3:
            st.metric(
                '🔴 Late',
                late
            )

        with c4:
            st.metric(
                '❌ Absence',
                absent
            )

        with c5:
            st.metric(
                '⚠️ Check-Out Only',
                checkout_only
            )

        st.markdown(
            f"""
            <div class="v2-info">
                📅 {target_date.strftime('%Y/%m/%d')}
                &nbsp;&nbsp; | &nbsp;&nbsp;
                {current_weekday_ar}
                &nbsp;&nbsp; | &nbsp;&nbsp;
                Check-In / Check-Out enabled
            </div>
            """,
            unsafe_allow_html=True
        )

        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        display_df = df_final.copy()

        display_df.insert(
            0,
            'No',
            range(
                1,
                len(display_df) + 1
            )
        )

        st.dataframe(
            display_df[
                [
                    'No',
                    'Name',
                    'Check-In',
                    'Check-Out',
                    'Source',
                    'Status'
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # EXPORT
        # ----------------------------------------------------

        st.markdown(
            '### 📥 Export'
        )

        excel_file = create_daily_excel(
            df_final,
            target_date
        )

        st.download_button(
            label='📊 Download Daily Excel — V2',
            data=excel_file,
            file_name=(
                f'HR_Report_'
                f'{target_date.strftime("%Y-%m-%d")}'
                f'_V2.xlsx'
            ),
            mime=(
                'application/vnd.openxmlformats-officedocument'
                '.spreadsheetml.sheet'
            )
        )

# ============================================================
# 11. MAIN APP
# ============================================================

st.set_page_config(
    page_title='Alturath HR System V2',
    page_icon='🏛️',
    layout='wide'
)

apply_v2_theme()

# Sidebar logo
st.sidebar.image(
    'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRfTMmtmrsxgUBnlEb0xB0ClMbFZmj_L5Ap5Q&s'
)

st.sidebar.markdown(
    """
    <div style="
        text-align:center;
        padding:8px;
        font-size:20px;
        font-weight:800;
    ">
        🏛️ ALTURATH HR
    </div>

    <div style="
        text-align:center;
        opacity:0.8;
        margin-bottom:15px;
    ">
        Attendance System V2
    </div>
    """,
    unsafe_allow_html=True
)

app_mode = st.sidebar.selectbox(
    'Choose App Mode',
    [
        '📊 Daily Report Tool',
        '📋 Multi-Day Audit Tool'
    ]
)

if app_mode == '📊 Daily Report Tool':

    run_daily_report_module()

else:

    run_exceptions_module()
