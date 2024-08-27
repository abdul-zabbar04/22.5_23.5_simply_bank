from django.contrib import admin
from django.urls import path, include
from core.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts', include('accounts.urls')),
    path('transactions', include('transactions.urls')),
    path('', home.as_view(), name= 'home')
]
