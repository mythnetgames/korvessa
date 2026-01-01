from django.contrib.auth.backends import ModelBackend
from evennia.accounts.models import AccountDB

class EmailAuthenticationBackend(ModelBackend):
    """
    Custom authentication backend that allows login with email address or username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        try:
            # Try to find by email first
            account = AccountDB.objects.get(email__iexact=username)
        except AccountDB.DoesNotExist:
            # Fallback to username
            try:
                account = AccountDB.objects.get(username__iexact=username)
            except AccountDB.DoesNotExist:
                return None
        if account.check_password(password):
            return account
        return None

    def get_user(self, user_id):
        try:
            return AccountDB.objects.get(pk=user_id)
        except AccountDB.DoesNotExist:
            return None
