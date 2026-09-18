from django.core.mail import send_mail
import random
from graduation.settings.base import *
from.models import CustomUser
from celery import shared_task

@shared_task
def  send_otp_via_email(email):
    subject='Your account verification email'
    otp=random.randint(1000,9999)
    message=f"Dear User,\n\nPlease verify your account by entering the following OTP {otp}"
    email_from= EMAIL_HOST
    send_mail(subject,message,email_from,[email])
    user_obj=CustomUser.objects.get(email=email)
    user_obj.otp=otp
    user_obj.save()
    
@shared_task
def send_welcome_email(email):
    subject='welcome to fit genie'
    message=f"Dear User,thanks for signing in our web"
    email_from= EMAIL_HOST
    send_mail(subject,message,email_from,[email])
    user_obj=CustomUser.objects.get(email=email)
    user_obj.save()


