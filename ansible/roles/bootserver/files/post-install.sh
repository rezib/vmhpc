#!/bin/bash

HOSTNAME=$(hostname)
SERVER=admin

# workaround for a bug with iproute/iproute2 when wheezy-backports is enable
apt-get install --reinstall --yes isc-dhcp-client ifupdown

# Deploy configuration locally with the following steps:
#   0/ install ansible
#   1/ download and extract tarball with conf playbook
#   2/ generate minimal ansible hosts file
#   3/ run ansible over
#   4/ delete the playbook
#   5/ uninstall ansible and its dependencies

apt-get install --yes ansible

# use --no-proxy to avoid usage of APT proxy
wget --no-proxy http://${SERVER}/config.tar.gz -O /tmp/config.tar.gz
tar -xzf /tmp/config.tar.gz --no-same-owner -C /opt

cd /opt/ansible

echo "${HOSTNAME} ansible_connection=local" > /etc/ansible/hosts

echo $http_proxy > /var/log/ansible-run
export http_proxy="http://admin:3128"
ansible-playbook cluster.yml &> /var/log/ansible-run

rm -rf /opt/ansible

apt-get remove --purge --yes ansible

apt-get autoremove --yes
