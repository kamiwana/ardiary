from ardiary.exception_handler import CustomValidation
from .models import *

def get_contents(pk):
    if pk is not None:
        if len(pk) < 1 or pk.isdigit() is False:
            raise CustomValidation('-17', "등록된 컨텐츠가 없습니다.")
        try:
            contents = Contents.objects.get(pk=pk)
        except Contents.DoesNotExist:
            raise CustomValidation('-17', '등록된 컨텐츠가 없습니다.')
        return contents
    else:
        raise CustomValidation('-17', '등록된 컨텐츠가 없습니다.')