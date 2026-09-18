from django.views import View
from rest_framework import status, generics,permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import*
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from .models import CustomUser,Profile
from.emails import*
from.Genai import genrativemealplan
from django.http import JsonResponse
from.firebase import*
from rest_framework.exceptions import NotFound
from django.conf import settings
from collections import defaultdict
from django.utils.encoding import smart_str,force_str,smart_bytes,DjangoUnicodeDecodeError
class SendOTPAPI(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.get(email=email)  
            
            # Send OTP via email
            send_otp_via_email(serializer.data['email'])
            
            return Response({
                'status': 200,
                'message': 'OTP sent successfully to the provided email address.',
                'data': {'email': email}
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': 400,
            'message': 'Invalid data',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class RegisterAPI(generics.GenericAPIView):
  serializer_class = RegisterSerializer
#  

  def post(self,request,*args,**kwargs):
       serializer=self.get_serializer(data=request.data)
       serializer.is_valid(raise_exception=True)
       user=serializer.save()
       return Response({
          "user":UserSerializer(user,context=self.get_serializer_context()).data,
          "token": AuthToken.objects.create(user)[1],
          "message":'registeration successfull please check your email ',
          },status=status.HTTP_201_CREATED)
  
      
class VerifyOTP(APIView):
    def post(self, request):
        data = request.data
        serializer = VerfiyOTPSerializer(data=data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            user = CustomUser.objects.filter(email=email).first()
            
            if user is None:
                return Response({
                    'status': 400,
                    'message': 'No User Found with this Email Id.',
                    'data': 'invalid email',
                }, status=status.HTTP_400_BAD_REQUEST)

            if user.otp != otp:
                return Response({
                    'status': 400,
                    'message': 'Invalid OTP. Please Try Again Later.',
                    'data': 'Wrong OTP',
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.is_verfied = True
            user.save()
            send_welcome_email(email)
            
            return Response({
                'status': 200,
                'message': 'Account verified',
                'data': serializer.data,
            }, status=status.HTTP_200_OK)

        return Response({
            'status': 400,
            'message': 'Something went wrong',
            'data': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
   

  
class LoginAPI(KnoxLoginView):
   permission_classes=(permissions.AllowAny,)

   def post(self,request,format=None):
    serializer=AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user=serializer.validated_data['user']
    login(request,user)
    response= super(LoginAPI,self).post(request,format=None)
    response_data = response.data
    response_data['user_id'] = user.id  # Add the user ID to the response

    return Response(response_data)
  
   
   
class ProfileDetailView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        email = self.request.query_params.get('email')
        if not email:
            raise serializers.ValidationError("Email not provided")
        
        try:
            user = CustomUser.objects.get(email=email)
            return Profile.objects.get(user=user)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found")
        except Profile.DoesNotExist:
            raise serializers.ValidationError("Profile not found")

class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    def get_object(self):
        user_email = self.request.user.email
        try:
            user = CustomUser.objects.get(email=user_email)
            return user.profile
        except CustomUser.DoesNotExist:
            raise NotFound('User not found.')
        except Profile.DoesNotExist:
            raise NotFound('Profile not found.')


class ChangePasswordView(generics.UpdateAPIView):
 serializer_class = ChangePasswordSerializer
 model=CustomUser
 permission_classes=(IsAuthenticated,)
 def  get_object(self, queryset=None):
   obj=self.request.user
   return obj
 def update(self, request, *args, **kwargs):
   self.object=self.get_object()
   serializer=self.get_serializer(data=request.data)
   if serializer.is_valid():
  
     if not self.object.check_password(serializer.data.get("old_password")):
       return Response({"old_password":["wrong password"]},status=status.HTTP_400_BAD_REQUEST)
     self.object.check_password(serializer.data.get("new_password"))
     self.object.save()
     response={
       'status':'success',
       'code':status.HTTP_200_OK,
       'message':'Password updated successfully',
       'data':[]
     }
     return Response(response)
   return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
 
class RequestPasswordResetEmail(generics.GenericAPIView):
   serializer_class = ResetPasswordEmailRequestSerializer
   def post(self,request):
    serializer=self.serializer_class(data=request.data)
    email=request.data['email']
    absurl = ''
    if CustomUser.objects.filter(email=email).exists():
        user=CustomUser.objects.get(email=email) 
        uidb64=urlsafe_base64_encode(smart_bytes(user.id))
        token=PasswordResetTokenGenerator().make_token(user)                             
        current_site=get_current_site(
            request=request).domain
        relativeLink=reverse('password-reset-confirm',
                             kwargs={'uidb64':uidb64,'token':token})              
        absurl='http://'+ current_site+relativeLink
    subject='Reset your password'
    message=f"Dear User,click here to reset your password {absurl}"
    email_from= settings.EMAIL_HOST
    send_mail(subject,message,email_from,[email]) 
    user_obj=CustomUser.objects.get(email=email)
    user_obj.save()
    return Response({
        'success':'we have sent a link to resest your password please check your email'},
        status=status.HTTP_200_OK)
     
class PasswordTokenCheckAPI(generics.GenericAPIView):
  def get(self,request,uidb64,token):
    try :
      id=smart_str(urlsafe_base64_decode(uidb64))
      user=CustomUser.objects.get(id=id)
      if not PasswordResetTokenGenerator().check_token(user,token):
        return Response({'error':'This is an invalid or expired URL.'},
                        status=status.HTTP_401_UNAUTHORIZED)
      return Response({'success':True,
                       'message':'credentials valid',
                       'uidb64':uidb64,
                       'token':token},
                       status=status.HTTP_200_OK)

      
    except DjangoUnicodeDecodeError as identifier:
      return Response({'error':'There was an error decoding the URL.'},
                      status=status.HTTP_400_BAD_REQUEST)
      
class SetNewPasswordAPIView(generics.GenericAPIView):
  serializer_class=SetNewPasswordSerializer
  def patch(self,request):
    serializer=self.serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'success':True,
                     'message':'password reset success'},
                     status=status.HTTP_200_OK)
  

class UserStateAPI(generics.GenericAPIView):
  
  def post(self,request,*args,**kwargs):
      #  user = self.request.user
        
        # Add the user's email to the request data
      #  request.data['user_email'] = user.email
        
       serializer = self.get_serializer(data=request.data)
       serializer.is_valid(raise_exception=True)
       userstate_instance = serializer.save()
       return Response({
          "user":userstateSerializer(userstate_instance,context=self.get_serializer_context()).data,
          "message":'user data has been created',
          },status=status.HTTP_201_CREATED)
  

class MealPlanapijson(generics.GenericAPIView):
    serializer_class = MealPlanSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                genai_instance = serializer.save()
                send_to_firestore(genai_instance)
                
                response_serializer = GenAISerializer(genai_instance)
                # categorize_and_calculate_meals_from_db()
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            
            except CustomUser.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WorkoutPlanapijson(generics.GenericAPIView):
    serializer_class = WorkoutPlanSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                genai_instance = serializer.save()
                send_to_firestorew(genai_instance)
                response_serializer = wGenAISerializer(genai_instance)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class Recipeapi(generics.GenericAPIView):
    serializer_class = RecipePlanSerializer
    def post(self,request,*args,**kwargs):
      email=request.data['email']
      image=request.data['image']
      data=genrativemealplan(email).get_recipe(image)
      return Response(data,status=status.HTTP_200_OK)
    

class FirestoreDataView(View):
    serializer_class = userstateSerializer
    serializer_class2 = RegisterSerializer

    def get(self, request, *args, **kwargs):
        doc_ids = get_all_document_ids('usersData')
        if not doc_ids: 
            return JsonResponse({'error': 'No documents found'}, status=404)
        
        response_data = []  # List to collect the response data for all documents

        for doc_id in doc_ids:
            doc_data = get_firestore_data(doc_id)
            if doc_data:
                email = get_value_from_key(doc_data, 'email')

                # Retrieve or create the user based on email
                user1 = CustomUser.objects.filter(email=email).first()

                # If user doesn't exist, create a new user with a random password and other fields
                if not user1:
                    user1 = CustomUser.objects.create(
                        email=email,
                        password=generate_random_password(16),
                        name=get_value_from_key(doc_data, 'firstName'),
                    )

                # Serialize the registration data
                serializer2 = self.serializer_class2(user1)

                # Create or get the userstate
                userstate_instance, _ = userstate.objects.get_or_create(
                    user=user1,
                    height=get_value_from_key(doc_data, 'height'),
                    weight=get_value_from_key(doc_data, 'weight'),
                    bmi=calculate_bmi(get_value_from_key(doc_data, 'weight'), get_value_from_key(doc_data, 'height')),
                    allergies=get_value_from_key(doc_data, 'allergies'),
                    age=get_value_from_key(doc_data, 'age'),
                    gender=get_value_from_key(doc_data, 'gender'),
                    activity_level=get_value_from_key(doc_data, 'activity_level'),
                    fitness_goals=get_value_from_key(doc_data, 'fitness_goal'),
                    Work_Out_Level=get_value_from_key(doc_data, 'work_out_level'),
                )

                # Serialize the userstate instance data
                serializer = self.serializer_class(userstate_instance)

                # Collect the serialized data into response_data
                response_data.append({
                    'userstate': serializer.data,
                    'register': serializer2.data
                })

        # If response_data has content, return the final JsonResponse
        if response_data:
            return JsonResponse(response_data, safe=False, status=200)
        else:
            return JsonResponse({'error': 'No valid data processed'}, status=404)
        

class MealDataAPIView(APIView):
    def get(self, request, email):
        # Call the function to process and categorize meals for the specified user
        result = self.categorize_and_calculate_meals_from_db(email)
        
        # Check if the result is an error message (when no user or meal data is found)
        if isinstance(result, dict) and 'error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        # Return the result
        return Response(result, status=status.HTTP_200_OK)

    def categorize_and_calculate_meals_from_db(self, email):
        categorized_meals = defaultdict(list)
        total = {'calories': 0, 'protein': 0, 'carbs': 0}
        

        # Get the user instance by email
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return {'error': f'User with email {email} not found'}

        # Get GenAI data for the specific user
        genai_data = GenAI.objects.filter(user=user)

        if not genai_data:
            return {'error': 'No meal data found for this user'}

        seen_meals = set()  # Set to track unique meals
        for genai in genai_data:
            meal_data = genai.data  # Assuming 'data' contains meal details as a string

            # Split the meal data based on lines or known meal types (e.g., Breakfast, Lunch, etc.)
            meal_lines = meal_data.split('\n')

            for line in meal_lines:
                meal_type = None
                # Identify the meal type based on the start of the line
                if line.startswith('Breakfast') | line.startswith('breakfast'):
                    meal_type = 'breakfast'
                elif  line.startswith('Lunch') | line.startswith('lunch'):
                    meal_type = 'lunch'
                elif  line.startswith('Snack 1') | line.startswith('snack1'):
                    meal_type = 'snack1'
                elif  line.startswith('Snack 2') | line.startswith('snack2'):
                    meal_type = 'snack2'
                elif  line.startswith('Dinner') | line.startswith('dinner'):
                    meal_type = 'dinner'

                if meal_type:
                    # Match meal details
                    meal_details = re.match(
                        r"(.+?)\s\((\d+)\scalories,\s(\d+)g\sprotein,\s(\d+)g\scarbs\)", line
                    )
                    if meal_details:
                        name = meal_details.group(1).strip()
                        calories = int(meal_details.group(2))
                        protein = int(meal_details.group(3))
                        carbs = int(meal_details.group(4))

                        # Create a unique key for this meal based only on type and name
                        meal_key = (meal_type, name)
                        if meal_key not in seen_meals:
                            seen_meals.add(meal_key)  # Mark this meal as seen

                            # Add meal to categorized meals
                            categorized_meals[meal_type].append({
                                'meal_type': meal_type.capitalize(),
                                'name': name,
                                'calories': calories,
                                'protein': protein,
                                'carbs': carbs
                            })

                            # Accumulate totals
                            total['calories'] += calories
                            total['protein'] += protein
                            total['carbs'] += carbs

        # Return the aggregated results
        return {
            'categorized_meals': categorized_meals,
            'total': total
        }

