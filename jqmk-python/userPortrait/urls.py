from django.contrib import admin
from django.urls import path
# from logistic.view_log import logistic_prediction_view
# from kmeans.kmeans_view import run_training, run_warning
# from logistic.view_train_log import logistic_train_view
# from comprehensive.Comprehensive import employees_predictions

urlpatterns = [
    path('admin/', admin.site.urls),

    # path('kmeans_view/training', run_training),
    # path('kmeans_view/warning', run_warning),
    #
    # path('logistic_prediction', logistic_prediction_view),
    # path('logistic_train', logistic_train_view),
    #
    # path('comprehensive/Comprehensive', employees_predictions),
]
