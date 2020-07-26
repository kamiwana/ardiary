from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
import django.contrib.auth.password_validation as validators
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

class CustomUserForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password')

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
        self.helper.form_method = 'POST'

    email = forms.EmailField(
        label='이메일',
        widget=forms.TextInput(

        )
    )
    username = forms.CharField(
        label='사용자이름',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        )
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
            }
        ),
        help_text='비밀번호는 최소8자 이상,영문과숫자를 포함해 등록해주세요.'
    )
    # 비밀번호 확인을 위한 필드
    password2 = forms.CharField(
        label='비밀번호 확인',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
            }
        )
    )
    #  이메일필드의 검증에 이메일 이미 사용중인지 여부 검사
    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('이메일이 이미 사용중입니다')
        return email

    # username필드의 검증에 username이 이미 사용중인지 여부 검사
    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('아이디가 이미 사용중입니다')
        return username

    # password1와 password2의 값이 일치하는지 유효성 검사
    def clean_password2(self):

        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password != password2:
            raise forms.ValidationError('비밀번호와 비밀번호 확인란의 값이 일치하지 않습니다')

        try:
            validators.validate_password(password)
        except ValidationError as exc:
            message = str(exc)
            if '8' in message:
                raise forms.ValidationError("비밀번호가 너무 짧습니다. 최소 8 문자를 포함해야 합니다.")
            elif '숫자' in message:
                raise forms.ValidationError("비밀번호는 영문과숫자를 포함하여 8자 이상으로 입력해주세요.")
            elif '일상' in message:
                raise forms.ValidationError("비밀번호가 너무 일상적인 단어입니다.")
            raise forms.ValidationError(str(exc))
        return password