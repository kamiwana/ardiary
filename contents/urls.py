from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^like/$', LikeViewSet.as_view({'post': 'create'}), name='like'),
    url(r'^unlike/$', UnLikeViewSet.as_view({'post': 'create'}), name='unlike'),
    url(r'^$', ContentsViewSet.as_view({'get': 'list'}), name='contents_list'),
    url(r'^(?P<pk>\w+)/$', ContentsViewSet.as_view({'get': 'retrieve'}), name='contents_detail'),
    url(r'^comments/create/$', CommentCreateAPIView.as_view(), name='create'),
    url(r'^comments/list/$', CommentViewSet.as_view({'get': 'list'}), name='comments_list'),
    url(r'^comments/(?P<pk>\w+)/$', CommentViewSet.as_view({'get': 'delete'}), name='contents_delete'),
#    url(r'^comments/delete/(?P<pk>\d+)/$', CommentViewSet.as_view({'get': 'delete'}), name='comment_delete'),
#   url(r'^comments/update/(?P<pk>\d+)/$', CommentViewSet.as_view({'contents': 'update'}), name='comment_update'),
#    url(r'^update/(?P<pk>\w+)/$', ContentsViewSet.as_view({'post': 'update'}), name='contents_update'),
#    url(r'^delete/(?P<pk>\w+)/$', ContentsViewSet.as_view({'get': 'delete'}), name='contents_delete'),
]