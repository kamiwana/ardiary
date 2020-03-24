from django.db import models
from django.conf import settings
from .choices import *
# Create your models here.

def contents_path(instance, filename):
    from random import choice
    import string
    arr = [choice(string.ascii_letters) for _ in range(8)]
    pid = ''.join(arr)
    extension = filename.split('.')[-1]
    return 'contents/{}/{}.{}'.format(instance.user_id, pid, extension)

class QRDatas(models.Model):
    qr_data = models.CharField(max_length=255, unique=True)
    is_active = models.SmallIntegerField(choices=IS_ACTIVE, default=0, verbose_name='사용 여부')
    activation_code = models.IntegerField(blank=True)
    create_dt = models.DateField(auto_now_add=True, verbose_name='생성일')
    update_dt = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    def __str__(self):
        return self.qr_data

    def username(self):
        return self.qrdatascontents.username()
    
    def contents_title(self):
        return self.qrdatascontents.title

    class Meta:
        verbose_name = '1. QR코드'
        verbose_name_plural = '1. QR코드'

class Contents(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="usercontents")
    qr_data = models.OneToOneField(QRDatas, on_delete=models.CASCADE, related_name="qrdatascontents")
    title = models.CharField(max_length=100, verbose_name='제목')
    contents_type = models.SmallIntegerField(choices=CONTENTS_TYPE, default=0, verbose_name='컨텐츠타입', blank=True)
    recog_type = models.SmallIntegerField(choices=RECOG_TYPE, default=0, verbose_name='인식타입', blank=True)
    password = models.IntegerField(verbose_name='패스워드', blank=True, null=True)
    video_url = models.URLField(max_length=100, verbose_name='영상주소', blank=True)
    label_text = models.CharField(max_length=20, verbose_name='label_text', blank=True)
    neon_text = models.CharField(max_length=20, verbose_name='neon_text', blank=True)
    neon_style = models.IntegerField(verbose_name='neon_style', blank=True, null=True)
    neon_effect = models.IntegerField(verbose_name='neon_effect', blank=True, null=True)
    neon_material = models.IntegerField(verbose_name='neon_material', blank=True, null=True)
    audio_url = models.URLField(max_length=100, verbose_name='음성 데이터 주소', blank=True, null=True)
    link_01_type = models.SmallIntegerField(choices=LIKE_TYPE, default=0, verbose_name='link_01_type', blank=True, null=True)
    link_01_url = models.URLField(max_length=100, verbose_name='link_01_url', blank=True, null=True)
    link_02_type = models.SmallIntegerField(choices=LIKE_TYPE, default=0, verbose_name='link_02_type', blank=True, null=True)
    link_02_url = models.URLField(max_length=100, verbose_name='link_02_url', blank=True, null=True)
    effect_type = models.SmallIntegerField(choices=EFFECT_TYPE, default=0, verbose_name='effect_type', blank=True, null=True)
    char_type = models.SmallIntegerField(choices=CHAR_TYPE, default=0, verbose_name='char_type', blank=True, null=True)
    update_dt = models.DateTimeField(auto_now=True, verbose_name='등록일', null=True)
    like_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                           blank=True,
                                           related_name='like_user_set',
                                           through='Like', null=True)
    unlike_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                           blank=True,
                                           related_name='unlike_user_set',
                                           through='UnLike', null=True)
    comment_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                           blank=True,
                                           related_name='comment_user_set',
                                           through='Comment', null=True)
    view_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = '2. 컨텐츠'
        verbose_name_plural = '2. 컨텐츠'

    def __str__(self):
        return self.title

    def like_count(self):
        return self.like_user_set.count()

    def unlike_count(self):
        return self.unlike_user_set.count()

    def comment_count(self):
        return self.comment_user_set.count()

    def username(self):
        return self.user.username

    def qr_code(self):
        return self.qr_data.qr_data

class ContentsFiles(models.Model):
    contents = models.ForeignKey(Contents, on_delete=models.CASCADE, related_name='contents_files')
    file = models.FileField(upload_to=contents_path, verbose_name='파일', null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    create_dt = models.DateTimeField(auto_now_add=True, verbose_name='등록일', null=True)

class Comment(models.Model):
    contents = models.ForeignKey(Contents, on_delete=models.CASCADE, related_name='contents_comment')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment_content = models.CharField(max_length=80, verbose_name="내용")
    create_dt = models.DateTimeField(auto_now_add=True, verbose_name='등록일')
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return self.comment_content

    def username(self):
        return self.user.username

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True

    def children(self): #replies
        return Comment.objects.filter(parent=self)

    class Meta:
        verbose_name = '3. 댓글'
        verbose_name_plural = '3. 댓글'

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contents = models.ForeignKey(Contents, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='등록일')

    class Meta:
        verbose_name = '4. 좋아요'
        verbose_name_plural = '4. 좋아요'

        unique_together = (
            ('user', 'contents')
        )

class UnLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contents = models.ForeignKey(Contents, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='등록일')

    class Meta:
        verbose_name = '5. 싫어요'
        verbose_name_plural = '5. 싫어요'

        unique_together = (
            ('user', 'contents')
        )