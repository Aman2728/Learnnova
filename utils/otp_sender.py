# utils/otp_sender.py

from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings

# ==============================
# Send OTP via SMS (Twilio)
# ==============================
# def send_otp_sms(mobile, otp):
#     try:
#         client = Client(
#             settings.TWILIO_ACCOUNT_SID,
#             settings.TWILIO_AUTH_TOKEN
#         )

#         client.messages.create(
#             body=f"Your OTP is {otp}. Valid for 5 minutes.",
#             from_=settings.TWILIO_FROM_NUMBER,
#             to=f"+91{mobile}"
#         )

#         return True

#     except Exception as e:
#         print("Twilio Error:", e)
#         return False


# ==============================
# Send OTP via Email (SendGrid)
# ==============================
def send_otp_email(email, otp):
    try:
        message = Mail(
            from_email=settings.SENDGRID_FROM_EMAIL,
            to_emails=email,
            subject="Your OTP Code",
            html_content=f"""
                <p>Your OTP is:</p>
                <h2>{otp}</h2>
                <p>This OTP is valid for 5 minutes.</p>
            """
        )

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)

        return True

    except Exception as e:
        print("SendGrid Error:", e)
        return False
