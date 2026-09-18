from rest_framework import serializers
from .models import CustomUser,userstate,Profile,GenAI,wGenAI
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from.Genai import*

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','email','password']
        

class userstateSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(write_only=True)  # Field to accept user email
    
    class Meta:
        model = userstate
        fields = ['user_email', 'height', 'weight', 'age', 'bmi', 'allergies',
                  'activity_level', 'fitness_goals', 'Work_Out_Level', 'gender']

    def create(self, validated_data):
        # Get the user's email from the request data
        user_email = validated_data.pop('user_email')
        
        try:
            # Retrieve the CustomUser object using the email
            user = CustomUser.objects.get(email=user_email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        # Create userstate object associated with the retrieved user
        userstate_instance = userstate.objects.create(
            user=user,
            height=validated_data['height'],
            weight=validated_data['weight'],
            bmi=validated_data['bmi'],
            allergies=validated_data['allergies'],
            age=validated_data['age'],
            gender=validated_data['gender'],
            activity_level=validated_data['activity_level'],
            fitness_goals=validated_data['fitness_goals'],
            Work_Out_Level=validated_data['Work_Out_Level'],
        )
        return userstate_instance

            
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:

        model=CustomUser
        fields=['id','name','email','password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
           
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
        )
        user.save()
        return user
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user','first-name','last-name','age','gender','Email','Avatar','bio','created_at','Update_at']


class ChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
     
     model=CustomUser
     fields=['old_password','new_password']

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class SendOTPSerializer(serializers.ModelSerializer):
    class Meta:

        model = CustomUser
        fields = ['email']
    model = CustomUser
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Check if the email exists in the CustomUser model.
        """
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is associated with this email address.")
        return value
    


class VerfiyOTPSerializer(serializers.Serializer):
    class Meta:

        model = CustomUser
        fields = ['email','otp']
    email = serializers.EmailField()
    otp = serializers.CharField()

    def create(self, validated_data):
        user = CustomUser.objects.get(
            email=validated_data['email'],
        )
        user.otp = validated_data['otp']
        user.save()
        return user
        
class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    class Meta:

        model = CustomUser
        fields = ['email']
        
class SetNewPasswordSerializer(serializers.Serializer):
    password=serializers.CharField(write_only=True)
    token=serializers.CharField(write_only=True)
    uidb64=serializers.CharField(write_only=True)
    
    class Meta:
        fields=['password','token','uidb64']
    
    def validate(self, attrs):
        password=attrs.get('password')
        token=attrs.get('token')
        uidb64=attrs.get('uidb64')
        
        # Call the parent class's validate method
        attrs = super().validate(attrs)
        
        try:
            id=force_str(urlsafe_base64_decode(uidb64))
            user=CustomUser.objects.get(id=id)
            
            if not PasswordResetTokenGenerator().check_token(user,token):
                raise serializers.ValidationError("Invalid or expired link",401)
            
            user.set_password(password)
            user.save()
            
            # Return the validated attributes
            return attrs
        
        except Exception as e:
            raise serializers.ValidationError("Invalid or expired link",401)
        
# class MealPlanSerializer(serializers.Serializer):
#      email = serializers.EmailField()
class MealPlanSerializer(serializers.Serializer):
    email = serializers.EmailField()

    

    def create(self, validated_data):
        user_email = validated_data['email']
        user = CustomUser.objects.get(email=user_email)
        ai = genrativemealplan(user_email)
        meal_plan = ai.get_nutritionJSON()

        genai_instance = GenAI.objects.create(
            user=user,
            data=meal_plan
        )
        
        return genai_instance


class GenAISerializer(serializers.ModelSerializer):
    class Meta:
        model = GenAI
        fields = ['user', 'data']

class wGenAISerializer(serializers.ModelSerializer):
    class Meta:
        model = GenAI
        fields = ['user', 'data']

class WorkoutPlanSerializer(serializers.Serializer):
     
    email = serializers.EmailField()

    

    def create(self, validated_data):
        user_email = validated_data['email']
        user = CustomUser.objects.get(email=user_email)
        ai = genrativemealplan(user_email)
        workout_plan = ai.get_workout()

        genai_instance = wGenAI.objects.create(
            user=user,
            data=workout_plan
        )
        
        return genai_instance
class RecipePlanSerializer(serializers.Serializer):
     email = serializers.EmailField()
     image=serializers.FileField()

# user/serializers.py


class MealSerializer(serializers.Serializer):
    meal_type = serializers.CharField()
    name = serializers.CharField()
    calories = serializers.IntegerField()
    protein = serializers.IntegerField()
    carbs = serializers.IntegerField()

class TotalSerializer(serializers.Serializer):
    calories = serializers.IntegerField()
    protein = serializers.IntegerField()
    carbs = serializers.IntegerField()

class MealResponseSerializer(serializers.Serializer):
    categorized_meals = serializers.DictField(child=MealSerializer())
    total = TotalSerializer()
