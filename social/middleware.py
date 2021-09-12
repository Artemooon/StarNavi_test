from datetime import datetime

from authentication.services.authentication_rules import JWTAuthTokenRequired
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from rest_framework import exceptions

from .models import SocialProfile

User = get_user_model()


class UpdateLastUserRequestMiddleware(MiddlewareMixin):

    def process_request(self, request):
        auth_class = JWTAuthTokenRequired()
        try:
            authentication_result = auth_class.authenticate(request=request)
            if authentication_result:
                current_user_id = authentication_result[1]['user_id']
                SocialProfile.objects.filter(user__id=current_user_id).update(last_activity=datetime.utcnow())

        except exceptions.AuthenticationFailed:
            pass
