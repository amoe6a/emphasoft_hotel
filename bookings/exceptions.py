from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError


def custom_IntegrityError_exception_handler(
    exc: Exception, context: dict
) -> Response | None:
    response = exception_handler(exc, context)
    if response is None and isinstance(exc, IntegrityError):
        error_message = "This room was just booked by someone else. (Race condition)"
        return Response(
            {"non_field_errors": [error_message]}, status=status.HTTP_409_CONFLICT
        )

    return response
