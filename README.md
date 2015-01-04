Build a small and fake Linux HPC cluster with some virtual machines on your
workstation.

Disclaimer: this is not real HPC! Do not expect good performances at all.

This testbed only aims to show and explain how real Linux HPC clusters work.
The purpose is purely educational. The targeted audience is any people who feel
curious about these systems and want to experiment with their software
technologies.

The cluster employs the following software:

- ansible
- slurm
- openmpi
- cblas
- openldap
- nfs
- clustershell

The cluster is composed of 5 nodes:

- admin, the cluster administration server which provides the following
  services:
  - Slurm controller
  - ansible server
  - LDAP server
  - NFS server
- login:
  - SSH frontend for users
  - Scientific codes compilation
  - Slurm jobs submission
- cn[1-3]
  - Slurm jobs execution

Requires the following dependencies:

- GNU/Linux workstation with sufficient RAM (>=4GB) and fairly recent Linux
  kernel
- cloubed >= 0.4
- fabric
