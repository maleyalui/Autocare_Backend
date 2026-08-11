import resend
import os
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv('RESEND_API_KEY')


def send_verification_email(full_name, email, code):
    params: resend.Emails.SendParams = {
        "from": "Auto Care <onboarding@resend.dev>",
        "to": [email],
        "subject": "Your Auto Care verification code",
        "html": f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #e85d04; padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0;">Auto Care</h1>
            </div>
            <div style="background-color: #ffffff; padding: 30px; border-radius: 0 0 12px 12px; border: 1px solid #eee;">
                <h2 style="color: #333;">Hi {full_name}, verify your account</h2>
                <p style="color: #555;">Enter this code to complete your registration:</p>
                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                    <h1 style="color: #e85d04; font-size: 48px; letter-spacing: 10px; margin: 0;">{code}</h1>
                </div>
                <p style="color: #aaa; font-size: 13px;">This code expires in 10 minutes.</p>
            </div>
        </div>
        """
    }
    resend.Emails.send(params)


def send_welcome_email(full_name, email, role):
    if role == 'mechanic':
        subject = "Welcome to Auto Care — Mechanic Account Ready"
        body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #e85d04; padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0;">Auto Care</h1>
            </div>
            <div style="background-color: #ffffff; padding: 30px; border-radius: 0 0 12px 12px; border: 1px solid #eee;">
                <h2 style="color: #333;">Welcome, {full_name}!</h2>
                <p style="color: #555;">Your mechanic account is ready. Go online to start receiving job requests.</p>
                <a href="https://autocare-nine.vercel.app/login"
                   style="display: inline-block; background-color: #e85d04; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 10px;">
                    Go to Dashboard
                </a>
            </div>
        </div>
        """
    else:
        subject = "Welcome to Auto Care"
        body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #e85d04; padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0;">Auto Care</h1>
            </div>
            <div style="background-color: #ffffff; padding: 30px; border-radius: 0 0 12px 12px; border: 1px solid #eee;">
                <h2 style="color: #333;">Welcome, {full_name}!</h2>
                <p style="color: #555;">Your account is ready. Book car services across Nairobi instantly.</p>
                <a href="https://autocare-nine.vercel.app/login"
                   style="display: inline-block; background-color: #e85d04; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 10px;">
                    Get Started
                </a>
            </div>
        </div>
        """

    params: resend.Emails.SendParams = {
        "from": "Auto Care <onboarding@resend.dev>",
        "to": [email],
        "subject": subject,
        "html": body
    }
    resend.Emails.send(params)
