def send_verification_sms(phone_number, code):
    if phone_number.startswith('0'):
        phone_number = '+254' + phone_number[1:]
        
    message = f"Your Auto Care verification code is: {code}. It will expire in 10 minutes."
    
    try:
        sms.send(message, [phone_number])
    except Exception as e:
        print(f"Failed to send verification SMS: {e}")