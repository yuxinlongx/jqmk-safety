"""
WSGI config for userPortrait project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'userPortrait.settings')

application = get_wsgi_application()


# 启动定时任务
import schedule
import time
from dailyPredictionapp.dailyPredictiontask import dailyPrediction_scheduled_task
from data.preprocessing.Penalty import penalty
import threading
# from dailyPrediction.X_view import x_call_external_api
# from dailyPrediction.T_view import t_call_external_api
# from data.preprocessing.Memory_monitoring import monitor_memory
from dailyPrediction.V_view import v_call_external_api

def start_scheduler():
    # schedule.every().day.at('00:00').do(dailyPrediction_scheduled_task)
    # schedule.every().day.at('00:00').do(monitor_memory)
    schedule.every().day.at('00:01').do(penalty)
    schedule.every().day.at('00:03').do(v_call_external_api)
    while True:
        schedule.run_pending()
        time.sleep(1)


# 启动一个新的线程来运行定时任务
thread = threading.Thread(target=start_scheduler)
thread.start()
