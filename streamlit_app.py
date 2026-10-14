"""Browser interface for the Digital Evidence Integrity system."""

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import streamlit as st

from audit import get_activity_summary, get_custody_log, get_recent_activity
from database import DB_PATH, get_connection, initialize_database
from evidence import get_all_evidence, get_evidence_by_id, register_evidence_record
from report import REPORTS_DIR, create_forensic_report
from utils import format_file_size
from verify import verify_evidence_record


st.set_page_config(
    page_title="Evidence integrity console",
    page_icon=":material/shield:",
    layout="wide",
)

initialize_database()

st.html(
    """
    <style>
    @keyframes evidence-gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes evidence-nav-arrive {
        from { opacity: 0; transform: translateY(-8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes evidence-arrive {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes evidence-scan {
        0% { transform: translateX(-120%); opacity: 0; }
        20% { opacity: .7; }
        80% { opacity: .7; }
        100% { transform: translateX(240%); opacity: 0; }
    }
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 88% 4%, rgba(133, 194, 235, .23), transparent 38%),
            radial-gradient(ellipse at 2% 38%, rgba(177, 194, 239, .19), transparent 40%),
            linear-gradient(135deg, #f5faff, #f5f7fd 58%, #f1faf8);
    }
    .block-container {
        padding-top: 2.7rem;
    }
    .evidence-nav-brand {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-top: .35rem;
        padding: .8rem 1rem 1rem;
        border: 1px solid #d9e8f0;
        border-radius: 16px;
        background: linear-gradient(110deg, rgba(231, 244, 253, .94), rgba(239, 239, 253, .9) 58%, rgba(232, 248, 244, .9));
        box-shadow: 0 8px 24px rgba(61, 105, 139, .07);
        animation: evidence-nav-arrive .45s ease-out both;
    }
    .evidence-brand-title {
        color: #16415b;
        font-size: 1.45rem;
        font-weight: 750;
        letter-spacing: -.035em;
    }
    .evidence-brand-subtitle {
        margin-top: .16rem;
        color: #5d778b;
        font-size: .88rem;
    }
    .evidence-system-tag {
        display: inline-flex;
        align-items: center;
        gap: .45rem;
        padding: .42rem .7rem;
        border: 1px solid #cfe2ec;
        border-radius: 999px;
        background: rgba(255, 255, 255, .68);
        color: #426b7c;
        font-size: .67rem;
        font-weight: 700;
        letter-spacing: .08em;
        white-space: nowrap;
    }
    .evidence-system-tag span {
        width: .48rem;
        height: .48rem;
        border-radius: 50%;
        background: #39a77a;
        box-shadow: 0 0 0 3px rgba(57, 167, 122, .13);
    }
    div[data-testid="stRadio"] {
        margin: .65rem 0 1.15rem;
        animation: evidence-nav-arrive .55s ease-out both;
    }
    div[data-testid="stRadio"] div[data-testid="stRadioGroup"] {
        display: flex;
        flex-wrap: wrap;
        gap: .35rem;
        padding: .35rem;
        border: 1px solid #dbe7ef;
        border-radius: 14px;
        background: rgba(231, 240, 249, .8);
    }
    div[data-testid="stRadio"] label[data-testid="stRadioOption"] {
        padding: .48rem .82rem;
        border: 1px solid transparent;
        border-radius: 10px;
        color: #52697d;
        transition: background .2s ease, color .2s ease, border-color .2s ease, transform .2s ease;
    }
    div[data-testid="stRadio"] label[data-testid="stRadioOption"] > div > div:first-child {
        display: none;
    }
    div[data-testid="stRadio"] label[data-testid="stRadioOption"]:hover {
        transform: translateY(-1px);
        border-color: #d6e6f1;
        background: rgba(255, 255, 255, .75);
        color: #1e6e9f;
    }
    div[data-testid="stRadio"] label[data-testid="stRadioOption"]:has(input:checked) {
        border-color: #c9dfef;
        background: linear-gradient(120deg, #d9efff, #e6e5ff);
        color: #155f8e;
        font-weight: 650;
    }
    .evidence-hero {
        position: relative;
        overflow: hidden;
        padding: 1.55rem 1.7rem;
        margin: .15rem 0 1.1rem;
        border: 1px solid rgba(113, 159, 193, .34);
        border-radius: 18px;
        background: linear-gradient(115deg, #e8f5ff, #f0f1ff, #e6f7f3, #edf6ff);
        background-size: 240% 240%;
        animation: evidence-gradient 18s ease infinite, evidence-arrive .55s ease-out both;
        box-shadow: 0 12px 34px rgba(41, 78, 105, .1);
    }
    .evidence-hero:after {
        content: "";
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        width: 16%;
        background: linear-gradient(90deg, transparent, rgba(59, 151, 203, .09), transparent);
        animation: evidence-scan 8s ease-in-out infinite;
        pointer-events: none;
    }
    .evidence-eyebrow {
        color: #2679a8;
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .17em;
        text-transform: uppercase;
    }
    .evidence-title {
        margin: .35rem 0 .3rem;
        color: #17344c;
        font-size: clamp(1.55rem, 3.3vw, 2.35rem);
        font-weight: 700;
        letter-spacing: -.035em;
    }
    .evidence-subtitle {
        margin: 0;
        color: #62798d;
        font-size: .98rem;
    }
    div[data-testid="stMetric"] {
        padding: .9rem 1rem;
        border: 1px solid #d5e5ee;
        border-radius: 14px;
        background: linear-gradient(135deg, rgba(232, 245, 255, .96), rgba(240, 242, 255, .94) 58%, rgba(234, 248, 244, .96));
        box-shadow: 0 7px 22px rgba(41, 78, 105, .05);
        animation: evidence-arrive .55s ease-out both;
        transition: transform .2s ease, box-shadow .2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 11px 26px rgba(41, 78, 105, .1);
    }
    @media (max-width: 700px) {
        .evidence-nav-brand {
            align-items: flex-start;
            flex-direction: column;
        }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *:before, *:after {
            animation-duration: .01ms !important;
            animation-iteration-count: 1 !important;
        }
    }
    </style>
    """
)


def records_as_dicts(records):
    return [dict(record) for record in records]


def render_hero(eyebrow: str, title: str, subtitle: str):
    st.html(
        f"""
        <section class="evidence-hero">
            <div class="evidence-eyebrow">{eyebrow}</div>
            <div class="evidence-title">{title}</div>
            <p class="evidence-subtitle">{subtitle}</p>
        </section>
        """
    )


def latest_verification(logs):
    for item in reversed(logs):
        if item["action"] == "Verified Integrity":
            return f'{item["result"]} · {item["timestamp"]}'
    return "Not yet verified"


st.html(
    """
    <header class="evidence-nav-brand">
        <div>
            <div class="evidence-brand-title">Evidence desk</div>
            <div class="evidence-brand-subtitle">Digital evidence integrity &amp; chain of custody</div>
        </div>
        <div class="evidence-system-tag"><span></span>LOCAL SYSTEM · SQLITE</div>
    </header>
    """
)
selected_page = st.radio(
    "Workspace",
    [
        "Overview",
        "Register evidence",
        "Evidence records",
        "Verify integrity",
        "Custody trail",
        "Forensic reports",
        "Database",
    ],
    horizontal=True,
    label_visibility="collapsed",
)


if selected_page == "Overview":
    render_hero(
        "Evidence operations",
        "Integrity, at a glance.",
        "Register files, verify SHA-256 fingerprints, and follow every custody event.",
    )
    evidence_records = get_all_evidence()
    activity = get_activity_summary()
    recent = records_as_dicts(get_recent_activity(8))
    metrics = st.columns(4)
    metrics[0].metric("Evidence items", len(evidence_records))
    metrics[1].metric("Integrity checks", activity["verified"] + activity["compromised"])
    metrics[2].metric("Verified", activity["verified"])
    metrics[3].metric("Compromised", activity["compromised"])

    st.subheader("Recent custody activity")
    if recent:
        st.dataframe(
            [
                {
                    "Date/time": item["timestamp"],
                    "Evidence ID": item["evidence_id"],
                    "Investigator": item["investigator"],
                    "Action": item["action"],
                    "Result": item["result"],
                }
                for item in recent
            ],
            hide_index=True,
        )
    else:
        st.info("No activity yet. Register a file to begin its custody trail.")

    st.caption(f"Active evidence database: `{DB_PATH}`")


elif selected_page == "Register evidence":
    render_hero(
        "New acquisition",
        "Register evidence",
        "Upload a file to create a local archive copy, calculate its SHA-256 hash, and start its custody record.",
    )
    with st.container(border=True):
        with st.form("register-evidence", clear_on_submit=True):
            upload = st.file_uploader(
                "Evidence file",
                help="The uploaded file is copied into this project's evidence_files folder. Your source file is not modified.",
            )
            investigator = st.text_input("Investigator name")
            case_id = st.text_input("Case ID")
            submitted = st.form_submit_button(
                "Register and calculate SHA-256",
                type="primary",
                icon=":material/fingerprint:",
            )

    if submitted:
        if upload is None:
            st.error("Choose an evidence file before registering.")
        elif not investigator.strip() or not case_id.strip():
            st.error("Enter both an investigator name and a case ID.")
        else:
            safe_name = Path(upload.name.replace("\\", "/")).name
            if not safe_name:
                st.error("The uploaded file must have a valid file name.")
            else:
                archive_dir = Path(__file__).parent / "evidence_files"
                archive_dir.mkdir(parents=True, exist_ok=True)
                archived_path = archive_dir / f"{uuid4().hex}_{safe_name}"
                try:
                    archived_path.write_bytes(upload.getbuffer())
                except OSError as error:
                    st.error(f"Could not archive the uploaded file: {error}")
                else:
                    try:
                        with st.status("Registering evidence...", expanded=True) as status:
                            st.write("Archived a separate copy; calculating SHA-256.")
                            record = register_evidence_record(
                                str(archived_path),
                                investigator.strip(),
                                case_id.strip(),
                            )
                            status.update(
                                label="Evidence registered",
                                state="complete",
                                expanded=False,
                            )
                        st.success(f"Registered as {record['evidence_id']}.")
                        st.json(
                            {
                                "Evidence ID": record["evidence_id"],
                                "Case ID": record["case_id"],
                                "File": record["file_name"],
                                "Size": format_file_size(record["file_size"]),
                                "SHA-256": record["sha256_hash"],
                                "Stored copy": record["file_path"],
                            }
                        )
                    except Exception as error:
                        st.error(f"Registration did not complete: {error}")
                        st.caption(
                            "The uploaded archive copy was retained in case the database write completed before the error."
                        )


elif selected_page == "Evidence records":
    render_hero(
        "Evidence library",
        "Registered records",
        "Search stored items and inspect metadata, hashes, and latest verification status.",
    )
    records = records_as_dicts(get_all_evidence())
    if not records:
        st.info("No evidence has been registered yet.")
    else:
        query = st.text_input(
            "Search records",
            placeholder="Evidence ID, case ID, file name, or investigator",
            icon=":material/search:",
        )
        filtered = [
            item
            for item in records
            if query.casefold()
            in " ".join(
                str(item[key])
                for key in ("evidence_id", "case_id", "file_name", "investigator")
            ).casefold()
        ]
        st.dataframe(
            [
                {
                    "Evidence ID": item["evidence_id"],
                    "Case ID": item["case_id"],
                    "File name": item["file_name"],
                    "Investigator": item["investigator"],
                    "Size": format_file_size(item["file_size"]),
                    "Collected": item["collected_date"],
                }
                for item in filtered
            ],
            hide_index=True,
        )
        if filtered:
            selected_id = st.selectbox(
                "Evidence details",
                [item["evidence_id"] for item in filtered],
            )
            record = get_evidence_by_id(selected_id)
            logs = get_custody_log(selected_id)
            left, right = st.columns(2)
            with left:
                with st.container(border=True):
                    st.subheader(record["file_name"])
                    st.caption(f'{record["evidence_id"]} · Case {record["case_id"]}')
                    st.write(f'**Investigator:** {record["investigator"]}')
                    st.write(f'**Size:** {format_file_size(record["file_size"])}')
                    st.write(f'**Collected:** {record["collected_date"]}')
                    st.write(f'**Latest verification:** {latest_verification(logs)}')
            with right:
                with st.container(border=True):
                    st.markdown("**SHA-256 fingerprint**")
                    st.code(record["sha256_hash"], language=None)
                    st.caption(record["file_path"])


elif selected_page == "Verify integrity":
    render_hero(
        "Verification",
        "Check file integrity",
        "Recalculate the archived file's SHA-256 hash and compare it with the original registration fingerprint.",
    )
    records = records_as_dicts(get_all_evidence())
    if not records:
        st.info("Register evidence before running an integrity check.")
    else:
        with st.container(border=True):
            with st.form("verify-evidence"):
                evidence_ids = [item["evidence_id"] for item in records]
                evidence_id = st.selectbox("Evidence ID", evidence_ids)
                investigator = st.text_input("Investigator performing this check")
                submitted = st.form_submit_button(
                    "Verify integrity",
                    type="primary",
                    icon=":material/fingerprint:",
                )
        if submitted:
            if not investigator.strip():
                st.error("Enter the investigator performing the check.")
            else:
                try:
                    with st.status("Recalculating SHA-256...", expanded=True) as status:
                        result = verify_evidence_record(
                            evidence_id,
                            investigator.strip(),
                        )
                        status.update(
                            label="Verification recorded",
                            state="complete",
                            expanded=False,
                        )
                    if result["result"] == "Integrity Verified":
                        st.success(result["result"])
                    elif result["result"] == "Integrity Compromised":
                        st.error("Warning: the evidence file has been modified.")
                    else:
                        st.warning(result["remarks"])
                    if result["current_hash"]:
                        st.write("**Stored hash**")
                        st.code(result["stored_hash"], language=None)
                        st.write("**Recalculated hash**")
                        st.code(result["current_hash"], language=None)
                    st.caption(result["remarks"])
                except LookupError as error:
                    st.error(str(error))


elif selected_page == "Custody trail":
    render_hero(
        "Audit history",
        "Chain of custody",
        "Review a complete chronological record of registration and integrity checks.",
    )
    records = records_as_dicts(get_all_evidence())
    if not records:
        st.info("No evidence or custody events to display.")
    else:
        evidence_id = st.selectbox(
            "Select evidence",
            [item["evidence_id"] for item in records],
            key="custody-evidence",
        )
        logs = records_as_dicts(get_custody_log(evidence_id))
        if logs:
            st.dataframe(
                [
                    {
                        "Date/time": item["timestamp"],
                        "Audit ID": item["audit_id"],
                        "Investigator": item["investigator"],
                        "Action": item["action"],
                        "Result": item["result"],
                        "Remarks": item["remarks"] or "-",
                    }
                    for item in logs
                ],
                hide_index=True,
            )
        else:
            st.info("There are no custody events for this evidence item.")


elif selected_page == "Forensic reports":
    render_hero(
        "Export",
        "Forensic reports",
        "Generate a PDF containing evidence details, verification status, and the complete custody history.",
    )
    records = records_as_dicts(get_all_evidence())
    if not records:
        st.info("Register evidence before generating a report.")
    else:
        evidence_id = st.selectbox(
            "Evidence ID",
            [item["evidence_id"] for item in records],
            key="report-evidence",
        )
        if st.button(
            "Generate report",
            type="primary",
            icon=":material/picture_as_pdf:",
        ):
            try:
                report_path = create_forensic_report(evidence_id)
                st.session_state["generated_report_path"] = str(report_path)
                st.success("The forensic report is ready.")
            except Exception as error:
                st.error(f"Could not generate the report: {error}")

        generated_path = st.session_state.get("generated_report_path")
        if generated_path and Path(generated_path).is_file():
            report_file = Path(generated_path)
            st.caption(f"Saved to `{report_file}`")
            st.download_button(
                "Download PDF report",
                data=report_file.read_bytes(),
                file_name=report_file.name,
                mime="application/pdf",
                icon=":material/download:",
            )
        existing_reports = sorted(
            REPORTS_DIR.glob("Forensic_Report_*.pdf"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if existing_reports:
            with st.expander("Previously generated reports"):
                st.dataframe(
                    [
                        {
                            "Report": path.name,
                            "Created": datetime.fromtimestamp(
                                path.stat().st_mtime
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                            "Size": format_file_size(path.stat().st_size),
                        }
                        for path in existing_reports
                    ],
                    hide_index=True,
                )


elif selected_page == "Database":
    render_hero(
        "Storage",
        "SQLite database",
        "Inspect the same local evidence and audit tables used by both the browser and CLI applications.",
    )
    connection = get_connection()
    try:
        evidence_count = connection.execute(
            "SELECT COUNT(*) FROM evidence"
        ).fetchone()[0]
        audit_count = connection.execute(
            "SELECT COUNT(*) FROM audit_log"
        ).fetchone()[0]
        evidence_schema = connection.execute(
            "PRAGMA table_info(evidence)"
        ).fetchall()
        audit_schema = connection.execute(
            "PRAGMA table_info(audit_log)"
        ).fetchall()
        audit_rows = connection.execute(
            """
            SELECT audit_id, evidence_id, investigator, action, result, remarks, timestamp
            FROM audit_log
            ORDER BY timestamp DESC
            LIMIT 500
            """
        ).fetchall()
    finally:
        connection.close()

    metric_left, metric_right = st.columns(2)
    metric_left.metric("Evidence rows", evidence_count)
    metric_right.metric("Audit rows", audit_count)
    st.caption(f"Database file: `{DB_PATH.resolve()}`")

    with st.expander("Evidence table schema"):
        st.dataframe(
            [
                {
                    "Column": column["name"],
                    "Type": column["type"],
                    "Required": bool(column["notnull"]),
                    "Primary key": bool(column["pk"]),
                }
                for column in evidence_schema
            ],
            hide_index=True,
        )
    with st.expander("Audit table schema"):
        st.dataframe(
            [
                {
                    "Column": column["name"],
                    "Type": column["type"],
                    "Required": bool(column["notnull"]),
                    "Primary key": bool(column["pk"]),
                }
                for column in audit_schema
            ],
            hide_index=True,
        )

    st.subheader("Evidence table")
    evidence_rows = records_as_dicts(get_all_evidence())
    if evidence_rows:
        st.dataframe(evidence_rows, hide_index=True)
    else:
        st.caption("No evidence rows yet.")

    st.subheader("Audit log")
    if audit_rows:
        st.dataframe(records_as_dicts(audit_rows), hide_index=True)
        if audit_count > len(audit_rows):
            st.caption("Showing the most recent 500 audit rows.")
    else:
        st.caption("No audit rows yet.")
