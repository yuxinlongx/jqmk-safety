from kmeans.Warning import warning
import pandas as pd
import os
from logistic.logistic_model import LogisticModel
from comprehensive.Rule import combine_warnings
from data.preprocessing.today_data0710 import get_today_data


def daily_prediction():
    print('综合预警开始')
    # 调用预处理函数
    behavior_data_df, meager_data = get_today_data()

    """
    # 实验数据
    columns_names = ['检测日期', '姓名', '工号']
    meager_data = [['2024-5-04', '刘金榜', '3673']]
    meager_data = pd.DataFrame(meager_data, columns=columns_names)
    behavior_data_df = [['2024-5-04', '徐如意', 'W516', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
                        ['2024-5-04', '郭长红', 'W3633', 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
                        ['2024-5-04', '罗永刚', 'W583', 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1]]
    columns_names = ['检测日期', '姓名', '工号', '安全帽佩戴情况_-7', '矿灯佩戴情况_7', '毛巾佩戴情况_7',
                     '胶鞋佩戴情况_7', '自救器佩戴情况_7',
                     '安全帽佩戴情况_-6', '矿灯佩戴情况_6', '毛巾佩戴情况_6', '胶鞋佩戴情况_6', '自救器佩戴情况_6',
                     '安全帽佩戴情况_-5', '矿灯佩戴情况_5', '毛巾佩戴情况_5', '胶鞋佩戴情况_5', '自救器佩戴情况_5',
                     '安全帽佩戴情况_-4', '矿灯佩戴情况_4', '毛巾佩戴情况_4', '胶鞋佩戴情况_4', '自救器佩戴情况_4',
                     '安全帽佩戴情况_-3', '矿灯佩戴情况_3', '毛巾佩戴情况_3', '胶鞋佩戴情况_3', '自救器佩戴情况_3',
                     '安全帽佩戴情况_-2', '矿灯佩戴情况_2', '毛巾佩戴情况_2', '胶鞋佩戴情况_2', '自救器佩戴情况_2',
                     '安全帽佩戴情况_-1', '矿灯佩戴情况_1', '毛巾佩戴情况_1', '胶鞋佩戴情况_1', '自救器佩戴情况_1']
    behavior_data_df = pd.DataFrame(behavior_data_df, columns=columns_names)  # 测试！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
    """

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
        if behavior_data_df.shape[1] == expected_columns + 3:  # 包含信息列
            names_without_nan_idx = [0]

    if len(names_without_nan_idx) == 0:
        return 'No valid data found.'

    # 使用索引过滤DataFrame
    p_behavior_data_df = behavior_data_df.loc[names_without_nan_idx]
    info_df = p_behavior_data_df[['检测日期', '姓名', '工号']]
    info_df = info_df.reset_index(drop=True)
    k_behavior_data_df = p_behavior_data_df
    l_behavior_data_df = k_behavior_data_df.drop(columns=['检测日期', '姓名', '工号'])

    # 运行logistic预警
    # 动态构建模型路径
    print('logistic开始')
    current_directory = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(current_directory, os.pardir))
    model_path = os.path.join(project_root, 'logistic', 'logistic_model.pkl')
    # 调试信息：打印模型路径
    # print(f"Model path: {model_path}")

    # 加载并使用逻辑回归模型进行预测
    model = LogisticModel()
    model.load_model(model_path)

    scores, predictions_array, normalized_scores, risk_levels = model.predict(l_behavior_data_df)

    # 根据风险等级设置预测结果
    risk_level = pd.DataFrame(risk_levels, columns=['风险等级'])
    print('logistic完成')

    # 运行KMeans++预警
    warning_data = warning(k_behavior_data_df)

    k_warning_bool = warning_data.loc[:, '是否预警']
    c_warning_data = pd.concat([info_df, risk_level, k_warning_bool], axis=1)
    c_warning_data.columns = ['检测日期', '姓名', '工号', '风险等级', '是否预警']
    c_warning_data_output = []

    # 进行综合预警
    for idx, row in c_warning_data.iterrows():
        c_warning_data_output.append(combine_warnings(row['风险等级'], row['是否预警']))
    c_warning_data_output_df = pd.DataFrame(c_warning_data_output)
    c_warning_data_output_df.columns = ['综合预警']
    final_warning_data = pd.concat([c_warning_data, c_warning_data_output_df], axis=1)
    output_data = final_warning_data.drop(columns=['风险等级', '是否预警'])

    print('综合预警完成')

    return output_data, meager_data

# daily_prediction()