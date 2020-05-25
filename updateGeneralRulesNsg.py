"""
Develop by Jose Rojas rojasrjosee@gmail.com
Script to update NSG general rules
"""

import os
import socket
import datetime
import re
import socket
import update_nsg_rules
import traceback
import pdb
import config
import rules_config

from requests import get
from sendmail import sendalert
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient

config = config.Config()
config_rules = rules_config.Config()

host_name = socket.gethostname()
host_ip_public = get('http://ifconfig.co/ip').text.rstrip('\n')

subscription_id = config.get_subscription_id()
credentials = ServicePrincipalCredentials(
    client_id =config.get_client_id(),
    secret= config.get_secret(),
    tenant=config.get_tenant()
)

compute_client = ComputeManagementClient(credentials, subscription_id)
network_client = NetworkManagementClient(credentials, subscription_id)

def update_rules(rules_element,rules_group):

    ip_list = []

    for keys,values in rules_element.items():
        if not values in ip_list:
            ip_list.append(values)

    if ip_list:
        update_nsg_rules.update_general_rules(config.get_os_system(), ip_list, rules_group, network_client, config.get_resource_group_name(), config.get_security_group_name())

try:
    update_rules(config_rules.get_all(), "all")
    update_rules(config_rules.get_sip(), "sip")
    update_nsg_rules.update_all_rules(config.get_os_system(), network_client, config.get_resource_group_name(), config.get_security_group_name())

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
