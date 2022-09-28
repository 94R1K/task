import os

from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from WebClient.views import index_page_router

urlpatterns = [
    # ... the rest of your URLconf goes here ...
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + [
  re_path('.*', index_page_router),
]

print(urlpatterns)
print('document_root=', settings.STATIC_ROOT)
