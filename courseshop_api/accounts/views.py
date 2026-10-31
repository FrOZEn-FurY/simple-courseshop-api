from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.exceptions import ValidationError

from django.core.cache import cache

from .serializers import *

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
            message="Invalid data."
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
            message="Token is invalid."
        )


class SignupView(CreateAPIView):
    serializer_class = SignupSerializer

    def perform_create(self, serializer):
        self.request.session.flush()
        return super().perform_create(serializer)
