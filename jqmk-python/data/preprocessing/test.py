import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sqlalchemy import create_engine, MetaData
from datetime import date
import os
def get_today_data():
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')
    time = str(yesterday)
    size = 7
    # date = datetime.strptime(date, "%Y-%m-%d")
    # date = pd.to_datetime(date)
    # 创建数据库连接
    engine_center = create_engine('mysql+mysqlconnector://root:root@localhost:3306/jinqiao_meikuang')
    # engine_center = create_engine('mysql+mysqlconnector://root:bjtu%408401a@8.135.100.109:3306/jinqiao_meikuang')
    # 创建一个 MetaData 实例
    metadata_center = MetaData()
    metadata_record = MetaData()
    # 将其与引擎关联
    metadata_center.reflect(bind=engine_center)
    # 获取所有表名
    center_table_names = list(metadata_center.tables.keys())
    # 选择最后一个表
    center_last_table = 'employee_clock_history'
    center = pd.read_sql_table(center_last_table, engine_center)

    # current_directory = os.path.dirname(__file__)
    # project_root = os.path.abspath(os.path.join(current_directory, os.pardir))
    # model_path = os.path.join(project_root, 'preprocessing', 'data711_2024.xlsx')
    # center = pd.read_excel(model_path)
    center = center.drop(columns=['id', 'alcohol', 'personTemp', 'deptCode', 'deptName', 'captureImg', 'cardDetectTime',
                                  'wireDeviceDetectTime', 'detectRes', 'alcoholDetectTime', 'doorOpenTime'])
    columns_name1 = ['姓名', '工号', '检测日期', '安全帽佩戴情况', '矿灯佩戴情况', '毛巾佩戴情况', '胶鞋佩戴情况', '自救器佩戴情况']
    center.columns = columns_name1
    center['检测日期'] = pd.to_datetime(center['检测日期'])
    center['检测日期'] = center['检测日期'].dt.date
    center['检测日期'] = center['检测日期'].astype(str)
    # center['姓名'] = center['姓名'] + '+' + center['工号']
    center = center.replace(1, 1)
    center = center.replace(0, 0)
    center = center.replace(2, 0)
    center = center.replace(-1, 0)

    all_behavior_data = center
    all_behavior_data = all_behavior_data.dropna(subset=["姓名", "检测日期"])
    all_behavior_data = all_behavior_data[['姓名', '工号','检测日期', '安全帽佩戴情况', '矿灯佩戴情况', '毛巾佩戴情况', '胶鞋佩戴情况', '自救器佩戴情况']]
    center2 = all_behavior_data[all_behavior_data['检测日期'] == time]
    # center2['姓名'] = center2['姓名'] + '' + center2['工号']
    employee_name = center2['姓名'].values.tolist()
    employee_name = set(employee_name)
    employee_name = list(employee_name)
    name = employee_name
    # date = ['2024-5-03', '2024-5-03', '2024-5-03']
    # date2 = []
    # for i in date:
    #     i = datetime.strptime(i, "%Y-%m-%d")
    #     date2.append(i)
    all_behavior_data = center

    all_behavior_data = all_behavior_data.dropna(subset=["姓名", "检测日期"])
    # all_behavior_data["检测日期"]=all_behavior_data.apply(lambda x: datetime.strptime(x["检测日期"], '%Y-%m-%d %H:%M:%S'),axis=1)
    all_behavior_data["unique_key_user"] = all_behavior_data.apply(lambda row: str(row["检测日期"])[:10] + row["工号"],
                                                                   axis=1)
    all_behavior_data = all_behavior_data.drop_duplicates(subset='unique_key_user', keep='last')
    all_behavior_data = all_behavior_data[
        ['姓名', '检测日期', '安全帽佩戴情况', '矿灯佩戴情况', '毛巾佩戴情况', '胶鞋佩戴情况', '自救器佩戴情况', 'unique_key_user']]
    n = pd.DataFrame()
    employee_name2 = []#缺少考勤的人
    h = 0
    for i in range(len(employee_name)):
        i = i - h
        if i == len(employee_name):
            # i = i -1
            # m = all_behavior_data[all_behavior_data['姓名'] == employee_name[i]]
            # m = m.sort_values('检测日期', ascending=False)
            # # target_date = pd.to_datetime(time)
            # m = m[m['检测日期'] < time].head(size)
            # if len(m) >= 7:
            #     m = m.drop('姓名', axis=1)
            #     m = m.drop('检测日期', axis=1)
            #     m = m.drop('unique_key_user', axis=1)
            #     e = pd.DataFrame()
            #     c = pd.DataFrame()
            #     # print(m)
            #     for j in range(size):
            #         e = m.iloc[[j], :]
            #         e = e.reset_index(drop=True)
            #         # e.transpose()
            #         # print(e)
            #         c = pd.concat([c, e], axis=1, ignore_index=True)
            #     n = pd.concat([n, c], ignore_index=True)
            #     print(n)
            # else:
            #     employee_name = list(filter(lambda item: item != employee_name[i], employee_name))
            #     h = h + 1
            break
        else:
            m = all_behavior_data[all_behavior_data['姓名'] == employee_name[i]]
            m = m.sort_values('检测日期', ascending=False)
            # target_date = pd.to_datetime(time)
            m = m[m['检测日期'] < time].head(size)
            if len(m) >= 7:
                m = m.drop('姓名', axis=1)
                m = m.drop('检测日期', axis=1)
                m = m.drop('unique_key_user', axis=1)
                e = pd.DataFrame()
                c = pd.DataFrame()
                # print(m)
                for j in range(size):
                    e = m.iloc[[j], :]
                    e = e.reset_index(drop=True)
                    # e.transpose()
                    # print(e)
                    c = pd.concat([c, e], axis=1, ignore_index=True)
                n = pd.concat([n, c], ignore_index=True)
                # print(n)
            else:
                employee_name2.append(employee_name[i])
                employee_name = list(filter(lambda item: item != employee_name[i], employee_name))
                h = h + 1
    #有效数据
    employee_name1 = []
    employee_ids1 = []
    employee_time1 = []
    #无效数据
    # employee_name3 = []
    # employee_ids3 = []
    employee_time2 = []
    for i in range(len(employee_name)):
        # original_string = employee_name[i]
        # # 使用 split 方法基于 '+' 分割字符串
        # parts = original_string.split('+')
        # employee_name1.append(parts[0])
        # employee_ids1.append(parts[1])
        employee_time1.append(time)
    for i in range(len(employee_name2)):
        # original_string = employee_name2[i]
        # # 使用 split 方法基于 '+' 分割字符串
        # parts2 = original_string.split('+')
        # employee_name3.append(parts2[0])
        # employee_ids3.append(parts2[1])
        employee_time2.append(time)

    # n.insert(loc=0, column='工号', value=employee_ids1)
    n.insert(loc=0, column='姓名', value= employee_name)
    n.insert(loc=0, column='检测日期', value=employee_time1)
    columns_names = ['检测日期','姓名','安全帽佩戴情况_-7', '矿灯佩戴情况_7', '毛巾佩戴情况_7', '胶鞋佩戴情况_7', '自救器佩戴情况_7',
                     '安全帽佩戴情况_-6', '矿灯佩戴情况_6', '毛巾佩戴情况_6', '胶鞋佩戴情况_6', '自救器佩戴情况_6',
                     '安全帽佩戴情况_-5', '矿灯佩戴情况_5', '毛巾佩戴情况_5', '胶鞋佩戴情况_5', '自救器佩戴情况_5',
                     '安全帽佩戴情况_-4', '矿灯佩戴情况_4', '毛巾佩戴情况_4', '胶鞋佩戴情况_4', '自救器佩戴情况_4',
                     '安全帽佩戴情况_-3', '矿灯佩戴情况_3', '毛巾佩戴情况_3', '胶鞋佩戴情况_3', '自救器佩戴情况_3',
                     '安全帽佩戴情况_-2', '矿灯佩戴情况_2', '毛巾佩戴情况_2', '胶鞋佩戴情况_2', '自救器佩戴情况_2',
                     '安全帽佩戴情况_-1', '矿灯佩戴情况_1', '毛巾佩戴情况_1', '胶鞋佩戴情况_1', '自救器佩戴情况_1']
    n.columns = columns_names

    n_not = pd.DataFrame()
    n_not.insert(loc=0, column='姓名', value=employee_name2)
    n_not.insert(loc=0, column='检测日期', value=employee_time2)
    columns_name2 = ['检测日期', '姓名']
    n_not.columns = columns_name2
    return n,n_not

if __name__=="__main__":
    n,n_not =get_today_data()
    print(n.to_string())
    print(n_not.to_string())