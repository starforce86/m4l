#!/bin/bash

sudo chown -R www-data:www-data /var/www/tendenci_site
sudo chmod -R o+rX-w /var/www/tendenci_site
sudo chown -R "$(id -u -n)":www-data /srv/tendenci_site
chmod -R -x+X,g-w,o-rwx /var/www/tendenci_site
chmod -R ug-x+rwX,o-rwx /var/www/tendenci_site/media/ /var/www/tendenci_site/themes/
chmod -R ug-x+rwX,o-rwx /var/www/tendenci_site/whoosh_index/
sudo chown -Rh www-data:"$(id -u -n)" /var/log/tendenci_site/
sudo chmod -R -x+X,g+rw,o-rwx /var/log/tendenci_site/
