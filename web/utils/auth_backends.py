"""
Custom authentication backend for username-based login.

This allows users to log into the website using their account name (username),
which is a public-facing identifier separate from their private email address.
Email is stored for admin/password reset purposes only.
"""

from django.contrib.auth.backends import ModelBackend
from evennia.accounts.models import AccountDB


class EmailAuthenticationBackend(ModelBackend):
    """
    Authenticate using account name (username).
    
    This backend allows the Django web login to accept account names,
    keeping email addresses private for admin and password reset purposes only.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user by account name (username).
        
        Args:
            request: The HTTP request object
            username: The account name from the login form
            password: User's password
            
        Returns:
            Account object if authentication succeeds, None otherwise
        """
        if username is None or password is None:
            return None
            
        try:
            # Try to find account by username (case-insensitive for convenience)
            account = AccountDB.objects.get(username__iexact=username)
            
            # Check password
            if account.check_password(password):
                # Set backend attribute required by Django
                account.backend = "web.utils.auth_backends.EmailAuthenticationBackend"
                return account
            else:
                return None
                
        except AccountDB.DoesNotExist:
            # Username not found - return None
            return None
        except AccountDB.MultipleObjectsReturned:
            # Multiple accounts with same username - shouldn't happen but handle it
            return None

    def get_user(self, user_id):
        """
        Get user by ID (required by ModelBackend).
        
        Args:
            user_id: The user's database ID
            
        Returns:
            Account object or None
        """
        try:
            return AccountDB.objects.get(pk=user_id)
        except AccountDB.DoesNotExist:
            return None
