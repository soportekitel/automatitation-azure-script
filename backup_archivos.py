"""
Develop by Jose Rojas rojasrjosee@gmail.com
Script for copy freepbx files to Azure
"""

import os
import socket
import sys
import glob
import hashlib
import traceback
import pdb

from requests import get
from sendmail import sendalert
from backup_config import Config
from azure_container_access import DirectoryClient
from azure.storage.blob import BlobServiceClient

config = Config()

host_name = socket.gethostname()
host_ip_public = get('http://ifconfig.co/ip').text.rstrip('\n')

container_name = socket.gethostname()
container_name = container_name.lower()
container_name = container_name.replace("_", "-")

message = ""
local_path_backup = os.path.join(config.get_directory_backup())
remote_path_backup = os.path.join(config.get_container_backup())

if os.path.isdir(local_path_backup):

    try:
        blob_service_client = BlobServiceClient.from_connection_string(conn_str=config.get_connection())

        containers = blob_service_client.list_containers()
        create_container = True
        for container in containers:
            if container.name == container_name:
                create_container = False
                break

        if create_container:
            blob_service_client.create_container(container_name)

        backup_files = [f for f in glob.glob(local_path_backup + "/**/*.*", recursive=True)]
        backup_files_integrity = {}
        for backup_file in backup_files:
            backup_files_integrity[backup_file] = hashlib.md5(open(backup_file, 'rb').read()).hexdigest()

        container_client = DirectoryClient(config.get_connection(), container_name)

        get_files = container_client.ls_files(remote_path_backup)

        upload_result = {}

        if get_files:
            for file in get_files:
                if not(os.path.isfile(os.path.join(local_path_backup, file))):
                    container_client.rm(os.path.join(remote_path_backup, file))

        files = os.listdir(local_path_backup)
        for file in files:
            if os.path.isfile(os.path.join(local_path_backup, file)):
                if not(file in get_files):
                    local_path = os.path.join(local_path_backup, file)
                    remote_path = os.path.join(remote_path_backup, file)
                    upload = container_client.upload(local_path, remote_path)
                    upload_result.update(upload)

        if upload_result:
            for file in upload_result:
                if not(upload_result[file] == backup_files_integrity[file]):
                    message = "{}\nFile: {} Error: {}".format(message, file, socket.gethostname())

            if len(message) > 0:
                subj = "ERROR al copiar el Backup desde {} - {} hasta Azure".format(host_name, host_ip_public)
                message = "Ejecutar en {} el script:" \
                          "/usr/local/infodes/azure/env/azure/bin/python /usr/local/infodes/bin/{}\n\n" \
                          "Fallo la copia de:\n{}".format(host_ip_public, os.path.basename(__file__), message)
            else:
                subj = "Copia exitosa del Backup desde {} - {} hasta Azure".format(host_name, host_ip_public)
                message = "Copia exitosa del Backup desde {} - {} hasta Azure\n".format(host_name, host_ip_public)

    except Exception as eerror:
        subj = "ERROR al copiar Backup desde {} - {} hasta Azure".format(host_name, host_ip_public)
        message = "Ejecutar en {}:\n" \
                  "/usr/local/infodes/azure/env/azure/bin/python " \
                  "/usr/local/infodes/bin/{} \n\n" \
                  "Error {}".format(host_ip_public, os.path.basename(__file__),
                                    traceback.format_exc())

    if message:
        sendalert(subj, message)
