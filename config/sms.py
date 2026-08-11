import africastalking
import os
from dotenv import load_dotenv

load_dotenv()

africastalking.initialize(
    username=os.getenv('AT_USERNAME'),
    api_key=os.getenv('AT_API_KEY')
)

sms = africastalking.SMS


def send_verification_sms(phone_number, code):
    if phone_number.startswith('0'):
        phone_number = '+254' + phone_number[1:]

    message = f"Your Auto Care verification code is: {code}. It expires in 10 minutes."

    try:
        sms.send(message, [phone_number])
        print(f"Verification SMS sent to {phone_number}")
    except Exception as e:
        print(f"Failed to send verification SMS: {e}")


def send_welcome_sms(full_name, phone_number, role):
    if phone_number.startswith('0'):
        phone_number = '+254' + phone_number[1:]

    if role == 'mechanic':
        message = f"Hi {full_name}! Welcome to Auto Care. Your mechanic account is ready. Log in and go online to start receiving job requests."
    else:
        message = f"Hi {full_name}! Welcome to Auto Care. Book garages, car washes, diagnostics and emergency help across Nairobi."

    try:
        sms.send(message, [phone_number])
        print(f"Welcome SMS sent to {phone_number}")
    except Exception as e:
        print(f"Failed to send welcome SMS: {e}")


def send_request_sms(phone_number, mechanic_name, service_name):
    if phone_number.startswith('0'):
        phone_number = '+254' + phone_number[1:]

    message = f"Good news! {mechanic_name} has accepted your {service_name} request on Auto Care. They will contact you shortly."

    try:
        sms.send(message, [phone_number])
    except Exception as e:
        print(f"Failed to send request SMS: {e}")
