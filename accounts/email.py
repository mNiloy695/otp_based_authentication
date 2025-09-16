from django.conf import settings
from django.core.mail import send_mail
import threading
from celery import shared_task
import time

def send_email(subject,message,receiver_email):
    print(f"threading {receiver_email} {message} {subject}")
    threading.Thread(
        target=send_mail,
        args=(subject, message, settings.EMAIL_HOST_USER,#[receiver_email])
    ).start())