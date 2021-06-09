#!/bin/bash

set -e

GENUI_DOCKER_IMAGE_PREFIX=${GENUI_DOCKER_IMAGE_PREFIX:-"sichom"}
TAG=${GENUI_DOCKER_IMAGE_TAG:-"latest"}
NVIDIA_CUDA_VERSION=${NVIDIA_CUDA_VERSION:-""}

echo "The following commands will be run:"
echo "$(NVIDIA_CUDA_VERSION=${NVIDIA_CUDA_VERSION} python3 get_tags.py $TAG $TAG)"
eval "$(NVIDIA_CUDA_VERSION=${NVIDIA_CUDA_VERSION} python3 get_tags.py $TAG $TAG)"