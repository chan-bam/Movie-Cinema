from django.urls import path
from . import views

app_name = 'movies'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:movie_pk>/', views.detail, name='detail'),
    path('create/', views.create, name='create'),
    path('<int:movie_pk>/update/', views.update, name='update'),
    path('<int:movie_pk>/delete/', views.delete, name='delete'),
    path('<int:movie_pk>/comments/', views.comment_create, name='comment_create'),
    path('<int:movie_pk>/comments/<int:comment_pk>/update/', views.comment_update, name='comment_update'),
    path('<int:movie_pk>/comments/<int:comment_pk>/delete/', views.comment_delete, name='comment_delete'),
    path('<int:movie_pk>/scraps/', views.scraps, name='scraps'), # url 마지막에 '/' 누락으로 1시간 반동안 에러찾음.... url 못찾아서 404에러남
    path('movie/search/', views.movie_search, name="movie_search"),
    path('recommended/<int:options>/', views.recommended, name='recommended'),
    path('movie_list/<int:option>/', views.movie_list, name='movie_list'),
]