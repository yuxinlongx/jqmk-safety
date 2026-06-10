import logging
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from logistic.logistic_model import LogisticModel
from .result import R, StatusCodeEnum

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@csrf_exempt
def logistic_train_view(request):
    if request.method != 'GET':
        logger.error("Invalid request method")
        return JsonResponse(R.error(StatusCodeEnum.INVALID_REQUEST_METHOD, "Invalid request method"))

    try:
        # 获取是否运行训练的参数
        training = request.GET.get('training')
        logger.info(f"Received training request with parameter: {training}")
        # http://127.0.0.1:8000/logistic_train?training=yes

        if training is None:
            logger.error("Missing key parameter: training")
            return JsonResponse(R.error(StatusCodeEnum.MISSING_KEY_PARAMETER, "Missing key parameter: training"))

        if training != 'yes':
            logger.error("Invalid value for training parameter")
            return JsonResponse(R.error(StatusCodeEnum.INVALID_KEY_VALUE, "Invalid value for training: yes"))

        logger.info("Starting model training process")
        model = LogisticModel()
        current_directory = os.path.dirname(__file__)
        base_directory = os.path.dirname(current_directory)
        file_path = os.path.join(base_directory, 'data', 'final_result_encoder_2023-11-01_2024-05-31.csv')  # 修改为实际的训练数据路径
        model.train(file_path)
        logger.info("Model training completed.")

        return JsonResponse(R.ok('logistic模型训练完成'))

    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        return JsonResponse(R.error(StatusCodeEnum.OTHER, f"Error during training: {str(e)}"))
