import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
# import matplotlib.pyplot as plt
import joblib
import os

class LogisticModel:
    def __init__(self):
        # 创建逻辑回归模型实例
        self.model = LogisticRegression(max_iter=1000, random_state=42)
        # 初始化最佳阈值和分位数
        self.optimal_threshold = None
        self.percentiles = None
        self.min_score = None
        self.max_score = None

    def train(self, file_path):
        """
        使用指定的文件路径训练模型。
        """
        # 从CSV文件加载数据
        data = pd.read_csv(file_path, encoding='gbk')
        X = data.drop(['date_name', 'punished'], axis=1)  # 删除非特征列
        y = data['punished']  # 目标变量
        # 统计未被惩罚和被惩罚的总次数
        total_unpunished = (y == 0).sum()
        total_punished = (y == 1).sum()
        print("未被惩罚的总次数：", total_unpunished)
        print("被惩罚的总次数：", total_punished)

        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)

        # 在测试集上进行预测
        y_pred_prob = self.model.predict_proba(X_test)[:, 1]
        fpr, tpr, thresholds = roc_curve(y_test, y_pred_prob)
        auc_score = roc_auc_score(y_test, y_pred_prob)

        # 找到并设置最佳阈值
        optimal_idx = np.argmax(tpr - fpr)
        self.optimal_threshold = thresholds[optimal_idx]
        print("使用的最佳阈值为：", self.optimal_threshold)

        # 计算并存储分位数用于标准化分数
        scores = y_pred_prob * 100
        self.min_score = scores.min()
        self.max_score = scores.max()

        # 标准化分数
        normalized_scores = (scores - self.min_score) / (self.max_score - self.min_score) * 100

        # 计算新的分位数
        self.percentiles = np.percentile(normalized_scores, [95, 97.5])
        print("标准化后最小分数：", self.min_score)
        print("标准化后最大分数：", self.max_score)

        # 打印风险等级划分的分数段
        print("低风险: 分数 < {:.2f}".format(self.percentiles[0]))
        print("中风险: {:.2f} <= 分数 < {:.2f}".format(self.percentiles[0], self.percentiles[1]))
        print("高风险: 分数 >= {:.2f}".format(self.percentiles[1]))

        # # 绘制ROC曲线
        # plt.figure()
        # plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % auc_score)
        # plt.plot([0, 1], [0, 1], 'k--')
        # plt.xlim([0.0, 1.0])
        # plt.ylim([0.0, 1.05])
        # plt.xlabel('False Positive Rate')
        # plt.ylabel('True Positive Rate')
        # plt.title('Receiver Operating Characteristic')
        # plt.legend(loc="lower right")
        # plt.show()

        # 计算并打印95%分位数和97.5%分位数的标准化分数
        score_95_percentile = np.percentile(normalized_scores, 95)
        score_975_percentile = np.percentile(normalized_scores, 97.5)
        print("标准化后95%分位数的分数为：", score_95_percentile)
        print("标准化后97.5%分位数的分数为：", score_975_percentile)

        # 计算并打印混淆矩阵和分类报告
        y_pred = (y_pred_prob >= self.optimal_threshold).astype(int)
        conf_matrix = confusion_matrix(y_test, y_pred)
        class_report = classification_report(y_test, y_pred)
        print("混淆矩阵:\n", conf_matrix)
        print("\n分类报告:\n", class_report)

        # 保存测试集以供预测
        self.X_test = X_test
        self.y_test = y_test
        self.date_names = data['date_name']  # 保存日期列

    def predict(self, X):
        """
        使用最佳阈值对给定的数据进行预测，并计算分数和预测结果
        """
        y_pred_prob = self.model.predict_proba(X)[:, 1]
        scores = y_pred_prob * 100  # 计算分数
        y_pred = (y_pred_prob >= self.optimal_threshold).astype(int)

        # 标准化分数
        normalized_scores = (scores - self.min_score) / (self.max_score - self.min_score) * 100

        # 计算风险等级
        risk_levels = pd.cut(normalized_scores, bins=[-np.inf, self.percentiles[0], self.percentiles[1], np.inf],
                             labels=['低风险', '中风险', '高风险'])

        return scores, y_pred, normalized_scores, risk_levels

    def save_model(self, path):
        """
        将模型和阈值保存到指定路径
        """
        model_data = {
            'model': self.model,
            'optimal_threshold': self.optimal_threshold,
            'percentiles': self.percentiles,  # 保存分位数
            'min_score': self.min_score,  # 保存最小分数
            'max_score': self.max_score  # 保存最大分数
        }
        joblib.dump(model_data, path)

    def load_model(self, path):
        """
        从指定路径加载模型和阈值
        """
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.optimal_threshold = model_data['optimal_threshold']
        self.percentiles = model_data['percentiles']  # 加载分位数
        self.min_score = model_data['min_score']  # 加载最小分数
        self.max_score = model_data['max_score']  # 加载最大分数


if __name__ == "__main__":
    lm = LogisticModel()
    # 定位到数据文件夹
    current_directory = os.path.dirname(__file__)
    base_directory = os.path.dirname(current_directory)
    file_path = os.path.join(base_directory, 'data', 'final_result_encoder_2023-11-01_2024-05-31.csv')
    model_save_path = os.path.join(current_directory, 'logistic_model.pkl')

    # 训练模型并保存
    lm.train(file_path)
    lm.save_model(model_save_path)

    # 执行模型预测并打印结果
    scores, predictions, normalized_scores, risk_levels = lm.predict(lm.X_test)

    # 计算分数并保存预测结果到表格
    results_df = pd.DataFrame({
        'Date_Name': lm.date_names.iloc[lm.X_test.index],
        'Actual_Punished': lm.y_test,
        'Predicted_Probability': lm.model.predict_proba(lm.X_test)[:, 1],
        'Score': scores,
        'Normalized_Score': normalized_scores,
        'Predicted_Punished': predictions,
        'Risk_Level': risk_levels
    })
    results_df.to_csv('prediction_results_with_risk_levels.csv', index=False, encoding='utf-8')
    print("Prediction results saved to prediction_results_with_risk_levels.csv")

    # 打印结果
    print("预测结果:", predictions)
    print("分数:", scores)
    print("标准化分数:", normalized_scores)
    print("风险等级:", risk_levels)

