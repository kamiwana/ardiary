from rest_framework.exceptions import APIException
from django.utils.encoding import force_text
from rest_framework import status

class CustomValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'

    def __init__(self, result, detail):
       # if status_code is not None: self.status_code = status_code
        self.status_code = status.HTTP_200_OK
        if detail is not None:
            self.detail = {'result': int(result), 'error': detail, 'data': {}}
        else: self.detail = {'detail': force_text(self.default_detail)}