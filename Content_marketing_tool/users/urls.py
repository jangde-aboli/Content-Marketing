from django.urls import path
from .views import add_user_view , user_dashboard_view ,publication_list_view,dashboard_view

urlpatterns = [
    path('',dashboard_view, name='dashboard'),
    path('add-user/', add_user_view, name='add-user'),
    path('user-dashboard/',user_dashboard_view, name='user-dashboard'),
    path('publication-site/',publication_list_view, name='publication_list'),
     
]
