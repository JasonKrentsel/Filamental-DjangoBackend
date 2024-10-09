from django.urls import path
from .views import OrgMasterUserView

urlpatterns = [
    path('user-registration/', OrgMasterUserView.as_view(),
         name='user-registration'),
]
