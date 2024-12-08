from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/<int:pk>/', views.PlayerRetrieveView.as_view(), name='player-detail'),
    path('profile/<int:pk>/update/', views.PlayerUpdateView.as_view(), name='player-update'),
]
