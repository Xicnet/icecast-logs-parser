Icecast Logs Parser
===================

Icecast Logs Parser is a Python script designed for read and insert into a DB all the access log lines, with some bussines rules on mind.


Requirements
============

sudo apt-get install libmysqlclient-dev

If you test locally:
    sudo apt-get install mysql-server

sudo pip install -r requirements.txt

Centos 7 installation

yum install python-devel python-pip mariadb-devel GeoIP


Logrotate
=========

Replace your /etc/logrotate.d/icecast2 with the config we ship:

cp logrotate-icecast2.conf /etc/logrotate.d/icecast2

GeoIP.dat
=========

wget -O - http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz | /bin/gunzip -c > /usr/share/GeoIP/GeoLiteCity.dat
wget -O - http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz | /bin/gunzip -c > /usr/share/GeoIP/GeoIP.dat

