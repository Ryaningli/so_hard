from hard.validator.validate_base import ValidateBase
from hard.validator.validator_fields import CharFields, EmailFields, NumFields, DateFields, DatetimeFields, \
    IntegerFields


class Login(ValidateBase):
    username = CharFields('用户名', min_length=4, max_length=20, not_equal='test001')
    password = CharFields('密码', min_length=8, max_length=18)
    email = EmailFields('电子邮箱', required=True)
    height = NumFields('身高', required=False)
    birthday = DateFields('生日')
    create_time = DatetimeFields('创建时间')
    age = IntegerFields('年龄', greater_equal=0, less=150)
    test = IntegerFields('匿名函数', func=lambda x: x > 10)
