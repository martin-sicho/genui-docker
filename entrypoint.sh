#!/usr/bin/env bash

set -e

GENUI_FRONTEND_ROOT="/genui/src/genui-gui/"
GENUI_MEDIA_ROOT="/genui/src/genui/files/media/"

# compile the frontend app
npm run-script build --prefix ${GENUI_FRONTEND_ROOT}

# migrate the database and set everything up
python manage.py migrate --noinput
python manage.py genuisetup
python manage.py collectstatic --no-input

# ensure that only the genui user group has access to media files
mkdir -p ${GENUI_MEDIA_ROOT}
chgrp -R ${GENUI_USER_GROUP} ${GENUI_MEDIA_ROOT}
chmod g+rwxs,a+xs ${GENUI_MEDIA_ROOT} # FIXME: here we allow all users to list directories and read the media files by default -> this could be a possible security concern for some sensitive files
umask 002

# disable listing of models and compounds media files
mkdir -p "${GENUI_MEDIA_ROOT}models"
mkdir -p "${GENUI_MEDIA_ROOT}compounds"
chmod o-r "${GENUI_MEDIA_ROOT}models"
chmod o-r "${GENUI_MEDIA_ROOT}compounds"

# use authbind to allow the genui user group to bind the 443 port
touch /etc/authbind/byport/443
chgrp ${GENUI_USER_GROUP} /etc/authbind/byport/443
chmod g+rwx /etc/authbind/byport/443

# make sure the user has a home directory in the container and has the required permissions
mkdir -p /home/${GENUI_USER}
chgrp -R ${GENUI_USER_GROUP} /home/${GENUI_USER}
chown -R ${GENUI_USER} /home/${GENUI_USER}
chmod 770 /home/${GENUI_USER}

# execute the command as the declared user
exec runuser -u  ${GENUI_USER} -- "$@"