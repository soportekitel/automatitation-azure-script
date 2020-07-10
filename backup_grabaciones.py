"""
Develop by Jose Rojas rojasrjosee@gmail.com
Script for copy asterisk record files to Azure
"""

import os
import datetime
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
script_path = "/usr/local/infodes/azure/env/azure/bin/python "\
              "/usr/local/infodes/bin/{}".format(os.path.basename(__file__))

host_name = socket.gethostname()
host_ip_public = get('http://ifconfig.co/ip').text.rstrip('\n')

container_name = socket.gethostname()
container_name = container_name.lower()
container_name = container_name.replace("_", "-")

today = datetime.datetime.today()
today_30days_ago = datetime.datetime.today() - datetime.timedelta(days=30)
year_record = today_30days_ago.strftime("%Y")
month_record = today_30days_ago.strftime("%m")

message = ""
local_path_record = os.path.join(config.get_directory_record(),
                                 year_record, month_record
                                 )
local_path_record_year = os.path.join(config.get_directory_record(),
                                      year_record
                                      )
remote_path_record = os.path.join(config.get_container_record(),
                                  year_record
                                  )


run_backup = False
if len(sys.argv) > 1:
    run_backup = True
elif today.strftime("%-d") == config.get_day_record():
    run_backup = True


def verify_container(container_name):
    containers = blob_service_client.list_containers()
    create_container = True
    for container in containers:
        if container.name == container_name:
            create_container = False
            break

    if create_container:
        blob_service_client.create_container(container_name)


if run_backup:
    if os.path.isdir(local_path_record):

        try:
            blob_service_client = BlobServiceClient.from_connection_string(conn_str=config.get_connection())

            verify_container(container_name)

            record_files = [f for f in glob.glob(local_path_record + "/**/*.*", recursive=True)]
            record_files_integrity = {}
            for record_file in record_files:
                record_files_integrity[record_file] = hashlib.md5(open(record_file, 'rb').read()).hexdigest()

            container_client = DirectoryClient(config.get_connection(), container_name)

            upload_result = container_client.upload(local_path_record, remote_path_record)

            for file in record_files_integrity:
                if upload_result[file] == record_files_integrity[file]:
                    os.remove(file)
                else:
                    message = "{}\nFile: {} Error: {}"\
                        .format(message, file, socket.gethostname())

            if len(message) > 0:
                subj = "ERROR al copiar grabaciones desde {} - {} " \
                       "hasta Azure".format(host_name, host_ip_public)
                message = "Ejecutar en {}:\n{}'\n\nFallo la copia en:\n{}"\
                          .format(host_ip_public, script_path, message)
            else:
                subj = "Copia exitosa de las grabaciones desde {} - {} " \
                       "hasta Azure".format(host_name, host_ip_public)
                message = "Copia exitosa de las grabaciones desde {} - {} " \
                          "hasta Azure\n".format(host_name, host_ip_public)
                for root, dirs, files in os.walk(local_path_record):
                    if not(os.path.relpath(root, local_path_record) == '.'):
                        files = os.listdir(root)
                        if len(files) == 0:
                            os.rmdir(root)
                files = os.listdir(local_path_record)
                if len(files) == 0:
                    os.rmdir(local_path_record)
                    message = "{}\n\nCarpeta {} borrada del servidor".format(message, local_path_record)
                else:
                    message = "{}\n\nLa carpeta {} no fue borrada del servidor. " \
                              "Hay archivos que no se pueden borrar.\n\n" \
                              "Por favor verifique ".format(message,
                                                            local_path_record)

        except Exception:
            subj = "ERROR al copiar grabaciones desde {} - {} " \
                   "hasta Azure".format(host_name, host_ip_public)
            message = "Ejecutar en {}:\n{} \n\nError {}"\
                      .format(host_ip_public, script_path,
                              traceback.format_exc())

    else:
        subj = "ERROR no hay grabaciones en {} - {} para subir " \
               "a Azure".format(host_name, host_ip_public)
        message = "Verificar en {} que exista la carpeta {}\n\n" \
                  " Si la carperta existe ejecutar:\n{} \n\n"\
                  .format(host_ip_public, local_path_record, script_path)

if message:
    sendalert(subj, message)
