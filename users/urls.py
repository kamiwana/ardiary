from django.conf.urls import url
from .views import *

urlpatterns = [
    url("^login$", LoginAPI.as_view()),
    url("^user$", UserAPI.as_view()),
    url("^registration$", RegistrationAPI.as_view()),
    url("^password_change$", ChangePasswordAPI.as_view()),
]