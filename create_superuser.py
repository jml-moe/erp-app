#!/usr/bin/env python
"""
Script untuk membuat superuser non-interaktif
Usage: railway run python create_superuser.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Ganti dengan credentials yang diinginkan
USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if User.objects.filter(username=USERNAME).exists():
    print(f'User "{USERNAME}" already exists. Updating password...')
    user = User.objects.get(username=USERNAME)
    user.set_password(PASSWORD)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f'Password updated for user "{USERNAME}"')
else:
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print(f'Superuser "{USERNAME}" created successfully!')

print(f'\nLogin credentials:')
print(f'Username: {USERNAME}')
print(f'Password: {PASSWORD}')

