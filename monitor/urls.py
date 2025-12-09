from django.urls import path
from .views import monitor_view, home

urlpatterns = [
    path('', monitor_view, name='monitor'),
    path('dashboard/', home),
]