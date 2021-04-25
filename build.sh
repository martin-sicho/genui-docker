#!/bin/bash

set -e

REPO_PREFIX=${GENUI_DOCKER_IMAGE_PREFIX:-"sichom"}
TAG=${GENUI_DOCKER_IMAGE_TAG:-"latest"}
NVIDIA_CUDA_RUNFILE=${NVIDIA_CUDA_RUNFILE:-"./config/nvidia/cuda.run"}

docker build -t ${REPO_PREFIX}/genui-base:${TAG} -f Dockerfile-base .
docker build --build-arg GENUI_DOCKER_IMAGE_PREFIX=${REPO_PREFIX} --build-arg GENUI_DOCKER_IMAGE_TAG=${TAG} --build-arg NVIDIA_CUDA_RUNFILE=${NVIDIA_CUDA_RUNFILE} -t ${REPO_PREFIX}/genui-base-cuda:${TAG} -f Dockerfile-base-cuda .
docker build --build-arg GENUI_DOCKER_IMAGE_PREFIX=${REPO_PREFIX} --build-arg GENUI_DOCKER_IMAGE_TAG=${TAG} -t ${REPO_PREFIX}/genui-main:${TAG} -f Dockerfile-main .
docker build --build-arg GENUI_DOCKER_IMAGE_PREFIX=${REPO_PREFIX} --build-arg GENUI_DOCKER_IMAGE_TAG=${TAG} -t ${REPO_PREFIX}/genui-worker:${TAG} -f Dockerfile-worker .
docker build --build-arg GENUI_DOCKER_IMAGE_PREFIX=${REPO_PREFIX} --build-arg GENUI_DOCKER_IMAGE_TAG=${TAG} -t ${REPO_PREFIX}/genui-gpuworker:${TAG} -f Dockerfile-gpuworker .