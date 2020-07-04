"""
Develop by Jose Rojas rojasrjosee@gmail.com
Script for copy Evolution files to Azure
"""

import datetime
import glob
import hashlib
import os
import pdb
import socket
import traceback
from zipfile import ZipFile

from azure.storage.blob import BlobServiceClient
from requests import get

import pyodbc
from azure_container_access import DirectoryClient
from backup_windows_config import Config
from sendmail import sendalert

config = Config()
today = datetime.datetime.now()

SCRIPT_NAME = "c:\\infodes\\azure\\env\\azure\\Scripts\\python.exe " \
              "c:\\infodes\\bin\\backup_evolution_archivos.py"

HOST_NAME = socket.gethostname()
HOST_IP_PUBLIC = get('http://ifconfig.co/ip').text.rstrip('\n')

container_name = socket.gethostname()
container_name = container_name.lower()
container_name = container_name.replace("_", "-")

message = ""

local_path_bck = os.path.join(config.get_directory_backup())
remote_path_bck = os.path.join(config.get_container_backup())


def backup_evolution():
    try:
        bck_folder = config.get_directory_backup()

        if not os.path.exists(bck_folder):
            os.makedirs(bck_folder)

        cnxn_string = ';server={},{};database={};uid={};pwd={}'\
                      .format(config.get_backup_database_server(),
                              config.get_backup_database_port(),
                              config.get_backup_database(),
                              config.get_backup_database_user(),
                              config.get_backup_database_password())

        cnxn = pyodbc.connect('driver={ODBC Driver 17 '
                              'for SQL Server};' + cnxn_string)

        cnxn.autocommit = True
        file_bck = "{}\\evolution_backup_{}.bak"\
                   .format(bck_folder, today.strftime("%Y%m%d"))
        sql = "BACKUP DATABASE {} TO DISK = N'{}'"\
              .format(config.get_backup_database(), file_bck)

        cursor = cnxn.cursor()
        cursor.execute(sql)
        while cursor.nextset():
            pass
        cursor.close()
        cnxn.close()

        file_paths = []
        bck_folder_evolution = config.get_backup_directory_evolution()

        for root, directories, files in os.walk(bck_folder_evolution):
            for filename in files:
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)

        file_bck_evolution_files = "{}\\evolution_files_backup_{}.zip"\
                                   .format(bck_folder,
                                           today.strftime("%Y%m%d"))

        with ZipFile(file_bck_evolution_files, 'w') as zip:
            # writing each file one by one
            for file in file_paths:
                zip.write(file)
        zip.close()
        return True

    except Exception:
        return False


def verify_container(container_name):
    containers = blob_service_client.list_containers()
    create_container = True
    for container in containers:
        if container.name == container_name:
            create_container = False
            break

    if create_container:
        blob_service_client.create_container(container_name)


def copy_backup(cntnr_name):
    bck_files = [f for f in glob.glob(local_path_bck + "/**/*.*", recursive=True)]
    bck_files_integrity = {}
    for bck_file in bck_files:
        bck_files_integrity[bck_file] = hashlib.md5(open(bck_file, 'rb').read()).hexdigest()

    container_client = DirectoryClient(config.get_connection(), cntnr_name)

    get_files = container_client.ls_files(remote_path_bck)

    upload_result = {}

    if get_files:
        for file in get_files:
            if not os.path.isfile(os.path.join(local_path_bck, file)):
                container_client.rm(os.path.join(remote_path_bck, file))

    files = os.listdir(local_path_bck)
    for file in files:
        if os.path.isfile(os.path.join(local_path_bck, file)):
            if file not in get_files:
                local_path_bck_file = os.path.join(local_path_bck, file)
                remote_path_bck_file = os.path.join(remote_path_bck, file)
                upload = container_client.upload(local_path_bck_file,
                                                 remote_path_bck_file)
                upload_result.update(upload)

    return upload_result, bck_files_integrity


def remove_files():
    for file in bck_files_integrity:
        os.remove(file)


if backup_evolution():
    if os.path.isdir(local_path_bck):
        try:
            blob_service_client = BlobServiceClient.\
                                  from_connection_string(conn_str=config.
                                                         get_connection())

            verify_container(container_name)

            copy_result, bck_files_integrity = copy_backup(container_name)
            if copy_result:
                for file in copy_result:
                    if copy_result[file] != bck_files_integrity[file]:
                        message = "{}\nFile: {} Error: {}"\
                                .format(message, file, socket.gethostname())

                if message:
                    subj = "ERROR al copiar el Backup de Evolution desde {} - {} "\
                        "hasta Azure".format(HOST_NAME, HOST_IP_PUBLIC)
                    message = "Ejecutar en {} el script: {} \n"\
                              "Fallo la copia de:\n{}"\
                              .format(HOST_IP_PUBLIC, SCRIPT_NAME, message)
                else:
                    remove_files()

                    subj = "Copia exitosa del Backup de Evolution desde {} - {} "\
                        "hasta Azure".format(HOST_NAME, HOST_IP_PUBLIC)
                    message = "Copia exitosa del Backup desde {} - {} "\
                              "hasta Azure\n".format(HOST_NAME, HOST_IP_PUBLIC)
            else:
                remove_files()

        except Exception:
            subj = "ERROR al copiar Backup de Evolution desde {} - {} "\
                "hasta Azure".format(HOST_NAME, HOST_IP_PUBLIC)
            message = "Ejecutar en {} el script\n {} \n\nError {}"\
                      .format(HOST_IP_PUBLIC, SCRIPT_NAME,
                              traceback.format_exc())
else:
    subj = "ERROR al hacer Backup de Evolution desde {} - {} hasta Azure"\
           .format(HOST_NAME, HOST_IP_PUBLIC)
    message = "Ejecutar en {} el script: {} \n\n"\
              "Error {}".format(HOST_IP_PUBLIC,
                                SCRIPT_NAME, traceback.format_exc())

if message:
    sendalert(subj, message, config.get_notification_mailalert())
