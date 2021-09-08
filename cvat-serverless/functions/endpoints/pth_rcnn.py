from django.http import HttpResponse, JsonResponse
import boto3
import json
import io
import base64
from django.conf import settings


def infer(image):

    client = boto3.client('runtime.sagemaker')

    response = client.invoke_endpoint(EndpointName=settings.PTH_RCNN_ENDPOINT,
                                      Body=image,
                                      TargetContainerHostname=settings.PTH_RCNN_NAME,
                                      ContentType='application/x-image')
    response_body = response['Body'].read()
    result = json.loads(response_body.decode('utf-8'))

    return result

def call(data):
    buf = io.BytesIO(base64.b64decode(data["image"]))
    threshold = float(data.get("threshold", 0.5))

    predicts = infer(buf)

    results = []
    for i in range(len(predicts)):
        obj_score = predicts[i]['score']
        if obj_score >= threshold:
            results.append({
                "confidence": str(obj_score),
                "label": list(predicts[i].keys())[0],
                "points": list(predicts[i].values())[0],
                "type": "rectangle",
            })

	
    return JsonResponse(results, safe=False)