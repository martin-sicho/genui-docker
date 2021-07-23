#!/usr/bin/env bash

set -e

GENUI_FRONTEND_ROOT=${GENUI_FRONTEND_DIR}
GENUI_MEDIA_ROOT="${GENUI_DATA_DIR}/files/media/"


GENUI_FRONTEND_INFO_DIR=${GENUI_FRONTEND_ROOT}/build/info/
mkdir -p ${GENUI_FRONTEND_INFO_DIR}
echo "{\"url\": \"${GENUI_BACKEND_PROTOCOL}://${GENUI_BACKEND_HOST}:${GENUI_BACKEND_PORT}\"}" > ${GENUI_FRONTEND_INFO_DIR}/backend/host.json
cp -r ${GENUI_FRONTEND_ROOT}/build/. /genui/frontend/

# migrate the database and set everything up
python manage.py migrate --noinput
python manage.py genuisetup
python manage.py collectstatic --no-input

# ensure that only the genui user group has access to media files
mkdir -p ${GENUI_MEDIA_ROOT}
chgrp -R ${GENUI_USER_GROUP} ${GENUI_MEDIA_ROOT}
chmod g+rwxs,a+xs ${GENUI_MEDIA_ROOT} # TODO: all media directories and created files can be listed and read by default -> the application itself needs to take care of revoking the rights to files (this should be noted in the documentation)
umask 002

# we disable listing of models and compounds media directories by default
mkdir -p "${GENUI_MEDIA_ROOT}models"
mkdir -p "${GENUI_MEDIA_ROOT}compounds"
find "${GENUI_MEDIA_ROOT}models" -type d -exec chmod o-r {} +
find "${GENUI_MEDIA_ROOT}compounds" -type d -exec chmod o-r {} +

# use authbind to allow the genui user group to bind the 443 port
touch /etc/authbind/byport/443
chgrp ${GENUI_USER_GROUP} /etc/authbind/byport/443
chmod g+rwx /etc/authbind/byport/443

# make sure the genui user has a home directory in the container and has the required permissions
mkdir -p /home/${GENUI_USER}
chgrp -R ${GENUI_USER_GROUP} /home/${GENUI_USER}
chown -R ${GENUI_USER} /home/${GENUI_USER}
chmod 770 /home/${GENUI_USER}

# run the server (use certificate files in the default location if using https)
export CERTFILES=$(if [[ "${GENUI_BACKEND_PROTOCOL}" == "https" ]]; then echo "--certfile=/etc/certs/${GENUI_BACKEND_HOST}.crt --keyfile=/etc/certs/${GENUI_BACKEND_HOST}.key" ; fi)
if [[ "${GENUI_BACKEND_PROTOCOL}" == "https" ]]; then echo "Found SSL certfiles: ${CERTFILES}" ; fi
echo "Binding backend application to port ${GENUI_BACKEND_PORT} using ${GENUI_BACKEND_PROTOCOL}..."

# comment this out, if you want to pass another command
exec runuser -u  ${GENUI_USER} -- authbind --deep -- gunicorn --timeout 180 --limit-request-line 0 --graceful-timeout 120 ${CERTFILES} genui.wsgi:application --bind 0.0.0.0:${GENUI_BACKEND_PORT}

# execute the container command as the genui user
# uncomment if you want to run the server using the command directive in the docker-compose
#exec runuser -u  ${GENUI_USER} -- "$@"