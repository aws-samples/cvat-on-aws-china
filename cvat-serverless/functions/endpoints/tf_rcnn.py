from django.http import HttpResponse, JsonResponse
import boto3
from PIL import Image
import json
import io
import base64
import numpy as np
from django.conf import settings

def infer(image):
    width, height = image.size
    if width > 1920 or height > 1080:
        image = image.resize((width // 2, height // 2), Image.ANTIALIAS)
    image_np = np.array(image.getdata())[:, :3].reshape(
        (image.height, image.width, -1)).astype(np.uint8)
    image_np = np.expand_dims(image_np, axis=0)

    client = boto3.client('runtime.sagemaker')
    data = image_np.tolist()
    response = client.invoke_endpoint(EndpointName=settings.TF_RCNN_ENDPOINT, 
	                                  Body=json.dumps(data),
                                      TargetContainerHostname=settings.TF_RCNN_NAME,
	                                  ContentType='application/json')
    response_body = response['Body'].read()
    result = json.loads(response_body.decode('utf-8'))['predictions'][0]

    return (result['detection_boxes'], result['detection_scores'], 
    	result['detection_classes'], result['num_detections'])

def get_label(obj_class):
    f = open('functions/endpoints/tf_rcnn_labels.json',)
    labels = json.load(f)
    try:
        label = next(item for item in labels if item["id"] == obj_class)
    except Exception:
        return "unknown"
    return label['name']

def call(data):
    buf = io.BytesIO(base64.b64decode(data["image"]))
    threshold = float(data.get("threshold", 0.5))
    image = Image.open(buf)

    (boxes, scores, classes, num_detections) = infer(image)

    results = []
    for i in range(int(num_detections)):
        obj_class = int(classes[i])
        obj_score = scores[i]
        obj_label = get_label(obj_class)
        if obj_score >= threshold:
            xtl = boxes[i][1] * image.width
            ytl = boxes[i][0] * image.height
            xbr = boxes[i][3] * image.width
            ybr = boxes[i][2] * image.height

            results.append({
                "confidence": str(obj_score),
                "label": obj_label,
                "points": [xtl, ytl, xbr, ybr],
                "type": "rectangle",
            })

	
    return JsonResponse(results, safe=False)