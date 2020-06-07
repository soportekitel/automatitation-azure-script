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

def write_file_host(ip_private, ip_public):
    content_file="""127.0.0.1    localhost
::1    localhost
{}    asterisk.ip.private
{}    asterisk.ip.public
    """.format(ip_private, ip_public)
    outfile = open("C:\Windows\System32\drivers\etc\hosts", "w")
    outfile.writelines(content_file)
    outfile.close()

def write_file_linux_host(ip_private, ip_public, hostname):
    os.system("hostnamectl set-hostname {}".format(hostname))
    content_file="""127.0.0.1 {} localhost localhost.localdomain localhost4
::1 {} localhost localhost6
{} evolution.ip.private
{} evolution.ip.public
    """.format(hostname, hostname, ip_private, ip_public)
    outfile = open("/etc/hosts", "w")
    outfile.writelines(content_file)
    outfile.close()

def get_vm_ip(vm_name, compute_client, network_client):
    for vm in compute_client.virtual_machines.list_all():
        if vm_name == vm.name:
            for interface in vm.network_profile.network_interfaces:
                name=" ".join(interface.id.split('/')[-1:])
                sub="".join(interface.id.split('/')[4])

                try:
                    thing=network_client.network_interfaces.get(sub, name).ip_configurations

                    for x in thing:
                        name_ip_public_address =" ".join(x.public_ip_address.id.split('/')[-1:])
                        rg_ip_public_address ="".join(x.public_ip_address.id.split('/')[4])
                        publicIPAddress = network_client.public_ip_addresses.get(
                            rg_ip_public_address,
                            name_ip_public_address
                        )
                        return x.private_ip_address, publicIPAddress.ip_address

                except:
                    return "",""

evolution_name=""
asterisk_name=""
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
                                evolution_name = vm.tags[key_tag]
                            if key_tag == 'pbx':
                                config.set_asterisk(vm.tags[key_tag])
                                asterisk_name = vm.tags[key_tag]

    if evolution_name:
        evolution_private_ip, evolution_public_ip = get_vm_ip(evolution_name, compute_client, network_client)
    elif asterisk_name:
        asterisk_private_ip, asterisk_public_ip  = get_vm_ip(asterisk_name, compute_client, network_client)


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

    if evolution_name:
        evolution_public = evolution_public_ip + "/32"
        update_nsg_rules.update_rules_evolution(config.get_os_system(), evolution_public, network_client, config.get_resource_group_name(), config.get_security_group_name())
        write_file_linux_host(evolution_private_ip, evolution_public_ip, hostname)

    if asterisk_name:
        write_file_host(asterisk_private_ip, asterisk_public_ip)

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
