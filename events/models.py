from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_organizer = models.BooleanField(default=False)
    is_participant = models.BooleanField(default=True)

    def __str__(self):
        return self.username

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    max_participants = models.IntegerField()
    organizer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='organized_events')

    def __str__(self):
        return self.title

class Registration(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
