"""
verify.py
---------
Handles evidence integrity verification.

Re-calculates the SHA-256 hash of the original evidence file and
compares it against the hash stored at the time of registration.
Every verification attempt is recorded in the chain of custody,
regardless of whether it succeeds or fails, to preserve a complete
audit trail.
"""

from pathlib import Path

from evidence import get_evidence_by_id
from hashing import calculate_sha256, compare_hashes
from audit import log_action
from utils import validate_non_empty, print_header


def verify_evidence_integrity():
    """
    CLI workflow to verify the integrity of a registered evidence file.

    Steps:
        1. Prompt for Evidence ID.
        2. Look up the stored record.
        3. Recalculate the SHA-256 hash of the file at its stored path.
        4. Compare against the stored hash.
        5. Report result and log the outcome in the audit trail.
    """
    print_header("VERIFY EVIDENCE INTEGRITY")
    evidence_id = input("Enter Evidence ID to verify: ").strip()

    if not evidence_id:
        print("[!] Evidence ID cannot be empty.")
        return

    record = get_evidence_by_id(evidence_id)
    if not record:
        print(f"[!] No evidence found with ID '{evidence_id}'.")
        return

    investigator = validate_non_empty(
        input("Enter Investigator Name performing this verification: "),
        "Investigator Name",
    )

    print("\nRecalculating SHA-256 hash... please wait.")
    result = verify_evidence_record(evidence_id, investigator)
    if result["result"] == "Integrity Verified":
        print(f"\n[OK] {result['result']}")
    elif result["result"] == "Integrity Compromised":
        print("\n[!] WARNING: Evidence has been modified.")
    else:
        print(f"\n[!] {result['remarks']}")

    if result["current_hash"]:
        print(f"Stored Hash     : {result['stored_hash']}")
        print(f"Recalculated    : {result['current_hash']}")


def verify_evidence_record(evidence_id: str, investigator: str) -> dict:
    """Verify one evidence record, persist the audit event, and return the result."""
    record = get_evidence_by_id(evidence_id)
    if not record:
        raise LookupError(f"No evidence found with ID '{evidence_id}'.")

    file_path = Path(record["file_path"])
    stored_hash = record["sha256_hash"]

    if not file_path.exists():
        result = "Error"
        remarks = "Evidence file missing from its original location."
        log_action(evidence_id, investigator, "Verified Integrity", result, remarks)
        return {
            "result": result,
            "remarks": remarks,
            "stored_hash": stored_hash,
            "current_hash": None,
        }

    try:
        current_hash = calculate_sha256(str(file_path))

        if compare_hashes(current_hash, stored_hash):
            result = "Integrity Verified"
            remarks = "Recalculated hash matches the original stored hash."
        else:
            result = "Integrity Compromised"
            remarks = "Recalculated hash does NOT match the original stored hash."
        log_action(evidence_id, investigator, "Verified Integrity", result, remarks)
        return {
            "result": result,
            "remarks": remarks,
            "stored_hash": stored_hash,
            "current_hash": current_hash,
        }

    except (FileNotFoundError, IOError) as e:
        remarks = f"Verification failed due to file access error: {e}"
        log_action(evidence_id, investigator, "Verified Integrity", "Error", remarks)
        return {
            "result": "Error",
            "remarks": remarks,
            "stored_hash": stored_hash,
            "current_hash": None,
        }
    except Exception as e:
        remarks = f"Unexpected error during verification: {e}"
        log_action(evidence_id, investigator, "Verified Integrity", "Error", remarks)
        return {
            "result": "Error",
            "remarks": remarks,
            "stored_hash": stored_hash,
            "current_hash": None,
        }
