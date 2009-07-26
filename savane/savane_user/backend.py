from savane_user.models import User
from django.contrib.auth.backends import ModelBackend

class SavaneAuthBackend( ModelBackend ):
    """
    Authenticate against the savane_user model
    """
    def authenticate( self, username, password ):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
