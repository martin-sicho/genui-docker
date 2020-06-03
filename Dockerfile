FROM continuumio/miniconda:latest

ARG BASE_DIR="/genui/"
ARG BACKEND_REPO="./src/genui/"
ARG GUI_REPO="./src/genui-gui/"

# setup environment variables
ENV PYTHONUNBUFFERED 1
ENV DOCKER_CONTAINER 1

# setup dependencies
# wait-for-it: for the worker to wait until the backend is online
# authbind: to allow the app process to bind port 443 if run as nonroot
RUN apt-get update && apt-get install -y --no-install-recommends wait-for-it authbind
# initialize the conda environment (we have to use it to fetch rdkit since it is not on pip)
COPY ${BACKEND_REPO}/environment.yml ${BASE_DIR}/${BACKEND_REPO}/environment.yml
RUN conda install python=3.7 && conda env update -n base --file ${BASE_DIR}/${BACKEND_REPO}/environment.yml
# install the pip packages
COPY ${BACKEND_REPO}/requirements.txt ${BASE_DIR}/${BACKEND_REPO}/requirements.txt
RUN pip install -r ${BASE_DIR}/${BACKEND_REPO}/requirements.txt
# get the frontend app dependencies
COPY ${GUI_REPO}/package.json ${BASE_DIR}/${GUI_REPO}/package.json
RUN npm --prefix ${BASE_DIR}/${GUI_REPO} install ${BASE_DIR}/${GUI_REPO}

# copy over the sources
COPY ${BACKEND_REPO} ${BASE_DIR}/${BACKEND_REPO}
COPY ${GUI_REPO} ${BASE_DIR}/${GUI_REPO}

# copy the entrypoint script
COPY ./entrypoint.sh ${BASE_DIR}/entrypoint.sh

# set working directory to where the manage.py lives
WORKDIR ${BASE_DIR}/${BACKEND_REPO}/src/