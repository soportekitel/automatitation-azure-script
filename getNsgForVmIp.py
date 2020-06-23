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
import re
import socket
import pdb
import traceback
import update_nsg_rules

from config import Config
from requests import get
from sendmail import sendalert
from updateIPAsteriskEvolution import EvolutionServer, AsteriskServer
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient

config = Config()
script_path = "/usr/local/infodes/azure/env/azure/bin/python "\
              "/usr/local/infodes/bin/{}".format(os.path.basename(__file__))

host_name = socket.gethostname()
host_ip_public = get('http://ifconfig.co/ip').text.rstrip('\n')

subscription_id = config.get_subscription_id()
credentials = ServicePrincipalCredentials(
    client_id=config.get_client_id(),
    secret=config.get_secret(),
    tenant=config.get_tenant()
)

compute_client = ComputeManagementClient(credentials, subscription_id)
network_client = NetworkManagementClient(credentials, subscription_id)

vm_instance = dict(
    hostname="",
    nsg_id="",
    resource_group_name="",
    evolution_name="",
    asterisk_name=""
)
ddns_field = {}


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def get_vm_ip(vm_name):
    for vm in compute_client.virtual_machines.list_all():
        if vm_name == vm.name:
            for interface in vm.network_profile.network_interfaces:
                name = " ".join(interface.id.split('/')[-1:])
                sub = "".join(interface.id.split('/')[4])

                try:
                    interfaces = network_client.network_interfaces.\
                                    get(sub, name).ip_configurations

                    for iface in interfaces:
                        name_ip_public_address = " ".join(
                            iface.public_ip_address.id.split('/')[-1:]
                        )
                        rg_ip_public_address = "".join(
                            iface.public_ip_address.id.split('/')[4])
                        public_ip_address = network_client.public_ip_addresses.get(
                            rg_ip_public_address,
                            name_ip_public_address
                        )
                        return iface.private_ip_address, public_ip_address.ip_address

                except Exception:
                    return "", ""


def get_vm_values(vm_instance):

    ip_lan = get_ip_address()

    for vm in compute_client.virtual_machines.list_all():
        for interface in vm.network_profile.network_interfaces:
            interface_name = " ".join(interface.id.split('/')[-1:])
            group_name = "".join(interface.id.split('/')[4])
            ip_interface = network_client.network_interfaces.get(group_name, interface_name).ip_configurations
            for ip in ip_interface:
                if ip.private_ip_address == ip_lan:
                    vm_instance["hostname"] = vm.name
                    vm_instance["resource_group_name"] = group_name
                    vm_instance["nsg_id"] = network_client.\
                        network_interfaces.\
                        get(group_name, interface_name).\
                        network_security_group.id

                    config.set_os_system(
                        vm.storage_profile.os_disk.os_type.__dict__['_value_']
                    )
                    if vm.tags:
                        for key_tag in vm.tags:
                            if re.match(r'^DDNS.*', key_tag):
                                tags_values = vm.tags[key_tag].split(";")
                                for tag in tags_values:
                                    ddns_field[tag] = socket.gethostbyname(tag)
                            if key_tag == 'evolution':
                                config.set_evolution(vm.tags[key_tag])
                                vm_instance["evolution_name"] = vm.tags[key_tag]
                            if key_tag == 'pbx':
                                config.set_asterisk(vm.tags[key_tag])
                                vm_instance["asterisk_name"] = vm.tags[key_tag]
                    return


def update_nsg():
    ip_list = []
    for keys, values in ddns_field.items():
        values = values + "/32"
        if values not in ip_list:
            ip_list.append(values)

    if ip_list:
        update_nsg_rules.update_rules(
            config.get_os_system(),
            ip_list, network_client,
            config.get_resource_group_name(),
            config.get_security_group_name()
        )


def set_asteisk_rules(asterisk_name):
    asterisk_private_ip, asterisk_public_ip = get_vm_ip(asterisk_name)
    evolution_server = EvolutionServer(
        asterisk_private_ip,
        asterisk_public_ip,
        vm_instance["hostname"]
    )
    evolution_server.change_ip_db()
    evolution_server.write_file_host()


def set_evolution_rules(evolution_name):
    evolution_private_ip, evolution_public_ip = get_vm_ip(evolution_name)
    evolution_public = evolution_public_ip + "/32"
    update_nsg_rules.update_rules_evolution(
        config.get_os_system(),
        evolution_public,
        network_client,
        config.get_resource_group_name(),
        config.get_security_group_name()
    )
    asterisk_server = AsteriskServer(
        evolution_private_ip,
        evolution_public_ip,
        vm_instance["hostname"]
    )
    asterisk_server.write_file_host()
    asterisk_server.change_host_name()


try:

    get_vm_values(vm_instance)

    if vm_instance["nsg_id"]:
        m = re.search('^.+networkSecurityGroups/(.+)', vm_instance["nsg_id"])
        if m.groups():
            security_group_name = m.groups()[0]
            config.set_security_group_name(security_group_name)
            config.set_resource_group_name(vm_instance["resource_group_name"])
            config.set_ddns(ddns_field)

    update_nsg()

    if vm_instance["evolution_name"]:
        set_evolution_rules(vm_instance["evolution_name"])
    elif vm_instance["asterisk_name"]:
        set_asteisk_rules(vm_instance["asterisk_name"])

except Exception:
    subj = "ERROR al ejecutar script {} en {} - {}".\
        format(os.path.basename(__file__), host_name, host_ip_public)
    message = "Ejecutar en {}:\n{} \n\n" \
              "Error {}".format(host_ip_public, script_path,
                                traceback.format_exc())

    if message:
        sendalert(subj, message)
