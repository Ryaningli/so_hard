import json


class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        print('------------------------------请求----------------------------')
        print(json.loads(request.body))
        print('------------------------------请求----------------------------')
        response = self.get_response(request)
        print('------------------------------返回----------------------------')
        print('------------------------------返回----------------------------')

        # Code to be executed for each request/response after
        # the view is called.

        return response