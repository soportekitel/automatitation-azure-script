def update_rules(os_system, ip_list, network_client, resource_group_name, security_group_name ):
    if os_system.upper() == 'LINUX':
        new_security_rule_name = 'SIP_dinamic_ip'
        async_security_rule = network_client.security_rules.create_or_update(
        resource_group_name,
        security_group_name,
        new_security_rule_name,
        {
        'access':"allow",
        'description':'Accesos para clientes con dns dinamico',
        'destination_address_prefix':'*',
        'destination_port_range':'5060',
        'direction':"inbound",
        'priority':1400,
        'protocol':'*',
        'source_address_prefixes': ip_list,
        'source_port_range':'*',
        }
        )

        new_security_rule_name = 'RTP_dinamic_ip'
        async_security_rule = network_client.security_rules.create_or_update(
        resource_group_name,
        security_group_name,
        new_security_rule_name,
        {
        'access':"allow",
        'description':'Accesos para clientes con dns dinamico',
        'destination_address_prefix':'*',
        'destination_port_range':'10000-20000',
        'direction':"inbound",
        'priority':1401,
        'protocol':"udp",
        'source_address_prefixes': ip_list,
        'source_port_range':'*',
        }
        )

        new_security_rule_name = 'HTTPS_dinamic_ip'
        async_security_rule = network_client.security_rules.create_or_update(
        resource_group_name,
        security_group_name,
        new_security_rule_name,
        {
        'access':"allow",
        'description':'Accesos para clientes con dns dinamico',
        'destination_address_prefix':'*',
        'destination_port_range':'443',
        'direction':"inbound",
        'priority':1402,
        'protocol':'*',
        'source_address_prefixes': ip_list,
        'source_port_range':'*',
        }
        )
        new_security_rule_name = 'GRAFANA_dinamic_ip'
        async_security_rule = network_client.security_rules.create_or_update(
        resource_group_name,
        security_group_name,
        new_security_rule_name,
        {
        'access':"allow",
        'description':'Accesos para clientes con dns dinamico',
        'destination_address_prefix':'*',
        'destination_port_range':'3000',
        'direction':"inbound",
        'priority':1403,
        'protocol':'*',
        'source_address_prefixes': ip_list,
        'source_port_range':'*',
        }
        )
        new_security_rule_name = 'ICMP_dinamic_ip'
        async_security_rule = network_client.security_rules.create_or_update(
        resource_group_name,
        security_group_name,
        new_security_rule_name,
        {
        'access':"allow",
        'description':'Ping para clientes con dns dinamico',
        'destination_address_prefix':'*',
        'destination_port_range':'*',
        'direction':"inbound",
        'priority':1404,
        'protocol':'ICMP',
        'source_address_prefixes': ip_list,
        'source_port_range':'*',
        }
        )
    else:
        new_security_rule_name = 'Iagent_dinamic_ip'
        async_security_rule = network_client.security_rules.create_or_update(
        resource_group_name,
        security_group_name,
        new_security_rule_name,
        {
        'access':"allow",
        'description':'Accesos para clientes con dns dinamico',
        'destination_address_prefix':'*',
        'destination_port_ranges': ['3555','35555'],
        'direction':"inbound",
        'priority':1300,
        'protocol':"tcp",
        'source_address_prefixes': ip_list,
        'source_port_range':'*',
        }
        )

        new_security_rule_name = 'HTTPS_dinamic_ip'
        async_security_rule = network_client.security_rules.create_or_update(
        resource_group_name,
        security_group_name,
        new_security_rule_name,
        {
        'access':"allow",
        'description':'Accesos para clientes con dns dinamico',
        'destination_address_prefix':'*',
        'destination_port_range':'443',
        'direction':"inbound",
        'priority':1301,
        'protocol':'*',
        'source_address_prefixes': ip_list,
        'source_port_range':'*',
        }
        )


def update_rules_evolution(os_system, evolution, network_client, resource_group_name, security_group_name ):
    new_security_rule_name = 'evolution'
    async_security_rule = network_client.security_rules.create_or_update(
    resource_group_name,
    security_group_name,
    new_security_rule_name,
    {
    'access':"allow",
    'description':'Permitir evolution',
    'destination_address_prefix':'*',
    'destination_port_range':'*',
    'direction':"inbound",
    'priority':700,
    'protocol':'*',
    'source_address_prefix': evolution,
    'source_port_range':'*',
    }
    )


def update_general_rules(os_system, ip_list, general_group, network_client, resource_group_name, security_group_name ):
    if general_group == "all":
        new_security_rule_name = 'PermitirLocalidadesKitel'
        async_security_rule = network_client.security_rules.create_or_update(
        resource_group_name,
        security_group_name,
        new_security_rule_name,
        {
        'access':"allow",
        'description':'Accesos para localidades remotas de Kitel',
        'destination_address_prefix':'*',
        'destination_port_range':'*',
        'direction':"inbound",
        'priority':600,
        'protocol':'*',
        'source_address_prefixes': ip_list,
        'source_port_range':'*',
        }
        )
    elif os_system.upper() == 'LINUX':
        if general_group == 'sip':
            new_security_rule_name = 'PermitirPoveedoresSipSip'
            async_security_rule = network_client.security_rules.create_or_update(
            resource_group_name,
            security_group_name,
            new_security_rule_name,
            {
            'access':"allow",
            'description':'Accesos para proveedores sip Senalizacion',
            'destination_address_prefix':'*',
            'destination_port_range':'5060',
            'direction':"inbound",
            'priority':510,
            'protocol':'*',
            'source_address_prefixes': ip_list,
            'source_port_range':'*',
            }
            )
            new_security_rule_name = 'PermitirPoveedoresSipRTP'
            async_security_rule = network_client.security_rules.create_or_update(
            resource_group_name,
            security_group_name,
            new_security_rule_name,
            {
            'access':"allow",
            'description':'Accesos para proveedores sip media',
            'destination_address_prefix':'*',
            'destination_port_range':'10000-20000',
            'direction':"inbound",
            'priority':511,
            'protocol':'UDP',
            'source_address_prefixes': ip_list,
            'source_port_range':'*',
            }
            )


def update_all_rules(os_system, network_client, resource_group_name, security_group_name ):
    if os_system.upper() == 'LINUX':
        new_security_rule_name = 'FTP'
        async_security_rule = network_client.security_rules.create_or_update(
        resource_group_name,
        security_group_name,
        new_security_rule_name,
        {
        'access':"allow",
        'description':'Accesos ftp para las grabaciones',
        'destination_address_prefix':'*',
        'destination_port_range':'20-21',
        'direction':"inbound",
        'priority':410,
        'protocol':'TCP',
        'source_address_prefix': '*',
        'source_port_range':'*',
        }
        )
