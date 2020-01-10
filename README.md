# Installation

```sh
git clone https://github.com/realitylab-at/dsb

# Build the front-end application
cd dsb/client
npm install && npm run build

# Create a virtual environment for Python2
cd ../server
mkvirtualenv -p python2.7 --no-site-packages dsb

# Install extra OS requirements for Pillow
apt install python-dev libjpeg8-dev zlib1g-dev

# Install back-end dependencies
pip install -r requirements.txt

# Create secret key for running Django
cat <<EOT > server/settings/local.py
# -*- coding: utf-8 -*-
SECRET_KEY = '$(tr -dc 'a-z0-9()!@#$%^&*_=+-' < /dev/urandom | head -c50)'
from development import *
EOT

# Create the database and static assets
./manage.py migrate
./manage.py collectstatic

# Create first user account
./manage.py createsuperuser

# Start the back-end server
./manage.py runserver
```

## Create a New Building Entry

http://localhost:8000/-/admin/api/building/add/

(Use the same credentials for login as for previously created superuser.)

Then add the building to the user account and assign an apartment number:

http://localhost:8000/-/admin/auth/user/1/change/

## Display Screen

http://localhost:8000/client/default/index.html

![](https://raw.githubusercontent.com/realitylab-at/dsb/assets/screenshot.png)
