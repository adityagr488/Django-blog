"""
URL mappings for the blog API.
"""

from django.urls import path
from blog import views as blog_view

app_name = 'blog'

urlpatterns = [
    path('', blog_view.BlogView().as_view(), name='create-blog'),
    path('/<int:id>', blog_view.BlogWithCommentsView().as_view(), name='blog'),
    path('/my-blogs', blog_view.MyBlogsView.as_view(), name='my-blogs'),
    path('/all-blogs', blog_view.AllBlogsView.as_view(), name='all-blogs'),
    path('/comment/<int:id>', blog_view.CommentView().as_view(), name='comment'),
    path('/like/<int:id>', blog_view.LikeView().as_view(), name='like'),
    path('/unlike/<int:id>', blog_view.UnLikeView().as_view(), name='unlike'),
]
