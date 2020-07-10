"""
Develop by Jose Rojas rojasrjosee@gmail.com
Script for copy cdr csv files to Azure
"""

import datetime
import glob
import hashlib
import os
import pdb
import socket
import sys
import traceback
import pymysql
import pandas

from azure.storage.blob import BlobServiceClient
from requests import get

from azure_container_access import DirectoryClient
from backup_config import Config
from sendmail import sendalert

config = Config()
script_path = "/usr/local/infodes/bin/backup_table_cdr.sh | "\
              "/usr/local/infodes/azure/env/azure/bin/python "\
              "/usr/local/infodes/bin/{}".format(os.path.basename(__file__))

host_name = socket.gethostname()
host_ip_public = get('http://ifconfig.co/ip').text.rstrip('\n')

container_name = socket.gethostname()
container_name = container_name.lower()
container_name = container_name.replace("_", "-")

today = datetime.datetime.today()
today_30days_ago = datetime.datetime.today() - datetime.timedelta(days=30)
today_90days_ago = datetime.datetime.today() - datetime.timedelta(days=120)
year_cdr = today_30days_ago.strftime("%Y")
month_cdr = today_30days_ago.strftime("%m")
month_cdr_3 = today_90days_ago.strftime("%m")

message = ""
local_path_cdr = os.path.join(config.get_directory_cdr(), year_cdr)
remote_path_cdr = os.path.join(config.get_container_cdr(), year_cdr)
local_cdr_csv_file = "{}/CDR_{}_{}.csv"\
                     .format(local_path_cdr, year_cdr, month_cdr)

if not os.path.exists(local_path_cdr):
    os.makedirs(local_path_cdr)

run_backup = False
if len(sys.argv) > 1:
    run_backup = True
elif today.strftime("%-d") == config.get_day_cdr():
    run_backup = True


def db_connect():
    return pymysql.connect(host=config.get_backup_database_server(),
                           user=config.get_backup_database_user(),
                           password=config.get_backup_database_password(),
                           database=config.get_backup_database())


def db_backup():
    query = "select * from cdr where DATE_FORMAT(calldate ,'%Y-%m') = "\
        "'{}-{}'".format(year_cdr, month_cdr)
    results = pandas.read_sql_query(query, conn)
    results.to_csv(local_cdr_csv_file, index=False)


def db_delete_month():
    query = "DELETE from cdr where DATE_FORMAT(calldate , '%Y-%m') = "\
        "'{}-{}'".format(year_cdr, month_cdr_3)
    conn.execute(query)
    query = "OPTIMIZE TABLE cdr;"
    conn.execute(query)
    query = "ANALYZE TABLE cdr;"
    conn.execute(query)


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
    conn = db_connect()
    db_backup()
    if os.path.isfile(local_cdr_csv_file):

        try:
            blob_service_client = BlobServiceClient.\
                                  from_connection_string(conn_str=config.
                                                         get_connection())

            verify_container(container_name)

            cdr_files = [f for f in glob.glob(local_path_cdr + "/**/*.*",
                                              recursive=True)]
            cdr_files_integrity = {}
            for cdr_file in cdr_files:
                cdr_files_integrity[cdr_file] = \
                    hashlib.md5(open(cdr_file, 'rb').read()).hexdigest()

            container_client = DirectoryClient(config.get_connection(),
                                               container_name)

            upload_result = container_client.upload(local_path_cdr,
                                                    remote_path_cdr)

            for file in cdr_files_integrity:
                if upload_result[file] == cdr_files_integrity[file]:
                    os.remove(file)
                else:
                    message = "{}\nFile: {} Error: {}"\
                              .format(message, file, socket.gethostname())

            if message:
                subj = "ERROR al copiar CDR desde {} - {} hasta Azure"\
                       .format(host_name, host_ip_public)
                message = "Ejecutar en {}: {}'\n\n"\
                          "Fallo la copia en:\n{}"\
                          .format(host_ip_public, script_path, message)
            else:
                subj = "Copia exitosa del CDR desde {} - {} hasta Azure"\
                       .format(host_name, host_ip_public)
                message = "Copia exitosa del CDR desde {} - {} hasta Azure\n"\
                          .format(host_name, host_ip_public)
                files = os.listdir(local_path_cdr)
                db_delete_month()
                if not files:
                    os.rmdir(local_path_cdr)
                    message = "{}\n\nCarpeta {} borrada del servidor"\
                              .format(message, local_path_cdr)
                else:
                    message = "{}\n\nLa carpeta '{}' no fue borrada del "\
                              "servidor.\nHay archivos que no se pueden "\
                              "borrar.\n\nPor favor verifique"\
                              .format(message, local_path_cdr)

        except Exception:
            subj = "ERROR al copiar CDR desde {} - {} hasta Azure"\
                   .format(host_name, host_ip_public)
            message = "Ejecutar la secuencia de comandos en '{}':\n{}\n\n" \
                      "Error {}".format(host_ip_public,
                                        script_path, traceback.format_exc())

    else:
        subj = "ERROR para subir CDR desde {} - {} hasta Azure"\
               .format(host_name, host_ip_public)
        message = "No hay archivo de CDR en '/var/spool/asterisk/cdr' "\
                  "para subir a Azure.\n\nEjecutar la secuencia de "\
                  "comandos en '{}':\n{}".format(host_ip_public, script_path)

    if message:
        sendalert(subj, message)
