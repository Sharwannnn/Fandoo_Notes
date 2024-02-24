from celery import Celery, Task,shared_task
from . import init_app as fapp
from flask_mail import Message
from . import mail
from settings import settings

def celery_init_app(app) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.conf.enable_utc=False
    celery_app.conf.timezone='Asia/Kolkata'
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

app=fapp()
celery=celery_init_app(app)

@shared_task
def celery_send_mail(user, email, token):
    # return "Mail sent successfully"
    try:
        print(f"Sending mail to {email}")
        msg = Message(sender=f"{settings.email_username}", recipients=[email])
        with open('message.txt') as file:
            file_content = file.read()
            file_content = file_content.format(user=user, base_url=settings.base_url, token=token, sender=settings.email_username)
            msg.body = file_content
        mail.send(msg)
        print("Mail sent successfully!")
        return f"Mail sent successfully to {email}"
    except Exception as e:
        print(f"An error occurred while sending mail to {email}: {e}")
        return f"Error sending mail to {email}: {e}"
    