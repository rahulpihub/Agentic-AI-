from django.urls import path
from .views import test_connection

urlpatterns = [
    path('ping/', test_connection),
]
