from django.urls import path
from .views import *

urlpatterns = [
    path('generate-draft/', generate_mou_view),
]
