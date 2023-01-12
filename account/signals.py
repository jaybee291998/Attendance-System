from asyncio import SendfileNotAvailableError
from turtle import pos
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from .models import UserProfile

from random_username.generate import generate_username

User = get_user_model()

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, username=generate_username(1)[0])

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()