#!/usr/bin/env bash
cd /var/www/
# Make Sure site is stopped
sudo systemctl stop momsforliberty-web
# Setup directories and git clone
sudo rm -rf momsforliberty-web
sudo rm -rf /srv/venv_m4l_dev
sudo git clone git@github.com:fabiuslabs/momsforliberty-web.git
sudo chown -R ubuntu:ubuntu /var/www/momsforliberty-web
cd momsforliberty-web/
# Copy ENV variables
cp ~/.env ./.env
#sudo git checkout dev
# Install Python Virtual Env and Dependencies
python3 -m venv /srv/venv_m4l_dev
source /srv/venv_m4l_dev/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r momsforliberty/requirements/prod.txt --upgrade

# Set permissions for www
sudo chmod -R o+rX /srv/venv_m4l_dev/
sudo chgrp -Rh www-data /var/www/momsforliberty-web/
sudo chmod -R g+rwX /var/www/momsforliberty-web/momsforliberty/media/ /var/www/momsforliberty-web/momsforliberty/themes/
sudo chmod -R g+rwX /var/www/momsforliberty-web/momsforliberty/whoosh_index/
sudo chown -Rh www-data /var/log/momsforliberty-web/
sudo chmod -R g+rwX /var/log/momsforliberty-web/

# Copy the service, logs, and nginx over from repo to server
sudo cp momsforliberty-web.service /etc/systemd/system/momsforliberty-web.service
sudo cp dev.logs /etc/logrotate.d/momsforliberty-web
sudo cp dev.momsforliberty.org /etc/nginx/sites-available/dev.momsforliberty.org
sudo rm /etc/nginx/sites-enabled/dev.momsforliberty.org
sudo ln -s /etc/nginx/sites-available/dev.momsforliberty.org /etc/nginx/sites-enabled/dev.momsforliberty.org
# Start the website
sudo systemctl start momsforliberty-web
sudo systemctl enable momsforliberty-web
sudo service nginx restart
# Stop python
deactivate
