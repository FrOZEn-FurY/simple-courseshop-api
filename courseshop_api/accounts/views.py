from rest_framework.views import APIView, Http404
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView, TokenRefreshView
from rest_framework import status

from .models import User, Subscription, TransactionHistory
from .permission import IsAuthenticatedAndSelf, IsAuthenticatedAndNotSubscribed
from .serializers import (
    SubscriptionSerializer,
    ProfileSerializer,
    PhoneSerializer,
    TokenSerializer,
    SignupSerializer,
    ChangePasswordSerializer
)
from .throttles import AuthenticationThrottle
from utils.functions import get_response

from azbankgateways import bankfactories, models as bank_models, default_settings as settings

from django.utils import timezone

import pytz


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [AuthenticationThrottle]


class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_classes = [AuthenticationThrottle]


class ThrottledTokenVerifyView(TokenVerifyView):
    throttle_classes = [AuthenticationThrottle]
    

class SendOTPView(APIView):
    throttle_classes = [AuthenticationThrottle]
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
    throttle_classes = [AuthenticationThrottle]
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
    throttle_classes = [AuthenticationThrottle]
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


class BuySubscriptionView(APIView):
    permission_classes = [IsAuthenticatedAndNotSubscribed]

    def get(self, request, pk):
        sub = Subscription.objects.get(pk=pk)
        factory = bankfactories.BankFactory()
        bank = factory.create()
        bank.set_request(request)
        bank.set_amount(sub.price)
        bank.set_client_callback_url('https://front-end.ir/callback') # We redirect to the front'end side page that is meant to be for callback of the gateway
        bank.ready()

        last_transaction = TransactionHistory.objects.filter(user=request.user, subscription=sub).order_by("date_created").first()
        if (not last_transaction  
                or last_transaction.status != bank_models.PaymentStatus.COMPLETE
                or last_transaction.date_created.astimezone(pytz.timezone("Asia/Tehran")) < timezone.make_aware(timezone.now() - timezone.timedelta(minutes=15))):
            TransactionHistory.objects.create(user=request.user, subscription=sub)
        
        return get_response(
            status=status.HTTP_200_OK,
            message="Gateway created successfully.",
            data={
                'sub_id': sub.pk,
                'gateway_url': bank.get_gateway_payment_url()
            }
        )



class CallbackGatewayView(APIView):
    permission_classes = [IsAuthenticatedAndNotSubscribed]
    
    def get(self, request):
        tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
        if not tracking_code:
            raise Http404
    
        try:
            bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
        except bank_models.Bank.DoesNotExist:
            raise Http404
    
        if bank_record.is_success:
            last_transaction = TransactionHistory.objects.filter(user=request.user).order_by("date_created").first()
            if not last_transaction or last_transaction.status == bank_models.PaymentStatus.COMPLETE:
                return get_response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message='Something went wrong.',
                    data={
                        'message': "در فرایند پرداخت مشکلی به وجود آماده است. لطفا با پشتیبانی تماس بگیرید."
                    }
                )
            request.user.subscription = last_transaction.subscription
            request.user.subscription_date_started = timezone.now()
            request.user.save()
            return get_response(
                status=status.HTTP_200_OK,
                message="Payment successful.",
                data={
                    'message': "پرداخت با موفقیت انجام شد."
                }
            )
    
        return get_response(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Something went wront.",
            data={
                'message': "پرداخت با شکست مواجه شده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت."
            }
        )
