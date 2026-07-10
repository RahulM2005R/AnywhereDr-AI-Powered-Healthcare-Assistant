"""
AnywhereDr - AI Engine (Offline Mode)
Generates smart diagnosis results locally — no API key required.
"""

import time
import threading
import random


# ── Condition database keyed by body part keywords ────────────────────────────
CONDITION_DB = {
    "head": [
        {
            "name": "Tension Headache",
            "probability": "High",
            "description": "The most common type of headache, often caused by stress, poor posture, or eye strain. Typically felt as a band-like pressure around the head.",
            "risk": "Low",
            "home_care": [
                "Apply a warm or cold compress to your forehead or neck",
                "Take over-the-counter pain relievers (paracetamol or ibuprofen)",
                "Rest in a quiet, dark room",
                "Stay well-hydrated throughout the day",
                "Practice gentle neck and shoulder stretches",
            ],
            "immediate": [
                "Rest and avoid screens for at least 1 hour",
                "Drink 2–3 glasses of water immediately",
                "Take a mild analgesic if pain is moderate",
            ],
            "warnings": [
                "Go to ER if: sudden, severe 'thunderclap' headache unlike any before",
                "Seek urgent care if: headache with stiff neck, fever, or rash",
                "Call doctor if: headaches occurring daily or worsening over weeks",
                "Emergency if: headache following a head injury",
            ],
            "tests": ["Neurological examination", "Blood pressure check", "MRI brain (if recurring)"],
            "lifestyle": [
                "Maintain a regular sleep schedule (7–9 hours)",
                "Reduce caffeine and alcohol intake",
                "Take regular breaks from screens (20-20-20 rule)",
                "Manage stress with relaxation techniques",
            ],
        },
        {
            "name": "Migraine",
            "probability": "Moderate",
            "description": "A neurological condition causing intense, throbbing headaches often on one side, sometimes with nausea and light sensitivity.",
            "risk": "Moderate",
            "home_care": [
                "Rest in a dark, quiet room immediately",
                "Apply cold pack to the painful area",
                "Try prescribed triptan medications if available",
                "Avoid known triggers (bright lights, strong smells)",
            ],
            "immediate": ["Move to a dark, quiet room", "Apply cold compress to head"],
            "warnings": ["ER if: worst headache of your life", "Doctor if: more than 4 migraines/month"],
            "tests": ["Neurology consultation", "MRI/CT scan", "Migraine diary review"],
            "lifestyle": ["Identify and avoid personal triggers", "Maintain consistent sleep and meal times"],
        },
    ],
    "chest": [
        {
            "name": "Viral Upper Respiratory Infection",
            "probability": "High",
            "description": "A common viral illness affecting the respiratory tract, typically caused by rhinovirus or coronavirus. Usually self-limiting within 7–10 days.",
            "risk": "Low",
            "home_care": [
                "Drink plenty of warm fluids (water, herbal tea, broth)",
                "Take paracetamol or ibuprofen for fever and discomfort",
                "Use saline nasal spray for congestion relief",
                "Inhale steam to ease congestion",
                "Ensure adequate rest (8+ hours sleep)",
            ],
            "immediate": [
                "Rest at home and avoid contact with vulnerable people",
                "Monitor temperature every 4–6 hours",
                "Stay hydrated — aim for 8+ glasses of water",
            ],
            "warnings": [
                "ER immediately if: difficulty breathing or bluish lips",
                "Urgent care if: fever above 39.5°C persisting > 3 days",
                "Doctor if: symptoms worsen after initial improvement",
                "Emergency if: chest pain with shortness of breath",
            ],
            "tests": ["COVID-19 rapid antigen test", "CBC if fever persists", "Chest X-ray if worsening"],
            "lifestyle": [
                "Wash hands frequently for at least 20 seconds",
                "Wear a mask in crowded public spaces",
                "Boost immunity with Vitamin C and zinc",
                "Avoid smoking during recovery",
            ],
        },
        {
            "name": "Bronchitis",
            "probability": "Moderate",
            "description": "Inflammation of the bronchial tubes causing persistent cough, often with mucus. Usually follows a respiratory infection.",
            "risk": "Moderate",
            "home_care": [
                "Use a humidifier in your room",
                "Drink warm fluids to loosen mucus",
                "Avoid irritants like smoke and dust",
            ],
            "immediate": ["Use bronchodilator if prescribed", "Avoid cold air and exercise"],
            "warnings": ["Doctor if: cough persists > 3 weeks", "ER if: coughing blood"],
            "tests": ["Chest X-ray", "Sputum culture", "Spirometry (lung function test)"],
            "lifestyle": ["Quit smoking immediately", "Use air purifier at home"],
        },
    ],
    "abdomen": [
        {
            "name": "Gastroenteritis (Stomach Flu)",
            "probability": "High",
            "description": "Inflammation of the stomach and intestines, typically caused by a viral or bacterial infection. Characterized by nausea, vomiting, and diarrhea.",
            "risk": "Low",
            "home_care": [
                "Sip small amounts of clear fluids (water, oral rehydration salts)",
                "Eat bland foods — BRAT diet (Banana, Rice, Applesauce, Toast)",
                "Avoid dairy, caffeine, and fatty foods",
                "Rest and avoid strenuous activities",
                "Take ORS sachets to prevent dehydration",
            ],
            "immediate": [
                "Stop eating solid food for 2–4 hours",
                "Begin oral rehydration with small frequent sips",
                "Monitor for signs of dehydration",
            ],
            "warnings": [
                "ER if: severe abdominal pain with rigid abdomen",
                "Urgent if: unable to keep any fluids down for 12+ hours",
                "Doctor if: blood in stool or vomit",
                "Emergency if: signs of dehydration (dry mouth, no urination, confusion)",
            ],
            "tests": ["Stool culture", "Blood tests (electrolytes)", "Abdominal ultrasound if pain persists"],
            "lifestyle": [
                "Practice strict hand hygiene before meals",
                "Ensure food is properly cooked and stored",
                "Avoid street food during illness",
            ],
        },
        {
            "name": "Irritable Bowel Syndrome (IBS)",
            "probability": "Moderate",
            "description": "A chronic functional gastrointestinal disorder causing abdominal pain, bloating, and irregular bowel habits.",
            "risk": "Low",
            "home_care": [
                "Identify and eliminate trigger foods",
                "Eat smaller, more frequent meals",
                "Increase dietary fiber gradually",
            ],
            "immediate": ["Apply heat pad to abdomen", "Avoid gas-producing foods"],
            "warnings": ["Doctor if: unexplained weight loss", "ER if: severe abdominal pain"],
            "tests": ["Colonoscopy", "Food intolerance testing", "Gastroenterology consultation"],
            "lifestyle": ["Keep a food diary", "Manage stress — yoga or meditation", "Regular gentle exercise"],
        },
    ],
    "joints": [
        {
            "name": "Musculoskeletal Strain",
            "probability": "High",
            "description": "Overuse or injury to muscles, tendons, or ligaments causing pain and stiffness. Very common and usually resolves with rest.",
            "risk": "Low",
            "home_care": [
                "Apply RICE method: Rest, Ice, Compression, Elevation",
                "Take anti-inflammatory medications (ibuprofen)",
                "Gentle stretching exercises after 48 hours",
                "Use supportive bandage if needed",
                "Avoid heavy lifting or strenuous activity",
            ],
            "immediate": ["Rest the affected area immediately", "Apply ice pack (15–20 mins every hour)"],
            "warnings": [
                "Doctor if: pain not improving after 1 week",
                "ER if: visible deformity or inability to bear weight",
                "Urgent if: severe swelling with bruising",
            ],
            "tests": ["X-ray to rule out fracture", "MRI if soft tissue injury suspected", "Physiotherapy assessment"],
            "lifestyle": [
                "Warm up properly before exercise",
                "Strengthen core muscles to prevent injury",
                "Maintain healthy body weight",
            ],
        },
        {
            "name": "Arthritis (Osteoarthritis)",
            "probability": "Moderate",
            "description": "Degenerative joint disease causing cartilage breakdown, resulting in pain, stiffness, and reduced mobility.",
            "risk": "Moderate",
            "home_care": ["Low-impact exercise (swimming, cycling)", "Hot/cold therapy", "Use joint support braces"],
            "immediate": ["Rest the joint", "Take prescribed anti-inflammatory"],
            "warnings": ["Doctor if: joint hot, red, or swollen suddenly", "Rheumatology if: multiple joints affected"],
            "tests": ["X-ray of affected joint", "Rheumatoid factor blood test", "ESR/CRP inflammation markers"],
            "lifestyle": ["Weight management", "Regular physiotherapy", "Swimming or water aerobics"],
        },
    ],
    "general": [
        {
            "name": "Viral Fever / Flu-like Illness",
            "probability": "High",
            "description": "A systemic viral infection causing fever, fatigue, body aches, and malaise. Usually self-resolving within 5–7 days.",
            "risk": "Low",
            "home_care": [
                "Drink at least 8–10 glasses of water per day",
                "Take paracetamol 500mg–1g every 6 hours for fever",
                "Rest completely — avoid work or school",
                "Eat light, nutritious meals (soups, fruits)",
                "Sponge bath with lukewarm water if fever is high",
            ],
            "immediate": [
                "Measure temperature every 4–6 hours",
                "Take fever-reducing medication immediately",
                "Isolate to prevent spreading infection",
                "Start oral rehydration",
            ],
            "warnings": [
                "ER if: fever above 40°C (104°F)",
                "Emergency if: difficulty breathing, confusion, or seizure",
                "Doctor if: fever persists more than 5 days",
                "Urgent if: rash appears alongside fever",
            ],
            "tests": ["Complete Blood Count (CBC)", "Dengue NS1 Antigen test", "Malaria rapid test", "COVID-19 test"],
            "lifestyle": [
                "Boost immunity with Vitamin C and D supplements",
                "Get annual flu vaccination",
                "Maintain good sleep hygiene",
                "Avoid crowds when immunity is low",
            ],
        },
        {
            "name": "Dehydration",
            "probability": "Moderate",
            "description": "Occurs when the body loses more fluids than it takes in, leading to fatigue, dizziness, and headaches.",
            "risk": "Low",
            "home_care": ["Drink ORS or electrolyte drinks", "Eat water-rich fruits (watermelon, cucumber)"],
            "immediate": ["Drink 500ml of water immediately", "Sit or lie down in a cool area"],
            "warnings": ["ER if: no urination for 8+ hours or extreme confusion"],
            "tests": ["Serum electrolytes", "Urine specific gravity"],
            "lifestyle": ["Drink minimum 2–3 litres of water daily", "Increase fluid intake in hot weather"],
        },
    ],
    "skin": [
        {
            "name": "Allergic Dermatitis / Eczema",
            "probability": "High",
            "description": "Inflammation of the skin triggered by allergens or irritants, causing redness, itching, and rash.",
            "risk": "Low",
            "home_care": [
                "Apply fragrance-free moisturizer generously",
                "Use mild, unscented soap",
                "Apply cool, wet compress for itching",
                "Take antihistamine (cetirizine) for itch relief",
                "Avoid scratching to prevent infection",
            ],
            "immediate": ["Stop using any new products", "Apply hydrocortisone cream (1%) to rash"],
            "warnings": ["Doctor if: rash spreading rapidly", "ER if: difficulty breathing or throat swelling (anaphylaxis)"],
            "tests": ["Patch test (allergy testing)", "Skin biopsy if uncertain", "IgE antibody blood test"],
            "lifestyle": ["Use hypoallergenic products", "Wear breathable cotton clothing", "Identify and avoid triggers"],
        },
    ],
    "mental": [
        {
            "name": "Generalized Anxiety / Stress",
            "probability": "High",
            "description": "Excessive worry and tension that affects daily functioning. Often linked to life stressors, work pressure, or health concerns.",
            "risk": "Low",
            "home_care": [
                "Practice deep breathing: inhale 4s, hold 4s, exhale 6s",
                "Reduce caffeine and alcohol consumption",
                "Get 30 minutes of moderate exercise daily",
                "Limit news and social media consumption",
                "Talk to someone you trust about your worries",
            ],
            "immediate": ["Try the 5-4-3-2-1 grounding technique", "Take 10 slow, deep breaths"],
            "warnings": ["Urgent if: panic attacks with chest pain", "Doctor if: anxiety is affecting work/relationships daily"],
            "tests": ["GAD-7 anxiety screening", "Thyroid function test (rule out thyroid issue)", "Psychology consultation"],
            "lifestyle": ["Mindfulness meditation (Headspace, Calm apps)", "Regular yoga or walking", "Maintain social connections"],
        },
    ],
}


def _pick_conditions(body_parts: list, symptoms: list) -> list:
    """Select 2–3 relevant conditions based on selected body parts."""
    matched = []
    keywords = {
        "head": "head", "brain": "head", "eye": "head",
        "chest": "chest", "lung": "chest", "heart": "chest",
        "abdomen": "abdomen", "stomach": "abdomen",
        "muscle": "joints", "joint": "joints", "back": "joints",
        "skin": "skin", "mental": "mental", "anxiety": "mental",
    }

    used_keys = set()
    for part in body_parts:
        part_lower = part.lower()
        for kw, db_key in keywords.items():
            if kw in part_lower and db_key not in used_keys:
                used_keys.add(db_key)
                if db_key in CONDITION_DB:
                    matched.extend(CONDITION_DB[db_key])
                break

    if not matched:
        matched = CONDITION_DB["general"]

    # Remove duplicates by name
    seen = set()
    unique = []
    for c in matched:
        if c["name"] not in seen:
            seen.add(c["name"])
            unique.append(c)

    return unique[:3] if len(unique) >= 3 else unique


def _assess_risk(symptoms: list, followups: dict) -> str:
    """Determine risk level from symptoms and follow-up answers."""
    severity = followups.get("severity", "")
    preexisting = followups.get("preexisting", "")
    duration = followups.get("duration", "")

    # Critical symptoms
    critical_keywords = ["chest pain", "difficulty breathing", "shortness of breath",
                          "coughing blood", "blood in stool", "fainting"]
    for s in symptoms:
        if any(k in s.lower() for k in critical_keywords):
            return "High"

    if "Very Severe" in severity or "cannot carry on" in severity:
        return "High"
    if "Severe" in severity or "affects my daily" in severity:
        return "Moderate"
    if "More than 1 month" in duration or "More than 2 weeks" in duration:
        return "Moderate"
    if any(c in preexisting for c in ["Heart Disease", "Kidney", "Liver"]):
        return "Moderate"

    return "Low"


def get_diagnosis(patient: dict, body_parts: list, symptoms: list,
                  followups: dict, callback, error_callback):
    """
    Generate a smart offline diagnosis — no API needed.
    Runs in a background thread to keep UI responsive.
    """
    def _run():
        # Simulate processing time for realism
        time.sleep(3.0)

        conditions  = _pick_conditions(body_parts, symptoms)
        risk_level  = _assess_risk(symptoms, followups)
        age         = int(patient.get("age", 30))
        gender      = patient.get("gender", "")

        if not conditions:
            conditions = CONDITION_DB["general"]

        primary = conditions[0]

        # Build risk explanation
        risk_explanations = {
            "Low":      "Your symptoms appear mild and do not suggest an immediate emergency. Monitor your condition and rest.",
            "Moderate": "Some of your symptoms or history indicate a moderate concern. Medical consultation is recommended soon.",
            "High":     "Your symptoms suggest a condition that needs prompt medical attention. Please consult a doctor or visit urgent care today.",
            "Critical": "This combination of symptoms may indicate a serious condition. Please seek emergency care immediately.",
        }

        # Age-adjusted note
        age_note = ""
        if age > 60:
            age_note = " Given your age, we recommend consulting your doctor sooner rather than later."
        elif age < 12:
            age_note = " For children, we strongly recommend in-person evaluation by a paediatrician."

        doctor_note = (
            f"Based on your reported symptoms, the most likely cause appears to be {primary['name']}. "
            f"Please monitor your symptoms closely and don't hesitate to seek professional medical care if your condition worsens.{age_note} "
            f"Take care and feel better soon! 💙"
        )

        result = {
            "possible_conditions": [
                {
                    "name":        c["name"],
                    "probability": c["probability"],
                    "description": c["description"],
                }
                for c in conditions
            ],
            "risk_level":        risk_level,
            "risk_explanation":  risk_explanations.get(risk_level, risk_explanations["Low"]),
            "immediate_actions": primary.get("immediate", [
                "Rest and stay hydrated",
                "Monitor your symptoms carefully",
                "Avoid strenuous activities",
            ]),
            "home_care":         primary.get("home_care", [
                "Drink plenty of fluids",
                "Take appropriate over-the-counter medication",
                "Rest adequately",
            ]),
            "warning_signs":     primary.get("warnings", [
                "Seek emergency care if symptoms worsen suddenly",
                "Visit doctor if no improvement after 3 days",
            ]),
            "recommended_tests": primary.get("tests", [
                "Complete Blood Count (CBC)",
                "General physician consultation",
            ]),
            "lifestyle_advice":  primary.get("lifestyle", [
                "Maintain a balanced diet rich in fruits and vegetables",
                "Exercise moderately for 30 minutes daily",
                "Get 7–9 hours of sleep per night",
                "Manage stress through mindfulness or meditation",
            ]),
            "doctor_note": doctor_note,
        }

        callback(result)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return thread
