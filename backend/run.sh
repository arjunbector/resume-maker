#!/bin/bash

# Check for --amd flag
if [[ "$2" == "--amd" ]] || [[ "$1" == "--amd" ]]; then
    IMAGE_NAME="sohamghugare/resume-maker-backend-amd:latest"
    PLATFORM="--platform linux/amd64"
else
    IMAGE_NAME="sohamghugare/resume-maker-backend:latest"
    PLATFORM=""
fi

COMMAND="$1"
if [[ "$1" == "--amd" ]]; then
    COMMAND="$2"
fi

case "$COMMAND" in
  build)
    echo "Building Docker image: $IMAGE_NAME"
    docker build -t $IMAGE_NAME $PLATFORM .
    ;;
  push)
    echo "Pushing Docker image: $IMAGE_NAME"
    docker push $IMAGE_NAME
    ;;
  deploy)
    echo "Deploying Docker container: $IMAGE_NAME"
    docker run --rm -it -p 8000:8000 --env-file .env $IMAGE_NAME
    ;;
  *)
    echo "Usage: ./run.sh {build|push|deploy} [--amd]"
    exit 1
    ;;
esac
