# ForensiTrack: Digital Evidence Security System

ForensiTrack is a digital forensic evidence management system designed to verify digital evidence integrity using SHA-256 hashing, detect file modifications, maintain chain of custody records, and generate professional forensic reports. It provides both a command-line interface (CLI) and a browser-based interface.

## Features

- **Register Evidence:** Record case ID, investigator details, file metadata, and SHA-256 hash.
- **View Evidence:** Display registered evidence records and detailed information.
- **Integrity Verification:** Compare current and original SHA-256 hashes to detect file modifications.
- **Chain of Custody:** Maintain a chronological audit trail of evidence-related activities.
- **PDF Report Generation:** Generate forensic reports containing evidence details, hash values, verification results, and custody records.
- **Dual Interface:** Access the system through a command-line interface or a Streamlit web interface.
- **SQLite Database:** Store evidence records and audit logs locally.
- **Read-Only Evidence Access:** Read source files without modifying their contents.

## Technology Stack

- **Programming Language:** Python 3.8+
- **Database:** SQLite
- **Cryptographic Hashing:** SHA-256
- **Web Interface:** Streamlit
- **PDF Reports:** ReportLab
- **Standard Libraries:** `hashlib`, `sqlite3`, `os`, `pathlib`, `uuid`, `datetime`

## Prerequisites

- Python 3.8 or later
- pip package manager
- A code editor such as Visual Studio Code

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/PratikshaDhale04/ForensiTrack-Digital-Evidence-Security-System.git
```

### 2. Navigate to the Project Directory

```bash
cd ForensiTrack-Digital-Evidence-Security-System
```

### 3. Create a Virtual Environment (Recommended)

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` file should include:

```text
streamlit
reportlab
```

### 5. Run the Browser-Based Interface

```bash
streamlit run streamlit_app.py
```

Open the local URL displayed in the terminal, usually:

`http://localhost:8501`

### 6. Run the Command-Line Interface

Alternatively, run:

```bash
python main.py
```

Both interfaces are designed to use the same SQLite database.

## How It Works

### 1. Register Evidence

Enter the investigator's name, case ID, and path to the evidence file. The system generates a unique evidence ID, extracts file metadata, calculates the SHA-256 hash, and stores the record in the database.

### 2. View Evidence

View all registered evidence records, including evidence ID, case ID, file name, investigator, registration date, and hash information.

### 3. Verify Evidence Integrity

Select an evidence ID to recalculate its SHA-256 hash. The system compares the new hash with the originally stored hash.

- **Integrity Verified:** Both hashes match.
- **Integrity Warning:** The hashes differ, indicating that the file may have changed.

### 4. View Chain of Custody

Review the chronological history of evidence registration, integrity verification, and other recorded actions, including timestamps, investigator details, results, and remarks.

### 5. Generate Forensic Reports

Generate a PDF report containing evidence metadata, the original SHA-256 hash, verification status, case details, and the associated chain of custody.

## Database Design

The application uses SQLite with two primary tables.

### Evidence Table

| Column | Description |
|---|---|
| `evidence_id` | Unique evidence identifier |
| `case_id` | Associated case reference |
| `investigator` | Evidence registration investigator |
| `file_name` | Name of the evidence file |
| `file_path` | Location of the evidence file |
| `file_size` | File size in bytes |
| `sha256_hash` | Original SHA-256 hash |
| `collected_date` | Evidence registration timestamp |

### Audit Log Table

| Column | Description |
|---|---|
| `audit_id` | Unique audit record identifier |
| `evidence_id` | Associated evidence identifier |
| `investigator` | Person performing the action |
| `action` | Recorded operation |
| `result` | Operation outcome |
| `remarks` | Additional information |
| `timestamp` | Date and time of the action |

## Security and Design Principles

- **Integrity Verification:** SHA-256 hashing helps identify changes to registered evidence files.
- **Evidence Preservation:** Source files are opened in read-only mode.
- **Audit Trail:** Evidence-related operations are recorded with timestamps.
- **Modular Architecture:** Hashing, database management, auditing, verification, and reporting are handled by separate modules.
- **Error Handling:** The application should handle invalid input, missing files, and database or report-generation errors gracefully.
- 
GitHub: [PratikshaDhale04](https://github.com/PratikshaDhale04)
