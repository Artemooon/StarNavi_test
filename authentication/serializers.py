from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, write_only=True, required=True)
    confirm_password = serializers.CharField(max_length=255, write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'confirm_password']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email already exists')

        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Those passwords don't match.")

        return super().validate(attrs)

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'],
                                        email=validated_data['email'],
                                        password=validated_data['password'])
        return user


class UserLoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, write_only=True, required=True)
    username = serializers.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password']

    def validate(self, attrs):
        username = attrs.get('username')
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError('User with provided username not exists')

        else:
            password = attrs.get('password')
            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise serializers.ValidationError('Invalid password')

        return super().validate(attrs)


class RefreshAuthTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=255, min_length=1, required=True)

    class Meta:
        fields = ['refresh_token']
