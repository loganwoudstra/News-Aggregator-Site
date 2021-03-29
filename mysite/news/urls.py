from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('user_preferences/', views.user_preferences, name='user_preferences'),
]