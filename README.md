# Digital Evidence Integrity and Chain of Custody System

A digital forensic evidence management simulation, built for MSc Digital
Forensics coursework. It demonstrates evidence integrity verification (via
SHA-256 hashing) and chain of custody record-keeping, backed by an SQLite
database, with both a browser-based interface and a command-line interface.

---

## Features

1. **Register Evidence** — capture investigator, case ID, and file metadata,
   compute a SHA-256 hash, and store the record in SQLite.
2. **View Evidence** — list all registered evidence in a table, drill into
   full details for any item.
3. **Verify Evidence Integrity** — recompute the SHA-256 hash and compare it
   against the originally stored hash to detect tampering.
4. **View Chain of Custody** — see the full, chronological audit trail for
   any Evidence ID.
5. **Generate Forensic Report** — export a polished PDF report (via
   ReportLab) containing evidence details, hash, verification status, and
   the complete chain of custody.
6. **Exit**

The program never modifies source evidence files. It reads source files in
read-only binary mode; files uploaded through the browser are copied to a local
archive so later verification checks can read the registered bytes.

---

## Project Structure

```
DigitalEvidenceSystem/
├── main.py            # CLI entry point and menu loop
├── streamlit_app.py   # Browser interface
├── database.py         # SQLite connection + table creation
├── evidence.py         # Register / view evidence
├── hashing.py          # SHA-256 calculation and comparison
├── verify.py            # Evidence integrity verification
├── audit.py             # Chain of custody logging and viewing
├── report.py            # PDF forensic report generation (ReportLab)
├── utils.py              # Shared CLI/formatting/validation helpers
├── requirements.txt
├── README.md
├── database/
│   └── evidence.db      # Auto-created on first run
├── reports/
    └── *.pdf            # Auto-created; generated reports saved here
└── evidence_files/
    └── ...              # Local archive copies from browser uploads
```

---

## Requirements

- Python 3.8+
- [ReportLab](https://pypi.org/project/reportlab/) for PDF generation
- [Streamlit](https://pypi.org/project/streamlit/) for the browser interface

All other functionality relies on the Python standard library:
`hashlib`, `sqlite3`, `os`, `pathlib`, `uuid`, `datetime`.

---

## Setup

1. **Clone / extract the project** into a folder, e.g. `DigitalEvidenceSystem/`.

2. **(Recommended) create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Start the browser interface:**

   ```bash
   streamlit run streamlit_app.py
   ```

   Open the local URL printed in the terminal (usually
   `http://localhost:8501`).

5. **Or run the command-line interface:**

   ```bash
   python main.py
   ```

Both interfaces use the same SQLite database. On first run, the program
automatically:
- Creates the `database/` folder and `evidence.db` SQLite database with
  the required tables (`evidence`, `audit_log`).
- Creates the `reports/` folder for generated PDF reports.

Use **Register evidence** to upload and archive a file, **Evidence records** to
search and inspect stored evidence, **Verify integrity** to recalculate a
SHA-256 hash, **Custody trail** to view audit history, **Forensic reports** to
generate and download PDF reports, and **Database** to inspect rows and table
schemas.

---

## Usage Walkthrough

When you run `python main.py`, you'll see the main menu:

```
======================================================================
     DIGITAL EVIDENCE INTEGRITY & CHAIN OF CUSTODY SYSTEM
======================================================================
  MSc Digital Forensics - Evidence Management Simulation

  [1] Register Evidence
  [2] View Evidence
  [3] Verify Evidence Integrity
  [4] View Chain of Custody
  [5] Generate Forensic Report
  [6] Exit

Select an option (1-6):
```

### 1. Register Evidence
- Enter the full path to a digital evidence file (e.g. an image, document,
  or disk image).
- Enter the investigator's name and the case ID.
- The system reads file metadata (name, size, path, collected date/time),
  computes the SHA-256 hash, generates a unique Evidence ID (e.g.
  `EVD-A1B2C3D4`), and stores everything in the database.
- A "Registered Evidence" entry is automatically added to the chain of
  custody.

### 2. View Evidence
- Displays a table of all registered evidence (Evidence ID, Case ID, File
  Name, Investigator, Collected Date).
- Optionally enter an Evidence ID to see full details, including the
  SHA-256 hash and file path.

### 3. Verify Evidence Integrity
- Enter an Evidence ID and the investigator's name performing the check.
- The system recalculates the SHA-256 hash of the file at its original
  path and compares it to the stored hash.
- Displays **"Integrity Verified"** if the hashes match, or **"WARNING:
  Evidence has been modified."** if they differ.
- Every verification attempt (pass, fail, or error) is automatically
  logged to the chain of custody.

### 4. View Chain of Custody
- Enter an Evidence ID to see its complete, chronologically ordered audit
  trail: Audit ID, Date/Time, Investigator, Action, Result, and Remarks.

### 5. Generate Forensic Report
- Enter an Evidence ID to export a PDF report to the `reports/` folder,
  named `Forensic_Report_<EvidenceID>_<timestamp>.pdf`.
- The report includes evidence information, case ID, investigator, file
  metadata, SHA-256 hash, latest verification status, and the full chain
  of custody history.

### 6. Exit
- Cleanly exits the application.

---

## Database Schema

### `evidence`
| Column          | Type    | Description                        |
|-----------------|---------|-------------------------------------|
| evidence_id     | TEXT PK | Unique evidence identifier          |
| case_id         | TEXT    | Case reference                      |
| investigator    | TEXT    | Investigator who registered evidence|
| file_name       | TEXT    | Original file name                  |
| file_path       | TEXT    | Absolute path to the file            |
| file_size       | INTEGER | File size in bytes                   |
| sha256_hash     | TEXT    | SHA-256 hash at registration time     |
| collected_date  | TEXT    | Date/time the evidence was registered|

### `audit_log`
| Column       | Type    | Description                              |
|--------------|---------|-------------------------------------------|
| audit_id     | TEXT PK | Unique audit entry identifier              |
| evidence_id  | TEXT FK | References `evidence.evidence_id`          |
| investigator | TEXT    | Investigator who performed the action      |
| action       | TEXT    | Action performed (e.g. Registered Evidence)|
| result       | TEXT    | Outcome (e.g. Success, Integrity Verified) |
| remarks      | TEXT    | Additional notes                           |
| timestamp    | TEXT    | Date/time the action occurred              |

---

## Design Notes

- **Forensic soundness**: all file access is strictly read-only
  (`open(path, "rb")`); the program never writes to, renames, or deletes
  evidence files.
- **Auditability**: every registration and verification action creates an
  immutable-style audit log entry with a timestamp, so the full history
  of an evidence item can always be reconstructed.
- **Modularity**: each responsibility (hashing, database access, auditing,
  reporting, CLI orchestration) lives in its own module for readability
  and maintainability.
- **Error handling**: file-not-found, invalid input, and unexpected
  exceptions are all caught and reported to the user without crashing the
  program.

---

## Disclaimer

This project is a simplified educational simulation built for academic
purposes (MSc Digital Forensics coursework). It is **not** intended for
use in real legal or evidentiary proceedings.
#   F o r e n s i T r a c k - D i g i t a l - E v i d e n c e - S e c u r i t y - S y s t e m  
 