"""
Develop by Jose Rojas rojasrjosee@gmail.com
Script to update NSG rules
"""

import os
import socket
import traceback
import update_nsg_rules

from config import Config
from requests import get
from sendmail import sendalert
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient

config = Config()
script_path = "/usr/local/infodes/azure/env/azure/bin/python "\
              "/usr/local/infodes/bin/{}".format(os.path.basename(__file__))

host_name = socket.gethostname()
host_ip_public = get('http://ifconfig.co/ip').text.rstrip('\n')

ddns_field = config.get_ddns()
ddns_field_new = {}
ip_list = []
will_load_rules = False

try:

    for keys, values in ddns_field.items():
        if values != socket.gethostbyname(keys):
            will_load_rules = True
            values = socket.gethostbyname(keys)
        ip_values = values + "/32"
        if ip_values not in ip_list:
            ip_list.append(ip_values)
        ddns_field_new[keys] = socket.gethostbyname(values)

    if will_load_rules:
        subscription_id = config.get_subscription_id()
        credentials = ServicePrincipalCredentials(
            client_id=config.get_client_id(),
            secret=config.get_secret(),
            tenant=config.get_tenant()
        )

        compute_client = ComputeManagementClient(credentials, subscription_id)
        network_client = NetworkManagementClient(credentials, subscription_id)

        config.set_ddns(ddns_field_new)

        if ip_list:
            update_nsg_rules.update_rules(
                config.get_os_system(),
                ip_list, network_client,
                config.get_resource_group_name(),
                config.get_security_group_name()
            )

except Exception:
    subj = "ERROR al ejecutar script {} en {} - {}"\
            .format(os.path.basename(__file__), host_name, host_ip_public)
    message = "Ejecutar en {}:\n{} \n\n" \
              "Error {}".format(host_ip_public, script_path,
                                traceback.format_exc())

    if message:
        sendalert(subj, message)
