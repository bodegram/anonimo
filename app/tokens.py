from .models import CustomUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user: CustomUser, timestamp: int):
        return (
            str(user.is_active) + str(user.pk) + str(timestamp)
        )
        
email_verification_token = TokenGenerator()