from django.urls import path
from .views import *
from knox import views as knox_views



urlpatterns = [
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/',LoginAPI.as_view(),name='login'),
    path('api/logout/',knox_views.LogoutView.as_view(),name='logout'),
    path('api/logoutall/',knox_views.LogoutAllView.as_view(),name='logoutall'),

    path('api/change-password/',ChangePasswordView.as_view(),name='change-password'),
    path('verify-otp/', VerifyOTP.as_view(), name='verify-otp'),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(),name='request-reset-emai'),
    path('password-reset/<uidb64>/<token>/',PasswordTokenCheckAPI.as_view(),name='password-reset-confirm'),
    path('passwordset/',SetNewPasswordAPIView.as_view(),name='password-set-complete'),

    path('api/userstate/', UserStateAPI.as_view(), name='userstate'),

    path('api/recipe/', Recipeapi.as_view(), name='recipe'),
    path('profile/detail/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('workout-plan/json/', WorkoutPlanapijson.as_view(), name='workout-plan-json'),
    path('recipe/', Recipeapi.as_view(), name='recipe'),
    path('firestore-data/', FirestoreDataView.as_view(), name='firestore-data'),
    path('meal-plan/json/', MealPlanapijson.as_view(), name='meal-plan-json'),
    path('api/meals/<str:email>/', MealDataAPIView.as_view(), name='meal_data_api'),

]