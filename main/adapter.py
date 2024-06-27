# your_app/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from .models import User

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # If the user is already authenticated, connect the social account
        if request.user.is_authenticated:
            sociallogin.connect(request, request.user)
            raise ImmediateHttpResponse(redirect('/'))

        # If there's an existing account with the same email, connect it
        if sociallogin.is_existing:
            return

        try:
            email = sociallogin.account.extra_data['email']
            user = User.objects.get(email=email)
            sociallogin.connect(request, user)
            raise ImmediateHttpResponse(redirect('/'))
        except User.DoesNotExist:
            pass

