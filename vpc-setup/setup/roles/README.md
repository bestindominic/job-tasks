Role Name
=========


Ansible role to setup AWS VPC

How to run the playbook to install apticron
----------------


cd automation/deployment

ansible-playbook -vi roles/apticron/inventory/hosts -e "hostgroup=<<hostgroup-from-'hosts'>>"  apticron_setup.yml


