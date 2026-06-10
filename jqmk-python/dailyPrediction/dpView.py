import requests
from django.http import JsonResponse
from dailyPrediction.daily_prediction import daily_prediction


def call_external_api():
    print('调用API开始')
    # url = 'http://10.60.217.208:5389/jqmk/warning/data'  # Web
    # url = 'http://10.61.68.125:5389/jqmk/portrait/data'  # Phone
    url = 'http://localhost:5389/jqmk/portrait/data'
    headers = {
        # 'Authorization': 'Bearer YOUR_API_KEY',  # 验证身份的信息，通常是在使用 API 时需要提供的访问令牌（access token）
        'Content-Type': 'application/json'  # 指明发送给 API 的数据类型
    }
    # 运行预测函数
    results = []
    daily_data, meager_data = daily_prediction()
    for _, row in daily_data.iterrows():
        result = {
            'employeeId': row['工号'],
            'personName': row['姓名'],
            'date': row['检测日期'],
            'level': row['综合预警'],
        }
        results.append(result)
    if len(meager_data) > 0:
        for _, row in meager_data.iterrows():
            result = {
                'employeeId': row['工号'],
                'personName': row['姓名'],
                'date': row['检测日期'],
                'level': '数据不足',
            }
            results.append(result)

    # 构建响应数据
    payload = {
        'data': results,
    }

    # 发送请求
    response = requests.post(url, headers=headers, json=payload)
    print('调用API完成')

    # if response.status_code == 200:
    #     data = response.json()
    #     # data = response
    #     print('调用API完成')
    #     return JsonResponse(data, safe=False)
    # else:
    #     print('调用API完成')
    #     return JsonResponse({'error': 'Failed to fetch data'}, status=response.status_code)

# call_external_api()