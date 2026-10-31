from django.utils.translation import gettext_lazy as _

from rest_framework.response import Response

from typing import Any

def get_response(
        status: int,
        data: Any = {},
        message: str = '',
        raw: bool = False
): 
    if not raw:
        return Response({
            'status': status,
            'message': _(message),
            'data': data
        }, status=status)
    else:
        return {
            'status': status,
            'message': _(message),
            'data': data
        }