from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import *

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-token/', VerifyOTPView.as_view(), name='verify-token'),
    path('signup/', SignupView.as_view(), name='signup'),
    # path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    # path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    # path('subscriptions/', SubscriptionListView.as_view(), name='subscriptions'),
    # path('callback-gateway/', CallbackGatewayView.as_view(), name='callback-gateway'),
    # path('buy-subscription/<int:pk>/', BuySubscriptionView.as_view(), name='buy-subscription'),
]