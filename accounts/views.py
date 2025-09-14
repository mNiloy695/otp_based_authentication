from django.shortcuts import render
from rest_framework.decorators import api_view
from .serializers import RegistrationSerializer,ActiveAccountSerializer,PasswordChangeSerializer,ForgetPasswordSerializer,ResetPasswordSerializer,LoginSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
import random
from .email import send_email
from rest_framework.response import Response
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from .models import ForgotPasswordOTPModel
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from rest_framework import permissions
User=get_user_model()
# Create your views here.

#OTP generator
def Auto_Code_genarator():
    code=random.randint(100000,999999)
    return code
@api_view(['POST'])
def RegistrationView(request):

       serializer=RegistrationSerializer(data=request.data)
       if serializer.is_valid():
         user=serializer.save(is_active=False)
         uid=urlsafe_base64_encode(force_bytes(user.pk))
         token=default_token_generator.make_token(user)
         subject="Activation Code"
         code=Auto_Code_genarator()
         user.activation_code=code
         user.save()
         message=f"Your OTP is {code}"
         receiver_email=user.email
        
         send_email(subject,message,receiver_email)
 
         return Response({
            "message": "Account created successfully. Check your email for the activation code.",
            "redirect_url": f"http://127.0.0.1:8000/account/{uid}/{token}/activate/"
             }, status=status.HTTP_201_CREATED)
       else:
          return Response(serializer.errors)
   


@api_view(['POST'])
def active_account_view(request,uid64,token):
    serializer=ActiveAccountSerializer(data=request.data)
    if serializer.is_valid():
        code=serializer.validated_data['activation_code']
        try:
         uid=urlsafe_base64_decode(uid64).decode()
         user=User.objects.get(activation_code=code,pk=uid)
        except (User.DoesNotExist,ValueError,TypeError):
          return Response("invalid code")
        
        if default_token_generator.check_token(user,token):
           if not user.is_active:
             user.is_active=True
             user.activation_code=0
             user.save()
             return Response({"success": "Account activated successfully"}, status=status.HTTP_200_OK)
           else:
              return Response({"info": "Account already active"}, status=status.HTTP_200_OK)
        else:
           return Response({"error": "Activation link is invalid or expired"}, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['GET','PATCH','PUT'])
def UserDetailView(request,pk):
   if not request.user.is_authenticated:
      return Response("Only Authenticated user Can access UserDeatail View")
   
   try:
        user_detail = User.objects.get(pk=pk)
        serializer=RegistrationSerializer(user_detail)
   except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
   
   if request.method=='GET':
     
      if user_detail==request.user:
         return Response(serializer.data)
      else:
         return Response("only owner can get")
   
   if request.method in ['PUT','PATCH']:
      
      if not (user_detail==request.user):
         return Response("Only Owner can update his data or profile")
      serializer=RegistrationSerializer(user_detail,data=request.data,partial=True)
      if serializer.is_valid():
         user=serializer.save()
         return Response("your data updated")
    
   return Response(serializer.errors)


# password change view


class PasswordChangeView(APIView):
   def post(self,request,pk):
      try:
         user=User.objects.get(pk=pk)
      except User.DoesNotExist:
         return Response("user doesn't exitst")
      if user != request.user:
         return Response("You can not Change This Password only Owner can change it")
      serializer=PasswordChangeSerializer(data=request.data)
      if serializer.is_valid():
         old_password=serializer.validated_data.get('old_password',None)
         new_password=serializer.validated_data.get('new_password',None)
         if not user.check_password(old_password):
            return Response("Old Password not matched")
         user.set_password(new_password)
         user.save()
         return Response("your password changed")
      return Response(serializer.errors)
         



class ForgetOTPPasswordView(APIView):
   def post(self,request):
      serializer=ForgetPasswordSerializer(data=request.data)
      if serializer.is_valid():
         email=serializer.validated_data.get('email')
         try:
            user=User.objects.get(email=email)
         except User.DoesNotExist:
            return Response("User Doesn't exists")
         code =Auto_Code_genarator()
         otp_model=ForgotPasswordOTPModel(
            user=user,
            otp=code
         )
         otp_model.save()
         subject="Password Reset OTP"
         message=f"Hi {user.username} your password reset otp is {code} .It Valid for 5 munites"
         receiver_email=user.email
         send_email(subject,message,receiver_email)
         return Response({
            "message":"OTP Send To Your email Check it",
            "password_reset_url":"http://127.0.0.1:8000/account/reset_password/"
         })

         
      return Response(serializer.errors)





class ResetPasswordView(APIView):
   def post(self,request):
      serializer=ResetPasswordSerializer(data=request.data)
      if serializer.is_valid():
         email=serializer.validated_data.get('email')
         otp=serializer.validated_data.get('otp')
         new_password=serializer.validated_data.get('new_password')

         try:
            user=User.objects.get(email=email)
         except User.DoesNotExist:
            return Response("User Doesn't exists")
         
         try:
            otp_model=ForgotPasswordOTPModel.objects.filter(user=user,otp=otp).latest('created_at')
         except ForgotPasswordOTPModel.DoesNotExist:
            return Response("Invalid OTP")
         
         if otp_model.is_used or otp_model.expired_otp():
            return Response("Invalid OTP")
         
         otp_model.is_used=True
         otp_model.save()
         user.set_password(new_password)
         user.save()
         return Response("Password Successfully Reset")
      return Response(serializer.errors)
      


class LoginView(APIView):
   def post(self,request):
      serializer=LoginSerializer(data=request.data)
      if serializer.is_valid():
         username=serializer.validated_data.get('username')
         password=serializer.validated_data.get('password')

         user=authenticate(username=username,password=password)

         if user:
            refresh=RefreshToken.for_user(user)
            return Response({
               "message":"successfully login",
               "user":{
                  "id":user.id,
                  "username":user.username,
                  "email":user.email
               },
               "access":str(refresh.access_token),
               "refresh":str(refresh)
            })
         return Response("Invalid User or Password",status=401)
      return Response(serializer.errors,status=400)
   


class LogoutView(APIView):
   permission_classes = [permissions.IsAuthenticated]
   def post(self,request):
      refresh=request.data.get('refresh')
      if not refresh:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )      
      
      try:
         token=RefreshToken(refresh)
         print(token)
         token.blacklist()
      except TokenError:
         return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )
      
      return Response(
            {"message": "Logout successfully"},
            status=status.HTTP_205_RESET_CONTENT
        )
