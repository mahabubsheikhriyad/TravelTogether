from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
import jwt
from jwt import PyJWTError

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # If the user is already authenticated, connect the social account
        if request.user.is_authenticated:
            sociallogin.connect(request, request.user)
            raise ImmediateHttpResponse(redirect('/'))

        # If there's an existing account with the same email, connect it
        if sociallogin.is_existing:
            return

        # Get the email from the social account
        email = sociallogin.account.extra_data.get('email')

        # If the email is present, try to find the user and connect the social account
        if email:
            try:
                user = User.objects.get(email=email)
                sociallogin.connect(request, user)
                raise ImmediateHttpResponse(redirect('/'))
            except User.DoesNotExist:
                pass
