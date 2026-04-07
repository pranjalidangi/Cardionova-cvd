import joblib
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATH  = os.getenv("MODEL_PATH",  os.path.join(MODELS_DIR, "cardionova_model.pkl"))
SCALER_PATH = os.getenv("SCALER_PATH", os.path.join(MODELS_DIR, "scaler.pkl"))
SHAP_PATH   = os.getenv("SHAP_PATH",   os.path.join(MODELS_DIR, "shap_explainer.pkl"))

# ── Load artifacts ────────────────────────────────────────────────────────────
model_bundle  = joblib.load(MODEL_PATH)
scaler_bundle = joblib.load(SCALER_PATH)
explainer     = joblib.load(SHAP_PATH)

# ── Feature lists ─────────────────────────────────────────────────────────────
ORIGINAL_FEATURES = [
    'male', 'age', 'education', 'currentSmoker', 'cigsPerDay',
    'BPMeds', 'prevalentStroke', 'prevalentHyp', 'diabetes',
    'totChol', 'sysBP', 'diaBP', 'BMI', 'heartRate', 'glucose'
]

ENGINEERED_FEATURES = [
    'hypertension_stage', 'pack_years', 'pulse_pressure',
    'cholesterol_risk', 'age_group', 'bmi_category'
]

FEATURE_DISPLAY_NAMES = {
    'male':               'Sex (Male)',
    'age':                'Age',
    'education':          'Education Level',
    'currentSmoker':      'Current Smoker',
    'cigsPerDay':         'Cigarettes/Day',
    'BPMeds':             'BP Medication',
    'prevalentStroke':    'Prior Stroke',
    'prevalentHyp':       'Hypertension',
    'diabetes':           'Diabetes',
    'totChol':            'Total Cholesterol',
    'sysBP':              'Systolic BP',
    'diaBP':              'Diastolic BP',
    'BMI':                'BMI',
    'heartRate':          'Heart Rate',
    'glucose':            'Blood Glucose',
    'hypertension_stage': 'Hypertension Stage',
    'pack_years':         'Pack Years (Smoking)',
    'pulse_pressure':     'Pulse Pressure',
    'cholesterol_risk':   'Cholesterol Risk Tier',
    'age_group':          'Age Group',
    'bmi_category':       'BMI Category',
}

# ── Extract — handles both dict bundle AND direct object ──────────────────────
if isinstance(model_bundle, dict):
    model             = model_bundle['model']
    FEATURE_ORDER     = model_bundle['feature_names']
    OPTIMAL_THRESHOLD = model_bundle.get('optimal_threshold', 0.448)
else:
    model             = model_bundle
    OPTIMAL_THRESHOLD = 0.448
    FEATURE_ORDER     = ORIGINAL_FEATURES

# ── Extract scaler ────────────────────────────────────────────────────────────
scaler = scaler_bundle['scaler'] if isinstance(scaler_bundle, dict) else scaler_bundle

# ── Helper functions ──────────────────────────────────────────────────────────
def engineer_features(d: dict) -> dict:
    d = d.copy()
    d['pack_years']         = (d['cigsPerDay'] / 20) * d['age']
    d['pulse_pressure']     = d['sysBP'] - d['diaBP']
    d['hypertension_stage'] = (0 if d['sysBP'] < 120 else
                               1 if d['sysBP'] < 130 else
                               2 if d['sysBP'] < 140 else 3)
    d['cholesterol_risk']   = (0 if d['totChol'] < 200 else
                               1 if d['totChol'] < 240 else 2)
    d['age_group']          = (0 if d['age'] < 40 else
                               1 if d['age'] < 50 else
                               2 if d['age'] < 60 else 3)
    d['bmi_category']       = (0 if d['BMI'] < 18.5 else
                               1 if d['BMI'] < 25   else
                               2 if d['BMI'] < 30   else 3)
    return d

def get_recommendation(risk_level: str) -> str:
    return {
        "HIGH":     "Urgent cardiology consultation recommended. Please see a doctor within 1 week. Immediate lifestyle intervention and medication review required.",
        "MODERATE": "Schedule a doctor's appointment within 2-4 weeks. Begin lifestyle changes now — diet, exercise, and smoking cessation if applicable.",
        "LOW":      "Your heart health looks good! Maintain your healthy lifestyle and get a routine annual checkup.",
    }.get(risk_level, "")

# ── Main predict function ─────────────────────────────────────────────────────
def predict(input_data) -> dict:
    raw       = input_data.model_dump() if hasattr(input_data, 'model_dump') else input_data
    full_data = engineer_features(raw)

    # ── Scale original 15 for model ──────────────────────────────────────────
    original_df = pd.DataFrame(
        [[full_data[f] for f in ORIGINAL_FEATURES]],
        columns=ORIGINAL_FEATURES
    )
    scaled_15 = scaler.transform(original_df)   # shape (1, 15)

    # ── Predict using 15 features ────────────────────────────────────────────
    probability = float(model.predict_proba(scaled_15)[0][1])

    if probability >= OPTIMAL_THRESHOLD:
        risk_level = "HIGH"
    elif probability >= OPTIMAL_THRESHOLD * 0.7:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    # ── SHAP using 15 features (matches model coefficients) ──────────────────
    shap_vals = explainer(scaled_15).values[0]   # returns 15 shap values

    all_contributions = sorted([
        {
            'feature':    FEATURE_DISPLAY_NAMES.get(feat, feat),
            'value':      round(float(full_data[feat]), 2),
            'shap_value': round(float(sv), 4),
            'direction':  'INCREASES RISK' if sv > 0 else 'DECREASES RISK',
            'magnitude':  'High' if abs(sv) > 1.0 else ('Medium' if abs(sv) > 0.3 else 'Low'),
        }
        for feat, sv in zip(ORIGINAL_FEATURES, shap_vals)
    ], key=lambda x: abs(x['shap_value']), reverse=True)

    engineered = {k: full_data[k] for k in ENGINEERED_FEATURES}

    all_shap = {
        FEATURE_DISPLAY_NAMES.get(f, f): round(float(sv), 4)
        for f, sv in zip(ORIGINAL_FEATURES, shap_vals)
    }

    return {
        'probability':         probability,
        'cvd_probability':     round(probability, 4),
        'cvd_probability_pct': f"{probability:.1%}",
        'risk_level':          risk_level,
        'recommendation':      get_recommendation(risk_level),
        'top_risk_factors':    all_contributions[:5],
        'engineered_features': engineered,
        'all_shap':            all_shap,
    }