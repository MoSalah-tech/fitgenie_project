# FitGenie – AI-Powered Fitness & Nutrition Planner

## Overview:
## FitGenie project 2024 my graduation project , is a generative‑AI graduation project that automatically creates personalized nutrition and workout plans based on a user’s physical data, fitness goals, and dietary restrictions. The system also allows users to upload a photo of a meal, from which the AI extracts ingredients and estimates nutritional facts. The core of the application is built with Django REST Framework and leverages Google’s Gemini and Gemini Pro Vision models to generate content

### Key Features:
- **Personalized Meal Plans – Generates complete daily meal plans (breakfast, lunch, two snacks, dinner) with calorie, protein, and carbohydrate breakdowns, taking into account user allergies and fitness goals.**
- **Workout Plan Generation – Produces workout routines tailored to the user’s fitness level and objectives.**
-  **Meal Image Analysis – Accepts an image of a meal and returns a list of ingredients along with estimated nutrition facts using Gemini Pro Vision.**
-  **User Authentication – Email‑based registration, OTP verification, password reset, and token‑based authentication (Knox).**
-  **User State Management – Stores age, weight, height, BMI, allergies, activity level, fitness goals, workout level, and gender.**
-  **Firestore Sync – Background tasks sync user data and generated plans to Firebase Firestore.**
-  **Asynchronous Processing – Celery tasks handle email sending, Firestore updates, and other long‑running operations.**

### Tech Stack:

```text
Category	          Technology
Backend  	          Django, Django REST Framework
Authentication	    Knox, Django REST Knox
AI/ML	              Google Gemini (gemini‑pro), Gemini Pro Vision
Database	          MySQL
Task Queue	        Celery, Redis (broker)
Cloud	              Firebase(Firestore, Admin SDK)
Other             	CORS headers, Debug Toolbar, SSL server

```


### Architecture
```text

fitgenie_project/
├── graduation/                     # Django project root
│   ├── graduation/                 # Project settings & WSGI
│   │   ├── settings/               # Split settings (base, development, production)
│   │   ├── celery.py               # Celery configuration
│   │   ├── urls.py                 # Main URL routing
│   │   └── wsgi.py
│   ├── user/                       # Main application
│   │   ├── Genai.py                # AI generation logic (meal & workout)
│   │   ├── models.py               # CustomUser, Profile, userstate, GenAI, wGenAI
│   │   ├── serializers.py          # DRF serializers
│   │   ├── views.py                # API endpoints
│   │   ├── task.py                 # Celery tasks (Firestore sync, etc.)
│   │   ├── firebase.py             # Firebase Admin helpers
│   │   └── emails.py               # OTP & welcome email tasks
│   ├── manage.py
│   └── celery_tasks.log
├── notebooks/                      # Jupyter experiments
│   ├── cluster.ipynb
│   └── fitgenie11.ipynb
└── test_images/                    # Sample meal images
```

## System Design
```html
<img src="docs/system-design.png" alt="FitGenie System Design" width="800"/>

```


Typical workflow : 


