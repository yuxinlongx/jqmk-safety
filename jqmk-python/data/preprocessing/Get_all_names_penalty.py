import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import re

def get_all_names_penalty():
    # 连接到MySQL数据库
    engine = create_engine('mysql+mysqlconnector://root:jqmk%402023@localhost:3306/exam_system') # 金桥库

    # 计算日期范围
    end = datetime.now() - timedelta(days=1)
    start = end - timedelta(days=29)
    end_date = end.strftime('%Y-%m-%d')
    start_date = start.strftime('%Y-%m-%d')

    # 测试
    # end_date = '2024-10-16'
    # start_date = '2024-10-10'

    # 查询数据
    # cursor.execute("SELECT personName, employeeId FROM employee_clock_history")
    # data = cursor.fetchall()
    query = f"""
        SELECT duty_person, duty_unit
        FROM penalty_data
        WHERE violation_date >= '{start_date}' AND violation_date <= '{end_date}'
        """

    # df = pd.DataFrame(data)
    df = pd.read_sql_query(query, engine)
    df.columns = ['name', 'unit']
    df_unique = df.drop_duplicates(subset='name')
    df_unique.reset_index(drop=True, inplace=True)
    names_unique = df_unique['name'].tolist()

    engine_j = create_engine('mysql+mysqlconnector://root:jqmk%402023@localhost:3306/exam_system')  # 金桥库

    # for i in range(len(names_unique)):
    #     query_j = f"""
    #     SELECT employee_id, username
    #     FROM user_profile_data
    #     WHERE username = '{names_unique[i]}'
    #     """
    #
    #     df_name = pd.read_sql_query(query_j, engine_j)
    #     df_name.columns = ['id', 'name']
    #     df_name_unique = df_name.iloc[0:1]
    #     if i == 0:
    #         df_names_unique = df_name_unique
    #     else:
    #         df_names_unique = pd.concat([df_names_unique, df_name_unique], axis=0)

    # 将用户名列表转为 SQL 查询中适用的字符串格式
    names_str = ", ".join([f"'{name}'" for name in names_unique])

    # 构建一次性查询，查询所有用户名的 employee_id 和 username
    query_j = f"""
    SELECT employee_id AS id, username AS name
    FROM user
    WHERE username IN ({names_str})
    """

    # 执行查询并加载到 DataFrame
    df_names = pd.read_sql_query(query_j, engine_j)
    df_names_unique = df_names.drop_duplicates(subset='name')
    df_names_unique.reset_index(drop=True, inplace=True)

    merged_outer = pd.merge(df_unique, df_names_unique, on='name', how='outer')

    merged_outer_nan = merged_outer[merged_outer['id'].isna()]  # 该列值为NaN的行
    merged_outer_nan.reset_index(drop=True, inplace=True)
    merged_outer_not_nan = merged_outer[merged_outer['id'].notna()]  # 该列值不为NaN的行
    merged_outer_not_nan.reset_index(drop=True, inplace=True)

    # 删除中文名字后的字母
    merged_outer_nan_without = merged_outer_nan.copy()
    merged_outer_nan_without['name'] = merged_outer_nan['name'].str.replace(r'([\u4e00-\u9fff]+)[a-zA-Z]+', r'\1', regex=True
)
    # merged_outer_nan_without_name = merged_outer_nan['name'].apply(
    #     lambda x: re.sub(r'([\u4e00-\u9fff]+)[a-zA-Z]+', r'\1', str(x)) if pd.notna(x) else x
    # )

    merged_outer_nan_new = merged_outer_nan_without[['name', 'unit']]

    names_unique_new = merged_outer_nan_new['name'].tolist()

    # 将用户名列表转为 SQL 查询中适用的字符串格式
    names_str_new = ", ".join([f"'{name_new}'" for name_new in names_unique_new])

    # 构建一次性查询，查询所有用户名的 employee_id 和 username
    query_k = f"""
        SELECT employee_id AS id, username AS name
        FROM user
        WHERE username IN ({names_str_new})
        """

    # 执行查询并加载到 DataFrame
    df_names_new = pd.read_sql_query(query_k, engine_j)
    df_names_unique_new = df_names_new.drop_duplicates(subset='name')
    df_names_unique_new.reset_index(drop=True, inplace=True)

    merged_outer_new = pd.merge(merged_outer_nan_new, df_names_unique_new, on='name', how='outer')

    merged_outer_nan_new = merged_outer_new[merged_outer_new['id'].isna()]  # 该列值为NaN的行
    merged_outer_nan_new.reset_index(drop=True, inplace=True)
    merged_outer_not_nan_new = merged_outer_new[merged_outer_new['id'].notna()]  # 该列值不为NaN的行
    merged_outer_not_nan_new.reset_index(drop=True, inplace=True)

    final_merged = pd.concat([merged_outer_not_nan, merged_outer_not_nan_new])
    final_merged = final_merged.drop_duplicates(subset='name')
    final_merged.reset_index(drop=True, inplace=True)
    final_merged.drop(columns=['unit'], inplace=True)

    return final_merged

if __name__ == "__main__":
    get_all_names_penalty()
