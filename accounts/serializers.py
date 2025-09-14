from rest_framework import serializers
from django.contrib.auth import get_user_model

User=get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password=serializers.CharField(write_only=True)
    class Meta:
        model=User
        fields=['id','username','first_name','last_name','email','password','is_active','confirm_password']
        read_only_fields=['is_active']

    def validate(self,attrs):
            password=attrs.get('password',None)
            confirm_password=attrs.pop('confirm_password',None)
            email=attrs.get('email')
            if password and password!=confirm_password:
                raise serializers.ValidationError({"error":"password and confirm password not matched"})
            if email and User.objects.filter(email=email).exclude(id=self.instance.id if self.instance else None):
                raise serializers.ValidationError({"error":"The email already exists"})
            return attrs
        
    def create(self,validated_data):
            password=validated_data.pop('password')
            user=User(**validated_data)
            user.set_password(password)
            user.save()
            return user
        
    def update(self,instance,validated_data):
            password=validated_data.get("password",None)                 

            for attr,value in validated_data.items():
                setattr(instance,attr,value)
            if password:
                  validated_data.pop("password")
                  instance.set_password(password)
            
            instance.save()
            return  instance

            

class ActiveAccountSerializer(serializers.Serializer):
    activation_code=serializers.CharField(max_length=6)




#password change serializer


class PasswordChangeSerializer(serializers.Serializer):
     old_password=serializers.CharField(max_length=100)
     new_password=serializers.CharField(max_length=100)



#forget passsword serializer to check user


class ForgetPasswordSerializer(serializers.Serializer):
     email=serializers.CharField(max_length=100)


class ResetPasswordSerializer(serializers.Serializer):
     email=serializers.CharField(max_length=100)
     otp=serializers.CharField(max_length=6)
     new_password=serializers.CharField(max_length=100)


#login serialzier

class LoginSerializer(serializers.Serializer):
     username=serializers.CharField(max_length=100)
     password=serializers.CharField(max_length=100)
