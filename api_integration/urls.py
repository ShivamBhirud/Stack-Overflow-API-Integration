from . import views
from django.urls import path, include


urlpatterns = [
    path('data', views.get_data, name='data'),
]