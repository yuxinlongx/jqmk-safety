import os
from datetime import datetime


def checking():
    # 标志文件的路径
    flag_file_path = "kmeans/flag_script.txt"
    # 获取今天的日期
    today = datetime.now().strftime("%Y-%m-%d")

    # 检查标志文件是否存在
    if os.path.exists(flag_file_path):
        with open(flag_file_path, "r") as file:
            last_run_date = file.read().strip()
            # 如果脚本今天已经运行过，则退出
            if last_run_date == today:
                print("Script has already run today. Exiting.")
                return False

    # 更新标志文件的日期为今天
    with open(flag_file_path, "w") as file:
        file.write(today)
    return True
