import pandas as pd
import math
import os
from userPortrait.settings import BASE_DIR
from sqlalchemy import create_engine, MetaData
from datetime import date
from data.preprocessing.today_data0710 import get_today_data

def clustering():
    # 读取数据
    # center_data_path = os.path.join(BASE_DIR, 'kmeans/center.xlsx')
    # center = pd.read_excel(center_data_path)
    # record_data_path = os.path.join(BASE_DIR, 'kmeans/record.xlsx')
    # record = pd.read_excel(record_data_path)

    # engine_center = create_engine('mysql+mysqlconnector://root:bjtu%408401a@8.135.100.109:3306/jinqiao_meikuang')
    engine_center = create_engine('mysql+mysqlconnector://root:jqmk%402023@localhost:3306/exam_system')
    # engine_record = create_engine('mysql+mysqlconnector://root:bjtu%408401a@8.135.100.109:3306/jinqiao_meikuang')

    # 创建数据库连接
    # engine_center = create_engine('mysql+mysqlconnector://root:0266@localhost:3306/Center')
    # engine_record = create_engine('mysql+mysqlconnector://root:0266@localhost:3306/Record')

    # 创建一个 MetaData 实例
    metadata_center = MetaData()
    # metadata_record = MetaData()
    # 将其与引擎关联
    metadata_center.reflect(bind=engine_center)
    # metadata_record.reflect(bind=engine_record)
    # 获取所有表名
    # center_table_names = list(metadata_center.tables.keys())
    # record_table_names = list(metadata_record.tables.keys())
    # 选择最后一个表
    # center_last_table = center_table_names[-1]
    # record_last_table = record_table_names[-1]
    center_table_name = 'kmeans_center'
    record_table_name = 'kmeans_record'

    # 读取表格数据并转换为 DataFrame
    center = pd.read_sql_table(center_table_name, engine_center)
    # record = pd.read_sql_table(record_table_name, engine_record)

    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # file_path = os.path.join(current_dir, 'ClusteringData513.xlsx')  # 根据实际目录结构调整
    # ori_data = pd.read_excel(file_path, engine='openpyxl')
    ori_data, meager_data = get_today_data()
    info_data = pd.DataFrame(ori_data.iloc[:, 0:3])
    info_data.columns = ['检测日期', '姓名', '工号']
    clustering_data = pd.DataFrame(ori_data.iloc[:, 3:-1])


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


    # 获取当天的日期
    # today_date = date.today()
    # 获取当天的日期并转换为字符串
    # today_str = today_date.strftime('%Y_%m_%d')
    # 创建表名
    # record_table_name = 'record_' + today_str
    # record_table_name_save = '中心_' + today_str
    # record_table_name = 'record_2024_06_23'
    # record_table_name_save = '中心_2024_06_23'

    record_table_name_save = '聚类中心'
    # 找到每一行的最小值的索引
    center_assignment = pd.DataFrame(distances_fin_df.idxmin(axis=1))
    center_assignment.columns = [record_table_name_save]
    final_assignment = pd.concat([info_data, center_assignment], axis=1)

    # 保存记录
    # name_and_position_df = pd.concat([info_data, center_assignment], axis=1)
    # name_all = record.iloc[:, 0]
    # merged_df = pd.merge(name_all, name_and_position_df, on='姓名', how='left')
    # merged_df[record_table_name_save] = merged_df[record_table_name_save].fillna(-1).astype(int)
    # record_data = pd.concat([record, merged_df[record_table_name_save]], axis=1)
    # record_data_drop = record_data.drop(record_data.columns[1], axis=1)
    # record_data_path = os.path.join(BASE_DIR, 'kmeans/record.xlsx')
    # record_data.to_excel(record_data_path, index=False)

    # 预警
    # mask = record_data.iloc[:, -1] != record_data.iloc[:, -2]
    # different_center = record_data.loc[mask, '姓名']
    # warn_name = different_center.reset_index(drop=True).to_frame()
    # warning_data_path = os.path.join(BASE_DIR, 'kmeans/warning.xlsx')
    # warn_name.to_excel(warning_data_path, index=False)

    # 保存数据
    # 创建数据库连接
    # engine_record = create_engine('mysql+mysqlconnector://root:bjtu%408401a@8.135.100.109:3306/jinqiao_meikuang')
    engine_record = create_engine('mysql+mysqlconnector://root:jqmk%402023@localhost:3306/exam_system')
    # 将DataFrame的内容插入到数据库表中
    final_assignment.to_sql(record_table_name, con=engine_record, if_exists='append', index=False)

# clustering()