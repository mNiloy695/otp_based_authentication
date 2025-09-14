from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
# User=get_user_model()
class CustomUser(AbstractUser):
    activation_code=models.CharField(max_length=6,blank=True,null=True)
    pass_reset_code=models.CharField(max_length=6,blank=True,null=True)



class ForgotPasswordOTPModel(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='forgot_password')
    created_at=models.DateTimeField(auto_now_add=True)
    is_used=models.BooleanField(default=False)
    otp=models.CharField(max_length=6)
    def expired_otp(self):
        return timezone.now()>self.created_at+timedelta(minutes=5)
    