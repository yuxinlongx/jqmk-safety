from enum import Enum
import time


class StatusCodeEnum(Enum):
    """ 状态码枚举类，用于定义API响应中可能出现的各种状态码和对应的消息解释。 """
    OK = (0, '成功')
    # 111操作成功完成，数据有效且预测成功。

    NECESSARY_PARAM_ERR = (4001, '缺少员工姓名或日期')
    # 111请求中缺少了必须的参数，例如未提供员工姓名或日期。

    DATA_INSUFFICIENT = (4002, '7天的记录不足')
    # 111提供的行为数据不足以进行有效的预测，例如少于7天的行为记录。

    DATA_PROCESSING_TIMEOUT = (4003, '获取数据超时')
    # 111从数据库或数据源获取数据的过程耗时过长，超出了预定的时间限制。

    MODEL_NOT_FOUND = (4004, '模型文件未找到')
    # 111未能找到所需的预测模型文件，可能是文件路径错误或文件未被正确部署。

    INVALID_REQUEST_METHOD = (4005, '无效的请求方法')
    # 111使用了不适合当前端点的HTTP方法，例如对于需要POST方法的请求使用了GET。

    INVALID_JSON = (4006, '无效的JSON格式')
    # 111提交的JSON数据格式有误，无法解析。

    OTHER = (9999, '其他未知错误')
    # 111遇到了未预见的错误，用于不符合任何已定义错误类型的异常情况。

    @property
    def code(self):
        """获取状态码"""
        return self.value[0]

    @property
    def errmsg(self):
        """获取状态码信息"""
        return self.value[1]


class R:
    """ 统一返回结果类 """

    @staticmethod
    def ok(data):
        """ 成功响应 """
        return {
            'success': True,
            'code': StatusCodeEnum.OK.code,
            'msg': StatusCodeEnum.OK.errmsg,
            'data': data,
            # 'timestamp': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

    @staticmethod
    def error(enum, additional_msg=''):
        """ 错误响应 """
        return {
            'success': False,
            'code': enum.code,
            'msg': f'{enum.errmsg}: {additional_msg}',
            'data': None,
            # 'timestamp': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
