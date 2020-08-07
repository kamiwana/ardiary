from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
import os
from .models import *

class LikeInline(admin.TabularInline):
    model = Like

class UnLikeInline(admin.TabularInline):
    model = UnLike

class CommentInline(admin.TabularInline):
    model = Comment

class CommentInline(admin.TabularInline):
    model = Comment

class ContentsFileInline(admin.TabularInline):
    model = ContentsFiles

class ContentsPasswordInline(admin.TabularInline):
    model = ContentsPassword

class AddQRDatasForm(forms.ModelForm):

    def clean_images(self):
        images = self.files.getlist('images')
        for image in images:
            if image.name.find('arz.kr_') == -1:
                raise forms.ValidationError('이미지명 형식이 올바르지 않습니다. 다시 등록해주세요.')
            try:
                name_slice = image.name.split('_')
                qr_data = name_slice[0] + '_' + name_slice[1]
                contents_type = name_slice[1][3:4]
            except:
                raise forms.ValidationError('이미지명 형식이 올바르지 않습니다. 다시 등록해주세요.')
    class Meta:
        model = QRDatas
        exclude = ['qr_data', 'is_active', 'contents_type', 'activation_code', 'login_admin']
        widgets = {"images": forms.FileInput(attrs={'id': 'images', 'required': True, 'multiple': True})}

class ChangeQRDatasForm(forms.ModelForm):

    class Meta:
        model = QRDatas
        exclude = ['images']

from django.http import HttpResponseNotFound
@admin.register(QRDatas)
class QRDatasAdmin(admin.ModelAdmin):

    def delete_queryset(self, request, queryset):
        for obj in queryset:
          if obj.images and hasattr(obj.images, 'url'):
                if os.path.isfile(obj.images.path):
                    os.remove(obj.images.path)
          obj.delete()

    def delete_model(self, request, obj):
        os.remove(obj.images.path)
        obj.delete()

    list_display = ('qr_data', 'is_active', 'contents_type', 'activation_code', 'contents_title', 'username', 'create_dt')
    list_display_links = ['qr_data']
    list_editable = ['is_active',]
    ordering = ('-qr_data',)
    # 필터링 항목 설정
    list_filter = ('is_active', 'contents_type',)
    # 객체 검색 필드 설정
    search_fields = ('qr_data', )
    actions = [delete_model]

    def qrcode_image(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url = obj.images.url,
            width=827,
            height=621,
            )
    )

    change_form = ChangeQRDatasForm
    add_form = AddQRDatasForm

    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            self.form = AddQRDatasForm
        else:
            self.form = self.change_form
            self.readonly_fields = ('qr_data', 'contents_type', 'activation_code', 'login_admin', 'create_dt', 'qrcode_image', )

        return super(QRDatasAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):

        files = request.FILES.getlist('images')
        for f in files:
            name_slice = f.name.split('_')
            qr_data = name_slice[0] + '_' + name_slice[1]
            contents_type = name_slice[1][3:4]
            activation_code = name_slice[2].split('.')
            try:
                QRDatas.objects.get(qr_data=qr_data)
            except:
               QRDatas.objects.create(images=f, qr_data=qr_data, contents_type=contents_type, activation_code=activation_code[0], login_admin=request.user)

@admin.register(Contents)
class ContentsAdmin(admin.ModelAdmin):

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            QRDatas.objects.filter(pk=obj.qr_data_id).update(is_active=0)
            obj.delete()

    def delete_model(self, request, obj):
        QRDatas.objects.filter(pk=obj.qr_data_id).update(is_active=0)
        obj.delete()

    list_display = ('id', 'title', 'qr_code', 'user', 'on_air','view_count', 'comment_count', 'like_count', 'unlike_count', 'update_dt')
    list_display_links = ['title']
    list_editable = ['on_air']
    # 필터링 항목 설정
    list_filter = ('update_dt',)
    # 객체 검색 필드 설정
    search_fields = ('title', 'user')
    inlines = [ContentsPasswordInline, ContentsFileInline,  CommentInline, LikeInline, UnLikeInline, ]
    actions = [delete_model]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['contents', 'comment_content', 'user', 'create_dt']
    list_display_links = ['contents', 'comment_content', 'user']

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'contents', 'create_date']
    list_display_links = ['contents']

@admin.register(UnLike)
class UnLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'contents', 'create_date']
    list_display_links = ['contents']