# logistic/main_log.py

import matplotlib  # 导入matplotlib库进行图形绘制
matplotlib.use('Agg')  # 设置matplotlib使用非图形界面后端，便于在不支持GUI的环境中运行

# 从logistic模块导入LogisticModel类
from logistic.logistic_model import LogisticModel
import sys  # 导入sys库以获取命令行参数

def main():
    # 从命令行参数获取数据文件路径和模型保存路径
    file_path = sys.argv[1]  # 第一个参数：数据文件路径
    model_save_path = sys.argv[2]  # 第二个参数：模型保存路径

    # 实例化逻辑回归模型
    model = LogisticModel()

    # 使用指定的数据文件训练模型
    model.train(file_path)
    # 将训练好的模型保存到指定路径
    model.save_model(model_save_path)

    # 加载保存的模型，验证模型是否正确保存并可重新加载
    model.load_model(model_save_path)
    # 打印模型加载成功的确认信息
    print("模型已加载并准备好用于预测。")

# 如果直接运行这个脚本，则执行main函数
if __name__ == "__main__":
    main()

"""
使用 Python 命令运行脚本，并在命令后附加所需的参数。
命令格式为：python main_log.py [数据文件路径] [模型保存路径]
例如：python main_log.py /Users/username/data/train_data.csv /Users/username/models/logistic_model.pkl
"""