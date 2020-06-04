# About

This is a repository to build and deploy the GenUI application Docker image. At the moment the application is contained in a single docker image which can be either deployed on a single machine (see *Single Machine Build and Deployment*) or span over an infrastructure of computers (see *Distributed Setup*).

## Prerequisites

TODO

## Quick Start

TODO

## Single Machine Build and Deployment

This section describes how you build the GenUI application image and deploy it on a single machine along with a worker consuming task queues. If you are interested in a distributed setup (with workers residing on different machines), see the *Distributed Setup* section below. 

### Production Image

Edit the `prod.env` file accordingly or set the required environment variables. This file is intentionally left incomplete so you can easily identify and fill in the required information. You can see the list of available options and their meaning below (see `Environment Variables Reference`). When done link this file as the current environment definition. You can use the `set_env.sh` script for that:

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

Also note that in this setup Redis (6379) and PostgreSQL (5432) ports will be exposed on the host of the *main node* so that workers can connect. So make sure that these ports can only be accessed on the local network and not exposed to the internet.

### Setting up the Main Node

Provided that you have already built or pulled the desired GenUI Docker image that you want to deploy (see *Quick Start*), you can run `docker-compose` to setup the *main node* like so:

```bash
./set_env.sh prod.env
docker-compose -f docker-compose.yml -f docker-compose-node-main.yml up
```

This will setup the web application, but no workers. Instead, we expose the required ports on the host so that workers on the network can connect to the running database and task queue containers.

### Setting up a Worker Node

Setting up a *worker node* is not that different from the *main node*. All you need is to make sure that the `GENUI_DATA_MOUNT` is available and that the *worker node* host can connect to the *main node* host over the network. After that running the following should set things up:

```bash
./set_env.sh prod-worker.env
docker-compose -f docker-compose-worker.yml -f docker-compose-node-worker.yml up
```

Note that it is not mandatory to use docker images to set up workers, especially since setting up [nvidia-docker](https://github.com/NVIDIA/nvidia-docker) to expose GPU devices to the container might not be worth it if you only have one or two GPU equipped nodes. Especially since [native GPU support has not landed in docker-compose yet](https://github.com/docker/compose/issues/6691). 

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

# proceed to the run directory and run your worker
cd src
celery worker -c ${GENUI_CELERY_CONCURRENCY} -Q ${GENUI_CELERY_QUEUES} -E -A genui --loglevel=info --hostname ${GENUI_CELERY_NAME}@%h
```

If you want to run this sensibly in production, you will probably want to consider [daemonization](https://docs.celeryproject.org/en/stable/userguide/daemonizing.html) of this service as well.

## Environment Variables Reference

TODO