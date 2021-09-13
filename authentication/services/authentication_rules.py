import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.authentication import get_authorization_header, exceptions, BaseAuthentication

User = get_user_model()


def check_auth_token_in_blacklist(auth_token: str) -> bool:
    # check whether auth token has been blacklisted
    token = cache.get(auth_token)
    if token == 'blacklist':
        return True

    return False


def move_auth_token_to_blacklist(token: str, is_refresh_token: bool) -> None:
    if is_refresh_token:
        cache.set(token, 'blacklist', timeout=int(settings.REFRESH_TOKEN_LIFETIME * 60))
    else:
        cache.set(token, 'blacklist', timeout=int(settings.ACCESS_TOKEN_LIFETIME * 60))


class JWTAuthTokenRequired(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth:
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        auth_token = auth[1].decode("utf-8")

        if check_auth_token_in_blacklist(auth_token) is True:
            msg = 'Access Token is in a blacklist.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token_data = jwt.decode(auth_token, settings.SECRET_KEY, algorithms=["HS256"])

        except jwt.exceptions.ExpiredSignatureError:
            msg = 'Access Token expired.'
            raise exceptions.AuthenticationFailed(msg)
        except jwt.exceptions.InvalidTokenError:
            msg = 'Invalid access token.'
            raise exceptions.AuthenticationFailed(msg)

        if token_data['typ'] != 'access':
            msg = 'Provide access token for authorization.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token_data)

    def authenticate_credentials(self, auth_token):

        current_user = User.objects.filter(id=auth_token['user_id']).first()
        if not current_user:
            raise exceptions.AuthenticationFailed('User does not exists.')

        if not current_user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return (current_user, auth_token)


def get_auth_tokens_lifetime():
    return {
        'access_token_lifetime_in_minutes': settings.ACCESS_TOKEN_LIFETIME,
        'refresh_token_lifetime_in_minutes': settings.REFRESH_TOKEN_LIFETIME
    }
