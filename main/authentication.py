# main/authentication.py

import jwt
from jwt import PyJWTError
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class JWTAuthenticationBackend:
    def authenticate(self, request, token=None):
        if not token:
            return None

        try:
            # Decode the token using the secret key
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            # Extract user ID from the payload
            user_id = payload.get('user_id')

            # Fetch user object based on user_id
            user = User.objects.get(id=user_id)

            # Return the user object if found
            return user

        except PyJWTError as e:
            # Handle JWT decode error
            print(f"JWT decode error: {e}")
            return None
        except User.DoesNotExist:
            # Handle case where user does not exist
            print("User matching token not found.")
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
