# 🏥 AnywhereDr — AI-Powered Medical Consultation

A beautiful, professional desktop medical consultation app built with Python + Tkinter + OpenAI.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🧑 Patient Registration | Name, Age, Gender form with validation |
| 🫁 Body Part Selection | 10 body systems, clickable card grid |
| ✅ Symptom Checker | 80+ symptoms, two-column checkboxes |
| 📋 Medical History | 6 follow-up questions (duration, severity, meds, etc.) |
| 🤖 AI Diagnosis | OpenAI GPT-4o-mini with animated analysis screen |
| 📊 Diagnosis Report | Risk meter, conditions, home care, warnings |
| 📄 Report Download | Full printable text report |
| 🔄 Restart | New consultation without relaunching |

---

## 🚀 Quick Start

### 1. Install Python
Make sure Python 3.9+ is installed: https://python.org

### 2. Install Dependencies
```bash
cd AnywhereDr
pip install -r requirements.txt
```

### 3. Configure API Key (Optional — Demo works without it)
Open `.env` and add your key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```
> 💡 **No key?** No problem — the app runs in **Demo Mode** automatically with realistic sample results.

### 4. Run the App
```bash
python main.py
```

---

## 📁 Project Structure

```
AnywhereDr/
├── main.py              # Main app, all screens & UI
├── config.py            # Colors, fonts, symptom data, settings
├── ai_engine.py         # OpenAI API integration
├── report_generator.py  # PDF/TXT report creation
├── requirements.txt     # Dependencies
├── .env                 # Your API key (keep private!)
└── reports/             # Auto-generated consultation reports
```

---

## 🎨 Design

- **Theme:** Dark medical UI (`#0a0f1a` background)
- **Accent:** Teal (`#00d4aa`)
- **Font:** Segoe UI
- **Screens:** 7 screens with smooth navigation
- **Risk Meter:** Color-coded Low / Moderate / High / Critical

---

## ⚠️ Medical Disclaimer

This application is for **informational and demonstration purposes only**.
It is **NOT** a substitute for professional medical advice, diagnosis, or treatment.
Always consult a qualified healthcare provider for medical concerns.
In emergencies, call your local emergency services.

---

## 📋 Demo Mode

Without an API key, the app generates realistic demo results including:
- Common Cold / Flu / COVID-19 conditions
- Risk level based on your severity answer  
- Full home care, warning signs, and lifestyle advice
- Downloadable report

---

*Built with Python + Tkinter + OpenAI  |  AnywhereDr v1.0.0*
