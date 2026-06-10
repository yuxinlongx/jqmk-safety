import pandas as pd
from sqlalchemy import create_engine
from data.preprocessing.Crawler import crawler
from datetime import datetime
import logging
# logging.basicConfig(filename='task.log', level=logging.INFO)


def penalty():
    # data = pd.read_excel('C:/Users/Administrator/Desktop/金桥三违信息表.xlsx')
    # data.sort_values(by="违章日期", inplace=True, ascending=True)
    time_start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('定时存储开始' + ' ' + time_start)
    logging.info("Crawler started" + ' ' + time_start)
    data = crawler()
    data.columns = ['number', 'violation_date', 'classes',
                    'duty_unit', 'duty_person', 'inspect_place',
                    'violation_facts', 'penalty_amount', 'informant', 'cooperate',
                    'violation_type', 'violation_level', 'according', 'reporting_unit']

    # 创建数据库连接
    print(data.head())
    engine_center = create_engine('mysql+mysqlconnector://root:jqmk%402023@localhost:3306/exam_system')
    # 将DataFrame的内容插入到数据库表中
    data.to_sql('penalty_data', con=engine_center, if_exists='append', index=False)
    time_end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('定时存储完成' + ' ' + time_end)
    logging.info("Crawler completed" + ' ' + time_end)


if __name__ == "__main__":
    penalty()