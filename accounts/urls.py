from django.urls import path,include
from .views import RegistrationView,active_account_view,UserDetailView,PasswordChangeView,ForgetOTPPasswordView,ResetPasswordView,LoginView,LogoutView



urlpatterns = [
    path('register/',RegistrationView),
    path('<uid64>/<token>/activate/',active_account_view),
    path('<int:pk>/',UserDetailView),
    path('passwordchange/<int:pk>/',PasswordChangeView.as_view()),
    path('send_otp_for_password_reset/',ForgetOTPPasswordView.as_view()),
    path("reset_password/",ResetPasswordView.as_view()),
    path("login/",LoginView.as_view()),
    path("logout/",LogoutView.as_view()),
]
