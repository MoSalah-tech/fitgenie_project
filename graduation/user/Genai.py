import google.generativeai as genai
from graduation.settings.base import *
from.models import*
import PIL.Image
from celery import shared_task
import firebase_admin
from firebase_admin import credentials, firestore
import json
import re
import logging

     
class genrativemealplan:
    
    def __init__(self, user_email):
        self.queryset = userstate.objects.filter(user__email=user_email).first()
        if not self.queryset:
            raise ValueError(f"User state data not found for the given email: {user_email}")

        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        self.data = f"""my Age is {self.queryset.age}, 
        Weight {self.queryset.weight} kg,
        Height {self.queryset.height} cm, 
        BMI {self.queryset.bmi}, 
        Allergies: {self.queryset.allergies},
        activity_level: {self.queryset.activity_level},
        Fitness Goals: {self.queryset.fitness_goals},
        Work Out Level: {self.queryset.Work_Out_Level},
        Gender: {self.queryset.gender}"""
        self.meal_data = ""
        logging.basicConfig(level=logging.DEBUG)
        
    def get_nutritionJSON(self):
        logging.debug(f"Data received for meal plan generation: {self.data}")
        self.prompt = f"""
        Question: Generate a complete meal plan for this person data
        data : {self.data}

        Answer: Let's think step by step.

        IMPORTANT NOTES :
         - calculate for each meal the number of calories and protein and carbs
         - don't print the person data just give me the plan
         - and generate random meals
         - don't generate meals from Allergies
         - Allergies are meals that user don't like
         - make it string the output as follow 
         breakfast:data,/n
         lunch:data,/n
         snack1:data,/n
         snack2:data,/n
         dinner:data,/n
         total_calories,/n
         total_protein,/n
         total_carbs,/n
         like this example:
         Breakfast: Oatmeal with berries and nuts  (350 calories, 20g protein, 50g carbs) /nLunch: Grilled chicken salad with quinoa and vegetables (450 calories, 30g protein, 40g carbs)/n Snack 1: Protein shake (200 calories, 25g protein, 10g carbs) /n Snack 2: Apple with peanut butter (250 calories, 10g protein, 30g carbs)/n Dinner: Salmon with roasted vegetables and brown rice (400 calories, 35g protein, 45g carbs) /n Total Calories: 1650 Total Protein: 120g Total Carbs: 175g
         we can design a meal plan with quantities consisting of three meals and 
         two snacks per day, focus on allergies, calories intake per day and fitness goal
        """

        response = self.model.generate_content(self.prompt)
        self.meal_data = response.text

        return self.meal_data
      
    def get_nutrition(self):
       self.prompt = f"""
        Question: Generate a complete meal plan for this person data
        data : {self.data}

        Answer: Let's think step by step.

        IMPORTANT NOTES :
         - calculate for each meal the number of calories and protein and carbs
         - don't print the person data just give me the plan
         - and generate random meals
         - don't generate meals from Allergies
         - Allergies are meals that user don't like
         - make it string the output as follow 
         breakfast:data,/n
         lunch:data,/n
         snack1:data,/n
         snack2:data,/n
         dinner:data,/n
         total_calories,/n
         total_protein,/n
         total_carbs,/n
         like this example:
         Breakfast: Oatmeal with berries and nuts  (350 calories, 20g protein, 50g carbs) /nLunch: Grilled chicken salad with quinoa and vegetables (450 calories, 30g protein, 40g carbs)/n Snack 1: Protein shake (200 calories, 25g protein, 10g carbs) /n Snack 2: Apple with peanut butter (250 calories, 10g protein, 30g carbs)/n Dinner: Salmon with roasted vegetables and brown rice (400 calories, 35g protein, 45g carbs) /n Total Calories: 1650 Total Protein: 120g Total Carbs: 175g
         we can design a meal plan with quantities consisting of three meals and 
         two snacks per day, focus on allergies, calories intake per day and fitness goal
        """

       response = self.model.generate_content(self.prompt)
       self.meal_data = response.text  
       return self.meal_data

       

    def get_workout(self):
        
        self.prompt=f"""
        


        I'd like you to generate a workout plan based on the user data and diet plan provided. Please ensure that the user data and diet plan are not included in the output, but instead, use them to create a personalized workout plan that complements the user's nutritional intake.

        Here are the details you need to consider:

        User data: {self.data}
        Diet plan: {self.meal_data}
        Based on this information, please generate a workout plan that includes the following:

        Type of exercises: [e.g. cardio, strength training, flexibility, or a combination]
        Duration and frequency of workouts: [e.g. 30 minutes, 3 times a week]
        Intensity level: [e.g. low, moderate, or high]
        Specific exercises or routines: [e.g. squats, lunges, push-ups, or yoga poses]
        Please ensure that the workout plan is safe, effective, and tailored to the user's fitness level and goals. Thank you!

        IMPORTANT NOTES : 
        -Include the upcoming data into gathering information but don't print it.
        -make it as string format 
        make it like this example with the same symbols Type of exercises: Strength-training, cardio, flexibility / Duration :60 minutes & frequency-of-workouts:  4 times a week / Intensity level: Moderate to high Specific exercises / routines: Squats (3 sets of 10 reps) - 100 calories - Lunges (3 sets of 10 reps per leg) - 80 calories - Push-ups (3 sets of 10 reps) - 70 calories - Pull-ups (3 sets of 10 reps) - 60 calories - Bench press (3 sets of 10 reps) - 80 calories - Overhead press (3 sets of 10 reps) - 70 calories - Rows (3 sets of 10 reps) - 60 calories - Bicep curls (3 sets of 10 reps) - 50 calories - Triceps extensions (3 sets of 10 reps) - 40 calories + Cardio (30 minutes of running or cycling) - 250 calories + Flexibility (10 minutes of stretching) - 30 calories   
        please dont change the symbols that seperate between any thing 
        -Please While Printing Exclude anything written in this prompt except the work out data.
        -Only print Type of exercises, Duration and frequency of work outs, Intensity level, Specific exercises or routines.
        -calculate the burnt calories per each part of the workout on average
        """

        response = self.model.generate_content(self.prompt)
        workout_data = (response.text)
        return workout_data
  
    def get_workoutjson(self):
        
        self.prompt=f"""
        


        I'd like you to generate a workout plan based on the user data and diet plan provided. Please ensure that the user data and diet plan are not included in the output, but instead, use them to create a personalized workout plan that complements the user's nutritional intake.

        Here are the details you need to consider:

        User data: {self.data}
        Diet plan: {self.meal_data}
        Based on this information, please generate a workout plan that includes the following:

        Type of exercises: [e.g. cardio, strength training, flexibility, or a combination]
        Duration and frequency of workouts: [e.g. 30 minutes, 3 times a week]
        Intensity level: [e.g. low, moderate, or high]
        Specific exercises or routines: [e.g. squats, lunges, push-ups, or yoga poses]
        Please ensure that the workout plan is safe, effective, and tailored to the user's fitness level and goals. Thank you!

        IMPORTANT NOTES : 
        -Include the upcoming data into gathering information but don't print it.
        -make it as string format 
        make the output like this example:
        Type of exercises: Strength training, cardio, flexibility
Duration and frequency of workouts: 60 minutes, 4 times a week
Intensity level: Moderate to high
Specific exercises or routines:
- Squats (3 sets of 10 reps) - 100 calories
- Lunges (3 sets of 10 reps per leg) - 80 calories
- Push-ups (3 sets of 10 reps) - 70 calories
- Pull-ups (3 sets of 10 reps) - 60 calories
- Bench press (3 sets of 10 reps) - 80 calories
- Overhead press (3 sets of 10 reps) - 70 calories
- Rows (3 sets of 10 reps) - 60 calories
- Bicep curls (3 sets of 10 reps) - 50 calories
- Triceps extensions (3 sets of 10 reps) - 40 calories
- Cardio (30 minutes of running or cycling) - 250 calories
- Flexibility (10 minutes of stretching) - 30 calories
    
        -Please While Printing Exclude anything written in this prompt except the work out data.
        -Only print Type of exercises, Duration and frequency of work outs, Intensity level, Specific exercises or routines.
        -calculate the burnt calories per each part of the workout on average
        """

        response = self.model.generate_content(self.prompt)
        workout_data = (response.text)
        return workout_data
    
    def get_recipe(self,image_file):
      
      image =  PIL.Image.open(image_file) 
      image.resize(size=(300,300))
      genai.configure(api_key=GOOGLE_API_KEY)
      model2 = genai.GenerativeModel("gemini-1.5-flash")
      result = model2.generate_content([
     """Give me a recipe for these and try to estimate how many calories are in this :
     -make it as json format and every work out name is a key""", image])

      recipe = (result.text)  
      return recipe    
