from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from dotenv import load_dotenv

import os

import requests

from .models import Token

load_dotenv(settings.BASE_DIR / '.env')


@receiver(post_save, sender=Token)
def send_otp(sender, instance, created, **kwargs):
    url = 'https://api.iranpayamak.com/ws/v1/sms/pattern'
    data = {
        "recipient": instance.phone_number.as_e164.replace(r'+98', r'0'),
        "code": "I3ZqvZJmAc",
        "attributes": {
            "code": instance.value,
        },
        "number_format": "english",
        "line_number": "90008361"
    }
    headers = {
        "Accept": "application/json",
        "Api-Key": os.getenv("SMS_PANEL_API_KEY", None),
        'Content-Type': "application/json"
    }
    if created:
        response = requests.post(url, json=data, headers=headers)
        print(f'response from the request with data {data} and headers {headers}: {response.json()}')