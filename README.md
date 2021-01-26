# About

The files in this repository are used to build and deploy the GenUI platform using Docker images. In total, we define four Docker images for GenUI:
 
 1. *genui-base* -- A base image that contains the Python backend and all its dependencies. It is used to derive all the other images below. On its own this image can be used to deploy just the backend application without the frontend GUI. There is currently no Docker Compose file for this setup, but it could be achieved by simplification of [`docker-compose-main.yml`](./docker-compose-main.yml).
 2. *genui-main* -- This image is derived from *genui-base* and adds the GenUI frontend GUI. Therefore, this image contains the complete GenUI web application. It can be deployed as a service through the [`docker-compose-main.yml`](./docker-compose-main.yml) file, which also handles deployment of the PostgeSQL database and Redis message queue.
 3. *genui-worker* -- An image intended to be deployed as a worker consuming Celery tasks submitted to the Redis message queue. At least one worker node consuming tasks from all queues must be deployed in order for the application to function. Worker nodes can be deployed on the same host as the main application (see *[Single Machine Deployment](#Single Machine Deployment)*) or they can be setup in multiple copies spanning over an infrastructure of computers (see *[Distributed Deployment](#Distributed Deployment)*).
 4. *genui-gpuworker* --  An extended *genui-worker* image with access to one or more NVIDIA GPUs on the host system.
 
# Setting up Your Host

There are a few things you have to do on your host before you deploy. Your setup will probably vary based on your needs so we will only consider a simple deployment scenario. We will refer to the root of this code repository as `${REPO_ROOT}` in this readme and all commands are assumed to be run from the `${REPO_ROOT}` directory as well.

## Prerequisites

1. So far this app and its components are intended to be deployed on Linux hosts and deployments on Windows were not tested, but should be possible after some adjustments. Please, let us know your experience on the issue tracker.
2. You will need to install [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/). If you want to take advantage of NVIDIA GPUs installed on your system, you will also need to setup the `nvidia-container-runtime` on your host (see *[Enabling GPUs in Docker](#Enabling GPUs in Docker)* below).
3. If you want to deploy using an HTTPS certificate, you will have to place the certificate and the key in the `${REPO_ROOT}/config/nginx/certs/` directory. The names of the files should be consistent with the hostname on which you are deploying the *genui-main* services. For testing, you can easily generate a temporary unsigned certificate with `openssl`. For example, if you are deploying the application on your `localhost`, you would generate the key like this:

   ```bash
   # run in ${REPO_ROOT}
   mkdir config/nginx/certs
   openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out config/nginx/certs/localhost.crt -keyout config/nginx/certs/localhost.key 
   ```
   
### Enabling GPUs in Docker

If you have NVIDIA graphics cards, you can use the [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker) to build a worker image that will expose your GPUs to the processes inside the container. The first step is to install [nvidia-container-runtime](https://nvidia.github.io/nvidia-container-runtime/) on your host. In order to use the runtime from docker-compose, you will have to set it as the default runtime for the Docker daemon. Edit or create the `/etc/docker/daemon.json` on your system and add the following:

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

Then you should be able to use the `genui-gpuworker` image without problems. You can pull our build from the Docker Hub or make your own (see *[The `genui-gpuworker` Image](#The GPU Worker Image)* section below). 
 
# Quick Start

If you just want to quickly test the newest publicly available version of the app on your local machine, you can pull the latest docker images from Docker Hub:

```bash
docker pull sichom/genui-main:latest
docker pull sichom/genui-worker:latest
docker pull sichom/genui-gpuworker:latest
```

and setup all services to run locally:

```bash
GENUI_PROTOCOL=http \
GENUI_HOST=localhost \
GENUI_PORT=8000 \
POSTGRES_PASSWORD=genui \
REDIS_PASSWORD=redis \
GENUI_BACKEND_SECRET=`cat django_secret_example` \
GENUI_CELERY_QUEUES=celery,gpu \
GENUI_CELERY_CONCURRENCY=`nproc --all` \
docker-compose -f docker-compose-main.yml -f docker-compose-gpuworker.yml up
# docker-compose -f docker-compose-main.yml -f docker-compose-worker.yml up # if you do not have an NVIDIA GPU
```

You should now be able to access the GUI at `http://localhost:8080/app/` and see the API documentation at `http://localhost:8080/api/`. Check the *Environment Variables Reference* at the end of this document 
to learn about the settings we chose and other variables that can be set to configure your deployment.
Note that the variables defined in the `${REPO_ROOT}/.env` are automatically loaded by Docker Compose so you can save some common variables there and save yourself some space on the command line.

# Building Images from Source

If you want to build your own GenUI docker images, you can build them using the files in this repository. Make sure you have the source code for the submodules (the backend Python code and the frontend UI code) checked out by running the following in `${REPO_ROOT}`:

```bash
git submodule update --init --recursive
```

The submodules will be checked out to `${REPO_ROOT}/src/`. If you want, you can go to each module and check out the versions of the backend and GUI code that you want. If you want to replace these submodules with your own repositories, just replace the appropriate URLs in `${REPO_ROOT}/.gitmodules` before running the command above.

## The Base Image

Once you have the source code ready, you can build the GenUI base image:

```bash
docker build -t your_repo/genui-base:your_tag -f Dockerfile-base .
# for example: docker build -t sichom/genui-base:latest -f Dockerfile-base .
```

## The Main Image

If you successfully built the `genui-base` image, you can just build the 
main image the same way:

```bash
docker build -t your_repo/genui-main:your_tag -f Dockerfile-main .
# for example: docker build -t sichom/genui-main:latest -f Dockerfile-main .
```

## The Worker Image

And the same follows for the worker image:

```bash
docker build -t your_repo/genui-worker:your_tag -f Dockerfile-worker .
# for example: docker build -t sichom/genui-worker:latest -f Dockerfile-worker .
```

This image is meant for any tasks that do not require GPU acceleration. Such Celery
tasks should be queued to the default *celery* queue by the backend service. You can configure the queues that the worker consumes during deployment with the **GENUI_CELERY_QUEUES** environment, which is a comma-separated list of queue names.

### The GPU Worker Image

If you want the tasks submitted to the *gpu* queue to take advantage of GPUs on your system, you will need this image. You can build this image with a given CUDA Toolkit version. You can [download](https://developer.nvidia.com/cuda-toolkit-archive) the desired CUDA installation runfile and place it in `${REPO_ROOT}/config/nvidia`, for example. You should download a runfile for Debian/Ubuntu since the GenUI images are all based on Debian. On Linux, you can download the runfile with `wget` like so:

```bash
mkdir -p config/nvidia
wget http://developer.download.nvidia.com/compute/cuda/10.2/Prod/local_installers/cuda_11.2.0_460.27.04_linux.run -P ./config/nvidia/
```

Then you can set the **NVIDIA_CUDA_RUNFILE** environment variable to the path of the runfile and build your `genui-gpuworker`:

```bash
docker build --build-arg NVIDIA_CUDA_RUNFILE=path_to_your_runfile -t your_repo/genui-gpuworker:your_tag -f Dockerfile-gpuworker .
# for example: docker build --build-arg NVIDIA_CUDA_RUNFILE=./config/nvidia/cuda_11.2.0_460.27.04_linux.run -t sichom/genui-gpuworker:latest -f Dockerfile-gpuworker .
```

# Deployment Scenarios

In this section, we will cover some common deployment scenarios. We already
covered the simplest case above, but we will focus on more production-ready options here.

## Single Machine Deployment

If you are deploying on a single machine, the task is very simple 
with Docker Compose. Here is a more involved production-ready example
with one basic worker and one GPU worker. We will use an environment 
file for this one because we will reuse some variables for different calls
to Docker Compose:

```bash
# ${REPO_ROOT}/.env
GENUI_USER=your_user
GENUI_USER_ID=your_user_id
GENUI_USER_GROUP=your_user_group
GENUI_USER_GROUP_ID=your_user_group_id
GENUI_PROTOCOL=https
GENUI_HOST=your_host
GENUI_PORT=443
GENUI_DATA_MOUNT=/path/to/data/directory
```

The **GENUI_USER_*** variables indicate under which user the GenUI containers should run.
By default all containers run as *root*, which is not always the safest option. Therefore,
with these settings you can specify the user you want to use instead of *root*. It should be a user that exists on your host as well. All media files generated by the application in **GENUI_DATA_MOUNT** are owned by this user. You should back up the directory specified by **GENUI_DATA_MOUNT** regularly since it contains all application data. If you want to move
the application to a different host, you can just take this data and migrate it to the new machine.

Now we can finally bring up the main service and also the default worker with Docker Compose:

```bash
POSTGRES_PASSWORD=some_secure_password \
REDIS_PASSWORD=some_secure_password \
GENUI_BACKEND_SECRET=some_secure_secret \
GENUI_CELERY_QUEUES=celery \
GENUI_CELERY_CONCURRENCY=0 \
docker-compose -f docker-compose-main.yml -f docker-compose-worker.yml up
```

The **GENUI_CELERY_CONCURRENCY** variable defines how many tasks the worker should process in parallel.
The value of 0 means that all available CPU cores will be used.
If you do not have a GPU, just set **GENUI_CELERY_QUEUES** to `celery,gpu`
so that the worker also consumes the GPU tasks. If you have a GPU 
installed on your system, you can spawn the GPU worker service to handle GPU accelerated 
tasks like so:

```bash
POSTGRES_PASSWORD=some_secure_password \
REDIS_PASSWORD=some_secure_password \
GENUI_BACKEND_SECRET=some_secure_secret \
GENUI_CELERY_QUEUES=gpu \
GENUI_CELERY_CONCURRENCY=1 \
NVIDIA_VISIBLE_DEVICES=0 \
docker-compose -f docker-compose-gpuworker.yml up
```

This will expose the first GPU (**NVIDIA_VISIBLE_DEVICES** set to 0) to the worker container, which will only let one task to execute on the GPU at one time (**GENUI_CELERY_CONCURRENCY** set to 1). If you want to make use of more GPUs on your system, you can spawn one such container per GPU.

### The `up.sh` Utility

If you want, you can also take advantage of the `up.sh` utility script. This script will bring up the whole GenUI platform on the current host including any number of GPU workers. You can call it like so:

```bash
POSTGRES_PASSWORD=some_secure_password \
REDIS_PASSWORD=some_secure_password \
GENUI_BACKEND_SECRET=some_secure_secret \
./up.sh 0,1,2
```

This will bring up the whole platform and initialize GPU workers for GPUs 0,1 and 2. The containers will run in detached mode, but you can see logs for any container using `docker logs`. For example:

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

- **DOCKER_NET_MTU** - Sets the [MTU](https://en.wikipedia.org/wiki/Maximum_transmission_unit) (Maximum Transmission Unit) for the docker network. On some hosts this value can be different than the docker default of 1500 so this option enables the user to choose the correct value for their system.
- **NVIDIA_CUDA_RUNFILE** - Path to the CUDA Toolkit runfile that will be installed in the *genui-gpuworker* image.
- **NVIDIA_VISIBLE_DEVICES** - Integer ID of the GPU that should be exposed to the deployed *genui-gpuworker* image. You can display GPUs connected to your host system with `nvidia-smi -L`. If you have multiple GPUs, you should run one instance of *genui-gpuworker* per GPU.
- **GENUI_DOCKER_IMAGE_PREFIX** - The prefix to use for the docker image repository. Normally,
this would be your Docker Hub username.
- **DOCKER_IMAGE_TAG** - The tag of the GenUI docker image to be build or pull by `docker-compose`.
- **DOCKER_USER_CONFIG_MOUNT** - In order to seamlessly map GenUI application data to the host system, the container will require read-only access to the following files:
    - `/etc/group`
    - `/etc/passwd`
    -  `/etc/shadow`
    
   These are normally located in the `/etc/` directory on Linux hosts, which is the default value for this variable. However, in some cases or on other platforms you might want to set your own path.
- **POSTGRES_HOST** - The hostname of the machine/container running the postgres database.
- **POSTGRES_DB** - The name for the created PostgreSQL database.
- **POSTGRES_USER** - The name for the created PostgreSQL database user.
- **POSTGRES_PASSWORD** - The password used to login to the PostgreSQL database.
- **POSTGRES_RDKIT_RELEASE** - Desired image tag for [*informaticsmatters/rdkit-cartridge-debian*](https://hub.docker.com/r/informaticsmatters/rdkit-cartridge-debian/tags?page=1&ordering=last_updated). Should match the version used in the *genui-base* image.
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
- **GENUI_PORT** - The port used to access the GenUI application over the network. For normal access over https, this should be `443`.
- **GENUI_HOST** - Sets the GenUI web application hostname.
- **GENUI_MAIN_NODE_HOST** - Also indicates the hostname of the web application, but it only helps to inform remote worker nodes about the backend host so that they can probe its status and so on. Use **GENUI_HOST** to configure the main node.
- **GENUI_DATA_MOUNT** - The directory/mounted volume where data generated by the GenUI services will be placed. This does not include the database, which is stored in a dedicated docker volume.
- **GENUI_FRONTEND_APP_PATH** - URI path relative to**GENUI_HOST** where the application GUI should be found.
- **GENUI_CELERY_NAME** - If we are deploying a celery worker, this will be its name.
- **GENUI_CELERY_QUEUES** - If a worker is deployed, it will consume tasks from these queues. Use `,` as a separator (for example `celery,gpu`). *Note*: `celery` is the default queue into which all tasks are sent by default. `gpu` is the queue to store tasks meant to be run on a GPU rather than a CPU. 
- **GENUI_CELERY_CONCURRENCY** - Number of worker processes spawned by the Celery worker. Set to `0` to automatically set this to the number of available CPUs.
- **DJANGO_SETTINGS_MODULE** - Set the Django settings module for the backend app.
    - `genui.settings.prod` for production
    - `genui.settings.stage` for staging (same as production, but with `DEBUG=True`)