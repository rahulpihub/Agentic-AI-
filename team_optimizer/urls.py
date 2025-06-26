from django.urls import path
from .views import *
from .langgraph_flow import *

urlpatterns = [
    path('generate-draft/', generate_mou_view),
    path('approvals/', get_approvals),
    path('update-approval/', update_approval),  # ✅ Add this
]
