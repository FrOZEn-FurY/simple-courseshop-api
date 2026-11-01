from rest_framework import serializers, status

from django.utils import timezone
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Token, Subscription
from posts.models import UserFavorite

from phonenumber_field.serializerfields import PhoneNumberField

import shortuuid
import pytz

from datetime import timedelta

from utils.functions import get_response


class PhoneSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()

    def validate(self, attrs):
        data = super().validate(attrs)
        s = shortuuid.ShortUUID(alphabet='0123456789')
        token = s.random(5)
        Token.objects.create(value=token, phone_number=data['phone_number'])
        return data


class TokenSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    token = serializers.CharField()

    def validate(self, attrs):
        data = super().validate(attrs)
        try:
            db_token = Token.objects.get(value=data['token'], phone_number=data['phone_number'])
            time_differnece = timezone.datetime.now() - timedelta(minutes=2)
            print(timezone.make_aware(time_differnece), db_token.date_created.astimezone(pytz.timezone('Asia/Tehran')))
            if timezone.make_aware(time_differnece) > db_token.date_created.astimezone(pytz.timezone('Asia/Tehran')):
                serializers.ValidationError('token', 'Token is expired.')
            db_token.status = 'validated'
            db_token.save()
        except ObjectDoesNotExist:
            serializers.ValidationError('token', "Token is invalid.")
        return data

class SignupSerializer(serializers.ModelSerializer):
    token = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'confirm_password', 'phone_number', 'token')

    def validate(self, attrs):
        data = super().validate(attrs)
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Passwords do not match.')
        try:
            token = Token.objects.get(value=data['token'], phone_number=data['phone_number'])
            if token.status != 'validated':
                raise serializers.ValidationError("Token is still not validated.")
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Token is invalid.")
        return data

    def create(self, validated_data):
        new_dict = validated_data
        del new_dict['confirm_password']
        del new_dict['token']
        user = User.objects.create_user(
            **new_dict, 
            username=new_dict['phone_number'], 
        )
        return user

    def to_representation(self, instance):
        return get_response(
            message="User created successfully.",
            status=status.HTTP_201_CREATED,
            data={ 
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'email': instance.email,
                'username': instance.username,
                'phone_number': instance.phone_number.as_e164,
            },
            raw=True
        )


class ProfileSerializer(serializers.ModelSerializer):
    subscription_duration = serializers.SerializerMethodField()
    favorites = serializers.SerializerMethodField()
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    phone_number = PhoneNumberField(required=False)
    email = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'phone_number', 'email', 'subscription_duration', 'favorites')

    def get_subscription_duration(self, obj):
        if not obj.subscription:
            return None
        now = timezone.datetime.now()
        expiration_date = obj.subscription_date_started.astimezone(pytz.timezone("Asia/Tehran")) + timedelta(days=obj.subscription.duration)
        difference = expiration_date - timezone.make_aware(now, pytz.timezone("Asia/Tehran"))
        return difference.days

    def get_favorites(self, obj):
        urls = []
        posts = UserFavorite.objects.filter(user=obj)
        for post in posts:
            urls.append(post.get_absolute_url())
        return urls

    def to_representation(self, instance):
        return get_response(
            message="User retrieved successfully.",
            status=status.HTTP_200_OK,
            data={ 
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'email': instance.email,
                'username': instance.username,
                'phone_number': instance.phone_number.as_e164,
                'favorites': self.get_favorites(instance),
                'subscription_duration': self.get_subscription_duration(instance),
            },
            raw=True
        )


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        data = super().validate(attrs)
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = "__all__"