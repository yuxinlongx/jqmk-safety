from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime, timedelta
from data.preprocessing.Get_all_names_penalty import get_all_names_penalty


def v_get_personal_penalty_data():
    # 连接到MySQL数据库
    """
    mysql+mysqlconnector:// - 数据库类型(MySQL)和使用的驱动(mysqlconnector)
    root - 数据库用户名
    jqmk%402023 - 数据库密码（实际密码为jqmk@2023，%40是@的URL编码）
    localhost - 数据库服务器地址（本地主机）
    3306 - MySQL默认端口号
    exam_system - 要连接的数据库名称
    """
    engine = create_engine('mysql+mysqlconnector://root:jqmk%402023@localhost:3306/exam_system') # 金桥库
    # engine = create_engine('mysql+mysqlconnector://root:0266@localhost:3306/jinqiao_meikuang') # 本地库

    # 编写SQL查询，获取查询周期数据。提取按时间降序排列后的第一行数据(即最新的数据)
    query = f"""
        SELECT * FROM threshold_table ORDER BY creat_time DESC LIMIT 1
        """
    # 读取数据到DataFrame
    threshold_value = pd.read_sql(query, engine)
    date_scale = threshold_value['cycle'].iloc[0]
    critical_value = threshold_value['temporary_value'].iloc[0]
    date_scale = int(date_scale)
    critical_value = int(critical_value)

    # 计算日期范围
    end = datetime.now() - timedelta(days=1)
    start = end - timedelta(days=date_scale)
    end_date = end.strftime('%Y-%m-%d')
    start_date = start.strftime('%Y-%m-%d')
    # print(start_date, end_date)

    # 测试
    # end_date = '2026-05-30'
    # start_date = '2026-05-21'

    # 编写SQL查询
    query = f"""
        SELECT violation_date, duty_person, violation_level
        FROM penalty_data
        WHERE violation_date BETWEEN '{start_date}' AND '{end_date}';
        """

    # 读取数据到DataFrame
    duty_person = pd.read_sql(query, engine)
    duty_person.columns = ['date', 'name', 'level']
    all_name = get_all_names_penalty()

    # 定义违章记分字典
    score_map = {
        '一般违章': 1,
        '动态违章': 3,
        '严重违章': 7
    }
    # 把每条记录的分数算出来，放到新列 'score' 中
    duty_person['score'] = duty_person['level'].map(score_map)
    # 使用 groupby() 再按 name 分组，对 score 求和，并重置索引
    duty_person_value = (duty_person.groupby('name')['score'].sum().reset_index(name='total_score'))

    # 合并 DataFrame
    result_df = all_name.merge(duty_person_value, on='name', how='left')
    # 将未赋值的 count 填充为 0
    result_df['value'] = result_df['total_score'].fillna(0)
    # 移除不需要的列
    result_df.drop(columns=['total_score'], inplace=True)


    # 生成重复的行
    date_list = [end_date] * len(result_df)
    # 创建 DataFrame
    checking_date = pd.DataFrame(date_list, columns=['date'])
    result_finally_df = pd.concat([checking_date, result_df], axis=1)

    return result_finally_df, critical_value, start_date, end_date, engine


if __name__ == "__main__":
    v_get_personal_penalty_data()
