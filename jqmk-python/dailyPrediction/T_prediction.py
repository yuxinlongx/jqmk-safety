from data.preprocessing.T_get_penalty_data import t_get_personal_penalty_data
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta

def t_prediction():
    penalty_data, critical_value, start_date, end_date, engine = t_get_personal_penalty_data()
    penalty_results = []
    engine = create_engine('mysql+mysqlconnector://root:jqmk%402023@localhost:3306/exam_system') # 金桥库
    # engine = create_engine('mysql+mysqlconnector://root:0266@localhost:3306/jinqiao_meikuang')  # 本地库

    for _, row in penalty_data.iterrows():
        if row.iloc[3] > critical_value:
            # 查询最后培训日期
            query = f"""
                SELECT username, MAX(creat_time) AS last_qualified_date
                FROM qualified_list
                WHERE username = '{row.iloc[1]}'
                GROUP BY username;
                """
            qualified_data = pd.read_sql(query, engine)
            if not qualified_data.empty:
                # 加上一天
                qualified_date = qualified_data['last_qualified_date'].iloc[0] + timedelta(days=1)
                qualified_date_sft = qualified_date.strftime('%Y-%m-%d')
                qualified_date_spt = datetime.strptime(qualified_date_sft, '%Y-%m-%d')
                start_date_spt = datetime.strptime(start_date,'%Y-%m-%d')

                if qualified_date_spt > start_date_spt:
                    # 查询最后培训日期到现在的违章次数
                    query = f"""
                        SELECT COUNT(*) AS violation_count
                        FROM penalty_data
                        WHERE duty_person = '{row.iloc[1]}'
                        AND violation_date BETWEEN '{qualified_date_sft}' AND '{end_date}';
                        """
                    violation_num = pd.read_sql(query, engine)
                    # 修改违章次数
                    penalty_data.loc[penalty_data['name'] == row.iloc[1], 'value'] = violation_num['violation_count'].iloc[0]
                    new_violation_num = violation_num['violation_count'].iloc[0]
                    # 再次判断
                    if new_violation_num > critical_value:
                        # penalty_result = '安全薄弱人员'
                        penalty_result = '高风险'
                    elif new_violation_num == critical_value:
                        # penalty_result = '安全预警人员'
                        penalty_result = '中风险'
                    else:
                        # penalty_result = '安全放心人员'
                        penalty_result = '低风险'
                else:
                    # penalty_result = '安全薄弱人员'
                    penalty_result = '高风险'
            else:
                # penalty_result = '安全薄弱人员'
                penalty_result = '高风险'

        elif row.iloc[3] == critical_value:
            # penalty_result = '安全预警人员'
            penalty_result = '中风险'

        else:
            # penalty_result = '安全放心人员'
            penalty_result = '低风险'

        penalty_results.append(penalty_result)

    penalty_result_df = pd.DataFrame(penalty_results)


    finally_result = pd.concat([penalty_data, penalty_result_df], axis=1)
    finally_result.columns = ['检测日期', '姓名', '工号', '违章次数', '综合预警']

    return finally_result


if __name__ == "__main__":
    t_prediction()
