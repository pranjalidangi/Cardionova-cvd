import io
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from io import BytesIO


# ── Colors ───────────────────────────────────────────────────────────────────
PRIMARY    = colors.HexColor("#C0392B")
DARK       = colors.HexColor("#2C3E50")
LIGHT_BG   = colors.HexColor("#FDFEFE")
GREEN      = colors.HexColor("#27AE60")
YELLOW     = colors.HexColor("#E67E22")
GRAY       = colors.HexColor("#7F8C8D")
LIGHT_GRAY = colors.HexColor("#ECF0F1")


# ── Healthy ranges by age ─────────────────────────────────────────────────────
HEALTHY_RANGES = {
    18: {"sysBP": (90,120), "diaBP": (60,80),  "totChol": (125,200), "BMI": (18.5,24.9), "glucose": (70,100),  "heartRate": (60,100)},
    35: {"sysBP": (90,120), "diaBP": (60,80),  "totChol": (125,200), "BMI": (18.5,24.9), "glucose": (70,100),  "heartRate": (60,100)},
    45: {"sysBP": (90,130), "diaBP": (60,85),  "totChol": (125,210), "BMI": (18.5,27.0), "glucose": (70,105),  "heartRate": (60,100)},
    55: {"sysBP": (90,135), "diaBP": (60,85),  "totChol": (125,220), "BMI": (18.5,27.0), "glucose": (70,110),  "heartRate": (60,100)},
    65: {"sysBP": (90,140), "diaBP": (60,90),  "totChol": (125,240), "BMI": (18.5,27.0), "glucose": (70,115),  "heartRate": (60,100)},
}


FEATURE_PLAIN_LANGUAGE = {
    "Systolic BP":          ("your top blood pressure number",         "Above 130 mmHg means your heart is constantly working harder than it should. High blood pressure silently damages arteries over time."),
    "Diastolic BP":         ("your bottom blood pressure number",      "Above 85 mmHg means your arteries are under constant pressure even when your heart is at rest."),
    "Total Cholesterol":    ("fat-like substance in your blood",       "Above 200 mg/dL can slowly clog your arteries like rust in a pipe, increasing heart attack risk."),
    "BMI":                  ("body weight relative to your height",    "Above 25 means overweight — extra body weight forces your heart to pump harder every single day."),
    "Blood Glucose":        ("your blood sugar level",                 "Above 100 mg/dL could indicate pre-diabetes, which damages blood vessels and doubles heart risk."),
    "Heart Rate":           ("how many times your heart beats per minute", "Normal is 60–100 bpm. A persistently high rate means your heart is under extra strain."),
    "Cigarettes/Day":       ("number of cigarettes smoked daily",      "Even 1–5 cigarettes a day significantly increases heart disease risk. Quitting reduces risk by 50% within one year."),
    "Pack Years (Smoking)": ("your total lifetime smoking burden",     "Calculated as (cigarettes/day ÷ 20) × years smoked. The higher this number, the more damage to your blood vessels."),
    "Pulse Pressure":       ("difference between your two BP readings","A gap above 60 is a sign of stiff arteries — one of the strongest predictors of future heart disease."),
    "Diabetes":             ("whether you have diabetes",              "Diabetes means high blood sugar is damaging your blood vessels. It doubles the risk of heart disease."),
    "Hypertension":         ("history of high blood pressure",         "A long history of high BP means your heart has been under extra strain for years."),
    "Age":                  ("your age",                               "Arteries naturally stiffen with age. But lifestyle changes reduce risk effectively at any age."),
    "Sex (Male)":           ("your biological sex",                    "Men statistically face higher cardiovascular risk than women before age 65."),
    "Age Group":            ("which age bracket you fall into",        "Risk increases with age — your age group benchmark is used to personalise your healthy ranges."),
    "BMI Category":         ("your weight category",                   "Being overweight puts extra strain on the heart and increases blood pressure and cholesterol."),
    "Cholesterol Risk Tier":("how risky your cholesterol level is",    "Higher cholesterol tiers mean more fatty deposits building up in your arteries over time."),
    "Hypertension Stage":   ("how severe your blood pressure elevation is", "Higher stages mean greater strain on your heart and higher risk of stroke or heart attack."),
    "BP Medication":        ("whether you take blood pressure medication", "Being on BP medication means your blood pressure was already high enough to require treatment. This indicates a pre-existing cardiovascular risk factor."),
    "Prior Stroke":         ("whether you have had a stroke before", "A prior stroke means a blood vessel in your brain was blocked or burst. This significantly increases the risk of a future cardiovascular event."),
    "Current Smoker":       ("whether you currently smoke", "Active smoking damages blood vessel walls and reduces oxygen in the blood, directly increasing heart disease risk."),
    "Education Level":      ("your highest level of education", "Education level is a socioeconomic proxy — lower education is associated with higher cardiovascular risk due to lifestyle and healthcare access factors."),
}



def get_healthy_range(age: int, metric: str):
    breakpoints = sorted(HEALTHY_RANGES.keys())
    selected = breakpoints[0]
    for bp in breakpoints:
        if age >= bp:
            selected = bp
    return HEALTHY_RANGES[selected].get(metric, (0, 100))



def generate_observation_text(input_data: dict, age: int) -> str:
    concerns, positives = [], []
    metrics = {
        "sysBP":     ("blood pressure (systolic)", get_healthy_range(age, "sysBP")[1]),
        "diaBP":     ("blood pressure (diastolic)", get_healthy_range(age, "diaBP")[1]),
        "totChol":   ("cholesterol",                get_healthy_range(age, "totChol")[1]),
        "BMI":       ("BMI",                        get_healthy_range(age, "BMI")[1]),
        "glucose":   ("blood sugar",                get_healthy_range(age, "glucose")[1]),
        "heartRate": ("heart rate",                 get_healthy_range(age, "heartRate")[1]),
    }
    for key, (label, max_val) in metrics.items():
        val = input_data.get(key, 0)
        if val > max_val:
            concerns.append(f"{label} ({val:.0f})")
        else:
            positives.append(label)
    text = ""
    if concerns:
        text += f"⚠ Values above healthy range for your age: {', '.join(concerns)}. These need attention. "
    if positives:
        text += f"✅ Values within normal limits — keep it up: {', '.join(positives)}."
    return text



def get_action_steps(risk_level: str) -> list:
    actions = {
        "HIGH": [
            "[!]  See a cardiologist or your doctor WITHIN 1 WEEK. Do not delay.",
            "[+]  Ask your doctor whether blood pressure or cholesterol medication is needed.",
            "[x]  If you smoke, contact a quit-smoking helpline today.",
            "[!]  Cut salt intake immediately — aim for less than 5g per day.",
            "[>]  Bring this report to your doctor's appointment.",
        ],
        "MODERATE": [
            "[>]  Book a doctor's appointment WITHIN 2-4 WEEKS and share this report.",
            "[+]  Start the DASH diet — more fruits, vegetables, whole grains; less salt.",
            "[>]  Begin 30 minutes of brisk walking, 5 days a week.",
            "[+]  Monitor your blood pressure at home — target below 130/80 mmHg.",
            "[x]  If you smoke, make a plan to quit. Even cutting down helps.",
        ],
        "LOW": [
            "[v]  Get a routine health checkup once a year to stay on track.",
            "[+]  Keep eating a balanced diet rich in vegetables and whole grains.",
            "[>]  Maintain at least 150 minutes of moderate exercise per week.",
            "[x]  Stay smoke-free — it is one of the best things for your heart.",
            "[v]  Aim for 7-8 hours of quality sleep per night.",
        ],
    }
    return actions.get(risk_level, actions["MODERATE"])



def get_risk_level_text(risk_level: str, probability: float) -> str:
    pct = probability * 100
    texts = {
        "LOW": (
            f"Great news — your heart health looks good right now! "
            f"Your score of {pct:.1f}% means that out of 100 people with a similar health profile, "
            f"fewer than 15 are likely to experience a heart event in the next 10 years. "
            f"Keep maintaining your healthy lifestyle."
        ),
        "MODERATE": (
            f"Your heart health needs some attention. "
            f"Your score of {pct:.1f}% means that out of 100 people with a similar health profile, "
            f"about {pct:.0f} may experience a heart attack, stroke, or related event in the next 10 years. "
            f"The good news — making lifestyle changes now can significantly reduce this risk."
        ),
        "HIGH": (
            f"Your heart health requires urgent attention. "
            f"Your score of {pct:.1f}% means that out of 100 people with a similar health profile, "
            f"about {pct:.0f} are likely to experience a serious cardiovascular event in the next 10 years. "
            f"Please consult a doctor promptly — early action can make a major difference."
        ),
    }
    return texts.get(risk_level, "")



# ── Chart generators ──────────────────────────────────────────────────────────
def make_gauge_chart(probability: float, risk_level: str) -> BytesIO:
    fig, ax = plt.subplots(figsize=(4, 2.5), subplot_kw=dict(aspect="equal"))
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.3, 1.3)
    ax.axis("off")


    from matplotlib.patches import Wedge
    for start, width, color, label in [
        (180, 60, "#27AE60", "LOW"),
        (120, 60, "#E67E22", "MOD"),
        (60,  60, "#E74C3C", "HIGH"),
    ]:
        ax.add_patch(Wedge((0,0), 1.1, start, start+width, width=0.3, facecolor=color, alpha=0.85))
        mid = np.radians(start + 30)
        ax.text(0.8*np.cos(mid), 0.8*np.sin(mid), label, ha="center", va="center",
                fontsize=6, fontweight="bold", color="white")


    needle_angle = np.radians(180 - (probability * 180))
    ax.annotate("", xy=(0.75*np.cos(needle_angle), 0.75*np.sin(needle_angle)),
                xytext=(0,0), arrowprops=dict(arrowstyle="-|>", color="#2C3E50", lw=2))
    ax.add_patch(plt.Circle((0,0), 0.08, color="#2C3E50", zorder=5))


    risk_color = {"LOW": "#27AE60", "MODERATE": "#E67E22", "HIGH": "#E74C3C"}.get(risk_level, "gray")
    ax.text(0, -0.2,  f"{probability*100:.1f}%", ha="center", fontsize=14, fontweight="bold", color=risk_color)
    ax.text(0, -0.42, risk_level,                ha="center", fontsize=9,  fontweight="bold", color=risk_color)


    buf = BytesIO()
    plt.tight_layout(pad=0.2)
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight", transparent=True)
    plt.close()
    buf.seek(0)
    return buf



def make_benchmark_chart(input_data: dict, age: int) -> BytesIO:
    metrics      = ["sysBP", "diaBP", "totChol", "BMI", "glucose", "heartRate"]
    labels       = ["Sys BP", "Dia BP", "Cholesterol", "BMI", "Glucose", "Heart Rate"]
    user_vals    = [input_data.get(m, 0) for m in metrics]
    healthy_max  = [get_healthy_range(age, m)[1] for m in metrics]


    x, width = np.arange(len(metrics)), 0.35
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(x - width/2, user_vals,   width, label="Your Values",  color="#E74C3C", alpha=0.85)
    ax.bar(x + width/2, healthy_max, width, label="Healthy Max",  color="#27AE60", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Value", fontsize=9)
    ax.set_title("Your Values vs Healthy Benchmarks", fontsize=10, fontweight="bold")
    ax.legend(fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for bar in ax.patches[:len(metrics)]:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{bar.get_height():.0f}", ha="center", fontsize=7, color="#2C3E50")
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf



def make_radar_chart(input_data: dict, age: int) -> BytesIO:
    categories = ["Blood\nPressure", "Cholesterol", "Blood\nSugar", "BMI", "Heart\nRate", "Smoking"]


    def norm(val, lo, hi):
        return max(0, min(1, (val - lo) / (hi - lo)))


    values = [
        norm(input_data.get("sysBP",      120), 90,  200),
        norm(input_data.get("totChol",     200), 100, 400),
        norm(input_data.get("glucose",      80), 60,  300),
        norm(input_data.get("BMI",          22), 15,   50),
        norm(input_data.get("heartRate",    70), 40,  150),
        min(1, input_data.get("cigsPerDay", 0) / 40.0),
    ]
    values += values[:1]
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)] + [0]


    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color="#E74C3C", alpha=0.25)
    ax.plot(angles, values, color="#E74C3C", linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=8)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75])
    ax.set_yticklabels(["Low", "Med", "High"], size=6, color="gray")
    ax.set_title("Health Risk Profile", size=10, fontweight="bold", pad=15)
    ax.grid(color="gray", alpha=0.3)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf



def make_shap_chart(factors: list) -> BytesIO:
    names  = [f["feature"] for f in factors]
    values = [f["shap_value"] for f in factors]
    bar_colors = ["#E74C3C" if v > 0 else "#27AE60" for v in values]


    fig, ax = plt.subplots(figsize=(6, 3))
    ax.barh(range(len(names)), values, color=bar_colors, alpha=0.85)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=9)
    ax.axvline(x=0, color="#2C3E50", linewidth=0.8)
    ax.set_xlabel("SHAP Value (Impact on Risk)", fontsize=9)
    ax.set_title("Top Risk Factor Contributions", fontsize=10, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf



# ── Main PDF generator ────────────────────────────────────────────────────────
def generate_pdf(prediction_result: dict, input_data: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=1.5*cm,  bottomMargin=1.5*cm
    )


    styles = getSampleStyleSheet()
    story  = []


    def S(name, **kw):
        return ParagraphStyle(name, parent=styles["Normal"], **kw)


    # FIXED: Increased all leading values by 4-6px to prevent overlapping
    title_s  = S("T",  fontSize=20, textColor=PRIMARY, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=6, leading=24)
    sub_s    = S("Su", fontSize=10, textColor=DARK,    fontName="Helvetica",      alignment=TA_CENTER, spaceAfter=6, leading=14)
    h1_s     = S("H1", fontSize=12, textColor=DARK,    fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=6, leading=16)
    body_s   = S("B",  fontSize=9,  textColor=DARK,    fontName="Helvetica",      leading=14, alignment=TA_JUSTIFY, spaceAfter=4)
    bold_s   = S("Bd", fontSize=9,  textColor=DARK,    fontName="Helvetica-Bold", leading=14)
    small_s  = S("Sm", fontSize=7.5,textColor=GRAY,    fontName="Helvetica-Oblique", alignment=TA_JUSTIFY, leading=12)
    box_s    = S("Bx", fontSize=9,  textColor=DARK,    fontName="Helvetica",      leading=14, spaceAfter=6,
                 backColor=colors.HexColor("#F4F6F7"), borderPadding=(10,10,10,10))


    age  = input_data.get("age", 40)
    sex  = "Male" if input_data.get("male", 1) == 1 else "Female"
    prob = prediction_result["probability"]
    risk = prediction_result["risk_level"]
    factors = prediction_result["top_risk_factors"]
    today = datetime.now().strftime("%B %d, %Y  %I:%M %p")
    risk_hex = {"LOW": "#27AE60", "MODERATE": "#E67E22", "HIGH": "#C0392B"}.get(risk, "#7F8C8D")


    def page_header(subtitle):
        story.append(Paragraph("CARDIONOVA", title_s))
        story.append(Paragraph(subtitle, sub_s))
        story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=6))
        meta = Table([[
            Paragraph(f"Age: <b>{age}</b>  |  Sex: <b>{sex}</b>  |  Generated: <b>{today}</b>", body_s),
            Paragraph(f'Risk: <font color="{risk_hex}"><b>{risk}</b></font>', bold_s)
        ]], colWidths=[12*cm, 5*cm])
        meta.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), LIGHT_GRAY),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("ALIGN",         (1,0), (1,0),   "RIGHT"),
        ]))
        story.append(meta)
        story.append(Spacer(1, 0.4*cm))


    # ── PAGE 1 — RISK SUMMARY ────────────────────────────────────────────────
    page_header("Cardiovascular Risk Assessment Report")


    gauge_buf = make_gauge_chart(prob, risk)
    story.append(RLImage(gauge_buf, width=8*cm, height=5*cm, hAlign="CENTER"))
    story.append(Spacer(1, 0.3*cm))


    story.append(Paragraph("What Does This Number Mean?", h1_s))
    story.append(Paragraph(get_risk_level_text(risk, prob), box_s))
    story.append(Spacer(1, 0.4*cm))


    # FIXED: Action steps with proper spacing
    story.append(Paragraph("What Should You Do Right Now?", h1_s))
    action_bg  = {"HIGH": "#FADBD8", "MODERATE": "#FEF9E7", "LOW": "#EAFAF1"}.get(risk, "#F4F6F7")
    
    # Use simple Paragraph with increased leading and spacers
    act_s = S("Act", fontSize=9, textColor=DARK, fontName="Helvetica", leading=16, spaceAfter=6)
    for step in get_action_steps(risk):
        para = Paragraph(step, act_s)
        # Wrap each paragraph in a mini table for background color
        mini_table = Table([[para]], colWidths=[17*cm])
        mini_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor(action_bg)),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 12),
            ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ]))
        story.append(mini_table)
        story.append(Spacer(1, 0.15*cm))


    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Your Top 3 Risk Factors", h1_s))
    story.append(Paragraph(
        "These are the health measurements contributing most to your current risk score. "
        "Improving these specific areas will have the biggest impact on reducing your risk.", body_s))
    story.append(Spacer(1, 0.3*cm))


    for i, f in enumerate(factors[:3], 1):
        is_bad   = "INCREASES" in f["direction"]
        card_bg  = "#FDEDEC" if is_bad else "#EAFAF1"
        icon     = "[HIGH RISK]" if is_bad else "[LOW RISK]"
        dir_word = "⬆ INCREASES YOUR RISK" if is_bad else "⬇ REDUCES YOUR RISK"
        plain_name, plain_desc = FEATURE_PLAIN_LANGUAGE.get(f["feature"], (f["feature"], "This factor contributes to your cardiovascular risk score."))
        card_s = S(f"C{i}", fontSize=9, textColor=DARK, fontName="Helvetica", leading=15,
                   backColor=colors.HexColor(card_bg), borderPadding=(10,10,10,10), spaceBefore=6, spaceAfter=6)
        story.append(Paragraph(
            f"<b>{icon} #{i}  {f['feature']}: {f['value']}</b>  —  <i>{dir_word}</i><br/>"
            f"<b>What is this?</b> {f['feature']} measures {plain_name}.<br/>{plain_desc}", card_s))


    story.append(PageBreak())


    # ── PAGE 2 — HEALTH NUMBERS ──────────────────────────────────────────────
    page_header("Your Health Numbers — How Do You Compare?")


    story.append(Paragraph("Your Values vs Healthy Benchmarks for Your Age", h1_s))
    story.append(Paragraph(
        f"The <b>red bars</b> show YOUR current values. The <b>green bars</b> show the maximum healthy "
        f"limit recommended for a {age}-year-old. When your red bar is taller than the green bar, "
        f"that value needs attention.", box_s))
    story.append(Spacer(1, 0.3*cm))
    story.append(RLImage(make_benchmark_chart(input_data, int(age)), width=15*cm, height=7*cm, hAlign="CENTER"))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(generate_observation_text(input_data, int(age)), body_s))
    story.append(Spacer(1, 0.4*cm))


    story.append(Paragraph("Your Measurements at a Glance", h1_s))
    metric_defs = [
        ("sysBP",     "Systolic BP (mmHg)"),
        ("diaBP",     "Diastolic BP (mmHg)"),
        ("totChol",   "Cholesterol (mg/dL)"),
        ("BMI",       "BMI"),
        ("glucose",   "Blood Sugar (mg/dL)"),
        ("heartRate", "Heart Rate (bpm)"),
    ]
    rows = [[Paragraph(f"<b>{h}</b>", bold_s) for h in ["Measurement", "Your Value", "Healthy Range", "Status"]]]
    for key, label in metric_defs:
        val = input_data.get(key, 0)
        lo, hi = get_healthy_range(int(age), key)
        if val > hi:
            status = Paragraph('<font color="#C0392B"><b>⚠ Above Range</b></font>', body_s)
        elif val < lo:
            status = Paragraph('<font color="#E67E22"><b>⚠ Below Range</b></font>', body_s)
        else:
            status = Paragraph('<font color="#27AE60"><b>✓ Normal</b></font>', body_s)
        rows.append([Paragraph(label, body_s), Paragraph(f"{val:.1f}", body_s),
                     Paragraph(f"{lo} – {hi}", body_s), status])
    t = Table(rows, colWidths=[5.5*cm, 3.5*cm, 4*cm, 4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), DARK),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ("BOX",           (0,0), (-1,-1), 0.5, GRAY),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, LIGHT_GRAY),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))


    story.append(Paragraph("Your Overall Health Risk Profile", h1_s))
    story.append(Paragraph(
        "This spider chart shows your health across 6 key areas. Think of the <b>center as perfect health</b>. "
        "The further a point stretches from the center, the more that area contributes to your heart risk. "
        "Your goal over time is to bring all 6 spokes as close to the center as possible.", box_s))
    story.append(Spacer(1, 0.2*cm))
    story.append(RLImage(make_radar_chart(input_data, int(age)), width=9*cm, height=9*cm, hAlign="CENTER"))


    story.append(PageBreak())


    # ── PAGE 3 — SHAP ANALYSIS ───────────────────────────────────────────────
    page_header("What Is Driving Your Risk Score?")


    story.append(Paragraph("How Did the AI Reach This Result?", h1_s))
    story.append(Paragraph(
        "Our AI model analysed all your health numbers and identified which ones are "
        "<b>pushing your risk UP</b> (shown in red) and which ones are "
        "<b>keeping your risk DOWN</b> (shown in green). "
        "The longer the bar, the bigger the impact that factor has on your personal score. "
        "This is calculated specifically for your values — not a generic result.", box_s))
    story.append(Spacer(1, 0.3*cm))
    story.append(RLImage(make_shap_chart(factors), width=14*cm, height=6*cm, hAlign="CENTER"))
    story.append(Spacer(1, 0.4*cm))


    story.append(Paragraph("What Each Factor Means — In Plain English", h1_s))
    for f in factors:
        is_bad   = "INCREASES" in f["direction"]
        icon     = "[+]" if is_bad else "[-]"
        card_bg  = "#FDEDEC" if is_bad else "#EAFAF1"
        dir_word = "INCREASES YOUR RISK" if is_bad else "REDUCES YOUR RISK"
        dir_hex  = "#C0392B" if is_bad else "#27AE60"
        plain_name, plain_desc = FEATURE_PLAIN_LANGUAGE.get(f["feature"], (f["feature"], "This factor contributes to your cardiovascular risk score."))
        card_s = S(f"SC{f['feature']}", fontSize=9, textColor=DARK, fontName="Helvetica",
                   leading=15, backColor=colors.HexColor(card_bg), borderPadding=(10,10,10,10), spaceBefore=6, spaceAfter=6)
        story.append(Paragraph(
            f"<b>{icon}  {f['feature']}</b>  |  Your value: <b>{f['value']}</b>  |  "
            f'<font color="{dir_hex}"><b>{dir_word}</b></font><br/>'
            f"<i>{f['feature']} is {plain_name}.</i> {plain_desc}", card_s))


    story.append(PageBreak())


    # ── PAGE 4 — ACTION PLAN ─────────────────────────────────────────────────
    page_header("Your Personalised Heart Health Action Plan")


    story.append(Paragraph("Immediate Steps to Take", h1_s))
    story.append(Paragraph(
        "Based on your risk level and specific health values, here are the most important "
        "actions to take right now — ranked by impact.", body_s))
    story.append(Spacer(1, 0.3*cm))
    
    # FIXED: Page 4 action steps with proper spacing
    step_s = S("St", fontSize=9.5, textColor=DARK, fontName="Helvetica", leading=16, spaceAfter=4)
    for step in get_action_steps(risk):
        story.append(Paragraph(step, step_s))
        story.append(Spacer(1, 0.2*cm))


    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Lifestyle Recommendations", h1_s))
    lifestyle = [
        [Paragraph("<b>Area</b>", bold_s), Paragraph("<b>Recommendation</b>", bold_s)],
        [Paragraph("🥗  Diet",     body_s), Paragraph("Follow the DASH diet — more fruits, vegetables, whole grains. Reduce salt to <5g/day and avoid processed foods.", body_s)],
        [Paragraph("🏃  Exercise", body_s), Paragraph("Aim for 150 minutes of moderate exercise per week. Even a 30-minute brisk walk 5 days a week makes a measurable difference.", body_s)],
        [Paragraph("🚭  Smoking",  body_s), Paragraph("Quitting smoking reduces cardiovascular risk by up to 50% within just one year. Ask your doctor about nicotine replacement.", body_s)],
        [Paragraph("😴  Sleep",    body_s), Paragraph("Poor sleep raises blood pressure and stress hormones. Aim for 7–8 hours of quality sleep per night.", body_s)],
        [Paragraph("💊  Medication",body_s),Paragraph("If prescribed BP, cholesterol, or diabetes medication — take it every day without skipping, even when you feel fine.", body_s)],
        [Paragraph("🧘  Stress",   body_s), Paragraph("Chronic stress raises blood pressure. Try yoga, deep breathing, or 10 minutes of daily meditation.", body_s)],
    ]
    lt = Table(lifestyle, colWidths=[3.5*cm, 13*cm])
    lt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), DARK),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, LIGHT_GRAY]),
        ("BOX",           (0,0), (-1,-1), 0.5, GRAY),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, LIGHT_GRAY),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))
    story.append(lt)
    story.append(Spacer(1, 0.5*cm))


    # Emergency box
    story.append(Paragraph(
        "<b>CALL 112 IMMEDIATELY IF YOU EXPERIENCE ANY OF THESE:</b><br/>"
        "* Chest pain, pressure, or tightness    * Sudden shortness of breath<br/>"
        "* Numbness or weakness in arm, face, or leg    * Sudden severe headache<br/>"
        "* Sudden dizziness, loss of balance, or blurred vision<br/>"
        "These are warning signs of a heart attack or stroke. Every minute matters.",
        S("Emrg", fontSize=9, textColor=colors.HexColor("#7B241C"), fontName="Helvetica-Bold",
          leading=15, backColor=colors.HexColor("#FADBD8"), borderPadding=(12,12,12,12), spaceAfter=8)
    ))


    story.append(Spacer(1, 0.5*cm))


    story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY, spaceAfter=8))
    story.append(Paragraph(
        "⚠ Medical Disclaimer: This report was generated by Cardionova, an AI-based cardiovascular risk prediction tool "
        "developed as a Minor Project at Medicaps University, Indore (2026). It is for informational and educational "
        "purposes ONLY. It does NOT constitute a medical diagnosis or professional medical advice. "
        "Always consult a qualified healthcare professional before making any health-related decisions.", small_s))


    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
