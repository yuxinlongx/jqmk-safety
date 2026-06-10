import json
import os
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from logistic.logistic_model import LogisticModel
from .result import R, StatusCodeEnum
import uuid
# from data.raw_data0702 import get_employee_behavior_data  # 导入张阳的函数

@csrf_exempt
def logistic_prediction_view(request):
    # 检查请求方法是否为POST
    if request.method != 'POST':
        return JsonResponse(R.error(StatusCodeEnum.INVALID_REQUEST_METHOD))

    try:
        # 解析请求体中的JSON数据
        input_data = json.loads(request.body)
        # 从解析后的数据中获取员工信息
        employees_data = input_data.get('employees', [])
    except json.JSONDecodeError:
        # 如果JSON解析失败，返回错误响应
        return JsonResponse(R.error(StatusCodeEnum.INVALID_JSON))

    # 初始化结果列表、员工姓名列表和日期列表
    predictions = []
    employee_names = []
    dates = []

    # 遍历员工数据，提取每个员工的姓名和日期
    for employee_data in employees_data:
        employee_name = employee_data.get("employee_name")
        date = employee_data.get("date")

        # 检查是否缺少员工姓名或日期
        if not employee_name or not date:
            return JsonResponse(R.error(StatusCodeEnum.NECESSARY_PARAM_ERR))

        employee_names.append(employee_name)
        dates.append(date)

    try:
        # 使用张阳的函数获取行为数据
        behavior_data_df = get_employee_behavior_data(employee_names, dates)

        # 检查预处理后数组的维度是否正确
        names_with_nan = []
        for _, row in behavior_data_df.iterrows():
            if pd.isna(row.iloc[-1]):
                names_with_nan.append(row['姓名'])

        # 检查行为数据的列数是否为35列（5个设备 * 7天）
        expected_columns = 35
        if behavior_data_df.shape[1] != expected_columns + 1:  # 包含姓名列
            return JsonResponse(R.error(StatusCodeEnum.DATA_INSUFFICIENT, f"数据列数不足 {expected_columns}"))

        # 移除不需要的姓名列
        behavior_data_df = behavior_data_df.drop(columns=['姓名'])

        behavior_data_list = behavior_data_df.to_dict(orient='records')

        # 遍历每个员工的数据，进行预测
        for i, employee_data in enumerate(employees_data):
            employee_name = employee_data.get("employee_name")
            date = employee_data.get("date")
            if employee_name in names_with_nan:
                predictions.append({
                    'employee_name': employee_name,
                    'date': date,
                    'score':None,
                    'level': None,
                    'reason': f"以下员工的7次行为数据记录不足: {employee_name}",
                    # 'score': None  # 无法计算标准化分数
                })
                continue  # 跳过数据不足的员工

            # 将行为数据转换为模型预测用的DataFrame
            behavior_data = behavior_data_list[i]
            X_new = pd.DataFrame([behavior_data])

            # 动态构建模型路径
            current_directory = os.path.dirname(__file__)
            model_path = os.path.join(current_directory, '../logistic/logistic_model.pkl')

            # 调试信息：打印模型路径
            print(f"Model path: {model_path}")

            # 加载并使用逻辑回归模型进行预测
            model = LogisticModel()
            model.load_model(model_path)

            scores, predictions_array, normalized_scores, risk_levels = model.predict(X_new)

            # 根据风险等级设置预测结果
            risk_level = risk_levels[0]
            normalized_score = normalized_scores[0]

            # 添加每个员工的预测结果到结果列表
            predictions.append({
                'employee_name': employee_name,
                'date': date,
                'score': normalized_score,
                'level': risk_level,
                'reason': None
            })

        # 返回所有员工的预测结果
        response_data = {
            'predictions': predictions
        }
        return JsonResponse(R.ok(response_data))

    except FileNotFoundError as e:
        # 模型文件未找到
        print(f"FileNotFoundError: {e}")
        return JsonResponse(R.error(StatusCodeEnum.MODEL_NOT_FOUND, f"模型文件未找到: {str(e)}"))

    except TimeoutError as e:
        # 获取数据超时
        print(f"TimeoutError: {e}")
        return JsonResponse(R.error(StatusCodeEnum.DATA_PROCESSING_TIMEOUT, f"获取数据超时: {str(e)}"))

    except ValueError as e:
        # 员工7次数据不足
        print(f"ValueError: {e}")
        return JsonResponse(R.error(StatusCodeEnum.DATA_INSUFFICIENT, f"{str(e)}"))

    except Exception as e:
        # 捕捉所有其他错误
        print(f"Exception: {e}")
        return JsonResponse(R.error(StatusCodeEnum.OTHER, f"其他错误: {str(e)}"))
