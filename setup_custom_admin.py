import os
import django
import importlib

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_kedai.settings')
django.setup()

from django.contrib import admin
from django.apps import apps

# Unregister all models from default admin
print("Unregistering all models from default admin...")
registered_models = list(admin.site._registry.keys())
for model in registered_models:
    admin.site.unregister(model)
print(f"Unregistered {len(registered_models)} models.")

# Import custom admin modules
print("\nImporting custom admin modules...")
from core import admin_custom as core_admin
from inventory import admin_custom as inventory_admin

print("\nCustom admin setup completed!")
print("\nNow you can run the following command to generate fake data:")
print("python generate_fake_data.py")