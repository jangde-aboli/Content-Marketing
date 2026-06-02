from django.urls import path
from .views import add_project_view, add_in_existing_project_view 

urlpatterns = [
    path('add-new/', add_project_view, name='add-project'),
    path('add-existing/', add_in_existing_project_view, name='add-in-existing-project'),
]
