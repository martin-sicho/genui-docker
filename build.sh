#!/bin/bash

set -e

while getopts ":r:t:c:" opt; do
  case $opt in
    r) REPO="$OPTARG"
    ;;
    t) TAG="$OPTARG"
    ;;
    c) CUDA_RUNFILE="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

REPO_PREFIX=${REPO:-"sichom"}
TAG=${TAG:-"latest"}
CUDA_RUNFILE=${CUDA_RUNFILE:-""}

printf "TAG is %s\n" "$TAG"
printf "REPO is %s\n" "$REPO"
if [ -z "$CUDA_RUNFILE" ]
then
      echo "No CUDA runfile specified. GPU images will not be built."
else
      printf "CUDA images will be built with the following CUDA runfile: %s\n" "$CUDA_RUNFILE"
fi

read -p "Do you want to proceed? Type YES to confirm: " userInput
if [[ $userInput != 'YES' ]] || [[ $userInput == '' ]]; then
   echo "Build cancelled by user."
   exit 1
else
   echo "Building images..."
fi

docker build -t ${REPO_PREFIX}/genui-base:${TAG} -f Dockerfile-base .
docker build --build-arg GENUI_DOCKER_IMAGE_PREFIX=${REPO_PREFIX} --build-arg GENUI_DOCKER_IMAGE_TAG=${TAG} -t ${REPO_PREFIX}/genui-main:${TAG} -f Dockerfile-main .
docker build --build-arg GENUI_DOCKER_IMAGE_PREFIX=${REPO_PREFIX} --build-arg GENUI_DOCKER_IMAGE_TAG=${TAG} -t ${REPO_PREFIX}/genui-worker:${TAG} -f Dockerfile-worker .

if [ -z "$CUDA_RUNFILE" ]
then
      echo "No CUDA runfile specified. GPU images were not built."
      exit 1
else
      printf "Building CUDA images with the following CUDA runfile: %s\n" "$CUDA_RUNFILE"
      docker build --build-arg GENUI_DOCKER_IMAGE_PREFIX=${REPO_PREFIX} --build-arg GENUI_DOCKER_IMAGE_TAG=${TAG} --build-arg NVIDIA_CUDA_RUNFILE=${CUDA_RUNFILE} -t ${REPO_PREFIX}/genui-base-cuda:${TAG} -f Dockerfile-base-cuda .
      docker build --build-arg GENUI_DOCKER_IMAGE_PREFIX=${REPO_PREFIX} --build-arg GENUI_DOCKER_IMAGE_TAG=${TAG} -t ${REPO_PREFIX}/genui-gpuworker:${TAG} -f Dockerfile-gpuworker .
fi