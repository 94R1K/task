import logging

from django.conf import settings
from django.http import FileResponse

logger = logging.getLogger(__name__)


def index_page_router(request):
  print('index_page_router')
  logger.info("index_page_router: " + request.path)
  return FileResponse(open(settings.STATIC_ROOT + '/index.html', 'rb'))
