FROM continuumio/miniconda:latest

ARG ROOT_DIR=/genui
ARG BACKEND_DIR=./src/genui
ARG FRONTEND_DIR=./src/genui-gui
ARG DATA_DIR=./data

# setup environment variables
ENV GENUI_ROOT_DIR=${ROOT_DIR}
ENV GENUI_BACKEND_DIR=${ROOT_DIR}/${BACKEND_DIR}
ENV GENUI_FRONTEND_DIR=${ROOT_DIR}/${FRONTEND_DIR}
ENV GENUI_DATA_DIR=${ROOT_DIR}/${DATA_DIR}
ENV PYTHONUNBUFFERED 1
ENV DOCKER_CONTAINER 1

# setup dependencies
# wait-for-it: for the worker to wait until the backend is online
# authbind: to allow the app process to bind port 443 if run as nonroot
RUN apt-get update && apt-get install -y --no-install-recommends wait-for-it authbind
# initialize the conda environment (we have to use it to fetch rdkit since it is not on pip)
COPY ${BACKEND_DIR}/environment.yml ${GENUI_BACKEND_DIR}/environment.yml
RUN conda install python=3.7 && conda env update -n base --file ${GENUI_BACKEND_DIR}/environment.yml
# install the pip packages
COPY ${BACKEND_DIR}/requirements.txt ${GENUI_BACKEND_DIR}/requirements.txt
RUN pip install -r ${GENUI_BACKEND_DIR}/requirements.txt
# get the frontend app dependencies
COPY ${FRONTEND_DIR}/package.json ${GENUI_FRONTEND_DIR}/package.json
RUN npm --prefix ${GENUI_FRONTEND_DIR} install ${GENUI_FRONTEND_DIR}

# copy over the sources
COPY ${BACKEND_DIR} ${GENUI_BACKEND_DIR}
COPY ${FRONTEND_DIR} ${GENUI_FRONTEND_DIR}

# copy the entrypoint script
COPY ./entrypoint.sh ${GENUI_ROOT_DIR}/entrypoint.sh

# set working directory to where the manage.py lives
WORKDIR ${GENUI_BACKEND_DIR}/src/