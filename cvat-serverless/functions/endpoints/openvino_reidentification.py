from django.http import HttpResponse, JsonResponse
import boto3
import json
import io
import base64
from django.conf import settings
from PIL import Image
import math
import numpy
import os
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import euclidean, cosine


def infer(image0, boxes0, image1, boxes1, threshold, distance):
    similarity_matrix = _compute_similarity_matrix(image0, boxes0, image1, boxes1, distance)
    row_idx, col_idx = linear_sum_assignment(similarity_matrix)
    results = [-1] * len(boxes0)
    for idx0, idx1 in zip(row_idx, col_idx):
        if similarity_matrix[idx0, idx1] <= threshold:
            results[idx0] = int(idx1)

    return results

def _match_boxes(box0, box1, distance):
    cx0 = (box0["points"][0] + box0["points"][2]) / 2
    cy0 = (box0["points"][1] + box0["points"][3]) / 2
    cx1 = (box1["points"][0] + box1["points"][2]) / 2
    cy1 = (box1["points"][1] + box1["points"][3]) / 2
    is_good_distance = euclidean([cx0, cy0], [cx1, cy1]) <= distance
    is_same_label = box0["label_id"] == box1["label_id"]

    return is_good_distance and is_same_label

def sagemaker_call(image):
    image_np = np.array(image.getdata())[:, :3].reshape(
            (-1, image.height, image.width)).astype(np.uint8)
    image_np = np.expand_dims(image_np, axis=0)

    data = {'instances': image_np.tolist()}

    client = boto3.client('runtime.sagemaker')

    # response = client.invoke_endpoint(EndpointName='openvinio-reidentification-2021-09-01-03-56-10',
    #                                   #TargetContainerHostname=settings.OPENVINO_IDENTIFICATION_NAME,
    #                                   Body=json.dumps(data),
    #                                   ContentType='application/json')

    response = client.invoke_endpoint(EndpointName=settings.OPENVINO_IDENTIFICATION_ENDPOINT,
                                      TargetContainerHostname=settings.OPENVINO_IDENTIFICATION_NAME,
                                      Body=json.dumps(data),
                                      ContentType='application/json')
    response_body = response['Body'].read()
    result = json.loads(response_body.decode('utf-8'))
    result_np = np.array(result['predictions'])
    return result_np


def _match_crops(crop0, crop1):
    embedding0 = sagemaker_call(crop0)
    embedding1 = sagemaker_call(crop1)

    embedding0 = embedding0.reshape(embedding0.size)
    embedding1 = embedding1.reshape(embedding1.size)

    return cosine(embedding0, embedding1)

def _compute_similarity_matrix(image0, boxes0, image1, boxes1,
    distance):
    def _int(number, upper):
        return math.floor(numpy.clip(number, 0, upper - 1))

    DISTANCE_INF = 1000.0

    matrix = numpy.full([len(boxes0), len(boxes1)], DISTANCE_INF, dtype=float)
    for row, box0 in enumerate(boxes0):
        w0, h0 = image0.size
        xtl0, xbr0, ytl0, ybr0 = (
            _int(box0["points"][0], w0), _int(box0["points"][2], w0),
            _int(box0["points"][1], h0), _int(box0["points"][3], h0)
        )

        for col, box1 in enumerate(boxes1):
            w1, h1 = image1.size
            xtl1, xbr1, ytl1, ybr1 = (
                _int(box1["points"][0], w1), _int(box1["points"][2], w1),
                _int(box1["points"][1], h1), _int(box1["points"][3], h1)
            )

            if not _match_boxes(box0, box1, distance):
                continue

            crop0 = image0.crop((xtl0, ytl0, xbr0, ybr0))
            crop1 = image1.crop((xtl1, ytl1, xbr1, ybr1))
            matrix[row][col] = _match_crops(crop0, crop1)

    return matrix

def call(data):
    buf0 = io.BytesIO(base64.b64decode(data["image0"]))
    buf1 = io.BytesIO(base64.b64decode(data["image1"]))
    threshold = float(data.get("threshold", 0.5))
    max_distance = float(data.get("max_distance", 50))
    image0 = Image.open(buf0)
    image1 = Image.open(buf1)
    boxes0 = data["boxes0"]
    boxes1 = data["boxes1"]

    results = infer(image0, boxes0, image1, boxes1, threshold, max_distance)

    return JsonResponse(results, safe=False)