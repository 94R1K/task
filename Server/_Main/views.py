import json

from django.http import HttpResponse


def login_page_router(request):
  response = {}
  response['data'] = '{test: \"Welcome!\"}'
  return HttpResponse(json.dumps(response), content_type="application/json")
