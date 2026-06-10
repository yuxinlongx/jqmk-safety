from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime, timedelta
from data.preprocessing.Get_all_names import get_all_names


def get_personal_penalty_data():
    # 连接到MySQL数据库
    engine = create_engine('mysql+mysqlconnector://root:jqmk%402023@localhost:3306/exam_system')

    # 计算日期范围
    end = datetime.now() - timedelta(days=1)
    start = end - timedelta(days=6)
    end_date = end.strftime('%Y-%m-%d')
    start_date = start.strftime('%Y-%m-%d')
    # print(start_date, end_date)

    # 测试
    # end_date = '2025-03-17'
    # start_date = '2025-03-11'

    # 编写SQL查询
    query = f"""
    SELECT violation_date, duty_person
    FROM penalty_data
    WHERE violation_date BETWEEN '{start_date}' AND '{end_date}';
    """

    # 读取数据到DataFrame
    duty_person = pd.read_sql(query, engine)
    duty_person.columns = ['date', 'name']
    all_name = get_all_names()
    # 使用 groupby()
    duty_person_count = duty_person.groupby('name').size().reset_index(name='count')


    # 合并 DataFrame
    result_df = all_name.merge(duty_person_count, on='name', how='left')
    # 将未赋值的 count 填充为 0
    result_df['value'] = result_df['count'].fillna(0)
    # 移除不需要的列
    result_df.drop(columns=['count'], inplace=True)


    # 生成重复的行
    date_list = [end_date] * len(result_df)
    # 创建 DataFrame
    checking_date = pd.DataFrame(date_list, columns=['date'])
    result_finally_df = pd.concat([checking_date, result_df], axis=1)

    return result_finally_df


# print(get_personal_penalty_data())