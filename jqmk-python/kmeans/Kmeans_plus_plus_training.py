from sklearn.cluster import KMeans
from sklearn import metrics
import pandas as pd
from pypinyin import lazy_pinyin
import os
from userPortrait.settings import BASE_DIR
import math
from datetime import date
from sqlalchemy import create_engine
from kmeans.Checking import checking
from tqdm import tqdm


def kmeans_plus_plus_training():
    # 判断当天是否运行过脚本
    # if checking():
    #     # 如果今天脚本没运行过，则继续执行代码
    #     pass
    # else:
    #     # 直接返回
    #     return False

    # # 获取当天的日期
    # today_date = date.today()
    # # 获取当天的日期并转换为字符串
    # today_str = today_date.strftime('%Y_%m_%d')
    # # 创建表名
    # center_table_name = 'center_' + today_str
    # record_table_name = 'record_' + today_str + '_训练'

    # 读取数据
    data_file_path = os.path.join(BASE_DIR, 'data/final_result_encoder_2023-11-01_2024-05-31.csv')
    ori_data = pd.read_csv(data_file_path, encoding='gbk')
    data = ori_data.iloc[:, 0: -2]
    name_data = pd.DataFrame(ori_data.iloc[:, -2])

    # 使用KMeans++进行初始化
    kmeans_plus_plus = KMeans(n_clusters=5, init='k-means++', max_iter=300, n_init=10, random_state=0)

    # 使用KMeans进行迭代
    predict_position = kmeans_plus_plus.fit_predict(data)
    center = pd.DataFrame(kmeans_plus_plus.cluster_centers_)
    center.columns = data.columns
    center.index = ['中心1', '中心2', '中心3', '中心4', '中心5']

    # print(metrics.calinski_harabasz_score(data, predict_position))
    # print(predict_position)
    # print(center)

    # # 使用正则表达式提取姓名和可能存在的字母
    # names_all = (name_data.iloc[:, 0].str.extract(r'(\d{4}-\d{2}-\d{2}([\u4e00-\u9fff]+[A-Za-z]?))', expand=True)).iloc[:, 1]
    # names_all_df = pd.DataFrame(names_all)
    # names_all_df.columns = ['姓名']
    # names_all_df = pd.concat([names_all_df, data], axis=1)
    # names_all_df = names_all_df.drop_duplicates(subset='姓名', keep='last')
    #
    # # 将中文名字转换为拼音
    # names_all_df['pinyin'] = names_all_df.iloc[:, 0].apply(lambda x: ''.join(lazy_pinyin(x)))
    # # 按照拼音顺序进行排序
    # names_all_df = names_all_df.sort_values(by='pinyin')
    # # 删除拼音列
    # del names_all_df['pinyin']
    #
    # clustering_data = names_all_df.iloc[:, 1:]
    #
    # 获取最近聚类结果
    # 计算所有点到每个中心的距离

    """
    distances_fin = []
    clustering_data = data  # 测试用
    names_all_df = name_data  # 测试用

    # 遍历clustering_data中的每个点
    for i in tqdm(range(len(names_all_df)), desc="Processing Points"):
        # 获取当前点的数据
        point = clustering_data.iloc[i]

        # 创建一个空的列表来保存当前点到center中每个点的距离
        distances = []

        # 遍历center中的每个点
        for j in range(len(center)):
            # 获取当前中心点的数据
            center_point = center.iloc[j]
            # 计算当前点到当前中心点的欧氏距离
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

    # 找到每一行的最小值的索引
    center_assignment = pd.DataFrame(distances_fin_df.idxmin(axis=1))
    # center_table_name_save = '中心_' + today_str + '_训练'
    center_assignment.columns = ['中心']
    # name = pd.DataFrame(names_all_df.iloc[:, 0])
    # name = name.reset_index(drop=True)
    # record_data_df = pd.concat([name, center_assignment], axis=1)

    # 保存数据
    # center_data_path = os.path.join(BASE_DIR, 'kmeans/center.xlsx')
    # center.to_excel(center_data_path, index=False)
    # record_data_path = os.path.join(BASE_DIR, 'kmeans/record.xlsx')
    # record_data_df.to_excel(record_data_path, index=False)

    # 统计各个中心人数
    center_numeber = [0, 0, 0, 0, 0]
    for idx, row in center_assignment.iterrows():
        if row['中心'] == 0:
            center_numeber[0] = center_numeber[0] + 1
        elif row['中心'] == 1:
            center_numeber[1] = center_numeber[1] + 1
        elif row['中心'] == 2:
            center_numeber[2] = center_numeber[2] + 1
        elif row['中心'] == 3:
            center_numeber[3] = center_numeber[3] + 1
        else:
            center_numeber[4] = center_numeber[4] + 1
    print(center_numeber)
    """


    # 创建数据库连接
    engine_center = create_engine('mysql+mysqlconnector://root:jqmk%402023@localhost:3306/exam_system')
    # engine_center = create_engine('mysql+mysqlconnector://root:bjtu%408401a@8.135.100.109:3306/jinqiao_meikuang')
    # 将DataFrame的内容插入到数据库表中
    center.to_sql('kmeans_center', con=engine_center, if_exists='replace', index=False)

    # # engine_record = create_engine('mysql+mysqlconnector://root:0266@localhost:3306/Record')
    # engine_record = create_engine('mysql+mysqlconnector://root:bjtu%408401a@8.135.100.109:3306/jinqiao_meikuang')
    # # 将DataFrame的内容插入到数据库表中
    # record_data_df.to_sql('kmeans_record', con=engine_record, if_exists='append', index=False)

    return True


# kmeans_plus_plus_training()