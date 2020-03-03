from django.conf.urls import url
from .views import *
from django.urls import path

urlpatterns = [
    url(r'^like$', Like.as_view(), name='like'),
    url(r'^unlike$', UnLike.as_view(), name='unlike'),
    url(r'^qrdatas/(?P<qr_data>.*)$', QRDataDetail.as_view(), name='qrdata'),
    url(r'^$', ContentsList.as_view(), name='contents_create'),
    url(r'^(?P<pk>\d+)$', ContentsDetail.as_view(), name='contents_detail'),
  #  path('something/<slug:qr_data>', ContentsDetail.as_view(), name='contents_detail'),
    url(r'^comments/create$', CommentCreateAPIView.as_view(), name='create'),
    url(r'^comments$', CommentList.as_view(), name='comment_list'),
    url(r'^comments/(?P<pk>\d+)$', CommentDetail.as_view(), name='comment_detail'),

#    url(r'^comments/delete/(?P<pk>\d+)/$', CommentViewSet.as_view({'get': 'delete'}), name='comment_delete'),
#   url(r'^comments/update/(?P<pk>\d+)/$', CommentViewSet.as_view({'contents': 'update'}), name='comment_update'),
#    url(r'^update/(?P<pk>\w+)/$', ContentsViewSet.as_view({'post': 'update'}), name='contents_update'),
#    url(r'^delete/(?P<pk>\w+)/$', ContentsViewSet.as_view({'get': 'delete'}), name='contents_delete'),
]