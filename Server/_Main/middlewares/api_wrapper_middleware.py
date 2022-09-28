import copy
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import gettext_lazy
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnList

# origin
# https://djangosnippets.org/snippets/10717/
# https://docs.djangoproject.com/en/4.0/ref/request-response/#httpresponse-object

class ApiWrapperMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response
    
    # One-time configuration and initialization.
    self.pagination_response_keys = ['pag_cnt', 'pag_page_size', 'pag_cur', 'pag_next', 'pag_prev']

    self.default_response_keys = [
      'status', 'data', 'msg',                                          # basic custom fields
      'detail', 'non_field_errors',                                     # DJANGO error indicators
      # 'pag_cnt', 'pag_page_size', 'pag_cur', 'pag_next', 'pag_prev',  # pagination fields
    ] + self.pagination_response_keys

    # I suggest using message translation map
    self.lang_localization_map = {
      'en-us': {
        "internal": "Internal Server Error",
        "unknown": "Unknown Server Error",
        "success": "Success",
        "pag_err": "Have you just tried to use pagination? \
          Make sure you've provided all this fileds: " + ', '.join(self.pagination_response_keys),
      },
      'ru-ru': {
        "internal": "Сервис недоступен",
        "unknown": "Сервис недоступен",
        "success": "Успех",
        "pag_err": "Вы хотели использовать пагинацию? \
            Убедитесь, что верно указали все следующие поля: " + ', '.join(self.pagination_response_keys),
      }
    }

    # probably you may like to use LANGUAGE_CODE from settings
    # than import it here and there from common config to
    # resolve cycle dependency
    self.LANGUAGE_CODE = 'ru-ru'


    if self.LANGUAGE_CODE == None:
      self.LANGUAGE_CODE = 'en-us'
    if self.LANGUAGE_CODE in self.lang_localization_map:
      self.localization = self.lang_localization_map[self.LANGUAGE_CODE]
    else:
      print('[ api_wrapper_middleware ]', self.LANGUAGE_CODE,
        'encoding is not supported. English message description is used')
      self.localization = self.lang_localization_map['en-us']
    
    print('[ api_wrapper_middleware ] is active!')

  def __call__(self, request):
    # Code to be executed for each request before
    # the view (and later middleware) are called.

    response = self.get_response(request)

    # Code to be executed for each request/response after
    # the view is called

    # We need to assure if DRF Response type AND is JSON AND data is really JSON-object
    # that might be FileResponnse or HTTPResponse from your other django-apps
    if isinstance(response, Response):

      # __ response.get('Content-Type') __ usually looks like for DRF: __ application/json; charset=utf-8 __
      if response.get('Content-Type').lower().find('application/json') != -1 and \
          (isinstance(response.data, dict) or isinstance(response.data, ReturnList)):
        try:
          response_data = self.render_response(response)
          response.data = response_data
          response.content = json.dumps(response_data, cls=DjangoJSONEncoder)
        except Exception as e:
          print('[ api_wrapper_middleware ] [ERROR]', e)
          pass
  
    return response

  def render_response(self, response):
    """
    function to fixed the response API following with this format:
    
    __Default Response Structure__

    [1] success single
        {
          "status":      int64,    // <http-code>,
          "msg":         "",       // <empty on success>
          "data":        object,
        }

    [2] success list
        {
          "status":      int64,    // <http-code>,
          "msg":         "",       // <empty on success>
          "data":        object[],

          "count":       int64,
          "page_size":   int64,
          "cur_page":    int64,
          "next":        int64,   // <cur_page + 1 or so>,
          "prev":        null,
        }

    [3] failed
        {
          "status":      int64,    // <http-code> 4** and 5**,
          "msg":         string,   // <The error message>
          "data":        {},       // empty object
        }
    """
    data_copy = copy.deepcopy(response.data)

    response_data = {
      'data': {},
      'msg': "",
      'status': response.status_code,
    }


    # classic django error message propogation mechanism suggest using 'detail' key
    # https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling
    # 'non_field_errors' key appearce when dealing with forms 
    # https://docs.djangoproject.com/en/4.0/ref/forms/api/#django.forms.Form.non_field_errors

    # updating the response msg
    if 'detail' in data_copy:
      response_data.update({'msg': data_copy.get('detail')})
      del data_copy['detail']

    # this may help to display form validation error | probably it is better to do in
    # your frontend part. I do so and I've commented corresponding strings
    elif 'non_field_errors' in data_copy:
      # response_errors = '<br />'.join(data_copy.get('non_field_errors'))
      # response_data.update({'msg': response_errors})
      response_data.update({'msg': data_copy['non_field_errors']})
      del data_copy['non_field_errors']

    # store the internal errors messages. Responses with 4** and 5** codes are considered to be errors  
    # https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#1xx_informational_response
    if response.status_code >= 400:
      response_errors_msgs = []
      response_errors_keys = []

      for (key, value) in data_copy.items():
        # DRF places its error messages in JSON key-value pair as a value
        # of corresponing request key field. So all key-value pairs that
        # are not follow __Default Response Structure__ are error messages

        # E.g. I performed registration with 3 fields: email (unique), login (unique) and password.
        # When I try to register anather user with same parametres, DRF returns the following:
        # { "email": "user with this email already exists." }
        # and there is no other correct fields
        if key not in self.default_response_keys:
          errors = ' '.join([str(v) for v in value])
          response_errors_msgs.append('%s: %s' % (key, errors))
          response_errors_keys.append(key)

      if len(response_errors_msgs) > 0:
        # if you want to directly display it on form, uncomment the following
        # response_errors_msgs = '<br />'.join(response_errors_msgs)
        response_errors_msgs = '\n'.join(response_errors_msgs)
        response_data.update({'msg': response_errors_msgs})

      # deleting the errors in the field keys.
      # makes no sence if all the extra fields are considered as errors
      # if len(response_errors_keys) > 0:
      #   list(map(data_copy.pop, response_errors_keys))

      if not response_data.get('msg'):
        if response.status_code < 500:
          response_data.update({'msg': gettext_lazy(self.localization['unknown'])})
        else:
          response_data.update({'msg': gettext_lazy(self.localization['internal'])})

    # 1** codes are information messages. I Consider data to be empty. Not so useful.
    elif response.status_code >= 100 and response.status_code < 200:
      if not response_data.get('msg'):
        response_data.update({'msg': gettext_lazy(self.localization['success'])})

    # 2** and 3** codes
    else:
      if all([x in data_copy for x in self.pagination_response_keys]):
        for key in self.pagination_response_keys:
          response_data.update({key: data_copy[key]})
          del data_copy[key]
      elif any([x in data_copy for x in self.pagination_response_keys]):
        err_msg = self.localization['pag_err']
        print('[ api_wrapper_middleware ]', err_msg)
        response_data.update({'msg': '\n'.join([response_data.get('msg') + err_msg])})

      response_data.update({'data': data_copy})

    return response_data
