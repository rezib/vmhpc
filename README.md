vmhpc
=====

**Build a small and fake Linux HPC cluster with some virtual machines on your
workstation.**

*Disclaimer:* this is not real HPC! Do not expect good performances at all.

This testbed only aims to show and explain how real Linux HPC clusters work.
The purpose is purely educational. The targeted audience is any people who feel
curious about these systems and want to experiment with their software
technologies.

The cluster employs the following software:

- Debian GNU/Linux
- ansible
- dnsmasq
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
  - PXE server (DHCP/TFTP)
  - APT repository proxy
  - DNS server
- login:
  - SSH frontend for users
  - Scientific codes compilation
  - Slurm jobs submission
- cn[1-3]
  - Slurm jobs execution

Requirements
------------

Hardware:

- CPU with H/W virtualization instructions enable (VT-x or AMD-V)
- 4GB of RAM
- about 15GB of disk space
- good Internet connection

Software:

- GNU/Linux workstation and fairly recent Linux kernel
- cloubed >= 0.4 with all its dependencies including Libvirt and KVM
- fabric

Usage
-----

Simply run the following command:

```
$ fab install_cluster
```

This will automatically create all virtual networks, launch, install and
configure all virtual machines. At the end, the cluster will be fully
operational.


Beware, it takes quite a while to run, about 2 hours on a decent workstation.
Note that it also downloads about 600MB of debian packages over the Internet.

At the end, you will be able to:

- connect on login node as normal user
- compile a scientific code that uses BLAS and MPI, such as HPL linpack
- run it in on compute nodes with Slurm workload manager
