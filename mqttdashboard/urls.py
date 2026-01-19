from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/monitor/dashboard', permanent=False)),
    path('admin/', admin.site.urls),
    path('monitor/', include('monitor.urls')),
]
