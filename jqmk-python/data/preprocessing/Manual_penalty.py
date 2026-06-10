from sqlalchemy import create_engine
import pandas as pd


def manual_penalty():
    data = pd.read_excel('C:/Users/Administrator/Desktop/金桥三违信息表.xlsx') # 读取之前删除表格的第一行，第一列和最后一样
    data.columns = ['number', 'violation_date', 'classes',
                    'duty_unit', 'duty_person', 'inspect_place',
                    'violation_facts', 'penalty_amount', 'informant', 'cooperate',
                    'violation_type', 'violation_level', 'according', 'reporting_unit']
    data.sort_values(by=['violation_date'], ascending=False, inplace=True)
    data.reset_index(drop=True, inplace=True)
    engine = create_engine('mysql+mysqlconnector://root:jqmk%402023@localhost:3306/exam_system')
    data.to_sql('penalty_data', con=engine, if_exists='append', index=False)


manual_penalty()  # 执行前删除桌面金桥三违信息表的第一行第一列以及最后一行
