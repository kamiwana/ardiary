from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['pk', 'email', 'username', 'login_type', 'is_active', 'date_joined']
    list_display_links = ['email']
    list_filter = ('login_type', 'is_staff')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('개인 정보', {'fields': ('username', 'login_type', 'is_active', 'is_staff',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
