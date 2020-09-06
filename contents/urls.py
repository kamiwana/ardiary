from django.conf.urls import url
from .views import *
from django.urls import path

urlpatterns = [
    url(r'^like$', LikeAPI.as_view(), name='like'),
    url(r'^like/check$', LikeCheckAPI.as_view(), name='like_check'),
    url(r'^unlike$', UnLikeAPI.as_view(), name='unlike'),
    url(r'^unlike/check$', UnLikeCheckAPI.as_view(), name='unlike_check'),
    url(r'^like/set$', LikeSetAPI.as_view(), name='like_set'),
    url(r'^like/get$', LikeGetAPI.as_view(), name='like_get'),
    url(r'^list/(?P<user>\d+)$', ContentsListAPI.as_view(), name='contents_list'),
    url(r'^detail/(?P<qr_data>.*)$', ContentsDetailAPI.as_view(), name='contents_detail'),
    url(r'^qrdatas/(?P<qr_data>.*)$', QRDataDetailAPI.as_view(), name='qrdata'),
#    url(r'^contentsfiles$', ContentsFilesCreateAPI.as_view(), name='contetnsfiles'),
    url(r'^$', ContentsCreateAPI.as_view(), name='contents_create'),
    url(r'^(?P<pk>\d+)/(?P<user>\d+)$', ContentsUpdateAPI.as_view(), name='contents_update'),
    url(r'^password/create$', ContentsPasswordCreateAPI.as_view(), name='contents_password_create'),
    url(r'^password/update$', ContentsPasswordUpdateAPI.as_view(), name='contents_password_update'),
    url(r'^password/delete$', ContentsPasswordDeleteAPI.as_view(), name='contents_password_delete'),
    url(r'^password$', ContentsPasswordAPI.as_view(), name='contents_password_get'),
#    url(r'^password/update$', ContentsPasswordUpdateAPI.as_view(), name='contents_password_update'),
  #  url(r'^password$', ContentsPasswordDetail.as_view(), name='contents_passworde'),
    url(r'^comments/create$', CommentCreateAPI.as_view(), name='create'),
    url(r'^comments$', CommentListAPI.as_view(), name='comment_list'),
    url(r'^comments/delete/(?P<pk>\d+)$', CommentDeleteAPI.as_view(), name='comment_delete'),

    #  path('something/<slug:qr_data>', ContentsDetail.as_view(), name='contents_detail'),
#    url(r'^comments/delete/(?P<pk>\d+)/$', CommentViewSet.as_view({'get': 'delete'}), name='comment_delete'),
#   url(r'^comments/update/(?P<pk>\d+)/$', CommentViewSet.as_view({'contents': 'update'}), name='comment_update'),
#    url(r'^update/(?P<pk>\w+)/$', ContentsViewSet.as_view({'post': 'update'}), name='contents_update'),
#    url(r'^delete/(?P<pk>\w+)/$', ContentsViewSet.as_view({'get': 'delete'}), name='contents_delete'),
]