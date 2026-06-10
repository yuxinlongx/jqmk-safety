from data.preprocessing.Get_personal_penalty_data import get_personal_penalty_data
import pandas as pd


def x_prediction():
    penalty_data = get_personal_penalty_data()
    penalty_results = []

    for _, row in penalty_data.iterrows():
        if row.iloc[3] > 5:
            penalty_result = '高风险'
        elif row.iloc[3] > 2:
            penalty_result = '中风险'
        else:
            penalty_result = '低风险'
        penalty_results.append(penalty_result)

    penalty_result_df = pd.DataFrame(penalty_results)


    finally_result = pd.concat([penalty_data, penalty_result_df], axis=1)
    finally_result.columns = ['检测日期', '姓名', '工号', '违章次数', '综合预警']

    return finally_result

# print(x_prediction())