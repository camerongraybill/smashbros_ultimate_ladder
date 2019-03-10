from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('leader_board', views.LeaderBoard.as_view(), name='leader_board'),
    path('stats', views.Stats.as_view(), name='stats'),
    path('players/<int:pk>/', views.PlayerDetail.as_view(), name='player_details'),
    path('schools/<int:pk>/', views.SchoolDetail.as_view(), name='school_details'),
    path('characters/<int:pk>/', views.CharacterDetail.as_view(), name='character_details'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.SignUp.as_view(), name='signup'),
    path('profile', views.EditProfile.as_view(), name='profile'),
    path('report', views.Report.as_view(), name='report')
]
