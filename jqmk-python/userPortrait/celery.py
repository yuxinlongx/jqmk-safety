from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 为celery程序设置Django的默认设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'userPortrait.settings')

app = Celery('userPortrait')

# 从Django的设置中读取配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现异步任务
# app.autodiscover_tasks(['kmeansapp', 'comprehensiveapp', 'dailyPredictionapp'])
app.autodiscover_tasks(['dailyPredictionapp'])
