"""
Develop by Jose Rojas rojasrjosee@gmail.com
Runbook for holiday, startup and shutdown vm using tag_holiday, tag_start and tag_stop

Day of week:
Day of the week => Value
Sunday => 0
Monday => 1
Tuesday => 2
Wednesday => 3
Thursday => 4
Friday => 5
Saturday => 6


"""
from dateutil.tz import gettz
import datetime
import azure.mgmt.compute
from azure.mgmt.compute import ComputeManagementClient
import azure.mgmt.storage

import azure.mgmt.resource
import automationassets
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD

tag_start = 'Encender'
tag_stop = 'Apagar'
tag_holiday = 'Feriados'


def get_automation_runas_credential(runas_connection, resource_url, authority_url):
    """ Returns credentials to authenticate against Azure resoruce manager """
    from OpenSSL import crypto
    from msrestazure import azure_active_directory
    import adal

    # Get the Azure Automation RunAs service principal certificate
    cert = automationassets.get_automation_certificate("AzureRunAsCertificate")
    pks12_cert = crypto.load_pkcs12(cert)
    pem_pkey = crypto.dump_privatekey(crypto.FILETYPE_PEM, pks12_cert.get_privatekey())

    # Get run as connection information for the Azure Automation service principal
    application_id = runas_connection["ApplicationId"]
    thumbprint = runas_connection["CertificateThumbprint"]
    tenant_id = runas_connection["TenantId"]

    # Authenticate with service principal certificate
    authority_full_url = (authority_url + '/' + tenant_id)
    context = adal.AuthenticationContext(authority_full_url)
    return azure_active_directory.AdalAuthentication(
        lambda: context.acquire_token_with_client_certificate(
            resource_url,
            application_id,
            pem_pkey,
            thumbprint)
    )


def vm_get_status(vm_status):
    # Get vm status running or deallocated
    if vm_status.instance_view.statuses[1].display_status == "VM running":
        return tag_stop
    elif vm_status.instance_view.statuses[1].display_status in ("VM deallocated", "VM stopped"):
        return tag_start
    else:
        return ''


# Authenticate to Azure using the Azure Automation RunAs service principal
runas_connection = automationassets.get_automation_connection("AzureRunAsConnection")
resource_url = AZURE_PUBLIC_CLOUD.endpoints.active_directory_resource_id
authority_url = AZURE_PUBLIC_CLOUD.endpoints.active_directory
resource_manager_url = AZURE_PUBLIC_CLOUD.endpoints.resource_manager
azure_credential = get_automation_runas_credential(runas_connection, resource_url, authority_url)

# Intialize the resource management client with the RunAs credential and subscription
resource_client = azure.mgmt.resource.ResourceManagementClient(
    azure_credential,
    str(runas_connection["SubscriptionId"]),
    base_url=resource_manager_url)

# Initialize the compute management client with the RunAs credential and specify the subscription to work against.
compute_client = ComputeManagementClient(
                                         azure_credential,
                                         str(runas_connection["SubscriptionId"])
                                        )

today = datetime.datetime.now(gettz("Europe/Madrid"))

for group in resource_client.resource_groups.list():
    vms = compute_client.virtual_machines.list(group.name)
    for vm in vms:
        if vm.tags:
            # These are the statuses of the VM about the event execution status and the vm state, the vm state is the second one.
            vm_status = compute_client.virtual_machines.get(group.name, vm.name, expand='instanceView')
            vm_tag_key = vm_get_status(vm_status)

            print("vm: " + vm.name + " vm_status: " + vm_status.instance_view.statuses[1].display_status + " vm_tag: " + vm_tag_key)
            if vm_tag_key:
                print("vm: " + vm.name + " workingday True")
                vm_runs_flag = False
                workingday = True
                if tag_holiday in vm.tags:
                    if vm.tags[tag_holiday]:
                        tags_values = vm.tags[tag_holiday].split(";")
                        for tag in tags_values:
                            print("vm: " + vm.name + " tag: " + tag_holiday + " value: " + tag + " today : " + today.strftime("%d/%m"))
                            if today.strftime("%d/%m") == tag:
                                workingday = False
                if workingday:
                    if vm_tag_key in vm.tags:
                        tags_values = vm.tags[vm_tag_key].split(";")
                        for tag in tags_values:
                            print("vm: " + vm.name + " tag: " + vm_tag_key + " value: " + tag + " today : " + today.strftime("%w,%H"))
                            if ":" not in tag:
                                if today.strftime("%w,%H") == tag:
                                    vm_runs_flag = True
                            else:
                                sub_tag = tag.split(":")
                                if today.strftime("%w,%H") == sub_tag[0] and today.strftime("%M") >= sub_tag[1]:
                                    vm_runs_flag = True

                    print("vm: " + vm.name + " vm_runs_flag: " + str(vm_runs_flag))

                    if vm_runs_flag:
                        print("vm: " + vm.name + " Entrando a vm_runs_flag")

                        if vm_tag_key == tag_start:
                            print("Starting VM " + vm.name)
                            print("Start " + str(datetime.datetime.now(gettz("Europe/Madrid"))))
                            compute_client.virtual_machines.start(group.name, vm.name)
                            print("End " + str(datetime.datetime.now(gettz("Europe/Madrid"))))

                        if vm_tag_key == tag_stop:
                            print("Shutdown VM " + vm.name)
                            print("Start " + str(datetime.datetime.now(gettz("Europe/Madrid"))))
                            compute_client.virtual_machines.power_off(group.name, vm.name)
                            print("End " + str(datetime.datetime.now(gettz("Europe/Madrid"))))
