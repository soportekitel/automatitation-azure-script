"""
Develop by Jose Rojas rojasrjosee@gmail.com
Script for copy Evolution files to Azure
"""

import os
import pyodbc
import datetime
import socket
import sys
import glob
import hashlib
import traceback
import pdb

from requests import get
from zipfile import ZipFile
from sendmail import sendalert
from backup_windows_config import *
from azure_container_access import *
from azure.storage.blob import BlobServiceClient



config = Config()
today = datetime.datetime.now()

host_name = socket.gethostname()
host_ip_public = get('http://ifconfig.co/ip').text.rstrip('\n')

container_name = socket.gethostname()
container_name = container_name.lower()
container_name = container_name.replace("_","-")

local_path_backup = os.path.join(config.get_directory_backup())
remote_path_backup = os.path.join(config.get_container_backup())

def backup_evolution():
    try:
        backup_folder = config.get_directory_backup()

        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        cnxn = pyodbc.connect('driver={ODBC Driver 17 for SQL Server};server=' + \
                               config.get_backup_database_server() + ','+ \
                               config.get_backup_database_port() + ';database=' + \
                               config.get_backup_database() + ';uid='+ \
                               config.get_backup_database_user() + ';pwd=' + \
                               config.get_backup_database_password())

        cnxn.autocommit = True
        file_backup = backup_folder + "\\evolution_backup_" + today.strftime("%Y%m%d") + ".bak"
        sql = "BACKUP DATABASE " + config.get_backup_database() + \
              " TO DISK = N'{0}'".format(file_backup)

        cursor = cnxn.cursor()
        cursor.execute(sql)
        while cursor.nextset():
              pass
        cursor.close()
        cnxn.close()

        file_paths = []

        for root, directories, files in os.walk(config.get_backup_directory_evolution()):
            for filename in files:
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)

        file_backup_evolution_files = backup_folder + "\\evolution_files_backup_" + \
                                      today.strftime("%Y%m%d") + ".zip"
        with ZipFile(file_backup_evolution_files,'w') as zip:
            # writing each file one by one
            for file in file_paths:
                zip.write(file)

        zip.close()
        return True
    except Exception as eerror:
        return False



if backup_evolution():
    if os.path.isdir(local_path_backup ):

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
                    if not(os.path.isfile(os.path.join(local_path_backup,file))):
                        container_client.rm(os.path.join(remote_path_backup,file))

            files = os.listdir(local_path_backup)
            for file in files:
                if os.path.isfile(os.path.join(local_path_backup,file)):
                    if not(file in get_files):
                        upload = container_client.upload(os.path.join(local_path_backup,file), os.path.join(remote_path_backup,file))
                        upload_result.update(upload)

            message = ""

            if upload_result:
                for file in upload_result:
                    if not(upload_result[file] == backup_files_integrity[file]):
                        message = "{}\nFile: {} Error: {}".format(file, socket.gethostname())

                if len(message) > 0:
                    subj = "ERROR al copiar el Backup de Evolution desde {} - {} hasta Azure".format(host_name, host_ip_public)
                    message = "Ejecutar en {} el script:" \
                              "c:\infodes\azure\env\azure\Scripts\python.exe c:\infodes\bin\backup_evolution_archivos.py\n\n" \
                              "Fallo la copia de:\n{}".format(host_ip_public, message)
                else:
                    for file in backup_files_integrity:
                        os.remove(file)

                    subj = "Copia exitosa del Backup de Evolution desde {} - {} hasta Azure".format(host_name, host_ip_public)
                    message = "Copia exitosa del Backup desde {} - {} hasta Azure\n".format(host_name, host_ip_public)
            else:
                for file in backup_files_integrity:
                    os.remove(file)

        except Exception as eerror:
            subj = "ERROR al copiar Backup de Evolution desde {} - {} hasta Azure".format(host_name, host_ip_public)
            message = "Ejecutar en {} el script\n" \
                      "'c:\infodes\azure\env\azure\Scripts\python.exe c:\infodes\bin\backup_evolution_archivos.py' \n\n" \
                      "Error {}".format(host_ip_public, traceback.format_exc())
else:
    subj = "ERROR al hacer Backup de Evolution desde {} - {} hasta Azure".format(host_name, host_ip_public)
    message = "Ejecutar en {} el script\n" \
              "'c:\infodes\azure\env\azure\Scripts\python.exe c:\infodes\bin\backup_evolution_archivos.py'\n\n" \
              "Error {}".format(host_ip_public, traceback.format_exc())

if message:
    sendalert(subj, message, config.get_notification_mailalert())
