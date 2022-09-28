import imp

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
  path('admin/', admin.site.urls),
  path('', include('Api.urls')),
  path('', include('WebClient.urls')),
]
