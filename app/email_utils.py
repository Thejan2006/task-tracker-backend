import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# load .env file 
load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

# genarte random 6 digit otp code
def generate_otp() -> str:
    return str(random.randint(100000, 999999))

def send_otp_email(email_to: str, otp_code: str): # send otp email to user
    subject = "Verify Your Account - Task Tracker App"
    body = f"""
    <h2>Welcome to Task Tracker App!</h2>
    <p>Please use the following 6-digit OTP code to verify your account:</p>
    <h1 style="color: #4F46E5; letter-spacing: 4px;">{otp_code}</h1>
    <p>This code will expire shortly. Do not share this with anyone.</p>
    """
    
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = MAIL_USERNAME
    message["To"] = email_to
    
    # set html type for the email body
    html_part = MIMEText(body, "html")
    message.attach(html_part)
    
    # sent gamil using SMTP server
    try:
        # Gmail Port 587 (TLS)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Encrypted connection 
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_USERNAME, email_to, message.as_string())
        server.quit()
        print(f"OTP successfully sent to {email_to}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False