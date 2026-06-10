import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 加载数据
results_df = pd.read_csv('prediction_results_with_risk_levels.csv', encoding='ISO-8859-1')

# 绘制标准化分数的直方图
plt.figure(figsize=(10, 6))
sns.histplot(results_df['Normalized_Score'], bins=30, kde=True)
plt.title('Distribution of Normalized Scores')
plt.xlabel('Normalized Score')
plt.ylabel('Frequency')
plt.show()

# 绘制标准化分数的箱线图
plt.figure(figsize=(10, 6))
sns.boxplot(x=results_df['Normalized_Score'])
plt.title('Box Plot of Normalized Scores')
plt.xlabel('Normalized Score')
plt.show()

# 绘制标准化分数与实际惩罚的散点图
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Normalized_Score', y='Actual_Punished', data=results_df)
plt.title('Normalized Score vs. Actual Punished')
plt.xlabel('Normalized Score')
plt.ylabel('Actual Punished')
plt.show()

# 计算描述性统计量
print(results_df['Normalized_Score'].describe())

# 标准化分数分段分析
results_df['Risk_Level'] = pd.qcut(results_df['Normalized_Score'], q=4, labels=['低风险', '中风险', '较高风险', '高风险'])
risk_level_counts = results_df['Risk_Level'].value_counts()
print(risk_level_counts)

# 分段惩罚率分析
punishment_rate_by_risk = results_df.groupby('Risk_Level')['Actual_Punished'].mean()
print(punishment_rate_by_risk)

