from .models import  GenAI,wGenAI
from firebase_admin import credentials, firestore
import firebase_admin
import string
import secrets


cred = credentials.Certificate('C:/Users/mhd_gamer/Desktop/grad/fitgenie-project-firebase-adminsdk-agbaf-df77862171.json') 

firebase_admin.initialize_app(cred)

db = firestore.client()

def generate_random_password(length=12):
    # Define the characters that can be used in the password
    alphabet = string.ascii_letters + string.digits + string.punctuation
    # Use secrets.choice to generate a secure random password
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password



def get_all_document_ids(collection_name):
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()
    
    doc_ids = []
    for doc in docs:
        doc_ids.append(doc.id)
    
    return doc_ids


def get_firestore_data(document_id):
    doc_ref = db.collection('usersData').document(document_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None


def send_to_firestore(user_email):
     queryset = GenAI.objects.filter(user__email=user_email).order_by('id').last()
    
        
     doc_ref = db.collection('meal_plans').document()
     doc_ref.set({
        'user': queryset.user.email, 
        'data': queryset.data,
        'data1': queryset.id  
        })



def send_to_firestorew(user_email):
     queryset = wGenAI.objects.filter(user__email=user_email).order_by('id').last()
    
        
     doc_ref = db.collection('workout').document()
     doc_ref.set({
        'user': queryset.user.email, 
        'data': queryset.data,
        'data1': queryset.id  
        })  



def get_value_from_key(data, key_string):
    keys = key_string.split('.')  
    value = data
    print("Keys:", keys)
    print("Data:", data)
    try:
        for key in keys:
            value = value[key]
            print("Value after key", key, ":", value)
    except (KeyError, TypeError) as e:
        print("Error:", e)
        return None
    return value



def calculate_bmi(weight, height):
    if weight is None or height is None:
        return None  # Handle the case where weight or height is None
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return bmi