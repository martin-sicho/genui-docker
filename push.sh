#!/bin/bash

set -e

while getopts ":r:t:" opt; do
  case $opt in
    r) REPO="$OPTARG"
    ;;
    t) TAG="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

printf "Argument TAG is %s\n" "$TAG"
printf "Argument REPO is %s\n" "$REPO"
NVIDIA_CUDA_VERSION=${NVIDIA_CUDA_VERSION:-""}
if [ -z "$NVIDIA_CUDA_VERSION" ]
then
      echo "No CUDA version specified."
else
      printf "CUDA images will be tagged with CUDA version: %s\n" "$NVIDIA_CUDA_VERSION"
fi

echo "The following commands will be run:"
echo "$(NVIDIA_CUDA_VERSION=${NVIDIA_CUDA_VERSION} GENUI_DOCKER_IMAGE_PREFIX=${REPO} python3 get_tags.py $TAG $TAG)"

read -p "Do you want to proceed? Type YES to confirm: " userInput
if [[ $userInput != 'YES' ]] || [[ $userInput == '' ]]; then
   echo "Push cancelled by user."
   exit 1
else
   echo "OK"
   eval "$(NVIDIA_CUDA_VERSION=${NVIDIA_CUDA_VERSION} python3 get_tags.py $TAG $TAG)"
fi