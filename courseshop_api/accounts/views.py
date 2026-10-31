from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework import status

from django.core.cache import cache

from .models import User, Subscription
from .permission import IsAuthenticatedAndSelf, IsAuthenticatedAndNotSubscribed
from .serializers import (
    SubscriptionSerializer,
    ProfileSerializer,
    PhoneSerializer,
    TokenSerializer,
    SignupSerializer,
    ChangePasswordSerializer
)

from utils.functions import get_response


class SendOTPView(APIView):
    serializer_class = PhoneSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return get_response(
                status=status.HTTP_200_OK,
                message="OTP Sent successfully."
            )
        
        return get_response(
            status=status.HTTP_400_BAD_REQUEST,
            message="Some fields are not valid.",
            data=serializer.errors
        )


class VerifyOTPView(APIView):
    serializer_class = TokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return get_response(
                status=status.HTTP_200_OK,
                message="Token is valid."
            )
        return get_response(
            status=status.HTTP_400_BAD_REQUEST,
            message="Some fields are not valid.",
            data=serializer.errors
        )


class SignupView(CreateAPIView):
    serializer_class = SignupSerializer

    def perform_create(self, serializer):
        self.request.session.flush()
        return super().perform_create(serializer)


class ProfileView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedAndSelf]
    serializer_class = ProfileSerializer
    queryset = User.objects.all()


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticatedAndSelf]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.validated_data['current_password']):
                user.set_password(serializer.validated_data['password'])
                user.save()
                return get_response(
                    status=status.HTTP_200_OK,
                    message="Password changed, successfully, Please login again."
                )
            return get_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Your current password is incorrect."
            )
        return get_response(
            status=status.HTTP_400_BAD_REQUEST,
            message="Some fields are not valid.",
            data=serializer.errors
        )


class SubscriptionListView(ListAPIView):
    permission_classes = [IsAuthenticatedAndNotSubscribed]
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()