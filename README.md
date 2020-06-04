# About

The code in this repository is used to build and deploy the GenUI application Docker image. This image can be deployed as either the web application or a worker using one copy on one host (see *Single Machine Build and Deployment*) or in multiple copies spanning over an infrastructure of computers (see *Distributed Build and Deployment*).

# Installation

This installation guide is meant to be a brief overview of two common deployment scenarios for the GenUI application. You will probably have to modify the files in this repository to suit your needs, but it should be enough to give you a general idea of where to start.

## Prerequisites

1. You will need to install [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/). However, as you will see below, using docker is not required on all instances.
2. So far this app and its components is intended to be deployed in Linux environments.
3. You will need a valid SSL certificate and key placed in the `config/nginx/certs/` directory. They should be named after the host on which you are deploying the application. You can easily generate a temporary unsigned certificate with `openssl`:

    ```bash
    openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out config/nginx/certs/localhost.crt -keyout config/nginx/certs/localhost.key 
   ```

## Quick Start

If you just want to quickly test the latest version of the app on your local machine, you can pull the latest docker image from Docker Hub:

```bash
docker pull sichom/genui:latest # or sichom/genui:dev for the latest development snapshot
```

After that you should be able to setup all services locally:

```bash
# set all environment variables to reasonable defaults to host locally
./set_env.sh quickstart.env

# map the current host user as the genui user inside the container
export GENUI_USER="$(id -un)"
export GENUI_USER_GROUP="$(id -gn)"
export GENUI_USER_ID="$(id -u)"
export GENUI_USER_GROUP_ID="$(id -g)"

# deploy the services
docker-compose -f docker-compose.yml -f docker-compose-worker.yml up
```

You should now be able to access the GUI at https://localhost/. Note that by default the docker container does not have access to specialized hardware such as GPUs on the system. If you want to take advantage of this hardware, you will either have to expose it to the docker container with [nvidia-docker](https://github.com/NVIDIA/nvidia-docker) or avoid using a docker container altogether (see *Distributed Build and Deployment*).

The `quickstart.env` contains some variables that need to be specified for deployment. If you want to expose the service to the outside world or otherwise customize the deployment, read the *Environment Variables Reference*.

## Single Machine Build and Deployment

This section describes how to build the GenUI application image from source and deploy it on a single machine along with a worker consuming task queues. If you are interested in a distributed setup (with workers residing on different machines), see the *Distributed Build and Deployment* section below. 

### Production Image

Edit the `prod.env` file accordingly or set the required environment variables. This file is intentionally left incomplete so you can easily identify and fill in the required information. You can see the list of available options and their meaning below (see *Environment Variables Reference*). When done link this file as the current environment definition. You can use the `set_env.sh` script for that:

```bash
./set_env.sh prod.env
```

Then checkout current backend and frontend source code:

```bash
git clone git@github.com:martin-sicho/genui.git src/genui
git clone git@github.com:martin-sicho/genui-gui.git src/genui-gui
```

Finally, run `docker-compose` to build and deploy the application:

```bash
docker-compose -f docker-compose.yml -f docker-compose-worker.yml up
```

This will setup the GenUI web application on the current machine as a host and will expose ports 80 and 443 to enable access via web browser with https. The address is defined using the information in the `prod.env` file (`${GENUI_BACKEND_PROTOCOL}://${GENUI_BACKEND_HOST}:${GENUI_BACKEND_PORT}`).

Along with the web application we also deploy a worker to consume the user submitted tasks (make sure to include both `celery` and `gpu` queues in the `GENUI_CELERY_QUEUES` variable). The worker is defined in the `docker-compose-worker.yml` file and also uses the `prod.env` file for its setup.

Do not forget the `--build` flag if you want to rebuild existing images and `--detach` to run in the background see `docker-compose up -h` for details.

### Development Image

If you want to build a development image with debug options (to use in staging environment, for example), you can edit and link the `debug.env` file:

```bash
./set_env.sh debug.env
```

Then checkout the required development branches of the backend and frontend:

```bash
git clone git@github.com:martin-sicho/genui.git src/genui --branch dev/master
git clone git@github.com:martin-sicho/genui-gui.git src/genui-gui --branch dev/master
```

Now build and deploy it just like you would in production:

```bash
docker-compose -f docker-compose.yml -f docker-compose-worker.yml up
```

This is useful when you just want to test the newest features locally and have debug outputs available.

## Distributed Build and Deployment

If you want to deploy GenUI to a larger infrastructure, it is possible to host the web application on one server (the *main node*) with multiple remote *worker nodes* connected to it over the network.

This setup assumes that both the *main node* and the *worker nodes* are sharing data in the `GENUI_DATA_MOUNT`. This directory must be readable and writable by containers running on all nodes. This can be for example an [NFS volume](https://wiki.archlinux.org/index.php/NFS) hosted on the *main node* and mounted on the *worker nodes*.

Also note that in this setup Redis (6379) and PostgreSQL (5432) ports will be exposed on the host of the *main node* so that workers can connect. So make sure that these ports can only be accessed on the local network and are not exposed to the internet.

### Setting up the Main Node

Provided that you have already built or pulled the desired GenUI Docker image (see *Quick Start*), you can run `docker-compose` to setup the *main node* like so:

```bash
./set_env.sh prod.env
docker-compose -f docker-compose.yml -f docker-compose-node-main.yml up
```

This will setup the web application, but no workers. Instead, the required ports are exposed on the host so that workers on the network can connect to the running database and task queue containers.

### Setting up a Worker Node

Setting up a *worker node* is not that different from the *main node*. All you need is to make sure that the `GENUI_DATA_MOUNT` is available and that the *worker node* host can connect to the *main node* host over the network. After that running the following should set things up:

```bash
./set_env.sh prod-worker.env
docker-compose -f docker-compose-worker.yml -f docker-compose-node-worker.yml up
```

Note that it is not mandatory to use docker images to set up workers, especially since setting up [nvidia-docker](https://github.com/NVIDIA/nvidia-docker) to expose GPU devices to the container might not be worth it if you only have one or two GPU equipped nodes and since [native GPU support has not landed in docker-compose yet](https://github.com/docker/compose/issues/6691). 

You can use the following script as a general guide to start the worker natively on the target system (make sure you do this as `GENUI_USER`):

```bash
# we only need the backend code for this
git clone git@github.com:martin-sicho/genui.git src/genui

# set the environment variables in your shell
set -a
source prod-worker.env

# go to the backend repo
cd src/genui/

# link the shared GENUI_DATA_MOUNT directory
ln -s ../../data files

# install dependencies (this assumes you have anaconda or miniconda installed and available in your PATH)
conda create -n genui -f environment.yml
conda activate genui
pip install -r requirements.txt

# proceed to the main directory and run your worker
cd src
celery worker -c ${GENUI_CELERY_CONCURRENCY} -Q ${GENUI_CELERY_QUEUES} -E -A genui --loglevel=info --hostname ${GENUI_CELERY_NAME}@%h
```

If you want to run this in production, you might want to consider [daemonization](https://docs.celeryproject.org/en/stable/userguide/daemonizing.html) of this service.

## Environment Variables Reference

In order to customize the GenUI image for deployment on different hosts and on different system, a selection of environment variables is available:

- **DOCKER_NET_MTU** - Sets the [MTU](https://en.wikipedia.org/wiki/Maximum_transmission_unit) (Maximum Transmission Unit) for the docker network. On some hosts this value can be different than the docker default of 1500 so this option enables the user to choose the correct value for their system.
- **DOCKER_IMAGE_TAG** - The tag of the GenUI docker image to be build or pulled by `docker-compose`.
- **DOCKER_USER_CONFIG_MOUNT** - In order to seamlessly map GenUI application data to the host system, the container will require sharing of the following files:
    - `/etc/group`
    - `/etc/passwd`
    -  `/etc/shadow`
    
   These are normally located in the `/etc/` directory on the host system. However, this variables allows specification of a different directory.
- **POSTGRES_HOST** - The hostname of the machine/container running the postgres database.
- **POSTGRES_DB** - The name for the created PostgreSQL database.
- **POSTGRES_USER** - The name for the created PostgreSQL database user.
- **POSTGRES_PASSWORD** - The password used to login to the PostgreSQL database.
- **REDIS_HOST** - The hostname of the machine/container running the redis task queue.
- **REDIS_PASSWORD** - Password used by workers to access Redis data.
- **GENUI_USER** - Username of the user on the host, which will be mapped to the container. The docker run command is executed by this user inside containers.
- **GENUI_USER_ID** - Numerical ID of the mapped user.
- **GENUI_USER_GROUP** - The effective group name for the mapped user. Usually is the same as the username on most systems.
- **GENUI_USER_GROUP_ID** - Numerical ID of the effective group for the mapped user. Usually is the same as the numerical user ID.
- **GENUI_BACKEND_SECRET** - A secret key for the backend Django application. 
    - It can be generated in python like so: 
      ```python
      from django.core.management.utils import get_random_secret_key
      print(get_random_secret_key())
      ```
- **GENUI_BACKEND_PROTOCOL** - The protocol used to access the GenUI application over the network. This should always be set to `https`.
- **GENUI_BACKEND_PORT** - The port used to access the GenUI application over the network. For normal access over https, this should be `443`.
- **GENUI_BACKEND_HOST** - Hostname of the GenUI application host.
- **GENUI_DATA_MOUNT** - The directory/mounted volume where data generated by the GenUI services will be placed. This does not include the database, which is stored in a dedicated docker volume.
- **GENUI_FRONTEND_APP_PATH** - URI path relative to**GENUI_BACKEND_HOST** where the application GUI should be found.
- **GENUI_CELERY_NAME** - If we are deploying a celery worker, this will be its name.
- **GENUI_CELERY_QUEUES** - If a worker is deployed, it will consume tasks from these queues. Use `,` as a separator (for example `celery,gpu`). *Note*: `celery` is the default queue into which all tasks are sent by default. `gpu` is the queue to store tasks meant to be run on a GPU rather than a CPU. 
- **GENUI_CELERY_CONCURRENCY** - Number of worker processes spawned by the worker. Set to `0` to automatically use the number of available CPUs.
- **DJANGO_SETTINGS_MODULE** - Set the Django settings module for the backend app.
    - `genui.settings.prod` for production
    - `genui.settings.stage` for staging (same as production, but with `DEBUG=True`)