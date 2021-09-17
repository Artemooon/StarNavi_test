from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authentication import get_authorization_header

from .authentication_rules import move_auth_token_to_blacklist, check_auth_token_in_blacklist

User = get_user_model()


def encode_auth_token(user_id: int, exp: int, is_refresh_token: bool):
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=exp),
            'iat': datetime.utcnow(),
            'typ': 'refresh' if is_refresh_token else 'access',
            'user_id': str(user_id)
        }

        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    except ValueError as e:
        return {'message': str(e)}


def authenticate_user(username: str) -> dict:
    current_user = User.objects.filter(username=username).first()

    if current_user:
        access_token = encode_auth_token(current_user.id, settings.ACCESS_TOKEN_LIFETIME, is_refresh_token=False)
        refresh_token = encode_auth_token(current_user.id, settings.REFRESH_TOKEN_LIFETIME, is_refresh_token=True)

        User.objects.filter(username=username).update(last_login=datetime.utcnow())

        return {'access_token': access_token,
                'refresh_token': refresh_token,
                'user': current_user.id, 'status': status.HTTP_200_OK}

    return {'detail': 'User with provided username not found', 'status': status.HTTP_404_NOT_FOUND}


def logout_user(request, refresh_token: str) -> dict:
    if not request.user.is_authenticated:
        return {'detail': 'Invalid access token', 'status': status.HTTP_400_BAD_REQUEST}

    auth = get_authorization_header(request).split()

    access_token = auth[1].decode("utf-8")

    try:
        decoded_refresh_token = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.exceptions.ExpiredSignatureError:
        return {'detail': 'Refresh token expired.', 'status': status.HTTP_401_UNAUTHORIZED}
    except jwt.exceptions.InvalidTokenError:
        return {'detail': 'Invalid refresh token', 'status': status.HTTP_401_UNAUTHORIZED}

    decode_access_token = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])

    if decoded_refresh_token['typ'] == 'refresh' and decoded_refresh_token['user_id'] == decode_access_token['user_id']:

        # mark the token as blacklisted
        move_auth_token_to_blacklist(access_token, is_refresh_token=False)
        move_auth_token_to_blacklist(refresh_token, is_refresh_token=True)
        return {'detail': 'Successfully logged out.', 'status': status.HTTP_200_OK}
    else:
        return {'detail': 'Provide a valid access and refresh tokens.', 'status': status.HTTP_400_BAD_REQUEST}


def refresh_access_token(request, refresh_token: str) -> dict:
    if not request.user.is_authenticated:
        return {'detail': 'Invalid access token', 'status': status.HTTP_400_BAD_REQUEST}

    auth = get_authorization_header(request).split()

    access_token = auth[1].decode("utf-8")

    if not check_auth_token_in_blacklist(refresh_token):
        try:
            decode_refresh_token = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.exceptions.ExpiredSignatureError:
            return {'message': 'Your token expired, please login again', 'status': 401}

        decode_access_token = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        if decode_refresh_token['user_id'] == decode_access_token['user_id'] and \
                decode_refresh_token['typ'] == 'refresh':
            current_user_id = request.user.id
            result_access_token = encode_auth_token(current_user_id, settings.ACCESS_TOKEN_LIFETIME,
                                                    is_refresh_token=False)
            move_auth_token_to_blacklist(access_token, is_refresh_token=False)

            return {'access_token': result_access_token,
                    'user': int(current_user_id),
                    'status': 201}

        return {'message': 'Invalid refresh token', 'status': 400}

    return {'message': 'Provided refresh token not found', 'status': 401}
