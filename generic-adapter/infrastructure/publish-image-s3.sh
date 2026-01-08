#!/bin/sh

TAG="latest"
IMAGE="ia/${IMAGE_NAME}:$TAG"

if [ -z "$(docker images -q $IMAGE 2> /dev/null)" ]; then
  echo "Image: $IMAGE does not exist, exiting..."
  exit 1
fi

AWS_REGION=eu-west-2
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

aws ecr get-login-password --region $AWS_REGION | sudo docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com

AWS_IMAGE=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE

sudo docker tag $IMAGE $AWS_IMAGE
sudo docker push $AWS_IMAGE

echo "Revision tag: $TAG"
