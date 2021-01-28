#!/bin/bash

set -e

GENUI_DOCKER_IMAGE_PREFIX=${GENUI_DOCKER_IMAGE_PREFIX:-"sichom"}
TAG=${GENUI_DOCKER_IMAGE_TAG:-"latest"}

eval "$(python3 get_tags.py $TAG $TAG)"