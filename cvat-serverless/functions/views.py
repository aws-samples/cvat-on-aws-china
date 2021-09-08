from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from functions.models import Function
from functions.serializers import FunctionSerializer
from functions.endpoints import *
import json

NO_METHOD_ERR = {'message': 'This method is not allowed!'}
NO_HEADER_ERR = {'message': 'Some headers not exist!'}
NO_MODEL_ERR = {'message': 'This model not exists!'}

@csrf_exempt
def function_list(request):
    """
    List all functions.
    """
    if request.method == 'GET':
        functions = Function.objects.all()
        serializer = FunctionSerializer(functions, many=True)
        result = dict()
        for item in serializer.data:
            result.update({item['name']: get_result_dict(item)})
        return JsonResponse(result, safe=False)

    else:
        return JsonResponse(NO_METHOD_ERR, status=405)

@csrf_exempt
def function_detail(request, name):
    """
    Retrieve a function.
    """
    try:
        function = Function.objects.get(name=name)
    except Function.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = FunctionSerializer(function)
        return JsonResponse(get_result_dict(serializer.data))
    else:
        return JsonResponse(NO_METHOD_ERR, status=405)

@csrf_exempt
def function_invoke(request):
    """
    Invoke a function.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        if 'x-nuclio-function-name' in request.headers:
            if request.headers['x-nuclio-function-name'] == 'tf-faster-rcnn-inception-v2-coco':
                return tf_rcnn.call(data)
            elif request.headers['x-nuclio-function-name'] == 'pth-faster-rcnn':
                return pth_rcnn.call(data)
            elif request.headers['x-nuclio-function-name'] == 'pth-shiyinzhang-iog':
                return shiyinzhang_iog.call(data)
            elif request.headers['x-nuclio-function-name'] == 'pth-foolwood-siammask':
                return foolwood_siammask.call(data)
            elif request.headers['x-nuclio-function-name'] == 'openvino-person-reidentification-retail':
                return openvino_reidentification.call(data)
            else:
                return JsonResponse(NO_MODEL_ERR, status=406)
        else:
            return JsonResponse(NO_HEADER_ERR, status=406)
    else:
        return JsonResponse(NO_METHOD_ERR, status=405)

def get_result_dict(item):
    return dict(metadata=dict(name=item['name'], annotations=item), 
                status=dict(state=item['status']),
                spec=dict(description=item['description']))
