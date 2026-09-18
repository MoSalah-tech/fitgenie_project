from split_settings.tools import include
import os


# Include the base settings file
include('base.py')

# Include the environment-specific settings file based on the environment
if 'development' in os.environ.get('DJANGO_SETTINGS_MODULE', 'graduation.settings.split_settings'):
    include('development.py')
elif 'production' in os.environ.get('DJANGO_SETTINGS_MODULE', 'graduation.settings.split_settings'):
    include('production.py')