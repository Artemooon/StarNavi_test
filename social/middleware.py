from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from rest_framework import exceptions

User = get_user_model()


class UpdateLastUserRequestMiddleware(MiddlewareMixin):

    def process_request(self, request):
        try:
            if request.user.is_authenticated:
                current_user_id = request.user.id
                User.objects.filter(id=current_user_id).update(last_activity=datetime.utcnow())

        except exceptions.AuthenticationFailed:
            pass
