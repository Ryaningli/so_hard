import datetime
import re
from functools import reduce

from hard.data_factory import DotDict


class Fields:

    def __init__(self, zh_name=None, custom_error_message=None, required=True, **kwargs):
        self.kw = DotDict(kwargs)
        self.is_valid = True
        self.error_message = '校验成功'
        self.zh_name = zh_name or '参数'
        self.custom_error_message = custom_error_message
        self.required = required

        self._data_type = self.kw.data_type
        self._max_length = self.kw.max_length
        self._min_length = self.kw.min_length
        self._equal = self.kw.equal
        self._not_equal = self.kw.not_equal
        self._greater = self.kw.greater
        self._less = self.kw.less
        self._greater_equal = self.kw.greater_equal
        self._less_equal = self.kw.less_equal
        self._regex = self.kw.regex
        self._date = self.kw.date
        self._datetime = self.kw.datetime
        self._func = self.kw.func

    def __call__(self, value, *args, **kwargs):
        """
        1.首先判断是否为必填，为非必填且值为None时，停止验证，直接返回成功
        2.通过初始化得kw值中获取需要验证的方法，
        :param value:
        :param args:
        :param kwargs:
        :return:
        """
        if self.required:
            if not self.check_required(value):
                return self.check_fail('不可为空')
        else:
            if value is None:
                return self.check_success()

        # 组合需要验证的方法
        checkers = []
        for k, v in self.kw.items():
            if hasattr(self, '_' + k):
                checkers.append('_check' + '_' + k)  # 如：max_length -> self._max_length
            else:
                raise AttributeError('无此属性: {}'.format(k))

        # 执行需要验证的方法
        for checker in checkers:
            check = getattr(self, checker)
            if not check(value):
                if self.custom_error_message:  # 子类自定义错误信息
                    err_msg = self.get_error_message(self.custom_error_message, default=False)
                else:  # 使用验证函数的注释文档作为错误信息
                    err_msg = self.get_error_message(check.__doc__)

                fmt = list(map(lambda x: str(getattr(self, '_' + x)), err_msg[1]))
                return self.check_fail(err_msg[0].format(*fmt))
        return self.check_success()

    @staticmethod
    def make_kwargs(old_kwargs, default_para_back='required', **kwargs):
        """
        此函数的使用场景：创建Fields类的子类时，按照合理的顺序传参验证(应该用不着了)
        :param old_kwargs: 子类中的参数
        :param default_para_back: 默认放到required后面
        :param kwargs: 字类中需要添加的参数
        :return: 按照合理顺序组合的参数
        """

        over = False
        if default_para_back not in old_kwargs:
            new_kwargs = {**kwargs, **old_kwargs}
        else:
            kw1 = {}
            kw2 = {}
            for o_k, o_v in old_kwargs.items():
                if not over:
                    kw1[o_k] = o_v
                    if o_k == default_para_back:
                        over = True
                else:
                    kw2[o_k] = o_v
            new_kwargs = {**kw1, **kwargs, **kw2}
        return new_kwargs

    @staticmethod
    def and_or(pattern, func, rule):
        """
        当验参方法需要考虑多个规则值时，使用此函数
        :param pattern: 可为字符串and或or
        :param func: 匿名函数
        :param rule: 规则参数
        :return: 是或否
        """
        Rule = []
        if isinstance(rule, tuple) or isinstance(rule, list):
            Rule = rule
        else:
            Rule.append(rule)

        if pattern == 'or':
            return reduce(lambda x, y: x or y, map(func, Rule))
        if pattern == 'and':
            return reduce(lambda x, y: x and y, map(func, Rule))

    @staticmethod
    def get_error_message(value, default=True):
        """
        传入参数，转换成合理的错误信息与format参数
        :param value: 错误信息
        :param default: 当为True时，取验证函数的注释，当为False时，直接取value
        :return: 返回元组，[0]为错误信息，[1]为format参数
        """
        err_msg = ''
        if default:
            for msg in value.split('\n'):
                if msg.strip().startswith(':error_message:'):  # 通过指定字符串开头的行找到错误信息行
                    err_msg = msg.split(':error_message:')[1].strip()  # 通过split取得错误信息
                    break
        else:
            err_msg = value
        if err_msg:
            msg_split = re.split(r'[{|}]', err_msg)  # 通过正则拆分大括号内的内容
            error_message = '{}'.join(msg_split[::2])  # 组装错误信息，加上{}
            fmt = msg_split[1::2]  # 组装format信息成列表，解包
            return error_message, fmt
        else:
            return '', ''

    def check_fail(self, error_message):
        return {
            'is_valid': False,
            'error_message': '{}: {}'.format(self.zh_name, error_message)
        }

    @staticmethod
    def check_success():
        return {
            'is_valid': True,
            'error_message': '校验成功'
        }

    def _check_data_type(self, value):
        """
        :error_message: 数据类型错误
        :param value: 为tuple时，为or关系
        """
        return self.and_or('or', lambda x: isinstance(value, x), self._data_type)

    def check_required(self, value):
        """
        :error_message: 不可为空
        :param value:
        :return:
        """
        if self.required:
            if value is not None:
                return True
        else:
            return True

    def _check_max_length(self, value):
        """
        :error_message: 长度不可大于{max_length}
        :param value:
        :return:
        """
        # 后期需考虑数据类型（字典、列表）
        return len(str(value)) <= self._max_length

    def _check_min_length(self, value):
        """
        :error_message: 长度不可小于{min_length}
        :param value:
        :return:
        """
        return len(str(value)) >= self._min_length

    def _check_equal(self, value):
        """
        :error_message: 必须等于{equal}
        :param value:
        :return:
        """
        return self.and_or('or', lambda x: x == value, self._equal)

    def _check_not_equal(self, value):
        """
        :error_message: 不可等于{not_equal}
        :param value:
        :return:
        """
        return self.and_or('or', lambda x: x != value, self._not_equal)

    def _check_greater(self, value):
        """
        :error_message: 必须大于{greater}
        :param value:
        :return:
        """
        return value > self._greater

    def _check_less(self, value):
        """
        :error_message: 必须小于{less}
        :param value:
        :return:
        """
        return value < self._less

    def _check_greater_equal(self, value):
        """
        :error_message: 必须大于等于{greater_equal}
        :param value:
        :return:
        """
        return value >= self._greater_equal

    def _check_less_equal(self, value):
        """
        :error_message: 必须小于等于{less_equal}
        :param value:
        :return:
        """
        return value <= self._less_equal

    def _check_regex(self, value):
        """
        :error_message: 正则匹配失败
        :param value:
        :return:
        """
        pattern = re.compile(self._regex)
        return self.and_or('or', lambda x: pattern.match(value), self._regex)

    def _check_date(self, value):
        """
        :error_message: 日期格式错误
        :param value:
        :return:
        """
        if self._date:
            try:
                datetime.datetime.strptime(value, '%Y-%m-%d')
                return True
            except ValueError:
                return False

    def _check_datetime(self, value):
        """
        :error_message: 时间格式错误
        :param value:
        :return:
        """
        if self._datetime:
            try:
                datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                return True
            except ValueError:
                return False

    def _check_func(self, value):
        """
        :error_message: 匿名函数检查错误
        :param value:
        :return:
        """
        return self._func(value)


class CharFields(Fields):
    def __init__(self, *args, **kwargs):
        # kwargs = self.make_kwargs(kwargs, data_type=str)
        super(CharFields, self).__init__(data_type=str, *args, **kwargs)


class IntegerFields(Fields):
    def __init__(self, *args, **kwargs):
        # kwargs = self.make_kwargs(kwargs, data_type=int)
        super(IntegerFields, self).__init__(data_type=int, *args, **kwargs)


class FloatFields(Fields):
    def __init__(self, *args, **kwargs):
        # kwargs = self.make_kwargs(kwargs, data_type=float)
        super(FloatFields, self).__init__(data_type=float, *args, **kwargs)


class NumFields(Fields):
    def __init__(self, *args, **kwargs):
        super(NumFields, self).__init__(data_type=(float, int), *args, **kwargs)


class EmailFields(CharFields):
    def __init__(self, *args, **kwargs):
        super(EmailFields, self).__init__(custom_error_message='格式错误',
                                          regex=r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', *args, **kwargs)
        
        
class DateFields(CharFields):
    def __init__(self, *args, **kwargs):
        super(DateFields, self).__init__(custom_error_message='日期格式错误', date=True, *args, **kwargs)


class DatetimeFields(CharFields):
    def __init__(self, *args, **kwargs):
        super(DatetimeFields, self).__init__(custom_error_message='时间格式错误', datetime=True, *args, **kwargs)
