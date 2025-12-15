from django.urls import path
from .views import monitor_view, home, data_view

urlpatterns = [
    path('', monitor_view, name='monitor'),
    path('dashboard/', home),
    path('data/', data_view, name='data'),
]