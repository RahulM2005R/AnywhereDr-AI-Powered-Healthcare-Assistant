"""
AnywhereDr - Report Generator
Creates professional PDF and TXT medical consultation reports
"""

import os
import json
from datetime import datetime
from config import REPORTS_DIR, APP_NAME, APP_VERSION, MEDICAL_DISCLAIMER


def ensure_reports_dir():
    """Create the reports directory if it doesn't exist."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    return REPORTS_DIR


def generate_report_filename(patient_name: str) -> str:
    """Generate a unique timestamped filename for the report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in patient_name)
    return f"AnywhereDr_Report_{safe_name}_{timestamp}.txt"


def format_text_report(patient: dict, body_parts: list, symptoms: list,
                        followups: dict, diagnosis: dict) -> str:
    """
    Format the full medical consultation report as plain text.
    """
    now = datetime.now()
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%I:%M %p")

    lines = []
    sep  = "═" * 60
    sep2 = "─" * 60
    sep3 = "·" * 60

    # ── Header ────────────────────────────────────────────────────
    lines += [
        sep,
        f"    {APP_NAME.upper()}  —  AI-Powered Medical Consultation",
        f"    Version {APP_VERSION}",
        sep,
        f"    Date : {date_str}",
        f"    Time : {time_str}",
        f"    Report ID : RPT-{now.strftime('%Y%m%d%H%M%S')}",
        sep,
        "",
    ]

    # ── Patient Details ──────────────────────────────────────────
    lines += [
        "  PATIENT INFORMATION",
        sep2,
        f"  Name   : {patient.get('name', 'N/A')}",
        f"  Age    : {patient.get('age', 'N/A')} years",
        f"  Gender : {patient.get('gender', 'N/A')}",
        "",
    ]

    # ── Consultation Details ─────────────────────────────────────
    lines += [
        "  CONSULTATION DETAILS",
        sep2,
        f"  Affected Area(s) : {', '.join(body_parts) if body_parts else 'N/A'}",
        "",
        "  Reported Symptoms:",
    ]
    for s in symptoms:
        lines.append(f"    ✓ {s}")
    lines.append("")

    # ── Follow-up Answers ────────────────────────────────────────
    if followups:
        lines += ["  MEDICAL HISTORY", sep2]
        label_map = {
            "duration":    "Symptom Duration",
            "severity":    "Severity Level",
            "medications": "Current Medications",
            "allergies":   "Known Allergies",
            "preexisting": "Pre-existing Conditions",
            "smoking":     "Smoking Status",
        }
        for qid, answer in followups.items():
            label = label_map.get(qid, qid.capitalize())
            lines.append(f"  {label:25s}: {answer}")
        lines.append("")

    # ── Diagnosis Results ────────────────────────────────────────
    lines += [
        "  AI DIAGNOSTIC ASSESSMENT",
        sep,
    ]

    risk = diagnosis.get("risk_level", "Unknown")
    risk_explanation = diagnosis.get("risk_explanation", "")
    lines += [
        f"  ⚠  RISK LEVEL: {risk.upper()}",
        f"  {risk_explanation}",
        "",
    ]

    conditions = diagnosis.get("possible_conditions", [])
    if conditions:
        lines += ["  POSSIBLE CONDITIONS", sep2]
        for i, c in enumerate(conditions, 1):
            lines += [
                f"  {i}. {c.get('name', 'Unknown')}",
                f"     Probability : {c.get('probability', 'N/A')}",
                f"     Description : {c.get('description', 'N/A')}",
                "",
            ]

    # ── Immediate Actions ────────────────────────────────────────
    immediate = diagnosis.get("immediate_actions", [])
    if immediate:
        lines += ["  IMMEDIATE ACTIONS", sep2]
        for a in immediate:
            lines.append(f"  ▶ {a}")
        lines.append("")

    # ── Home Care ────────────────────────────────────────────────
    home_care = diagnosis.get("home_care", [])
    if home_care:
        lines += ["  HOME CARE RECOMMENDATIONS", sep2]
        for h in home_care:
            lines.append(f"  • {h}")
        lines.append("")

    # ── Warning Signs ────────────────────────────────────────────
    warning = diagnosis.get("warning_signs", [])
    if warning:
        lines += ["  ⚠  WARNING SIGNS — SEEK URGENT CARE IF:", sep2]
        for w in warning:
            lines.append(f"  ! {w}")
        lines.append("")

    # ── Recommended Tests ────────────────────────────────────────
    tests = diagnosis.get("recommended_tests", [])
    if tests:
        lines += ["  RECOMMENDED TESTS & REFERRALS", sep2]
        for t in tests:
            lines.append(f"  🔬 {t}")
        lines.append("")

    # ── Lifestyle Advice ─────────────────────────────────────────
    lifestyle = diagnosis.get("lifestyle_advice", [])
    if lifestyle:
        lines += ["  LIFESTYLE RECOMMENDATIONS", sep2]
        for l in lifestyle:
            lines.append(f"  ✦ {l}")
        lines.append("")

    # ── Doctor Note ──────────────────────────────────────────────
    note = diagnosis.get("doctor_note", "")
    if note:
        lines += [
            "  NOTE FROM YOUR AI DOCTOR",
            sep2,
            f"  \"{note}\"",
            "",
        ]

    # ── Disclaimer ───────────────────────────────────────────────
    lines += [
        sep,
        "  MEDICAL DISCLAIMER",
        sep2,
        "  This report is generated by an AI system for informational",
        "  purposes only. It is NOT a substitute for professional medical",
        "  advice, diagnosis, or treatment. Always consult a qualified",
        "  healthcare provider for any medical condition.",
        "  In case of emergency, call your local emergency services.",
        sep,
        f"  Generated by {APP_NAME} v{APP_VERSION}  |  {date_str} {time_str}",
        sep,
    ]

    return "\n".join(lines)


def save_report(patient: dict, body_parts: list, symptoms: list,
                followups: dict, diagnosis: dict) -> str:
    """
    Save the report to the reports directory.
    Returns the full file path.
    """
    ensure_reports_dir()
    filename = generate_report_filename(patient.get("name", "patient"))
    filepath = os.path.join(REPORTS_DIR, filename)

    content = format_text_report(patient, body_parts, symptoms, followups, diagnosis)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


def save_json_report(patient: dict, body_parts: list, symptoms: list,
                     followups: dict, diagnosis: dict) -> str:
    """
    Save the raw JSON data for programmatic access.
    Returns the full file path.
    """
    ensure_reports_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in patient.get("name", "patient"))
    filename = f"AnywhereDr_Data_{safe_name}_{timestamp}.json"
    filepath = os.path.join(REPORTS_DIR, filename)

    data = {
        "generated_at": datetime.now().isoformat(),
        "patient": patient,
        "body_parts": body_parts,
        "symptoms": symptoms,
        "followups": followups,
        "diagnosis": diagnosis,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return filepath
