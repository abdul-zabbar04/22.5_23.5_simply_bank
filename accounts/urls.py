from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserLogoutView, UserUpdateView, UserPasswordChangeView
urlpatterns = [
    path('signup/', UserRegistrationView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserUpdateView.as_view(), name='profile'),
    path('password/change/', UserPasswordChangeView.as_view(), name='password'),
]
