from .Kmeans_plus_plus_training import kmeans_plus_plus_training
from .Warning import warning
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # 导入csrf_exempt装饰器
import uuid
# from data.raw_data0702 import get_employee_behavior_data
from .Response import R, StatusCodeEnum
import pandas as pd
from functools import wraps


# 定义回调函数
def training_callback(result, error=None):
    if error:
        if isinstance(error, StatusCodeEnum):
            return JsonResponse(R.error(error))
        else:
            return JsonResponse(R.error(StatusCodeEnum.OTHER, f"其他错误: {str(error)}"))
    else:
        return JsonResponse(R.ok(result))


# 修改主函数以接受回调函数
def run_training_main(request, callback):
    if request.method != 'GET':
        return callback(None, StatusCodeEnum.INVALID_REQUEST_METHOD)

    try:
        # http://10.61.70.112:8000/kmeans/training
        if kmeans_plus_plus_training():
            return callback('KMeans++训练完成')  # 返回成功响应
        else:
            return callback("今日KMeans++训练已完成")

    except Exception as e:
        # 发生其他未知错误
        print(f"Exception: {e}")
        return callback(None, e)


# 调用主函数时传递回调函数
@csrf_exempt
def run_training(request):
    return run_training_main(request, training_callback)


# 定义回调函数
def warning_callback(response_data=None, status_code=StatusCodeEnum, msg=None):
    if response_data is not None:
        return JsonResponse(R.ok(response_data))
    else:
        return JsonResponse(R.error(status_code, msg))


@csrf_exempt
def run_warning_view(request, callback):
    if request.method != 'POST':
        return callback(None, StatusCodeEnum.INVALID_REQUEST_METHOD)

    try:
        # 解析请求体中的JSON数据
        input_data = json.loads(request.body)
        # 从解析后的数据中获取员工信息
        employees_data = input_data.get('employees', [])
    except json.JSONDecodeError:
        # 如果JSON解析失败，返回错误响应
        return callback(None, StatusCodeEnum.INVALID_JSON)

    # 初始化员工姓名列表和日期列表
    employee_names = []
    dates = []

    # 遍历员工数据，提取每个员工的姓名和日期
    for employee_data in employees_data:
        employee_name = employee_data.get("employee_name")
        date = employee_data.get("date")

        # 检查是否缺少员工姓名或日期
        if not employee_name or not date:
            return callback(None, StatusCodeEnum.NECESSARY_PARAM_ERR)

        employee_names.append(employee_name)
        dates.append(date)

    print(employee_names)
    print(dates)

    try:
        # 调用预处理函数
        behavior_data_df = get_employee_behavior_data(employee_names, dates)

        # 检查预处理后数组的纬度是否正确
        # 初始化一个空列表来存储符合条件的姓名
        names_with_nan_idx = []
        names_without_nan_idx = []
        # 逐行检查最后一个值是否为NaN
        if behavior_data_df.shape[0] > 1:
            for idx, row in behavior_data_df.iterrows():
                if pd.isna(row.iloc[-1]):
                    names_with_nan_idx.append(idx)
                else:
                    names_without_nan_idx.append(idx)
        else:
            # 检查行为数据的列数是否为35列（5个设备 * 7天）
            expected_columns = 35
            if behavior_data_df.shape[1] != expected_columns + 1:  # 包含姓名列
                return callback(None, StatusCodeEnum.DATA_INSUFFICIENT, f"数据列数不足 {expected_columns}")

        # 使用索引过滤DataFrame
        new_behavior_data_df = behavior_data_df.loc[names_without_nan_idx]
        false_data = behavior_data_df.loc[names_with_nan_idx]

        # 运行KMeans++预警
        warning_data = warning(new_behavior_data_df)

        dates_df = pd.DataFrame(dates, columns=['日期'])
        date_warning_df = pd.DataFrame(dates_df.loc[names_without_nan_idx], columns=['日期'])
        warning_data_output = pd.concat([date_warning_df, warning_data], axis=1)
        data_false_df = pd.DataFrame(dates_df.loc[names_with_nan_idx], columns=['日期'])
        false_data_output = pd.concat([data_false_df, false_data], axis=1)

        # 初始化结果列表
        results = []
        for i in range(len(behavior_data_df)):
            if behavior_data_df.iloc[i]['姓名'] in warning_data_output['姓名'].values:
                mask = warning_data_output['姓名'].isin([behavior_data_df.iloc[i]['姓名']])
                result = {
                    'employee_name': behavior_data_df.iloc[i]['姓名'],
                    'date': dates[i],
                    'predictions': warning_data_output.loc[mask, '是否预警'].values[0],
                }
                results.append(result)
            else:
                result = {
                    'employee_name': behavior_data_df.iloc[i]['姓名'],
                    'date': dates[i],
                    'predictions': None,
                    'reason': f"以下员工的7次行为数据记录不足: {behavior_data_df.iloc[i]['姓名']}",
                }
                results.append(result)

        # 构建响应数据
        response_data = {
            'results': results,
        }
        return callback(response_data)

    except ValueError as e:
        # 员工7次数据不足
        print(f"ValueError: {e}")
        return callback(None, StatusCodeEnum.DATA_INSUFFICIENT, f"{str(e)}")

    except FileNotFoundError as e:
        # 模型文件未找到
        print(f"FileNotFoundError: {e}")
        return callback(None, StatusCodeEnum.MODEL_NOT_FOUND, f"模型文件未找到: {str(e)}")

    except TimeoutError as e:
        # 获取数据超时
        print(f"TimeoutError: {e}")
        return callback(None, StatusCodeEnum.DATA_PROCESSING_TIMEOUT, f"获取数据超时: {str(e)}")

    except Exception as e:
        # 发生其他未知错误
        print(f"Exception: {e}")
        return callback(None, StatusCodeEnum.OTHER, f"其他错误: {str(e)}")


@csrf_exempt
def run_warning(request):
    return run_warning_view(request, warning_callback)


# @csrf_exempt
# def run_training(request):
#     if request.method != 'GET':
#         return JsonResponse(R.error(StatusCodeEnum.INVALID_REQUEST_METHOD))
#
#     try:
#         # 获取是否运行KMeans++训练的参数
#         training = request.GET.get('training')
#         # http://127.0.0.1:8000/kmeans/training?training=yes
#
#         if training is None:
#             return JsonResponse(R.error(StatusCodeEnum.MISSING_KEY_PARAMETER, "Missing key parameter: training"))
#
#         if training != 'yes':
#             return JsonResponse(R.error(StatusCodeEnum.INVALID_KEY_VALUE, "Invalid value for training: yes"))
#
#         if kmeans_plus_plus_training():
#             return JsonResponse(R.ok('KMeans++训练完成'))   # 返回成功响应
#         else:
#             return JsonResponse(R.ok("今日KMeans++训练已完成"))
#
#     except Exception as e:
#         # 发生其他未知错误
#         print(f"Exception: {e}")
#         return JsonResponse(R.error(StatusCodeEnum.OTHER, f"其他错误: {str(e)}"))


# @csrf_exempt
# def run_warning(request):
#     # 生成请求ID，用于唯一标识每个请求（时间戳在最外层的 R.ok() 方法中实现）
#     # request_id = uuid.uuid4().hex
#
#     if request.method != 'POST':
#         return JsonResponse(R.error(StatusCodeEnum.INVALID_REQUEST_METHOD))
#
#     try:
#         # 解析请求体中的JSON数据
#         input_data = json.loads(request.body)
#         # 从解析后的数据中获取员工信息
#         employees_data = input_data.get('employee_info', [])
#     except json.JSONDecodeError:
#         # 如果JSON解析失败，返回错误响应
#         return JsonResponse(R.error(StatusCodeEnum.INVALID_JSON))
#
#     # 初始化员工姓名列表和日期列表
#     employee_names = []
#     dates = []
#
#     # 遍历员工数据，提取每个员工的姓名和日期
#     for employee_data in employees_data:
#         employee_name = employee_data.get("employee_name")
#         date = employee_data.get("date")
#
#         # 检查是否缺少员工姓名或日期
#         if not employee_name or not date:
#             return JsonResponse(R.error(StatusCodeEnum.NECESSARY_PARAM_ERR))
#
#         employee_names.append(employee_name)
#         dates.append(date)
#
#     print(employee_names)
#     print(dates)
#
#     try:
#         # 调用预处理函数
#         behavior_data_df = get_employee_behavior_data(employee_names, dates)
#
#         # 检查预处理后数组的纬度是否正确
#         # 初始化一个空列表来存储符合条件的姓名
#         names_with_nan_idx = []
#         names_without_nan_idx = []
#         # 逐行检查最后一个值是否为NaN
#         if behavior_data_df.shape[0] > 1:
#             for idx, row in behavior_data_df.iterrows():
#                 if pd.isna(row.iloc[-1]):
#                     names_with_nan_idx.append(idx)
#                 else:
#                     names_without_nan_idx.append(idx)
#         else:
#             # 检查行为数据的列数是否为35列（5个设备 * 7天）
#             expected_columns = 35
#             if behavior_data_df.shape[1] != expected_columns + 1:  # 包含姓名列
#                 return JsonResponse(R.error(StatusCodeEnum.DATA_INSUFFICIENT, f"数据列数不足 {expected_columns}"))
#
#         # 使用索引过滤DataFrame
#         new_behavior_data_df = behavior_data_df.loc[names_without_nan_idx]
#         false_data = behavior_data_df.loc[names_with_nan_idx]
#
#         # 运行KMeans++预警
#         warning_data, center_table_name_save = warning(new_behavior_data_df)
#
#         dates_df = pd.DataFrame(dates, columns=['日期'])
#         date_warning_df = pd.DataFrame(dates_df.loc[names_without_nan_idx], columns=['日期'])
#         warning_data_output = pd.concat([date_warning_df, warning_data], axis=1)
#         data_false_df = pd.DataFrame(dates_df.loc[names_with_nan_idx], columns=['日期'])
#         false_data_output = pd.concat([data_false_df, false_data], axis=1)
#
#         # 初始化结果列表
#         results = []
#         for i in range(len(behavior_data_df)):
#             if behavior_data_df.iloc[i]['姓名'] in warning_data_output['姓名'].values:
#                 mask = warning_data_output['姓名'].isin([behavior_data_df.iloc[i]['姓名']])
#                 result = {
#                     'employee_name': behavior_data_df.iloc[i]['姓名'],
#                     'date': dates[i],
#                     'predictions': warning_data_output.loc[mask, '是否预警'].values[0],
#                 }
#                 results.append(result)
#             else:
#                 result = {
#                     'employee_name': behavior_data_df.iloc[i]['姓名'],
#                     'date': dates[i],
#                     'predictions': None,
#                     'reason': f"7天的记录不足: 以下员工的7次数据不足: {behavior_data_df.iloc[i]['姓名']}",
#                 }
#                 results.append(result)
#
#         # 构建响应数据
#         response_data = {
#             # 'request_id': request_id,
#             'results': results,
#         }
#         return JsonResponse(R.ok(response_data))
#
#     except ValueError as e:
#         # 员工7次数据不足
#         print(f"ValueError: {e}")
#         return JsonResponse(R.error(StatusCodeEnum.DATA_INSUFFICIENT, f"{str(e)}"))
#
#     except FileNotFoundError as e:
#         # 模型文件未找到
#         print(f"FileNotFoundError: {e}")
#         return JsonResponse(R.error(StatusCodeEnum.MODEL_NOT_FOUND, f"模型文件未找到: {str(e)}"))
#
#     except TimeoutError as e:
#         # 获取数据超时
#         print(f"TimeoutError: {e}")
#         return JsonResponse(R.error(StatusCodeEnum.DATA_PROCESSING_TIMEOUT, f"获取数据超时: {str(e)}"))
#
#     except Exception as e:
#         # 发生其他未知错误
#         print(f"Exception: {e}")
#         return JsonResponse(R.error(StatusCodeEnum.OTHER, f"其他错误: {str(e)}"))


# def handle_exceptions(callback):
#     @wraps(callback)
#     def wrapper(*args, **kwargs):
#         try:
#             return callback(*args, **kwargs)
#         except ValueError as e:
#             print(f"ValueError: {e}")
#             return JsonResponse(R.error(StatusCodeEnum.DATA_INSUFFICIENT, f"{str(e)}"))
#         except FileNotFoundError as e:
#             print(f"FileNotFoundError: {e}")
#             return JsonResponse(R.error(StatusCodeEnum.MODEL_NOT_FOUND, f"模型文件未找到: {str(e)}"))
#         except TimeoutError as e:
#             print(f"TimeoutError: {e}")
#             return JsonResponse(R.error(StatusCodeEnum.DATA_PROCESSING_TIMEOUT, f"获取数据超时: {str(e)}"))
#         except Exception as e:
#             print(f"Exception: {e}")
#             return JsonResponse(R.error(StatusCodeEnum.OTHER, f"其他错误: {str(e)}"))
#     return wrapper
#
#
# def extract_employee_data(request):
#     input_data = json.loads(request.body)
#     employees_data = input_data.get('employee_info', [])
#     employee_names = []
#     dates = []
#     for employee_data in employees_data:
#         employee_name = employee_data.get("employee_name")
#         date = employee_data.get("date")
#         if not employee_name or not date:
#             raise ValueError("缺少必要员工信息")
#         employee_names.append(employee_name)
#         dates.append(date)
#     return employee_names, dates
#
#
# def preprocess_data(employee_names, dates):
#     behavior_data_df = get_employee_behavior_data(employee_names, dates)
#     names_with_nan_idx = []
#     names_without_nan_idx = []
#     if behavior_data_df.shape[0] > 1:
#         for idx, row in behavior_data_df.iterrows():
#             if pd.isna(row.iloc[-1]):
#                 names_with_nan_idx.append(idx)
#             else:
#                 names_without_nan_idx.append(idx)
#     else:
#         expected_columns = 35
#         if behavior_data_df.shape[1] != expected_columns + 1:
#             raise ValueError(f"数据列数不足 {expected_columns}")
#     new_behavior_data_df = behavior_data_df.loc[names_without_nan_idx]
#     false_data = behavior_data_df.loc[names_with_nan_idx]
#     return new_behavior_data_df, false_data, names_with_nan_idx, names_without_nan_idx, dates
#
#
# def generate_warning_data(new_behavior_data_df, dates, names_without_nan_idx):
#     warning_data, center_table_name_save = warning(new_behavior_data_df)
#     dates_df = pd.DataFrame(dates, columns=['日期'])
#     date_warning_df = pd.DataFrame(dates_df.loc[names_without_nan_idx], columns=['日期'])
#     warning_data_output = pd.concat([date_warning_df, warning_data], axis=1)
#     return warning_data_output
#
#
# def compile_results(behavior_data_df, warning_data_output, dates):
#     results = []
#     for i in range(len(behavior_data_df)):
#         if behavior_data_df.iloc[i]['姓名'] in warning_data_output['姓名'].values:
#             mask = warning_data_output['姓名'].isin([behavior_data_df.iloc[i]['姓名']])
#             result = {
#                 'employee_name': behavior_data_df.iloc[i]['姓名'],
#                 'date': dates[i],
#                 'predictions': warning_data_output.loc[mask, '是否预警'].values[0],
#             }
#             results.append(result)
#         else:
#             result = {
#                 'employee_name': behavior_data_df.iloc[i]['姓名'],
#                 'date': dates[i],
#                 'predictions': None,
#                 'reason': f"7天的记录不足: 以下员工的7次数据不足: {behavior_data_df.iloc[i]['姓名']}",
#             }
#             results.append(result)
#     return results
#
#
# @csrf_exempt
# @handle_exceptions
# def run_warning(request):
#     if request.method != 'POST':
#         return JsonResponse(R.error(StatusCodeEnum.INVALID_REQUEST_METHOD))
#     # 提取json员工数据
#     employee_names, dates = extract_employee_data(request)
#     # 数据预处理
#     new_behavior_data_df, false_data, names_with_nan_idx, names_without_nan_idx, dates = preprocess_data(employee_names, dates)
#     # 通过KMeans++预警
#     warning_data_output = generate_warning_data(new_behavior_data_df, dates, names_without_nan_idx)
#     # 输出结果构建
#     results = compile_results(new_behavior_data_df, warning_data_output, dates)
#     # 构建json输出数据
#     response_data = {
#         'results': results,
#     }
#     return JsonResponse(R.ok(response_data))