# About

TODO

## Quick Start

TODO

## Single Machine Build and Deployment

This is how you build the GenUI application image and deploy it on a single machine along with a worker consuming all task queues. If you are interested in a distributed setup (with workers residing on different machines), see the *Distributed Setup* section below. 

### Production Image

Edit the `prod.env` file accordingly or set the required environment variables. Then link this file as the current environment definition. You can use the `set_env.sh` script for that:

```bash
./set_env.sh prod.env
```

Finally, checkout current backend and frontend source code:

```bash
git clone git@github.com:martin-sicho/genui.git src/genui
git clone git@github.com:martin-sicho/genui-gui.git src/genui-gui
```

Now run `docker-compose` to build and deploy the main application:

```bash
docker-compose up # do not forget the --build flag if you want to rebuild an existing image
```

If you just want to build the GenUI app image to deploy and configure later, you can do:

```bash
docker-compose build genui
```

This image can be shared between various machines and customized to either serve as a worker or the main server. See the *Distributed Setup* section for details.

### Development Image

If you want to build a development image with debug options (to use in staging environment, for example), make sure to edit the `debug.env` file accordingly and link it with `set_env.sh`:

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
docker-compose up # do not forget the --build flag if you want to rebuild an existing image
```

## Distributed Build and Deployment

TODO