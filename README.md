# About

> See [Quick Start](#quick-start) if you want to deploy locally for quick testing.

The files in this repository are used to build and deploy the GenUI platform from Docker images. In total, five Docker images are defined for GenUI:
 
 1. *genui-base* -- A base image that contains all dependencies of the [Python backend](https://github.com/martin-sicho/genui). It is used to derive all the other images below. It should only be necessary to rebuild this image if the dependencies of the backend change.
 1. *genui-base-cuda* -- This base image is derived from *genui-base* and contains the CUDA Toolkit in addition to the standard backend libraries (see [The NVIDIA CUDA Base Image](#the-nvidia-cuda-base-image)). Like in the case of *genui-base*, this image does not have to be rebuilt if the dependencies of the backend application did not change.
 2. *genui-main* -- This image is derived from *genui-base* and adds [GenUI frontend GUI](https://github.com/martin-sicho/genui-gui) and also the source code for the Python backend. Therefore, this image contains the complete GenUI web application and its source code. It can be deployed as a service through the [`docker-compose-main.yml`](./docker-compose-main.yml) file, which also handles deployment of the PostgeSQL database and Redis message queue (see [Deployment Scenarios](#deployment-scenarios)).
 3. *genui-worker* -- Image based on *genui-base* intended to be deployed as a worker consuming Celery tasks submitted to the Redis message queue. The worker runs the same code as the backend of *genui-main* and multiple workers consuming different queues can be deployed. Currently, at least one worker node consuming tasks from the *celery* and *gpu* queue must be deployed in order for the main application to fully function. Workers are processes deployed either on the same host as the main application (see [Single Machine Deployment](#single-machine-deployment)) or in multiple copies spanning over an infrastructure of computers (see [Distributed Deployment](#distributed-deployment)).
 4. *genui-gpuworker* --  Image based on *genui-base-cuda* that can be configured to access one or more NVIDIA GPUs on the host system and should consume the tasks in the *gpu* queue.
 
# Setting up Your Host

There are a few things you have to do on your host before you deploy and your setup will probably vary based on your needs so we will only cover a simple deployment scenario on a single machine in this explanation. We will refer to the root of this code repository as `${REPO_ROOT}` throughout the readme and all commands shown are assumed to be run from the `${REPO_ROOT}` directory if not stated otherwise.

## Prerequisites

1. So far this app and its components are intended to be deployed on Linux hosts and deployments under Windows or Mac were not tested, but should be possible after some adjustments. Please, let us know your experience on the issue tracker.
2. You will need to install [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/). If you want to take advantage of NVIDIA GPUs installed on your system, you will also need to setup the `nvidia-container-runtime` on your host (see [Enabling GPUs in Docker](#enabling-gpus-in-docker) below).
3. If you want to deploy with HTTPS, you should point to the certificate and the associated key on the host filesystem with the `${GENUI_SSL_CERTFILE}` and `${GENUI_SSL_KEYFILE}` environment variables (see [Environment Variables Reference](#environment-variables-reference) for these and other configuration options)

For testing, you can easily generate a temporary unsigned certificate with `openssl`. For example, if you are deploying the application on your `localhost`, you could generate the key like this:

   ```bash
   # run in ${REPO_ROOT}
   mkdir config/nginx/certs
   openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out config/nginx/certs/localhost.crt -keyout config/nginx/certs/localhost.key 
   ```

Then you just point to the generated files via `${GENUI_SSL_CERTFILE}` and `${GENUI_SSL_KEYFILE}`.
   
### Enabling GPUs in Docker

If you have NVIDIA graphics cards, you can use the [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker) to build or deploy a worker image that will expose your GPUs to the processes inside the container. The first step is to install [nvidia-container-runtime](https://nvidia.github.io/nvidia-container-runtime/) on your host. In order to use the runtime from docker-compose, you will have to set it as the default runtime for the Docker daemon. Edit or create the `/etc/docker/daemon.json` on your system and add the following:

```json
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
```

You might have to restart the daemon in order for the settings to take effect:

```bash
sudo systemctl restart docker
sudo systemctl status -l docker # check if the service is running properly
```

Then you should be able to use the `genui-gpuworker` image without problems. You can pull our build from the Docker Hub or make your own (see [The `genui-gpuworker` Image](#the-gpu-worker-image) section below). 
 
# Quick Start

If you just want to quickly test the newest publicly available version of the app on your local machine, you can pull the latest docker images from Docker Hub:

```bash
docker pull sichom/genui-main
docker pull sichom/genui-worker
docker pull sichom/genui-gpuworker # needed only if you want to use GPUs
```

GenUI deployment with *docker-compose* is configured with environment variables that can be either specified on command line or in host environment or saved to a special file called `.env`. You can create this file inside the `${REPO_ROOT}` or edit the existing one that was created for the purpose of this quick start guide:

```bash
# ${REPO_ROOT}/.env
GENUI_PROTOCOL=http
GENUI_HOST=localhost
GENUI_PORT=8000
POSTGRES_PASSWORD=genui 
REDIS_PASSWORD=redis
GENUI_BACKEND_SECRET=some_django_secret_key
GENUI_CELERY_QUEUES=celery,gpu
GENUI_CELERY_CONCURRENCY=0
```

This configuration should now be picked up by *docker-compose* and the GenUI platform can be deployed as follows:

```bash
docker-compose -f docker-compose-main.yml -f docker-compose-worker.yml up
# docker-compose -f docker-compose-main.yml -f docker-compose-gpuworker.yml up # if you have an NVIDIA GPU
```

> The deployment process can take several minutes on some machines since the JavaScript frontend has to be rebuilt in case the backend host changes.

Once you see that the Celery workers have been started successfully, you should be able to access the GUI at `http://localhost:8000/app/` and see the REST API documentation at `http://localhost:8000/api/`. 

For more information on configurable deployment options, see the [Environment Variables Reference](#environment-variables-reference) at the end of this document. If you want to look into other deployment strategies, check the [Deployment Scenarios](#deployment-scenarios) section.

# Building Images from Source

If you want to build your own GenUI Docker images, you can check out the source code from the appropriate public Git repositories:

```bash
git submodule update --init --recursive
```

The submodules will be checked out to `${REPO_ROOT}/src/`. If you want, you can go to each module folder and check out the versions of the backend and frontend that you want. If you want to replace the source of the submodules with your own repositories, just provide the appropriate URLs in `${REPO_ROOT}/.gitmodules` before running the command above.

## The Base Image

Once you have the source code ready, you can build the GenUI base image:

```bash
docker build -t your_repo/genui-base:your_tag -f Dockerfile-base .
# for example: docker build -t sichom/genui-base:latest -f Dockerfile-base .
```

## The NVIDIA CUDA Base Image

This variant of the [base image](#the-base-image) is meant to be used for applications that require GPU support. In particular, workers that want to consume tasks submitted to the *gpu* queue and take advantage of GPU hardware will have to use this image. You can build images for any desired CUDA Toolkit version. You can [download](https://developer.nvidia.com/cuda-toolkit-archive) the CUDA installation runfile you want. You should get a runfile for Debian/Ubuntu since the GenUI images are all based on Debian and place it somewhere in the context of your build (`${REPO_ROOT}/config/nvidia`, for example). On Linux, you can easily download the runfile with `wget` like so:

```bash
mkdir -p config/nvidia
wget http://developer.download.nvidia.com/compute/cuda/10.2/Prod/local_installers/cuda_11.2.0_460.27.04_linux.run -P ./config/nvidia/
```

Once you have the runfile in place, you just need to specify the **NVIDIA_CUDA_RUNFILE** build argument and build the image: 

```bash
docker build --build-arg NVIDIA_CUDA_RUNFILE=path_to_your_runfile -t your_repo/genui-base-cuda:your_tag -f Dockerfile-base-cuda .
# for example: docker build --build-arg NVIDIA_CUDA_RUNFILE=./config/nvidia/cuda_11.2.0_460.27.04_linux.run -t sichom/genui-base-cuda:latest -f Dockerfile-base-cuda .
```

Note that both base images do not have to be rebuilt each time. They only need to be changed if the frontend or backend dependencies have been updated.

## The Main App Image

If you successfully built the `genui-base` image, you can build the 
main image that contains the frontend and backend source code:

```bash
docker build -t your_repo/genui-main:your_tag -f Dockerfile-main .
# for example: docker build -t sichom/genui-main:latest -f Dockerfile-main .
```

## The Worker Image

And the same follows for the worker image, which only contains the backend code:

```bash
docker build -t your_repo/genui-worker:your_tag -f Dockerfile-worker .
# for example: docker build -t sichom/genui-worker:latest -f Dockerfile-worker .
```

This image is meant for any tasks that do not require GPU acceleration. Such Celery tasks will be queued to the default *celery* queue by the backend service. You can configure the queues that the worker consumes during deployment with the **GENUI_CELERY_QUEUES** environment variable, which is a comma-separated list of queue names.

## The GPU Worker Image

If you want to use a worker with GPU support for the tasks submitted to the *gpu* queue, you build the image the same way, but using a different Dockerfile:

```bash
docker build -t your_repo/genui-gpuworker:your_tag -f Dockerfile-gpuworker .
# for example: docker build -t sichom/genui-gpuworker:latest -f Dockerfile-gpuworker .
```

# Deployment Scenarios

In this section, we will cover some common deployment scenarios. We already
covered the simplest case above (see [Quick Start](#quick-start)), but we will focus on more production-ready options here.

## Single Machine Deployment

If you are deploying on a single machine, the task is very simple 
with *docker-compose*. Here is a more involved production-ready example
with one basic worker and one GPU worker. We will use an environment 
file to store some default settings:

```bash
# ${REPO_ROOT}/.env
GENUI_USER=your_user
GENUI_USER_ID=your_user_id
GENUI_USER_GROUP=your_user_group
GENUI_USER_GROUP_ID=your_user_group_id
GENUI_PROTOCOL=https
GENUI_HOST=genui.eu
GENUI_PORT=443
GENUI_CELERY_QUEUES=celery,gpu
GENUI_CELERY_CONCURRENCY=0
DAJNGO_SETTINGS_MODULE=genui.settings.prod
GENUI_CONTAINER_PREFIX=genui-docker-prod-
GENUI_SSL_KEYFILE=/etc/letsencrypt/live/genui.eu/privkey.pem
GENUI_SSL_CERTFILE=/etc/letsencrypt/live/genui.eu/fullchain.pem
GENUI_DATA_MOUNT=/path/to/data/directory
```

The variables starting with **GENUI_USER_** indicate the user that the GenUI containers should run under.
By default all containers run as *root*, which is not always the safest option. Therefore,
with these settings you can specify the user you want to use instead of *root*. It should be a user that exists on your host as well. 

All media files generated by the application are saved to **GENUI_DATA_MOUNT** and are owned by **GENUI_USER**. You should back up the directory specified by **GENUI_DATA_MOUNT** regularly since it contains all application data. If you want to move
the application to a different host, you can just take this data and migrate it to the new machine with ease. 

If you are using HTTPS, do not forget to specify the paths to your certificate and key file. In this example (deployment to https://genui.eu/), we use keys from Let's Encrypt located on the host in `/etc/letsencrypt/live/genui.eu/privkey.pem` and `/etc/letsencrypt/live/genui.eu/fullchain.pem`.

After these preliminary settings are done, we can deploy the GenUI images:

```bash
POSTGRES_PASSWORD=some_secure_password \
REDIS_PASSWORD=some_secure_password \
GENUI_BACKEND_SECRET=some_secure_secret \
docker-compose -f docker-compose-main.yml -f docker-compose-worker.yml up
```

If you have a GPU installed on your system, you can spawn a GPU worker instead:

```bash
POSTGRES_PASSWORD=some_secure_password \
REDIS_PASSWORD=some_secure_password \
GENUI_BACKEND_SECRET=some_secure_secret \
NVIDIA_VISIBLE_DEVICES=0 \
docker-compose -f docker-compose-main.yml -f docker-compose-worker.yml up
```

This will expose the first GPU (**NVIDIA_VISIBLE_DEVICES** set to 0) to the worker container.

### The `up.sh` Utility

If you want to efficiently use multiple GPUs on your system, you can also take advantage of the `up.sh` utility script. This script will bring up the whole GenUI platform on the current host including any number of GPU workers. You can call it like so:

```bash
POSTGRES_PASSWORD=some_secure_password \
REDIS_PASSWORD=some_secure_password \
GENUI_BACKEND_SECRET=some_secure_secret \
./up.sh 0,1,2
```

This will bring up the whole platform and initialize one regular worker for the *celery* queue and three GPU workers for GPUs 0,1 and 2. The containers will run in detached mode, but you can see logs for any container using `docker logs`. For example:

```bash
docker logs genui-celery -f
```

will follow the logs generated by the default worker. You can see names of all running services with `docker ps` and use the name to follow their logs. 

You can stop all services by running the `up.sh` script again. You just need to pass the *stop* command this time:

```bash
./up.sh 0,1,2 stop
```

## Distributed Deployment

Another useful deployment scenario could be running the main GenUI application on one server (the *main node*), 
but distributing the tasks over multiple servers (*worker nodes*).

This setup assumes that both the *main node* and the *worker nodes* are sharing data in the `GENUI_DATA_MOUNT`. This directory must be readable and writable by containers running on all nodes. This can be for example an [NFS volume](https://wiki.archlinux.org/index.php/NFS) hosted on the *main node* and just mounted on the *worker nodes*.

Also note that in this setup Redis and PostgreSQL ports (`6379` and `5432`, respectively) will be exposed on the host of the *main node* so that workers have database and task queue access. So make sure that these services are not exposed to the internet or untrusted network by setting up your firewall properly.

### Setting up the Main Node

To bring up the *main node*, all you have to do is just add 
the `docker-compose-node-main.yml` into the mix:

```bash
# we assume the same variables are set in the '.env' file demonstrated above
POSTGRES_PASSWORD=some_secure_password \
REDIS_PASSWORD=some_secure_password \
GENUI_BACKEND_SECRET=some_secure_secret \
docker-compose -f docker-compose-main.yml -f docker-compose-node-main.yml up
```

This will setup the main web application and expose the required ports.

### Setting up a Worker Node

Setting up a *worker node* is not that different from the *main node*. All you need is to make sure that the `GENUI_DATA_MOUNT` is available and that the *worker node* host can connect to the *main node* host over the network. After that you can just initialize the worker 
by adding `docker-compose-node-worker.yml` file and specifying the correct hosts for the main node, PostgreSQL and Redis servers:

```bash
# we assume the same variables are set in the '.env' file demonstrated above
GENUI_MAIN_NODE_HOST=localhost \
REDIS_HOST=localhost \
POSTGRES_HOST=localhost \
POSTGRES_PASSWORD=some_secure_password \
REDIS_PASSWORD=some_secure_password \
GENUI_BACKEND_SECRET=some_secure_secret \
docker-compose -f docker-compose-gpuworker.yml -f docker-compose-node-gpuworker.yml up
# or: docker-compose -f docker-compose-worker.yml -f docker-compose-node-worker.yml up
```

## Environment Variables Reference

In order to customize the GenUI images for various deployment scenarios, a collection of environment variables is available:

- **DOCKER_NET_MTU** - Sets the [MTU](https://en.wikipedia.org/wiki/Maximum_transmission_unit) (Maximum Transmission Unit) for the docker network. On some hosts this value can be different than the docker default of 1500 so this option enables the user to choose the correct value for their system. For example, DOCKER_NET_MTU=1442 must be set so that the app works on the openstack cloud
- **NVIDIA_CUDA_RUNFILE** - Path to the CUDA Toolkit runfile that will be installed in the *genui-gpuworker* image.
- **NVIDIA_VISIBLE_DEVICES** - Integer ID of the GPU that should be exposed to the deployed *genui-gpuworker* image. You can display GPUs connected to your host system with `nvidia-smi -L`. If you have multiple GPUs, you should run one instance of *genui-gpuworker* per GPU.
- **GENUI_DOCKER_IMAGE_PREFIX** - The prefix to use for the docker image repository. Normally,
this would be your Docker Hub username.
- **DOCKER_IMAGE_TAG** - The tag of the GenUI docker image to be build or pull by `docker-compose`.
- **GENUI_CONTAINER_PREFIX** - Prefix for the running containers of this project. Defaults to `genui-docker-`
- **DOCKER_USER_CONFIG_MOUNT** - In order to seamlessly map GenUI application data to the host system, the container will require read-only access to the following files:
    - `/etc/group`
    - `/etc/passwd`
    -  `/etc/shadow`
    
   These are normally located in the `/etc/` directory on Linux hosts, which is the default value for this variable. However, in some cases or on other platforms you might want to set your own path.
- **POSTGRES_HOST** - The hostname of the machine/container running the postgres database.
- **POSTGRES_DB** - The name for the created PostgreSQL database.
- **POSTGRES_USER** - The name for the created PostgreSQL database user.
- **POSTGRES_PASSWORD** - The password used to login to the PostgreSQL database.
- **POSTGRES_RDKIT_RELEASE** - Desired image tag for [informaticsmatters/rdkit-cartridge-debian](https://hub.docker.com/r/informaticsmatters/rdkit-cartridge-debian/tags?page=1&ordering=last_updated). Should match the version used in the *genui-base* image.
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
- **GENUI_PROTOCOL** - The protocol used to access the GenUI application over the network. Set either to *http* or *https*.
- **GENUI_SSL_CERTFILE** - Path to the SSL certificate file on your host that you want to use for HTTPS.
- **GENUI_SSL_KEYFILE** - Path to the SSL key file on your host that you want to use for HTTPS.
- **GENUI_PORT** - The port used to access the GenUI application over the network. For normal access over https, this should be `443`.
- **GENUI_HOST** - Sets the GenUI web application hostname.
- **GENUI_MAIN_NODE_HOST** - Also indicates the hostname of the web application, but it only helps to inform remote worker nodes about the backend host so that they can probe its status and so on. Use **GENUI_HOST** to configure the main node.
- **GENUI_DATA_MOUNT** - The directory/mounted volume where data generated by the GenUI services will be placed. This does not include the database, which is stored in a dedicated docker volume.
- **GENUI_FRONTEND_APP_PATH** - URI path relative to**GENUI_HOST** where the application GUI should be found.
- **GENUI_CELERY_NAME** - If we are deploying a celery worker, this will be its name.
- **GENUI_CELERY_QUEUES** - If a worker is deployed, it will consume tasks from these queues. Use `,` as a separator (for example `celery,gpu`). *Note*: `celery` is the default queue into which all tasks are sent by default. `gpu` is the queue to store tasks meant to be run on a GPU rather than a CPU. 
- **GENUI_CELERY_CONCURRENCY** - Number of worker processes spawned by the Celery worker. Set to `0` to automatically set this to the number of available CPUs.
- **GENUI_CELERY_CONTAINER_SUFFIX** - Custom suffix for the Celery worker containers. Makes it possible to spawn multiple worker containers without using a Docker swarm if combined with the `--project-name` parameter of `docker-compose`. Defaults to and empty string.
- **DJANGO_SETTINGS_MODULE** - Set the Django settings module for the backend app.
    - `genui.settings.prod` for production
    - `genui.settings.stage` for staging (same as production, but with `DEBUG=True`)