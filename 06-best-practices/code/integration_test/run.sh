#!/usr/bin/env bash

# cd to current directory
cd "$(dirname "$0")"

# build the Docker image
if [ "${LOCAL_IMAGE_NAME}" == "" ]; then 
    LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
    export LOCAL_IMAGE_NAME="stream-model-duration:${LOCAL_TAG}"
    echo "LOCAL_IMAGE_NAME is not set, building a new image with tag ${LOCAL_IMAGE_NAME}"
    docker build -t ${LOCAL_IMAGE_NAME} ..
else
    echo "no need to build image ${LOCAL_IMAGE_NAME}"
fi

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
