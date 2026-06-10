import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta


def get_all_names():
    # 连接到MySQL数据库
    engine = create_engine('mysql+mysqlconnector://root:root@192.168.59.185:3306/jinqiao_meikuang') # 金桥库
    # engine = create_engine('mysql+mysqlconnector://root:0266@localhost:3306/jinqiao_meikuang') # 本地库

    # 计算日期范围
    end = datetime.now() - timedelta(days=1)
    start = end - timedelta(days=14)
    end_date = end.strftime('%Y-%m-%d')
    start_date = start.strftime('%Y-%m-%d')

    # 测试
    # end_date = '2024-10-16'
    # start_date = '2024-10-10'

    # 查询数据
    # cursor.execute("SELECT personName, employeeId FROM employee_clock_history")
    # data = cursor.fetchall()
    query = f"""
        SELECT personName, employeeId
        FROM employee_clock_history
        WHERE detectTime >= '{start_date}' AND detectTime <= '{end_date}'
        """

    # df = pd.DataFrame(data)
    df = pd.read_sql_query(query, engine)
    df.columns = ['name', 'Id']
    df_unique = df.drop_duplicates(subset='name')
    df_unique.reset_index(drop=True, inplace=True)

    # 关闭连接
    # cursor.close()
    # conn.close()

    return df_unique

# print(get_all_names())