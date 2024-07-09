from django.urls import path
from .views import *

urlpatterns = [
    path('test/', IndexView.as_view(), name='index'),
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('users/<str:userId>', UserDetailView.as_view(), name='user-detail'),
    path('organisations', OrganisationView.as_view(), name='organisations'),
    path('organisations/<str:orgId>', OrganisationDetailView.as_view(), name='organisation-detail'),
    path('organisations/<str:orgId>/users', AddUserToOrganisationView.as_view(), name='add-user-to-organisation'),
]