"""
AnywhereDr - Configuration Module
All app constants, theme colors, symptom data, and settings
"""

import os

# ─────────────────────────────────────────
# App Identity
# ─────────────────────────────────────────
APP_NAME        = "AnywhereDr"
APP_TAGLINE     = "AI-Powered Medical Consultation"
APP_VERSION     = "1.0.0"
WINDOW_WIDTH    = 900
WINDOW_HEIGHT   = 700
MIN_WIDTH       = 800
MIN_HEIGHT      = 600

# ─────────────────────────────────────────
# Color Palette (Dark Medical Theme)
# ─────────────────────────────────────────
COLORS = {
    # Backgrounds
    "bg_primary":       "#0a0f1a",
    "bg_secondary":     "#0f1729",
    "bg_card":          "#141e35",
    "bg_card_hover":    "#1a2641",
    "bg_input":         "#0d1729",

    # Accents
    "accent":           "#00d4aa",
    "accent_dark":      "#00a882",
    "accent_glow":      "#00d4aa33",
    "accent_secondary": "#3b82f6",
    "accent_sec_dark":  "#2563eb",

    # Text
    "text_primary":     "#e8f0fe",
    "text_secondary":   "#8b9ab0",
    "text_muted":       "#4a5568",
    "text_accent":      "#00d4aa",
    "text_white":       "#ffffff",

    # Status Colors
    "success":          "#10b981",
    "warning":          "#f59e0b",
    "danger":           "#ef4444",
    "info":             "#3b82f6",

    # Risk Meter
    "risk_low":         "#10b981",
    "risk_medium":      "#f59e0b",
    "risk_high":        "#ef4444",

    # Borders
    "border":           "#1e2d4a",
    "border_accent":    "#00d4aa44",

    # Scrollbar
    "scrollbar_bg":     "#0f1729",
    "scrollbar_thumb":  "#1e3a5f",
}

FONTS = {
    "family":           "Segoe UI",
    "family_mono":      "Consolas",
    "title_xl":         ("Segoe UI", 26, "bold"),
    "title_lg":         ("Segoe UI", 20, "bold"),
    "title_md":         ("Segoe UI", 15, "bold"),
    "title_sm":         ("Segoe UI", 13, "bold"),
    "body":             ("Segoe UI", 11),
    "body_bold":        ("Segoe UI", 11, "bold"),
    "small":            ("Segoe UI", 9),
    "small_bold":       ("Segoe UI", 9, "bold"),
    "mono":             ("Consolas", 10),
    "button":           ("Segoe UI", 11, "bold"),
    "label":            ("Segoe UI", 10),
}

# ─────────────────────────────────────────
# Body Parts & Their Symptoms
# ─────────────────────────────────────────
BODY_PARTS = {
    "🧠 Head & Brain": {
        "icon": "🧠",
        "symptoms": [
            "Headache",
            "Migraine",
            "Dizziness / Vertigo",
            "Blurred Vision",
            "Memory Problems",
            "Confusion / Disorientation",
            "Fainting / Syncope",
            "Numbness in Face",
            "Tinnitus (Ringing in Ears)",
            "Difficulty Speaking",
        ]
    },
    "👁️ Eyes": {
        "icon": "👁️",
        "symptoms": [
            "Eye Pain",
            "Redness / Irritation",
            "Blurred Vision",
            "Double Vision",
            "Sensitivity to Light",
            "Watery Eyes",
            "Discharge from Eyes",
            "Swollen Eyelids",
        ]
    },
    "👃 Nose & Throat": {
        "icon": "👃",
        "symptoms": [
            "Runny Nose",
            "Stuffy / Blocked Nose",
            "Sore Throat",
            "Difficulty Swallowing",
            "Loss of Smell",
            "Sneezing",
            "Postnasal Drip",
            "Hoarse Voice",
            "Swollen Tonsils",
            "Nosebleed",
        ]
    },
    "🫁 Chest & Lungs": {
        "icon": "🫁",
        "symptoms": [
            "Chest Pain",
            "Shortness of Breath",
            "Dry Cough",
            "Productive Cough (with mucus)",
            "Wheezing",
            "Rapid Breathing",
            "Palpitations",
            "Tightness in Chest",
            "Coughing Blood",
            "Night Sweats",
        ]
    },
    "❤️ Heart": {
        "icon": "❤️",
        "symptoms": [
            "Chest Pain",
            "Palpitations",
            "Irregular Heartbeat",
            "Shortness of Breath",
            "Swollen Legs / Ankles",
            "Fatigue",
            "Dizziness",
            "Fainting",
        ]
    },
    "🫃 Abdomen & Stomach": {
        "icon": "🫃",
        "symptoms": [
            "Abdominal Pain / Cramps",
            "Nausea",
            "Vomiting",
            "Bloating",
            "Diarrhea",
            "Constipation",
            "Loss of Appetite",
            "Heartburn / Acid Reflux",
            "Blood in Stool",
            "Jaundice (Yellow Skin)",
        ]
    },
    "🦴 Muscles & Joints": {
        "icon": "🦴",
        "symptoms": [
            "Joint Pain",
            "Muscle Pain / Aches",
            "Muscle Weakness",
            "Joint Swelling",
            "Stiffness",
            "Limited Range of Motion",
            "Back Pain",
            "Neck Pain",
            "Numbness / Tingling in Limbs",
        ]
    },
    "🩺 General / Systemic": {
        "icon": "🩺",
        "symptoms": [
            "Fever",
            "Chills",
            "Fatigue / Weakness",
            "Weight Loss (unexplained)",
            "Weight Gain (unexplained)",
            "Night Sweats",
            "Loss of Appetite",
            "Swollen Lymph Nodes",
            "Skin Rash",
            "Itching",
        ]
    },
    "🧬 Skin": {
        "icon": "🧬",
        "symptoms": [
            "Rash",
            "Itching",
            "Redness / Inflammation",
            "Dry / Flaky Skin",
            "Blisters",
            "Hives / Urticaria",
            "Skin Discoloration",
            "Lesions / Sores",
            "Hair Loss",
            "Nail Changes",
        ]
    },
    "🧘 Mental Health": {
        "icon": "🧘",
        "symptoms": [
            "Anxiety",
            "Depression",
            "Mood Swings",
            "Insomnia / Sleep Problems",
            "Panic Attacks",
            "Concentration Difficulties",
            "Irritability",
            "Social Withdrawal",
            "Fatigue / Low Energy",
        ]
    },
}

# ─────────────────────────────────────────
# Follow-up Questions (by symptom keywords)
# ─────────────────────────────────────────
FOLLOWUP_QUESTIONS = [
    {
        "id": "duration",
        "question": "How long have you been experiencing these symptoms?",
        "type": "radio",
        "options": [
            "Less than 24 hours",
            "1–3 days",
            "4–7 days",
            "1–2 weeks",
            "More than 2 weeks",
            "More than 1 month"
        ]
    },
    {
        "id": "severity",
        "question": "How would you rate the severity of your symptoms?",
        "type": "radio",
        "options": [
            "Mild – I can carry on with daily activities",
            "Moderate – It affects my daily activities",
            "Severe – I cannot carry on with daily activities",
            "Very Severe – I need immediate help"
        ]
    },
    {
        "id": "medications",
        "question": "Are you currently taking any medications?",
        "type": "radio",
        "options": [
            "No medications",
            "Over-the-counter medications",
            "Prescription medications",
            "Herbal / Traditional medicines",
            "Multiple medications"
        ]
    },
    {
        "id": "allergies",
        "question": "Do you have any known allergies?",
        "type": "radio",
        "options": [
            "No known allergies",
            "Food allergies",
            "Drug / Medication allergies",
            "Environmental allergies (pollen, dust, etc.)",
            "Multiple allergies"
        ]
    },
    {
        "id": "preexisting",
        "question": "Do you have any pre-existing medical conditions?",
        "type": "radio",
        "options": [
            "None",
            "Diabetes",
            "Hypertension / High Blood Pressure",
            "Heart Disease",
            "Asthma / Respiratory Condition",
            "Kidney / Liver Disease",
            "Other chronic condition"
        ]
    },
    {
        "id": "smoking",
        "question": "Do you smoke or use tobacco products?",
        "type": "radio",
        "options": [
            "Never smoked",
            "Former smoker (quit)",
            "Occasional smoker",
            "Regular smoker",
            "Heavy smoker"
        ]
    },
]

# ─────────────────────────────────────────
# Google Gemini Settings
# ─────────────────────────────────────────
GEMINI_MODEL        = "gemini-1.5-flash"
GEMINI_MAX_TOKENS   = 1500
GEMINI_TEMPERATURE  = 0.3

# Default .env path
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")

# ─────────────────────────────────────────
# Disclaimer
# ─────────────────────────────────────────
MEDICAL_DISCLAIMER = (
    "⚠️  IMPORTANT MEDICAL DISCLAIMER\n\n"
    "This application uses Artificial Intelligence for informational purposes only. "
    "It is NOT a substitute for professional medical advice, diagnosis, or treatment. "
    "Always consult a qualified healthcare provider for any medical condition. "
    "In case of a medical emergency, call your local emergency services immediately."
)
