from O365.utils.token import BaseTokenBackend
from .models import O365Token
from django.utils import timezone

class DjangoTokenBackend(BaseTokenBackend):
    def __init__(self, user):
        self.user = user

    def get_token(self):
        try:
            token_obj = O365Token.objects.get(user=self.user)
            return token_obj.token
        except O365Token.DoesNotExist:
            return None

    def save_token(self, token):
        obj, created = O365Token.objects.update_or_create(
            user=self.user,
            defaults={
                'token': token,
                'last_updated': timezone.now()
            }
        )
        return True

    def delete_token(self):
        O365Token.objects.filter(user=self.user).delete()