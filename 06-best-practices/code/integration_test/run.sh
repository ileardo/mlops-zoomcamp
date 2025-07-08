#!/usr/bin/env bash

# cd to current directory
cd "$(dirname "$0")"

# variable for tagging the image
LOCAL_TAG=$(date +"%Y-%m-%d-%H-%M")
export LOCAL_IMAGE_NAME="web-service-duration:${LOCAL_TAG}"

# build the Docker image
echo "Building Docker image with tag: ${LOCAL_IMAGE_NAME}"
docker build -t ${LOCAL_IMAGE_NAME} ..

# build docker-compose
echo "Building Docker Compose"
docker-compose up -d

sleep 1

# run the integration test
echo "Running integration test"
pipenv run python test_docker.py

ERROR_CODE=$?
if [ $ERROR_CODE -ne 0 ]; then
    echo "Integration test failed with error code: $ERROR_CODE"
    echo "Check the logs for more details:"
    docker-compose logs
else
    echo "Integration test passed successfully"
fi

# stop and remove the containers
echo "Stopping and removing containers"
docker-compose down