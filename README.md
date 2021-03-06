# CVAT on AWS China

This repo initially help us deploy CVAT on AWS China, which will refactor the [office deployment](https://openvinotoolkit.github.io/cvat/docs/administration/basics/installation/) architecture. But we can support deploy this architecture on global Tokyo region by now.

## Architecture

![Arch](images/Arch.png)


This architecture will do:

- All the architecture will running on a new AWS VPC, which will have 3 public subnets and 3 private subnets.

- CVAT Server and UI services will be running on ECS Fargate containers, traefik container will be substituted by AWS ALB.

- CVAT cache layer docker will be replaced by ElastiCache Redis.

- CVAT PostgreSQL will running on RDS.

- CVAT docker volumes for media files will be replaced by EFS.

- AI inference for auto annotation will be refactored by [CVAT Serverless](cvat-serverless/) service, and all the inference endpoint will deploy on SageMaker.

- We will have a ECS task running on Fargate only for once to init Database and copy some demo files from S3 to EFS.

## CVAT Docker Images
Firstly, create some CVAT docker images for ECS Fargate deployment.

### CVAT Serverless
Because we have refactored whole serverless modules, so we need create a totally new docker image for this service.

Git clone this repo into your local:
```bash
git clone https://github.com/aws-samples/cvat-on-aws-china
```
Change to the project folder, and build your docker image:
```bash
cd cvat-on-aws-china/cvat-serverless
docker build . -t openvino/cvat_serverless
```
Next you should push the local image to the ECR and replace the `YOUR_AWS_ACCOUNT_ID` with the real one:
```bash
aws ecr create-repository --repository-name dockerhub/openvino/cvat_serverless
$(aws ecr get-login --no-include-email)
docker tag openvino/cvat_serverless <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.cn-northwest-1.amazonaws.com.cn/dockerhub/openvino/cvat_serverless
docker push <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.cn-northwest-1.amazonaws.com.cn/dockerhub/openvino/cvat_serverless
```

### Modified CVAT Server
We will modify some official CVAT Server configurations, so we need a customization docker image.

```bash
cd ..
git clone https://github.com/openvinotoolkit/cvat.git
cd cvat
git checkout c48411ae5014aac4441aa03da8944fbd4373b312
git apply ../aws-cvat.patch
```
Then we need build our own customization docker image for CVAT server.

```bash
docker build . -t openvino/cvat_server
aws ecr create-repository --repository-name dockerhub/openvino/cvat_server
$(aws ecr get-login --no-include-email)
docker tag openvino/cvat_server <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.cn-northwest-1.amazonaws.com.cn/dockerhub/openvino/cvat_server
docker push <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.cn-northwest-1.amazonaws.com.cn/dockerhub/openvino/cvat_server
```

### CVAT UI (optional)

You can optionally create your own CVAT UI docker image or just use the docker hub standard one.
```bash
docker build . -f Dockerfile.ui -t openvino/cvat_ui
aws ecr create-repository --repository-name dockerhub/openvino/cvat_ui
$(aws ecr get-login --no-include-email)
docker tag openvino/cvat_ui <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.cn-northwest-1.amazonaws.com.cn/dockerhub/openvino/cvat_ui
docker push <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.cn-northwest-1.amazonaws.com.cn/dockerhub/openvino/cvat_ui
```

## CVAT AWS CloudFormation Template

We have crate a [CloudFormation Template](cvat-aws-all.yaml) to deploy the whole architecture on AWS Ningxia region. You should modify the template for all the CVAT docker images you have build. But if you don't want to use your own images you just built you can just deploy the default images from our creations.

## Deep learning serverless functions for automatic labeling

<!--lint disable maximum-line-length-->

| Name                                                                                                    | Type       | Framework  |
| ------------------------------------------------------------------------------------------------------- | ---------- | ---------- |
| [Object reidentification](cvat-serverless/functions/endpoints/openvino_reidentification.py)            | reid       | OpenVINO   |
| [SiamMask](cvat-serverless/functions/endpoints/foolwood_siammask.py)                                   | tracker    | PyTorch    |
| [Inside-Outside Guidance](cvat-serverless/functions/endpoints/shiyinzhang_iog.py)                     | interactor | PyTorch    |
| [Faster RCNN](cvat-serverless/functions/endpoints/pth_rcnn.py)                                         | detector   | PyTorch    |
| [Faster RCNN COCO v2](cvat-serverless/functions/endpoints/tf_rcnn.py)                                  | detector   | TensroFlow |

<!--lint enable maximum-line-length-->

## Deploy the CloudFormation template directly
We have two CloudFormation template quick start link bellow, and all the necessary AWS resource will be created automatically.

| Region | QuickStart Link  |
| -------|------------------|
|Beijing Region | [Quick Click](https://console.amazonaws.cn/cloudformation/home?#/stacks/quickcreate?templateUrl=https://cvat-quickstart.s3.cn-northwest-1.amazonaws.com.cn/latest/cvat-aws-all.yaml) |
|Tokyo Region | [Quick Click](https://console.aws.amazon.com/cloudformation/home#/stacks/quickcreate?templateUrl=https://cvat-aws.s3.ap-northeast-1.amazonaws.com/cvat-aws-ap-northeast-1-all.yaml) |
<!--lint disable maximum-line-length-->

<!--lint enable maximum-line-length-->
## License Summary
This sample code is made available under the MIT-0 license. See the LICENSE file.