from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('offer/<int:id>/', views.offer_detail, name='offer_detail'),
    path('donate/<int:offer_id>/', views.donate, name='donate'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('delete_offer/<int:offer_id>/', views.delete_offer, name='delete_offer'),
    path('profile/<int:user_id>/', views.view_profile, name='view_profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('success_stories/', views.success_stories, name='success_stories'),
    path('add_comment/<int:offer_id>/', views.add_comment, name='add_comment'),
    path('get_comments/<int:offer_id>/', views.get_comments, name='get_comments'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]
