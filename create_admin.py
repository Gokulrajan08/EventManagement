import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_system.settings')
django.setup()

from events.models import CustomUser

username = 'admin'
email = 'admin@eventhub.com'
password = 'Admin@1234'

if not CustomUser.objects.filter(username=username).exists():
    CustomUser.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created successfully.")
else:
    u = CustomUser.objects.get(username=username)
    u.set_password(password)
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print(f"Superuser '{username}' already existed. Password updated and permissions verified.")
