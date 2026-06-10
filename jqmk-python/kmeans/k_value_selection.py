import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from gap_statistic import OptimalK
from sklearn import mixture 
import os
from sklearn.metrics import davies_bouldin_score
from sklearn.metrics import calinski_harabasz_score


# 生成示例数据
current_directory = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_directory, os.pardir))
data_file_path = os.path.join(project_root, 'data', 'final_result_encoder_2023-11-01_2024-05-31.csv')  # 数据文件路径
ori_data = pd.read_csv(data_file_path, encoding='gbk')
data = ori_data.iloc[:, 0: -2].astype(float)  # 确保数据类型为浮点数
name_data = pd.DataFrame(ori_data.iloc[:, -2])
print('数据导入完成')

# 初始化存储各种评估指标的列表
sse = []
silhouette_scores = []
gap_statistics = []
aic_scores = []
bic_scores = []
db_scores = []
ch_scores = []
range_n_clusters = [2, 3, 4, 5, 6, 7, 8, 9, 10]  # 聚类数范围

# 计算每个聚类数下的评估指标
optimalK = OptimalK(parallel_backend='joblib')

for n_clusters in range_n_clusters:
    # 使用KMeans进行聚类
    kmeans_plus_plus = KMeans(n_clusters=n_clusters, init='random', max_iter=300, n_init=20, random_state=0)
    kmeans_plus_plus.fit(data)
    labels = kmeans_plus_plus.labels_
    sse.append(kmeans_plus_plus.inertia_)  # 存储SSE
    
    # 计算轮廓系数
    silhouette_avg = silhouette_score(data, kmeans_plus_plus.labels_)
    silhouette_scores.append(silhouette_avg)
    
    # 使用Gap Statistic方法
    gap_stat = optimalK(data, cluster_array=np.array([n_clusters]))
    gap_statistics.append(gap_stat)  # 修改这里以适应返回值格式
    
    # 使用高斯混合模型计算AIC和BIC
    gmm = mixture.GaussianMixture(n_components=n_clusters, random_state=0)
    gmm.fit(data)
    aic = gmm.aic(data)
    bic = gmm.bic(data)
    aic_scores.append(aic)
    bic_scores.append(bic)

    # 计算Davies-Bouldin指数
    db_score = davies_bouldin_score(data, labels)
    db_scores.append(db_score)
    
    # 计算Calinski-Harabasz指数
    ch_score = calinski_harabasz_score(data, labels)
    ch_scores.append(ch_score)

    print('聚类数为{}时的评估指标计算完成'.format(n_clusters))

# 设置 matplotlib 支持中文显示
plt.rcParams['font.family'] = ['Arial Unicode MS']  # 或者其他支持中文的字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 绘制评估指标随聚类数变化的曲线图
plt.figure(figsize=(18, 10))

# 绘制SSE曲线
plt.subplot(2, 3, 1)
# plt.figure(figsize=(18, 10))
plt.plot(range_n_clusters, sse, marker='o')
# for i, txt in enumerate(sse):
#     plt.annotate(f'{txt:.2f}', (range_n_clusters[i], sse[i]), textcoords="offset points", xytext=(0,10), ha='center')
plt.xlabel('聚类中心个数')
plt.ylabel('簇内误差平方和')
plt.title('肘部法')
# plt.xlabel('Number of clusters')
# plt.ylabel('SSE')
# plt.title('Elbow Method')
# plt.tight_layout()
# plt.show()

# 绘制轮廓系数曲线
plt.subplot(2, 3, 2)
# plt.figure(figsize=(18, 10))
plt.plot(range_n_clusters, silhouette_scores, marker='o')
# for i, txt in enumerate(silhouette_scores):
#     plt.annotate(f'{txt:.2f}', (range_n_clusters[i], silhouette_scores[i]), textcoords="offset points", xytext=(0,10), ha='center')
plt.xlabel('聚类中心个数')
plt.ylabel('轮廓系数')
plt.title('轮廓系数法')
# plt.xlabel('Number of clusters')
# plt.ylabel('Silhouette Score')
# plt.title('Silhouette Method')
# plt.tight_layout()
# plt.show()

# 绘制AIC曲线
plt.subplot(2, 3, 3)
# plt.figure(figsize=(18, 10))
plt.plot(range_n_clusters, aic_scores, marker='o')
# for i, txt in enumerate(aic_scores):
#     plt.annotate(f'{txt:.2f}', (range_n_clusters[i], aic_scores[i]), textcoords="offset points", xytext=(0,10), ha='center')
plt.xlabel('聚类中心个数')
plt.ylabel('AIC指数')
plt.title('赤池信息准则法')
# plt.xlabel('Number of clusters')
# plt.ylabel('AIC')
# plt.title('AIC Method')

# 绘制BIC曲线
plt.subplot(2, 3, 4)
# plt.figure(figsize=(18, 10))
plt.plot(range_n_clusters, bic_scores, marker='o')
# for i, txt in enumerate(bic_scores):
#     plt.annotate(f'{txt:.2f}', (range_n_clusters[i], bic_scores[i]), textcoords="offset points", xytext=(0,10), ha='center')
plt.xlabel('聚类中心个数')
plt.ylabel('BIC指数')
plt.title('贝叶斯信息准则')
# plt.xlabel('Number of clusters')
# plt.ylabel('BIC')
# plt.title('BIC Method')
plt.tight_layout()
plt.show()

# 绘制DB指数曲线
plt.subplot(2, 3, 5)
# plt.figure(figsize=(18, 10))
plt.plot(range_n_clusters, db_scores, marker='o')
# for i, txt in enumerate(db_scores):
#     plt.annotate(f'{txt:.2f}', (range_n_clusters[i], db_scores[i]), textcoords="offset points", xytext=(0,10), ha='center')
plt.xlabel('聚类中心个数')
plt.ylabel('Davies-Bouldin指数')
plt.title('DB指数法')
# plt.tight_layout()
# plt.show()

# 绘制CH指数曲线
plt.subplot(2, 3, 6)
# plt.figure(figsize=(18, 10))
plt.plot(range_n_clusters, ch_scores, marker='o')
# for i, txt in enumerate(ch_scores):
#     plt.annotate(f'{txt:.2f}', (range_n_clusters[i], ch_scores[i]), textcoords="offset points", xytext=(0,10), ha='center')
plt.xlabel('聚类中心个数')
plt.ylabel('Calinski-Harabasz指数')
plt.title('CH指数法')
# plt.tight_layout()
# plt.show()

"""
# 绘制Gap Statistic曲线
plt.subplot(2, 3, 3)
plt.plot(range_n_clusters, gap_statistics, marker='o')
# for i, txt in enumerate(gap_statistics):
#     plt.annotate(f'{txt:.2f}', (range_n_clusters[i], gap_statistics[i]), textcoords="offset points", xytext=(0,10), ha='center')
plt.xlabel('聚类中心个数')
plt.ylabel('最佳聚类中心')
plt.title('距离统计法')
# plt.xlabel('Number of clusters')
# plt.ylabel('Gap Statistic')
# plt.title('Gap Statistic Method')
"""

plt.tight_layout()
plt.show()
