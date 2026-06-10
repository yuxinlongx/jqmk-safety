from __future__ import absolute_import, unicode_literals

# 使celery应用在Django启动时即刻加载
from .celery import app as celery_app

__all__ = ('celery_app',)
