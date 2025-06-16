from O365.utils.token import BaseTokenBackend
from .models import O365Token
from django.utils import timezone

class DjangoTokenBackend(BaseTokenBackend):
    def __init__(self, user):
        super().__init__()
        self.user = user

    def load_token(self) -> bool:
        try:
            token_obj = O365Token.objects.get(user=self.user)
            self._cache = self.deserialize(token_obj.token)
            return True
        except O365Token.DoesNotExist:
            self._cache = {}
            return False

    def save_token(self, force=False) -> bool:
        if not self._has_state_changed and not force:
            return True

        serialized = self.serialize()
        O365Token.objects.update_or_create(
            user=self.user,
            defaults={
                'token': serialized,
                'last_updated': timezone.now()
            }
        )
        return True

    def delete_token(self) -> bool:
        deleted, _ = O365Token.objects.filter(user=self.user).delete()
        return deleted > 0
