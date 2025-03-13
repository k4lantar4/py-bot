import os
import sys

# List of apps to create
apps = ['api', 'v2ray', 'telegram', 'payments']

# Base directory
base_dir = 'backend'

# Create directories and files
for app in apps:
    app_dir = os.path.join(base_dir, app)
    
    # Create app directory
    os.makedirs(app_dir, exist_ok=True)
    
    # Create __init__.py
    with open(os.path.join(app_dir, '__init__.py'), 'w') as f:
        pass
    
    # Create models.py
    with open(os.path.join(app_dir, 'models.py'), 'w') as f:
        f.write('from django.db import models\n\n# Create your models here.\n')
    
    # Create views.py
    with open(os.path.join(app_dir, 'views.py'), 'w') as f:
        f.write('from django.shortcuts import render\n\n# Create your views here.\n')
    
    # Create admin.py
    with open(os.path.join(app_dir, 'admin.py'), 'w') as f:
        f.write('from django.contrib import admin\n\n# Register your models here.\n')
    
    # Create apps.py
    with open(os.path.join(app_dir, 'apps.py'), 'w') as f:
        class_name = app.capitalize() + 'Config'
        f.write(f'''from django.apps import AppConfig


class {class_name}(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app}'
''')
    
    # Create migrations directory
    migrations_dir = os.path.join(app_dir, 'migrations')
    os.makedirs(migrations_dir, exist_ok=True)
    
    # Create __init__.py in migrations directory
    with open(os.path.join(migrations_dir, '__init__.py'), 'w') as f:
        pass

# Create other directories
other_dirs = ['static', 'templates', 'locale', 'logs']
for directory in other_dirs:
    os.makedirs(os.path.join(base_dir, directory), exist_ok=True)

print("Django app directories created successfully!") 