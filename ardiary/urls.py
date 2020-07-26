"""ardiary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include # new
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

schema_view = get_schema_view(
   openapi.Info(
      title="ARDiary API",
      default_version='v2',
      description="인증은 로그인시 전달받은 사용자 id 값을  user 파라미터로  서버에 전달",
   ),
   validators=['flex'], #'ssv'],
   public=True,
   permission_classes=(permissions.AllowAny,),
)

admin.site.site_title = "ARDiary"
admin.site.site_header = "ARDiary"
admin.site.index_title = "ARDiary"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # new
    url(r'^auth/', include('users.urls')),
    url(r'^contents/', include('contents.urls')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/v1$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    url(r'^accounts/password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    #path('password_reset/', auth_views.PasswordResetView.as_view(
    #    template_name='./registration/password_reset_form.html',
    #    success_url=reverse_lazy('password_reset_done'),
    #    subject_template_name='./registration/password_reset_subject.txt'),
    #    name='password_reset'),
 #   path('accounts/', include('allauth.urls')),
#    path('rest-auth/', include('rest_auth.urls')),
#    path('rest-auth/registration/', include('rest_auth.registration.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)