from celery import shared_task
from dailyPrediction.dpView import call_external_api
from datetime import datetime
import logging
logging.basicConfig(filename='task.log', level=logging.INFO)


@shared_task()
def dailyPrediction_scheduled_task():
    try:
        time_start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info("Task started" + ' ' + time_start)
        # 任务的实际逻辑
        print("定时预测开始" + ' ' + time_start)
        call_external_api()
        time_end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("定时预测完成" + ' ' + time_end)
        logging.info("Task completed" + ' ' + time_end)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
