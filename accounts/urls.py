from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signout/', views.signout, name='signout'), # 회원탈퇴
    path('update/', views.update, name='update'),
    path('password/', views.change_password, name='change_password'),
    path('profile/<username>/', views.profile, name='profile'),
    path('<int:user_pk>/follow/', views.follow, name='follow'),
    path('follow_list/<username>/', views.follow_list, name='follow_list'),
]
