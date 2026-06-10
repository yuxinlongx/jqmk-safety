def combine_warnings(logistic_risk_level, kmeans_predictions):
    """
    结合Logistic回归模型和KMeans模型的预测结果，给出综合结果。

    Args:
    logistic_risk_level (str): Logistic模型的预测结果，可取值为'高风险'、'中风险'、'低风险'
    kmeans_risk_level (str): KMeans模型的预测结果，可取值为'预警'、'正常'

    Returns:
    str: 综合预测结果
    """
    if logistic_risk_level == '高风险' and kmeans_predictions == '预警':
        return '高风险'
    elif logistic_risk_level == '中风险' and kmeans_predictions == '预警':
        return '中风险'
    elif logistic_risk_level == '高风险' and kmeans_predictions == '正常':
        return '中风险'
    elif logistic_risk_level == '低风险' and kmeans_predictions == '预警':
        return '中风险'
    elif logistic_risk_level == '中风险' and kmeans_predictions == '正常':
        return '低风险'
    elif logistic_risk_level == '低风险' and kmeans_predictions == '正常':
        return '低风险'
    else:
        return None
