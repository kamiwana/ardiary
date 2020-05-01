from django.conf.urls import url
from .views import *

urlpatterns = [
    url("^registration$", RegistrationAPI.as_view()),
    url("^login$", LoginAPI.as_view()),
    url("^user/(?P<user>\d+)$", UserAPI.as_view()),
    url("^password_change$", ChangePasswordAPI.as_view()),
]