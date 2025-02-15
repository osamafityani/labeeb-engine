from django.dispatch import receiver
from authentication.models import CustomUser
from django.db.models.signals import post_save
from .models import Profile
from . import emails


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, first_name=instance.first_name, last_name= instance.last_name)
        emails.notify_preparer_new_profile(Profile.objects.get(user=instance), email='taxprep@j-1.org')
