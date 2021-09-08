from django.http import HttpResponse, JsonResponse
import boto3
import json
import io
import base64
from django.conf import settings

def call(data):
    client = boto3.client('runtime.sagemaker')

    response = client.invoke_endpoint(EndpointName=settings.PTH_SIAMMASK_ENDPOINT,
                                      TargetContainerHostname=settings.PTH_SIAMMASK_NAME,
                                      Body=json.dumps(data),
                                      ContentType='application/json')
    response_body = response['Body'].read()
    result = json.loads(response_body.decode('utf-8'))

    return JsonResponse(result, safe=False)