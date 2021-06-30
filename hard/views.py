from hard.response_factory import response

# Create your views here.
from hard.validator.validator import validator


@validator('Login')
def test(request):
    a = request.body
    print(a.is_valid)
    print(a.error_message)
    return response(code=0, msg='测试返回成功', data=a)


