from rest_framework import status
class ErrorCollection(object):

    def __init__(self, result, status, error, data):
        self.result = result
        self.status = status
        self.error = error
        self.data = data
    # ...

    def as_md(self):
        return '\n\n> **%s**\n\n```\n{\n\n\t"result": "%s"\n\n\t"error": "%s"\n\n\t"data": "%s"\n\n}\n\n```' % \
               (self.error, self.result, self.error, self.data)


# ...
NOT_FOUNT = ErrorCollection(
    result=0,
    status=status.HTTP_400_BAD_REQUEST,
    error='그외 오류',
    data='{}'
)
EMAIL_NOT_BLANK = ErrorCollection(
    result=-1,
    status=status.HTTP_400_BAD_REQUEST,
    error='이메일주소를 입력하세요.',
    data='{}'
)
USERNAME_NOT_BLANK = ErrorCollection(
    result=-2,
    status=status.HTTP_400_BAD_REQUEST,
    error='사용자 이름을 입력하세요.',
    data='{}'
)
PASSWORD_INVALID = ErrorCollection(
    result=-3,
    status=status.HTTP_400_BAD_REQUEST,
    error='비밀번호가 너무 짧습니다. 최소 8 문자를 포함해야 합니다.',
    data='{}'
)
LOGIN_TYPE_NOT_BLANK = ErrorCollection(
    result=-4,
    status=status.HTTP_403_FORBIDDEN,
    error='로그인타입 이 필드는 blank일 수 없습니다.',
    data='{}'
)
EMAIL_INVALID = ErrorCollection(
    result=-5,
    status=status.HTTP_400_BAD_REQUEST,
    error='유효한 이메일 주소를 입력하십시오.',
    data='{}'
)
USERNAME_INVALID = ErrorCollection(
    result=-6,
    status=status.HTTP_400_BAD_REQUEST,
    error='유효한 사용자 이름을 입력하세요.',
    data='{}'
)
EMAIL_PASSWORD_INVALID = ErrorCollection(
    result=-7,
    status=status.HTTP_400_BAD_REQUEST,
    error='이메일 또는 비밀번호가 올바르지 않습니다.',
    data='{}'
)
USERNAME_NOT_FOUND = ErrorCollection(
    result=-8,
    status=status.HTTP_400_BAD_REQUEST,
    error='존재하지 않는 ID 입니다.',
    data='{}'
)
USER_INVALID = ErrorCollection(
    result=-9,
    status=status.HTTP_400_BAD_REQUEST,
    error='user에 유효한 정수(integer)를 넣어주세요.',
    data='{}'
)
CURRENT_PASSWORD_NOT_BLANK = ErrorCollection(
    result=-10,
    status=status.HTTP_400_BAD_REQUEST,
    error='기존 비밀번호를 입력하세요.',
    data='{}'
)
CURRENT_PASSWORD_INVALID = ErrorCollection(
    result=-11,
    status=status.HTTP_400_BAD_REQUEST,
    error='기존 비밀번호가 다릅니다.',
    data='{}'
)
CHANGE_PASSWORD_NOT_BLANK = ErrorCollection(
    result=-12,
    status=status.HTTP_400_BAD_REQUEST,
    error='변경할 비밀번호를 입력하세요.',
    data='{}'
)
CHANGE_PASSWORD_INVALID = ErrorCollection(
    result=-13,
    status=status.HTTP_400_BAD_REQUEST,
    error='변경할 비밀번호가 너무 짧습니다. 최소 8 문자를 포함해야 합니다.',
    data='{}'
)
ACTIVATION_CODE_INVALID = ErrorCollection(
    result=-14,
    status=status.HTTP_400_BAD_REQUEST,
    error='등록된 시리얼 번호가 없습니다.',
    data='{}'
)
QRDATA_HAS_CONTENTS = ErrorCollection(
    result=-15,
    status=status.HTTP_400_BAD_REQUEST,
    error='컨텐츠가 등록된 QR코드 입니다.',
    data='{}'
)
QRDATA_NOT_FOUNDS = ErrorCollection(
    result=-16,
    status=status.HTTP_400_BAD_REQUEST,
    error='등록된 QR코드가 없습니다.',
    data='{}'
)
CONTENTS_NOT_FOUNDS = ErrorCollection(
    result=-17,
    status=status.HTTP_400_BAD_REQUEST,
    error='등록된 컨텐츠가 없습니다.',
    data='{}'
)
CONTENTS_CHECK_USER = ErrorCollection(
    result=-18,
    status=status.HTTP_400_BAD_REQUEST,
    error='작성자만 수정 가능합니다.',
    data='{}'
)
CONTENTS_DETAIL_NOT_FOUNDS = ErrorCollection(
    result=-19,
    status=status.HTTP_200_OK,
    error='등록된 컨텐츠가 없습니다.',
    data='{ "qr_data": "arz.kr/02ca00274000004", "activation_code": "4", "contents_type": 1}'
)
CONTENTS_HAS_NOT_USER = ErrorCollection(
    result=-20,
    status=status.HTTP_400_BAD_REQUEST,
    error='컨텐츠를 등록한 사용자가 아닙니다.',
    data='{}'
)
CONTENTS_PASSWORD_NOT_BLANK = ErrorCollection(
    result=-21,
    status=status.HTTP_400_BAD_REQUEST,
    error='비밀번호를 입력하세요.',
    data='{}'
)
CONTENTS_PASSWORD_INVALID = ErrorCollection(
    result=-22,
    status=status.HTTP_400_BAD_REQUEST,
    error='비밀번호는 4자리입니다.',
    data='{}'
)
CONTENTS_PASSWORD_DIGIT = ErrorCollection(
    result=-23,
    status=status.HTTP_400_BAD_REQUEST,
    error='비밀번호는 숫자만 입력하세요.',
    data='{}'
)
CONTENTS_HAS_PASSWORD = ErrorCollection(
    result=-24,
    status=status.HTTP_400_BAD_REQUEST,
    error='비밀번호가 이미 설정되었습니다.',
    data='{}'
)
CONTENTS_PASSWORD_NOT_FOUND = ErrorCollection(
    result=-25,
    status=status.HTTP_400_BAD_REQUEST,
    error='등록된 비밀번호가 없습니다.',
    data='{}'
)
CONTENTS_PASSWORD_NOT_MATCH = ErrorCollection(
    result=-26,
    status=status.HTTP_400_BAD_REQUEST,
    error='컨텐츠 비밀번호가 다릅니다.',
    data='{}'
)
CONTENTS_PASSWORD_NOT_MATCH = ErrorCollection(
    result=-26,
    status=status.HTTP_400_BAD_REQUEST,
    error='비밀번호가 다릅니다.',
    data='{}'
)
COMMENT_DELETE_USER_NOT_MATCH = ErrorCollection(
    result=-27,
    status=status.HTTP_400_BAD_REQUEST,
    error='작성자만 삭제 가능합니다.',
    data='{}'
)
COMMENT_NOT_FOUNDS = ErrorCollection(
    result=-28,
    status=status.HTTP_400_BAD_REQUEST,
    error='등록된 댓글이 없습니다.',
    data='{}'
)
PASSWORD_INVALID_NOMAL = ErrorCollection(
    result=-29,
    status=status.HTTP_400_BAD_REQUEST,
    error='비밀번호가 너무 일상적인 단어입니다.',
    data='{}'
)
PASSWORD_INVALID_CHAR = ErrorCollection(
    result=-29,
    status=status.HTTP_400_BAD_REQUEST,
    error='비밀번호는 문자가 포함되어야합니다.',
    data='{}'
)
USERNAME_EXIST = ErrorCollection(
    result=-30,
    status=status.HTTP_400_BAD_REQUEST,
    error='해당 사용자 이름은 이미 존재합니다.',
    data='{}'
)

