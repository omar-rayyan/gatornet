from django.urls import path
from social_app import views

urlpatterns = [
    path('', views.root, name='root'),
    path('home', views.home, name='home'),
    path('post/<int:id>', views.view_post, name='view_post'),
    path('profile/<int:id>', views.view_profile, name='view_profile'),
    path('edit_profile', views.view_edit_profile_page, name='view_edit_profile_page'),
    path('edit_profile_confirm', views.update_profile, name='edit_profile'),
    path('create_post', views.create_post, name='create_post'),
    path('add_comment', views.add_comment, name='add_comment'),
    path('add_friend', views.add_friend, name='add_friend'),
    path('remove_friend', views.remove_friend, name='remove_friend'),
    path('search_user', views.search_user, name='search'),
    path('search_results', views.view_search_results, name='search_results'),
    path('edit_comment', views.edit_comment, name='edit_comment'),
    path('delete_post', views.delete_post, name='delete_post'),
    path('delete_post_view_post_view', views.delete_post_view_post_view, name='delete_post_view_post_view'),
    path('delete_comment', views.delete_comment, name='delete_comment'),
    path('edit_post', views.edit_post, name='edit_post'),
    path('like_post', views.like_post, name='like_post'),
    path('comment_on_post', views.view_post, name='comment_on_post'),
    path('share_post', views.share_post, name='share_post'),
]