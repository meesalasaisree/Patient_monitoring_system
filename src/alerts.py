import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_alert(patient_id, hr, oxy):
    # --- 1. CONFIGURATION ---
    # NOTE: Use a Gmail "App Password", not your regular password.
    sender_email = "meesalasaisree@gmail.com"
    receiver_email = "323103282060.saisree@gvpcew.ac.in" # Can be the same as sender for testing
    app_password = "bykv mufn rusf atjz" # Your 16-digit App Password

    # --- 2. MESSAGE CONTENT ---
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"🚨 URGENT: Patient {patient_id} Critical Vitals"

    body = f"""
    HEALTH MONITORING ALERT
    -----------------------
    The Machine Learning model has detected a high-risk patient.
    
    Patient ID: {patient_id}
    Heart Rate: {hr} bpm
    Oxygen Saturation: {oxy}%
    
    Action Required: Please check the patient's vitals immediately.
    """
    message.attach(MIMEText(body, "plain"))

    # --- 3. SENDING PROCESS ---
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, app_password)
            server.send_message(message)
        print(f"✅ Email Alert Sent for Patient {patient_id}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")