import random

from django.db import models
from authentication.models import CustomUser


def generate_pin():
    random_code = ''.join([str(random.randint(1, 9)) for i in range(5)])
    return random_code


class Profile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=40, blank=True, null=True)
    last_name = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.first_name + ' ' + self.last_name
