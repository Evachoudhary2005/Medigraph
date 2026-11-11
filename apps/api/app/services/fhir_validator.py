"""HAPI FHIR R4 validator via subprocess.

Calls the official HL7 validator_cli.jar against a Bundle and parses
the OperationOutcome it produces.
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path

log = logging.getLogger("medigraph.fhir_validator")

JAR_PATH = Path(__file__).resolve().parents[2] / "tools" / "validator_cli.jar"
JAVA_BIN = os.getenv(
    "JAVA_BIN",
    r"C:\Users\manme\Downloads\openjdk-27_windows-x64_bin\jdk-27\bin\java.exe",
)
JAVA_HEAP = os.getenv("JAVA_HEAP", "-Xmx2g")
VALIDATOR_TIMEOUT = int(os.getenv("VALIDATOR_TIMEOUT", "240"))


def is_available() -> bool:
    """Return True if both the JAR and Java are present."""
    if not JAR_PATH.exists():
        log.warning("validator JAR not found at %s", JAR_PATH)
        return False
    try:
        subprocess.run(
            [JAVA_BIN, "-version"],
            capture_output=True, timeout=10, check=True,
        )
        return True
    except FileNotFoundError:
        log.warning("java not found at %s", JAVA_BIN)
        return False
    except Exception as e:
        log.warning("java check failed: %s", e)
        return False


def validate_bundle(bundle: dict, version: str = "4.0") -> dict:
    """Validate a FHIR Bundle using the official HL7 validator."""
    if not is_available():
        return {
            "available": False,
            "valid": False,
            "error_count": 0,
            "warning_count": 0,
            "info_count": 0,
            "issues": [],
            "raw": {},
            "stderr": f"validator not available (JAR or Java missing) - JAR_PATH={JAR_PATH} JAVA_BIN={JAVA_BIN}",
        }

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        bundle_file = tmp_path / "bundle.json"
        out_file = tmp_path / "outcome.json"

        bundle_file.write_text(
            json.dumps(bundle, ensure_ascii=False),
            encoding="utf-8",
        )

        cmd = [
            JAVA_BIN, JAVA_HEAP,
            "-jar", str(JAR_PATH),
            str(bundle_file),
            "-version", version,
            "-output", str(out_file),
        ]

        log.info("running HAPI validator on %d entries", len(bundle.get("entry", [])))

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=VALIDATOR_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            log.error("HAPI validator timed out after %ds", VALIDATOR_TIMEOUT)
            return {
                "available": True, "valid": False,
                "error_count": 1, "warning_count": 0, "info_count": 0,
                "issues": [{
                    "severity": "error",
                    "code": "timeout",
                    "diagnostics": f"validator timed out after {VALIDATOR_TIMEOUT}s",
                    "location": [],
                }],
                "raw": {}, "stderr": "timeout",
            }
        except FileNotFoundError as e:
            return {
                "available": False, "valid": False,
                "error_count": 0, "warning_count": 0, "info_count": 0,
                "issues": [],
                "raw": {},
                "stderr": f"FileNotFoundError: {e}",
            }

        stderr = (proc.stderr or "").strip()
        stdout = (proc.stdout or "").strip()

        if not out_file.exists():
            log.warning("no OperationOutcome file produced; exit code %d", proc.returncode)
            log.warning("validator stdout tail: %s", stdout[-400:])
            log.warning("validator stderr tail: %s", stderr[-400:])
            return {
                "available": True,
                "valid": proc.returncode == 0,
                "error_count": 0 if proc.returncode == 0 else 1,
                "warning_count": 0, "info_count": 0,
                "issues": [],
                "raw": {},
                "stderr": (stderr or stdout)[-800:],
            }

        try:
            outcome = json.loads(out_file.read_text(encoding="utf-8"))
        except Exception as e:
            log.exception("could not parse OperationOutcome: %s", e)
            return {
                "available": True, "valid": False,
                "error_count": 1, "warning_count": 0, "info_count": 0,
                "issues": [{
                    "severity": "error", "code": "parse_failed",
                    "diagnostics": str(e), "location": [],
                }],
                "raw": {}, "stderr": stderr,
            }

    issues: list[dict] = []
    counts = {"error": 0, "warning": 0, "information": 0}

    for issue in outcome.get("issue", []):
        sev = (issue.get("severity") or "information").lower()
        if sev not in counts:
            sev = "information"
        counts[sev] += 1

        loc: list[str] = []
        for entry in issue.get("location") or []:
            if isinstance(entry, str):
                loc.append(entry)
            elif isinstance(entry, list):
                loc.append(".".join(map(str, entry)))

        diagnostics = (
            issue.get("diagnostics")
            or (issue.get("details") or {}).get("text")
            or ""
        )

        issues.append({
            "severity": sev,
            "code": issue.get("code"),
            "diagnostics": diagnostics,
            "location": loc,
        })

    valid = proc.returncode == 0 and counts["error"] == 0

    log.info(
        "HAPI: valid=%s errors=%d warnings=%d info=%d",
        valid, counts["error"], counts["warning"], counts["information"],
    )

    return {
        "available": True,
        "valid": valid,
        "error_count": counts["error"],
        "warning_count": counts["warning"],
        "info_count": counts["information"],
        "issues": issues,
        "raw": outcome,
        "stderr": stderr[-500:] if stderr else "",
    }