from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AuthenticationThrottle(AnonRateThrottle):
    scope = 'authentication'


class BuySubscriptionThrottle(UserRateThrottle):
    scope = 'subscription'