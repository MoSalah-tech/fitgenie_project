from django.core.mail import send_mail
import random
from django.conf import settings
from.models import CustomUser

from celery import shared_task
from .views import *
import logging


# Setup logger
logger = logging.getLogger(__name__)
@shared_task
def firestore_data_task(*args, **kwargs):
    try:
        # Assuming the first argument is a list like ["mhd"]
        data = args[0] if args else []
        extra_param = kwargs.get('extra_param', 'default_value')
        
        logger.info(f"Starting firestore_data_task with data: {data}, extra_param: {extra_param}")
        
        # Fetch all document IDs
        doc_ids = get_all_document_ids('usersData')
        if not doc_ids:
            logger.warning('No documents found in Firestore.')
            return {'error': 'No documents found'}

        response_data = []
        
        # Process each document
        for doc_id in doc_ids:
            doc_data = get_firestore_data(doc_id)
            if doc_data:
                email = get_value_from_key(doc_data, 'email')
                
                # Find or create a user
                user1 = CustomUser.objects.filter(email=email).first()
                if not user1:
                    user1 = CustomUser.objects.create(
                        email=email,
                        password=generate_random_password(16),
                        name=get_value_from_key(doc_data, 'firstName'),
                    )
                    logger.info(f"Created new user with email: {email}")
                
                # Update or create user state
                userstate_instance, created = userstate.objects.update_or_create(
                    user=user1,
                    defaults={
                        'height': get_value_from_key(doc_data, 'height'),
                        'weight': get_value_from_key(doc_data, 'weight'),
                        'bmi': calculate_bmi(
                            get_value_from_key(doc_data, 'weight'), 
                            get_value_from_key(doc_data, 'height')
                        ),
                        'allergies': get_value_from_key(doc_data, 'allergies'),
                        'age': get_value_from_key(doc_data, 'age'),
                        'gender': get_value_from_key(doc_data, 'gender'),
                        'activity_level': get_value_from_key(doc_data, 'activity_level'),
                        'fitness_goals': get_value_from_key(doc_data, 'fitness_goal'),
                        'Work_Out_Level': get_value_from_key(doc_data, 'work_out_level'),
                    }
                )
                if created:
                    logger.info(f"Created new user state for user: {email}")
                else:
                    logger.info(f"Updated user state for user: {email}")

                # Append processed data to response
                response_data.append({
                    'email': email,
                    'user_state_created': created,
                })
        
        # Return accumulated results
        return {'status': 'Task completed successfully', 'data': response_data}
    
    except Exception as e:
        logger.error(f"Error in firestore_data_task: {e}")
        return {'error': str(e)}


