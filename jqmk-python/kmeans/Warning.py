import pandas as pd
import math
from sqlalchemy import create_engine, MetaData
from datetime import date
import numpy as np
from datetime import datetime, timedelta

"""第三版"""


def warning(new_dataframe):
    print('kmeans开始')
    # 创建数据库连接
    # engine_record = create_engine('mysql+mysqlconnector://root:bjtu%408401a@8.135.100.109:3306/jinqiao_meikuang')  # 阿里云
    # engine_center = create_engine('mysql+mysqlconnector://root:bjtu%408401a@8.135.100.109:3306/jinqiao_meikuang')
    # engine_record = create_engine('mysql+mysqlconnector://root:root@localhost:3306/jinqiao_meikuang')  # 金桥堡垒机
    # engine_center = create_engine('mysql+mysqlconnector://root:root@localhost:3306/jinqiao_meikuang')
    engine_record = create_engine('mysql+mysqlconnector://root:jqmk%402023@localhost:3306/exam_system')  # 本地数据库
    engine_center = create_engine('mysql+mysqlconnector://root:jqmk%402023@localhost:3306/exam_system')
    # 创建一个 MetaData 实例
    metadata_record = MetaData()
    metadata_center = MetaData()
    # 将其与引擎关联
    metadata_record.reflect(bind=engine_record)
    metadata_center.reflect(bind=engine_center)
    # 选择记录表
    record_table_name = 'kmeans_record'
    center_table_name = 'kmeans_center'
    # 读取表格数据并转换为 DataFrame
    record = pd.read_sql_table(record_table_name, engine_record)
    center = pd.read_sql_table(center_table_name, engine_center)

    # 整理新数据
    info_data = pd.DataFrame(new_dataframe[['检测日期', '姓名', '工号']])
    clustering_data = pd.DataFrame(new_dataframe.iloc[:, 3:])

    # 计算所有点到每个中心的距离
    distances_fin = []
    # 遍历clustering_data中的每个点
    for i in range(len(clustering_data)):
        # 获取当前点的数据
        point = clustering_data.iloc[i]
        # 创建一个空的列表来保存当前点到center中每个点的距离
        distances = []
        # 遍历center中的每个点
        for j in range(len(center)):
            # 获取当前中心点的数据
            center_point = center.iloc[j]
            # 计算当前点到当前中心点的欧氏距离
            # distance = np.sqrt(np.sum((point - center_point) ** 2))
            distance = 0
            for num in range(len(point)):
                distance_mid = math.pow(point.iloc[num] - center_point.iloc[num], 2)
                distance = distance_mid + distance
            distance_fin = math.sqrt(distance)
            # 将距离添加到列表中
            distances.append(distance_fin)

        # 将列表添加到DataFrame中
        distances_fin.append(distances)
        distances_fin_df = pd.DataFrame(distances_fin)

    center_table_name_save = '聚类中心'
    # 找到每一行的最小值的索引
    center_assignment = pd.DataFrame(distances_fin_df.idxmin(axis=1))
    center_assignment.columns = [center_table_name_save]
    yesterday_record = pd.concat([info_data, center_assignment], axis=1)
    check_date = datetime.now() - timedelta(days=1)  # 一天前
    check_date = str(check_date)
    # check_date = '2024-06-09'
    past_record = record[record['检测日期'] < check_date]  # 后期要加上

    """
    # 计算检测日期及数据
    past_record = [['2024-05-01', '徐如意', 'W516', '1'], ['2024-05-01', '郭长红', 'W3633', '0'], ['2024-05-01', '罗永刚', 'W583', '2'],
                    ['2024-05-02', '徐如意', 'W516', '1'], ['2024-05-02', '郭长红', 'W3633', '1'], ['2024-05-02', '罗永刚', 'W583', '2'],
                    ['2024-05-03', '徐如意', 'W516', '2'], ['2024-05-03', '郭长红', 'W3633', '0']]
    columns_names = ['检测日期', '姓名', '工号', '聚类中心']
    past_record = pd.DataFrame(past_record, columns=columns_names)
    # 测试！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
    """

    results = []
    results_nan_name = []
    results_nan_id = []
    for idx, row in yesterday_record.iterrows():
        name = row['姓名']
        id_number = row['工号']
        # 查找除最近一次外的最近三次记录
        result_one_person = past_record[(past_record['姓名'] == name) & (past_record['工号'] == id_number)]
        # 判断是否有三次记录
        if len(result_one_person) >= 3:
            result = []
            result_one_person_tail = result_one_person.tail(3)
            result_one_person_tail = result_one_person_tail.reset_index(drop=True)
            result.append(result_one_person_tail.loc[0, '姓名'])
            for i in range(len(result_one_person_tail)):
                result.append(result_one_person_tail.loc[i, '聚类中心'])
            results.append(result)
        else:
            result = []
            result_one_person = result_one_person.reset_index(drop=True)
            result.append(name)
            for i in range(len(result_one_person)):
                result.append(result_one_person.loc[i, '聚类中心'])
            while len(result) < 4:
                result.append(row['聚类中心'])
            results.append(result)  # 若要删除员工，则注释掉本行
            # 如果不足三条记录，记录姓名和工号
            results_nan_name.append(name)
            results_nan_id.append(id_number)
            # 是否做删除操作
            # useful_record = useful_record[(useful_record['姓名'] != name) & useful_record(useful_record['工号'] != id_number)]
            # useful_record.reset_index(drop=True)
            print(name + id_number + '记录不足三次')

    false_data = pd.concat(
        [pd.DataFrame(results_nan_name, columns=['姓名']), pd.DataFrame(results_nan_id, columns=['工号'])], axis=1)
    false_data = false_data.reset_index(drop=True)
    last_few_record = pd.DataFrame(results)

    # 是否预警
    warning_list = []
    # 遍历 yesterday_record 的每一行
    for idx, row in yesterday_record.iterrows():
        # 获取当前行的值
        value = row[yesterday_record.columns[-1]]
        # value_str = str(value)  # 将value转换为字符串,因为last_few_record中的值是字符串
        # 检查这个值是否存在于 useful_record 的对应行中
        is_in = value in np.ravel(last_few_record.iloc[idx].values)
        # 将结果添加到列表中
        warning_list.append(is_in)

    is_in_df = pd.DataFrame(warning_list, columns=['是否存在'])

    # 定义一个函数，如果值为True，则返回"正常"，否则返回"预警"
    def map_values(val):
        if val:
            return "正常"
        else:
            return "预警"

    # 使用map()函数将函数应用到每个元素
    final_data = is_in_df['是否存在'].map(map_values)
    final_data = pd.DataFrame(final_data)
    final_data.columns = ['是否预警']

    # 输出记录
    warning_data = pd.concat([yesterday_record, final_data], axis=1)
    warning_data = warning_data.reset_index(drop=True)

    # 保存数据
    # 创建数据库连接
    # engine_record = create_engine('mysql+mysqlconnector://root:bjtu%408401a@8.135.100.109:3306/jinqiao_meikuang')
    engine_record = create_engine('mysql+mysqlconnector://root:jqmk%402023@localhost:3306/exam_system')
    # 将DataFrame的内容插入到数据库表中
    yesterday_record.to_sql(record_table_name, con=engine_record, if_exists='append', index=False)

    print('kmeans完成')

    return warning_data


"""第二版"""
# def warning(new_dataframe):
#     # 创建数据库连接
#     engine_record = create_engine('mysql+mysqlconnector://root:bjtu%408401a@8.135.100.109:3306/jinqiao_meikuang')
#
#     # 创建一个 MetaData 实例
#     metadata_record = MetaData()
#     # 将其与引擎关联
#     metadata_record.reflect(bind=engine_record)
#     # 选择记录表
#     record_table_name = 'Kmeans_Record'
#
#     # 读取表格数据并转换为 DataFrame
#     record = pd.read_sql_table(record_table_name, engine_record)
#     # 计算昨天的日期
#     yesterday = datetime.now() - timedelta(days=1)  # 一天前
#     yesterday_record = record[record['日期'] == yesterday]
#     past_record = record[record['日期'] < yesterday]
#     useful_record = yesterday_record
#
#     results = []
#     results_nan_name = []
#     results_nan_id = []
#     for idx, row in yesterday_record.iterrows():
#         name = row['姓名']
#         id_number = row['工号']
#         # 查找除最近一次外的最近三次记录
#         result = past_record[(past_record['姓名'] == name) & (past_record['工号'] == id_number)]
#         # 判断是否有三次记录
#         if len(result) >= 3:
#             result = result.tail(3)
#             results.append(result)
#         else:
#             while len(result) < 3:
#                 result.append(row['聚类中心'])
#             results.append(result)  # 若要删除员工，则注释掉本行
#             # 如果不足三条记录，记录姓名和工号
#             results_nan_name.append(name)
#             results_nan_id.append(id_number)
#             # 是否做删除操作
#             # useful_record = useful_record[(useful_record['姓名'] != name) & useful_record(useful_record['工号'] != id_number)]
#             # useful_record.reset_index(drop=True)
#             print(name + id_number + '记录不足三次')
#
#     false_data = pd.concat([pd.DataFrame(results_nan_name, columns=['姓名']), pd.DataFrame(results_nan_id, columns=['工号'])], axis=1)
#     false_data = false_data.reset_index(drop=True)
#     last_few_record = pd.concat(results)
#
#     # 是否预警
#     warning_list = []
#     # 遍历 center_assignment 的每一行
#     for idx, row in useful_record.iterrows():
#         # 获取当前行的值
#         value = row[useful_record.columns[-1]]
#         # 检查这个值是否存在于 useful_record 的对应行中
#         # 这里假设 last_few_record 的对应行是 index 相同的行
#         is_in = value in np.ravel(last_few_record.iloc[idx].values)
#         # 将结果添加到列表中
#         warning_list.append(is_in)
#
#     is_in_df = pd.DataFrame(warning_list, columns=['是否存在'])
#
#     # 定义一个函数，如果值为True，则返回"正常"，否则返回"预警"
#     def map_values(val):
#         if val:
#             return "正常"
#         else:
#             return "预警"
#
#     # 使用map()函数将函数应用到每个元素
#     final_data = is_in_df.map(map_values)
#     final_data.columns = ['是否预警']
#
#     # 输出记录
#     warning_data = pd.concat([useful_record, final_data], axis=1)
#     warning_data = warning_data.reset_index(drop=True)
#
#     return warning_data

"""第一版"""
# def warning(new_dataframe):
# # 创建数据库连接
# engine_center = create_engine('mysql+mysqlconnector://remote:0266@10.61.70.112:3306/Center')
# engine_record = create_engine('mysql+mysqlconnector://remote:0266@10.61.70.112:3306/Record')
#
# # engine_center = create_engine('mysql+mysqlconnector://root:0266@localhost:3306/Center')
# # engine_record = create_engine('mysql+mysqlconnector://root:0266@localhost:3306/Record')
#
# # 创建一个 MetaData 实例
# metadata_center = MetaData()
# metadata_record = MetaData()
# # 将其与引擎关联
# metadata_center.reflect(bind=engine_center)
# metadata_record.reflect(bind=engine_record)
# # 获取所有表名
# center_table_names = list(metadata_center.tables.keys())
# record_table_names = list(metadata_record.tables.keys())
# # 选择最后一个表
# center_last_table = center_table_names[-1]
# record_last_few_table = record_table_names[-3:]
#
# # 读取表格数据并转换为 DataFrame
# center = pd.read_sql_table(center_last_table, engine_center)
#
# name_data = pd.DataFrame(new_dataframe.iloc[:, 0])
# name_data.columns = ['姓名']
# clustering_data = pd.DataFrame(new_dataframe.iloc[:, 1:])
# name_data_series = name_data.iloc[:, 0].squeeze()
#
# person_record_all = pd.DataFrame()
# for worker_name in name_data_series:
#     person_record = pd.DataFrame()
#     for table in record_last_few_table:
#         table_data = pd.read_sql_table(table, engine_record)
#         second_column_name = table_data.columns[1]
#         table_name_data = table_data[table_data['姓名'] == worker_name][second_column_name]
#         person_record = pd.concat([person_record, table_name_data], axis=1)
#     person_record_all = pd.concat([person_record_all, person_record])
# name_data = name_data.reset_index(drop=True)
# person_record_all = person_record_all.reset_index(drop=True)
# person_name_record_all = pd.concat([name_data, person_record_all], axis=1)
#
# # 计算所有点到每个中心的距离
# distances_fin = []
#
# # 遍历clustering_data中的每个点
# for i in range(len(clustering_data)):
#     # 获取当前点的数据
#     point = clustering_data.iloc[i]
#
#     # 创建一个空的列表来保存当前点到center中每个点的距离
#     distances = []
#
#     # 遍历center中的每个点
#     for j in range(len(center)):
#         # 获取当前中心点的数据
#         center_point = center.iloc[j]
#         # 计算当前点到当前中心点的欧氏距离
#         # distance = np.sqrt(np.sum((point - center_point) ** 2))
#         distance = 0
#         for num in range(len(point)):
#             distance_mid = math.pow(point.iloc[num] - center_point.iloc[num], 2)
#             distance = distance_mid + distance
#         distance_fin = math.sqrt(distance)
#         # 将距离添加到列表中
#         distances.append(distance_fin)
#
#     # 将列表添加到DataFrame中
#     distances_fin.append(distances)
#     distances_fin_df = pd.DataFrame(distances_fin)
#
# # 获取当天的日期
# today_date = date.today()
# # 获取当天的日期并转换为字符串
# today_str = today_date.strftime('%Y_%m_%d')
# # 创建表名
# center_table_name_save = '中心_' + today_str + '_预警'
#
# # 找到每一行的最小值的索引
# center_assignment = pd.DataFrame(distances_fin_df.idxmin(axis=1))
# center_assignment.columns = [center_table_name_save]
#
# # 自定义聚类中心，用于预警实验
# center_assignment = pd.DataFrame(np.ones(center_assignment.shape[0]))  # 实验
# center_assignment.columns = [center_table_name_save]  # 实验
#
# # 是否预警
# # 初始化一个空的列表来存储结果
# is_in_list = []
# # 遍历 center_assignment 的每一行
# for index, row in center_assignment.iterrows():
#     # 获取当前行的值
#     value = row[center_assignment.columns[0]]
#     # 检查这个值是否存在于 person_name_record_all 的对应行中
#     # 这里假设 person_name_record_all 的对应行是 index 相同的行
#     is_in = value in np.ravel(person_name_record_all.iloc[index].values)
#     # 将结果添加到列表中
#     is_in_list.append(is_in)
#
# # 将结果列表转换为数据帧
# is_in_df = pd.DataFrame(is_in_list, columns=['是否存在'])
#
# # 定义一个函数，如果值为True，则返回"正常"，否则返回"预警"
# def map_values(val):
#     if val:
#         return "正常"
#     else:
#         return "预警"
#
# # 使用applymap()函数将函数应用到每个元素
# final_data = is_in_df.map(map_values)
# final_data.columns = ['是否预警']
#
# # 输出记录
# name_and_position_df = pd.concat([name_data, center_assignment], axis=1)
# warning_data = pd.concat([name_and_position_df, final_data], axis=1)
# warning_data = warning_data.reset_index(drop=True)
#
# return warning_data


"""
# 测试数据
json_data = [
    {
        "employee_info": {
            "date": "2023-11-03",
            "name": "王伟B"
        },
        "behavior_data": {
            "安全帽佩戴情况_7": 0,
            "矿灯佩戴情况_7": 1,
            "毛巾佩戴情况_7": 0,
            "胶鞋佩戴情况_7": 1,
            "自救器佩戴情况_7": 0,
            "安全帽佩戴情况_6": 0,
            "矿灯佩戴情况_6": 1,
            "毛巾佩戴情况_6": 0,
            "胶鞋佩戴情况_6": 1,
            "自救器佩戴情况_6": 0,
            "安全帽佩戴情况_5": 0,
            "矿灯佩戴情况_5": 1,
            "毛巾佩戴情况_5": 0,
            "胶鞋佩戴情况_5": 1,
            "自救器佩戴情况_5": 0,
            "安全帽佩戴情况_4": 0,
            "矿灯佩戴情况_4": 1,
            "毛巾佩戴情况_4": 0,
            "胶鞋佩戴情况_4": 1,
            "自救器佩戴情况_4": 0,
            "安全帽佩戴情况_3": 0,
            "矿灯佩戴情况_3": 1,
            "毛巾佩戴情况_3": 0,
            "胶鞋佩戴情况_3": 1,
            "自救器佩戴情况_3": 0,
            "安全帽佩戴情况_2": 0,
            "矿灯佩戴情况_2": 1,
            "毛巾佩戴情况_2": 0,
            "胶鞋佩戴情况_2": 1,
            "自救器佩戴情况_2": 0,
            "安全帽佩戴情况_1": 0,
            "矿灯佩戴情况_1": 1,
            "毛巾佩戴情况_1": 0,
            "胶鞋佩戴情况_1": 1,
            "自救器佩戴情况_1": 0
        }
    },
    {
        "employee_info": {
            "date": "2023-11-03",
            "name": "于银房"
        },
        "behavior_data": {
            "安全帽佩戴情况_7": 0,
            "矿灯佩戴情况_7": 1,
            "毛巾佩戴情况_7": 0,
            "胶鞋佩戴情况_7": 0,
            "自救器佩戴情况_7": 0,
            "安全帽佩戴情况_6": 0,
            "矿灯佩戴情况_6": 1,
            "毛巾佩戴情况_6": 0,
            "胶鞋佩戴情况_6": 1,
            "自救器佩戴情况_6": 0,
            "安全帽佩戴情况_5": 0,
            "矿灯佩戴情况_5": 0,
            "毛巾佩戴情况_5": 0,
            "胶鞋佩戴情况_5": 1,
            "自救器佩戴情况_5": 1,
            "安全帽佩戴情况_4": 0,
            "矿灯佩戴情况_4": 1,
            "毛巾佩戴情况_4": 0,
            "胶鞋佩戴情况_4": 1,
            "自救器佩戴情况_4": 0,
            "安全帽佩戴情况_3": 0,
            "矿灯佩戴情况_3": 1,
            "毛巾佩戴情况_3": 1,
            "胶鞋佩戴情况_3": 1,
            "自救器佩戴情况_3": 0,
            "安全帽佩戴情况_2": 0,
            "矿灯佩戴情况_2": 1,
            "毛巾佩戴情况_2": 0,
            "胶鞋佩戴情况_2": 0,
            "自救器佩戴情况_2": 0,
            "安全帽佩戴情况_1": 0,
            "矿灯佩戴情况_1": 0,
            "毛巾佩戴情况_1": 0,
            "胶鞋佩戴情况_1": 1,
            "自救器佩戴情况_1": 0
        }
    },
    {
        "employee_info": {
            "date": "2023-11-03",
            "name": "王震C"
        },
        "behavior_data": {
            "安全帽佩戴情况_7": 0,
            "矿灯佩戴情况_7": 1,
            "毛巾佩戴情况_7": 0,
            "胶鞋佩戴情况_7": 0,
            "自救器佩戴情况_7": 1,
            "安全帽佩戴情况_6": 0,
            "矿灯佩戴情况_6": 1,
            "毛巾佩戴情况_6": 1,
            "胶鞋佩戴情况_6": 0,
            "自救器佩戴情况_6": 0,
            "安全帽佩戴情况_5": 0,
            "矿灯佩戴情况_5": 0,
            "毛巾佩戴情况_5": 0,
            "胶鞋佩戴情况_5": 1,
            "自救器佩戴情况_5": 1,
            "安全帽佩戴情况_4": 1,
            "矿灯佩戴情况_4": 1,
            "毛巾佩戴情况_4": 0,
            "胶鞋佩戴情况_4": 1,
            "自救器佩戴情况_4": 0,
            "安全帽佩戴情况_3": 0,
            "矿灯佩戴情况_3": 1,
            "毛巾佩戴情况_3": 0,
            "胶鞋佩戴情况_3": 1,
            "自救器佩戴情况_3": 0,
            "安全帽佩戴情况_2": 1,
            "矿灯佩戴情况_2": 1,
            "毛巾佩戴情况_2": 1,
            "胶鞋佩戴情况_2": 0,
            "自救器佩戴情况_2": 0,
            "安全帽佩戴情况_1": 0,
            "矿灯佩戴情况_1": 0,
            "毛巾佩戴情况_1": 1,
            "胶鞋佩戴情况_1": 1,
            "自救器佩戴情况_1": 0
        }
    }
]

# 创建一个空的DataFrame来保存结果
new_data = pd.DataFrame()

# 遍历JSON对象中的每个元素
for item in json_data:
    # 获取'employee_info'和'behavior_data'
    employee_info = item['employee_info']
    behavior_data = item['behavior_data']

    # 将'employee_info'和'behavior_data'合并为一个字典
    data = {**employee_info, **behavior_data}

    # 将字典转换为DataFrame
    df_item = pd.DataFrame(data, index=[0])

    # 将DataFrame添加到结果中
    new_data = pd.concat([new_data, df_item], ignore_index=True)

warning(new_data)
"""

"""
# 测试数据
new_data = [
    {
        "employee_info": {
            "date": "2024-05-03",
            "name": "王伟B"
        }
    },
    {
        "employee_info": {
            "date": "2024-05-03",
            "name": "于银房"
        }
    },
    {
        "employee_info": {
            "date": "2024-05-03",
            "name": "王震C"
        }
    }
]

warning(new_data)
"""
