#!/bin/bash

# get parameters
GPUS=$1
COMMAND=${2:-"up -d"}
PROJECT_NAME=${3:-"genui-docker"}

[ -z "$PROJECT_NAME" ] && echo "You must set a project name." && exit 1
[ -z "$GPUS" ] && echo "You must set at least one GPU." && exit 1
[ -z "$COMMAND" ] && echo "You must set compose command." && exit 1

# run the main application and the main worker
GENUI_CELERY_CONCURRENCY=0 \
GENUI_CELERY_QUEUES=celery \
eval "docker-compose \
  --project-name $PROJECT_NAME \
  -f docker-compose-main.yml \
  -f docker-compose-worker.yml \
  $COMMAND"

# run a worker container for each gpu in the list
# set comma as internal field separator for the string list
IFS=,
for gpu in $GPUS;
do
GENUI_CELERY_CONCURRENCY=1 \
GENUI_CELERY_QUEUES=gpu \
NVIDIA_VISIBLE_DEVICES=$gpu \
eval "docker-compose \
  --project-name "$PROJECT_NAME" \
  -f docker-compose-gpuworker.yml \
  $COMMAND"
done

