#!/usr/bin/python

from fabric.api import *
from fabric.colors import red, green

import cloubed
import logging
import os

# use ~/.ssh/config
env.use_ssh_config = True
env.ssh_config_path = "http/ssh_config"

NODES = { 'admin': ['10.5.0.1', '10.11.0.1'],
          'login': ['10.5.0.2', '10.11.0.2'],
          'cn1':   ['10.11.0.11'],
          'cn2':   ['10.11.0.12'],
          'cn3':   ['10.11.0.13'], }

def __gen_ssh_keypair():

    type = 'rsa'
    key_dir = "ansible/roles/ssh/files"
    priv_key = "{key_dir}/id_{type}".format(key_dir=key_dir,type=type)
    if not os.path.exists(priv_key):
        print(green("generating root ssh keypair"))
        if not os.path.isdir(key_dir): os.makedirs(key_dir)
        local("ssh-keygen -t {type} -N '' -C 'root@cluster' " \
              "-f {priv_key}".format(priv_key=priv_key))

def __gen_ssh_hosts_keys():

    for node in NODES.iterkeys():
        key_dir = "ansible/roles/ssh/files/{node}".format(node=node)
        if not os.path.isdir(key_dir): os.makedirs(key_dir)
        for type in ["rsa", "dsa", "ecdsa"]:
            key_path = "{dir}/ssh_host_{type}_key".format(dir=key_dir, type=type)
            if not os.path.exists(key_path):
                print(green("generating host keys type {type} for node {node}" \
                            .format(type=type, node=node)))
                local("ssh-keygen -t {type} -N '' -C 'root@{node}' " \
                      "-f {key}" \
                      .format(type=type,
                              node=node,
                              key=key_path))

    # generate known hosts file
    known_hosts = ""
    for node in NODES.iterkeys():
        key_dir = "ansible/roles/ssh/files/{node}".format(node=node)
        pubkey_path = "{dir}/ssh_host_ecdsa_key.pub".format(dir=key_dir)
        with open(pubkey_path,'r') as pubkey_file:
            # remove comment after public key
            pubkey = ' '.join(pubkey_file.readline().split(' ')[:2])
            known_hosts += "{node} {pubkey}\n".format(node=node, pubkey=pubkey)
            for ip in NODES[node]:
                known_hosts += "{ip} {pubkey}\n".format(ip=ip, pubkey=pubkey)
    known_hosts_path = "ansible/roles/ssh/files/known_hosts"
    with open(known_hosts_path,'w') as known_hosts_file:
        known_hosts_file.write(known_hosts)

def __gen_munge_key():

    key_path="ansible/roles/slurm/files/munge.key"
    local("dd if=/dev/urandom bs=1 count=1024 > {key_path}" \
          .format(key_path=key_path))

def __dl_extract_netboot():

    netboot_url = "http://ftp.fr.debian.org/debian/dists/wheezy/main/" \
                  "installer-amd64/current/images/netboot/netboot.tar.gz"
    netboot_lpath = "/tmp/netboot.tar.gz"
    if not os.path.exists('http/debian-installer/amd64/linux'):
        local("wget {url} -O {lpath}" \
              .format(url=netboot_url,
                      lpath=netboot_lpath))
        local("tar -xzf {lpath} -C http/".format(lpath=netboot_lpath))
        local("rm {lpath}".format(lpath=netboot_lpath))

def __create_needed_dirs():

    needed_dirs = [ 'pool', 'http' ]
    for dir in needed_dir:
        if not os.path.isdir(pool_dir):
            os.makedirs(pool_dir)

@task
def install_admin():

    node = "admin"

    __gen_ssh_keypair()
    __gen_ssh_hosts_keys()
    __gen_munge_key()
    __create_needed_dirs()
    __dl_extract_netboot()
    __pack_config()

    # generate the config files based on templates
    cloubed.gen_file(domain_name=node, template_name="ipxe")
    cloubed.gen_file(domain_name=node, template_name="preseed")
    cloubed.gen_file(domain_name=node, template_name="late-command")
    cloubed.gen_file(domain_name=node, template_name="ssh-config")

    # boot admin on network device
    cloubed.boot_vm(domain_name=node,
                    bootdev="network",
                    overwrite_disks=True,
                    recreate_networks=True)

    # wait admin shutdown
    cloubed.wait_event(node, "STOPPED", "SHUTDOWN")

    # boot admin on disk device
    cloubed.boot_vm(node)

def __pack_config():

    tar_file_name = "config.tar.gz"
    # generate tarball
    local("tar -czf http/{tarball} ansible".format(tarball=tar_file_name))

@task
@hosts('admin')
def run_ansible():

    __pack_config()
    put('http/config.tar.gz', '/tmp/config.tar.gz')
    run('tar -xzf /tmp/config.tar.gz -C /opt')

    with cd("/opt/ansible"):
        run("ansible-playbook cluster.yml")

@task
def install_login():

    node = "login"

    # boot node on network device
    cloubed.boot_vm(domain_name=node,
                    bootdev="network",
                    overwrite_disks=True)

    # wait node shutdown
    cloubed.wait_event(node, "STOPPED", "SHUTDOWN")

    # boot node on disk device
    cloubed.boot_vm(node)

@task
def install_node():

    node = env.host

    # boot node on network device
    cloubed.boot_vm(domain_name=node,
                    bootdev="network",
                    overwrite_disks=True)

    # wait node shutdown
    cloubed.wait_event(node, "STOPPED", "SHUTDOWN")

    # boot node on disk device
    cloubed.boot_vm(node)
