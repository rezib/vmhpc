#!/bin/bash

HOSTNAME=$(hostname)
SERVER=${network.backbone.ip_host}:5432

# workaround for a bug with iproute/iproute2 when wheezy-backports is enable
apt-get install --reinstall --yes isc-dhcp-client ifupdown
apt-get install --yes ansible

wget http://${SERVER}/http/config.tar.gz -O /tmp/config.tar.gz
tar -xzf /tmp/config.tar.gz --no-same-owner -C /opt

cd /opt/ansible

mv hosts /etc/ansible/hosts

ansible-playbook -l ${HOSTNAME} cluster.yml &> /var/log/ansible-run
