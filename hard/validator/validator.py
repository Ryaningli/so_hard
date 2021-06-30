from functools import wraps
from hard.validator import validate_scheme


def validator(scheme):
    def validator_decorator(func):
        @wraps(func)
        def wrapper(request):
            checker = getattr(validate_scheme, scheme)()
            data = request.body
            result = checker.__get_result__(data)
            request.body['is_valid'] = result['is_valid']
            request.body['error_message'] = result['error_message']
            return func(request)
        return wrapper
    return validator_decorator
