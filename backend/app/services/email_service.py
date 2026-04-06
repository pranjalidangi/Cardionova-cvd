import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER     = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def send_report_email(recipient_email: str, pdf_bytes: bytes, risk_level: str, probability: float) -> bool:
    risk_emoji = {"LOW": "🟢", "MODERATE": "🟡", "HIGH": "🔴"}.get(risk_level, "⚪")
    subject    = f"Your Cardionova Heart Risk Report — {risk_emoji} {risk_level} RISK"

    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;background:#f8f9fa;padding:20px;">
      <div style="max-width:600px;margin:auto;background:white;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1);overflow:hidden;">
        <div style="background:#C0392B;padding:20px;text-align:center;">
          <h1 style="color:white;margin:0;">❤ Cardionova</h1>
          <p style="color:#fadbd8;margin:5px 0;">Cardiovascular Risk Assessment</p>
        </div>
        <div style="padding:30px;">
          <p style="font-size:16px;color:#2C3E50;">Dear User,</p>
          <p style="color:#555;line-height:1.6;">Your cardiovascular risk assessment is complete. Please find your personalised <strong>Cardionova Health Report</strong> attached.</p>
          <div style="background:#f8f9fa;border-left:4px solid #C0392B;padding:15px;margin:20px 0;border-radius:4px;">
            <p style="margin:0;font-size:20px;font-weight:bold;color:#C0392B;">{risk_emoji} {risk_level} RISK</p>
            <p style="margin:5px 0 0;color:#555;">10-Year CVD Probability: <strong>{probability*100:.1f}%</strong></p>
          </div>
          <p style="color:#555;">The attached PDF contains your risk gauge, health benchmarks, AI-based factor analysis, and a personalised action plan.</p>
          <div style="background:#fff3cd;border:1px solid #ffc107;padding:12px;border-radius:6px;margin:20px 0;">
            <p style="margin:0;font-size:13px;color:#856404;">⚠ <strong>Disclaimer:</strong> This report is for informational purposes only and does not constitute medical advice. Please consult a qualified healthcare professional.</p>
          </div>
          <p style="color:#555;">Stay heart healthy,<br><strong style="color:#C0392B;">The Cardionova Team</strong></p>
        </div>
        <div style="background:#f8f9fa;padding:15px;text-align:center;border-top:1px solid #eee;">
          <p style="color:#aaa;font-size:11px;margin:0;">Cardionova | Medicaps University Minor Project 2026<br>This is an automated message. Please do not reply.</p>
        </div>
      </div>
    </body></html>
    """

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"]    = f"Cardionova Reports <{GMAIL_USER}>"
    msg["To"]      = recipient_email
    msg.attach(MIMEText(html_body, "html"))

    part = MIMEBase("application", "pdf")
    part.set_payload(pdf_bytes)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", 'attachment; filename="Cardionova_Heart_Report.pdf"')
    msg.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, recipient_email, msg.as_string())

    return True
