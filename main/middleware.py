# your_app/middleware.py

import jwt
from jwt import PyJWTError
from django.utils.deprecation import MiddlewareMixin

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        if token:
            try:
                decoded = jwt.decode(token, 'your_secret_key', algorithms=["HS256"])
                request.user = decoded  # Custom logic to attach user info to the request
            except PyJWTError as e:
                # Handle the error
                print(f"JWT error: {e}")
