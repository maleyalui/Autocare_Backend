import resend
import os
from dotenv import load_dotenv

load_dotenv()
resend.api_key = os.getenv('RESEND_API_KEY')

def send_verification_email(full_name, email, code):
    subject = "Verify Your Auto Care Account"  # Added this so the code works
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
      <div style= "background-color: #385d04; padding: 20px; border-radius: 12px 12px 0 0 ; text-align: center;">
        <h1 style="color: white; margin: 0;">Auto Care</h1>
        </div>
        <div style= "background-color: #ffffff; padding: 30px; border-radius: 0 0 12px 12px; border: 1px solid #e0e0e0;">
        <h2 style="color: #333333;">Hello {full_name}, verify your account</h2>
        <p style="color: #555555;">Enter this code to complete your registration:</p>
        <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
            <h1 style="color: #e85d04; font-size: 48px; letter-spacing: 10px; margin: 0;">{code}</h1>
        </div>
        <p style="color: #aaa; font-size: 13px;">This code will expire in 10 minutes. If you did not request this, please ignore this email.</p>
        </div>
    </div>
    """
    
    
    params = {
        "from": "Auto Care <onboarding@resend.dev>",
        "to": [email],
        "subject": subject,
        "html": body
    }
    
    
    resend.Emails.send(params)
