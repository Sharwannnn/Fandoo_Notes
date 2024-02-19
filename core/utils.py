from . import mail
from flask_mail import Message
from settings import settings

def send_mail(user, email, token):
    msg = Message('Hello from the other side!', 
                  sender=settings.email_username, 
                  recipients=[email])
    msg.body = f"Hey {user}, sending you this email from my Flask app, Click to verify" \
                f" http://127.0.0.1:5000/api/user/verify?token={token}"
    mail.send(msg)
    return "Message sent!"