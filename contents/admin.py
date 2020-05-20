from django.contrib import admin
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


@admin.register(QRDatas)
class QRDatasAdmin(admin.ModelAdmin):
    list_display = ('qr_data', 'is_active','contents_type', 'contents_title', 'username', 'activation_code',  'create_dt')
    list_display_links = ['qr_data']
    # 필터링 항목 설정
    list_filter = ('qr_data', 'is_active',)
    # 객체 검색 필드 설정
    search_fields = ('qr_data', )

@admin.register(Contents)
class ContentsAdmin(admin.ModelAdmin):

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            QRDatas.objects.filter(pk=obj.qr_data_id).update(is_active=0)
            obj.delete()

    def delete_model(self, request, obj):
        QRDatas.objects.filter(pk=obj.qr_data_id).update(is_active=0)
        obj.delete()


    list_display = ('id', 'title', 'user', 'view_count', 'comment_count', 'like_count', 'unlike_count', 'update_dt')
    list_display_links = ['title']
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