"""
Develop by Jose Rojas rojasrjosee@gmail.com
Script to get
resource_group_name
security_group_name
from private ip address of vm
and set enviroments variable
SECURITY_GROUP_NAME
RESOURCE_GROUP_NAME
"""

import os
import datetime
import re
import socket
import pdb
import traceback
import update_nsg_rules

from config import *
from requests import get
from sendmail import sendalert
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient

config = Config()

host_name = socket.gethostname()
host_ip_public = get('http://ifconfig.co/ip').text.rstrip('\n')

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

evolution_public=""
ip_lan = get_ip_address()
ip_list = []

try:

    subscription_id = config.get_subscription_id()
    credentials = ServicePrincipalCredentials(
        client_id =config.get_client_id(),
        secret= config.get_secret(),
        tenant=config.get_tenant()
    )

    compute_client = ComputeManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)

    not_find_instance = True

    for vm in compute_client.virtual_machines.list_all():
        for interface in vm.network_profile.network_interfaces:
            if not_find_instance:
                interface_name = " ".join(interface.id.split('/')[-1:])
                group_name = "".join(interface.id.split('/')[4])
                ip_interface = network_client.network_interfaces.get(group_name, interface_name).ip_configurations
                for ip in ip_interface:
                    if ip.private_ip_address == ip_lan:
                        not_find_instance = False
                        hostname = vm.name
                        resource_group_name = group_name
                        nsg_id = network_client.network_interfaces.get(group_name, interface_name).network_security_group.id
                        config.set_os_system(vm.storage_profile.os_disk.os_type.__dict__['_value_'])
                        ddns_field = {}
                        for key_tag in vm.tags:
                            if 	re.match(r'^DDNS.*', key_tag):
                                tags_values = vm.tags[key_tag].split(";")
                                for tag in tags_values:
                                    ddns_field[tag] = socket.gethostbyname(tag)
                            if key_tag == 'evolution':
                                config.set_evolution(vm.tags[key_tag])
                            if key_tag == 'evolution_public':
                                evolution_public = vm.tags[key_tag] + "/32"
                                config.set_evolution_public(vm.tags[key_tag])


    if nsg_id:
        m = re.search('^.+networkSecurityGroups/(.+)', nsg_id)
        if m.groups():
            security_group_name = m.groups()[0]
            config.set_security_group_name(security_group_name)
            config.set_resource_group_name(resource_group_name)
            config.set_ddns(ddns_field)

    for keys,values in ddns_field.items():
        values = values + "/32"
        if not values in ip_list:
            ip_list.append(values)

    if ip_list:
        update_nsg_rules.update_rules(config.get_os_system(), ip_list, network_client, config.get_resource_group_name(), config.get_security_group_name())

    if evolution_public:
        update_nsg_rules.update_rules_evolution(config.get_os_system(), evolution_public, network_client, config.get_resource_group_name(), config.get_security_group_name())

    if config.get_os_system.upper() == 'LINUX':
        os.system("hostnamectl set-hostname {}".format(vm.name))

except Exception as eerror:
    subj = "ERROR al ejecutar script {} en {} - {}".format(os.path.basename(__file__), \
                                                 host_name, host_ip_public)
    message = "Ejecutar en {}:\n" \
              "/usr/local/infodes/azure/env/azure/bin/python " \
              "/usr/local/infodes/bin/{} \n\n" \
              "Error {}".format(host_ip_public, os.path.basename(__file__), \
                                traceback.format_exc())

    if message:
        sendalert(subj, message)
