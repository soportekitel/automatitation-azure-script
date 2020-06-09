"""
Develop by Jose Rojas rojasrjosee@gmail.com
Script for update IP pbx on Evolution or IP Evolution on pbx
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

from backup_windows_config import *

config = Config()

class EvolutionServer(object):

    def __init__(self, asterisk_ip_private, asterisk_ip_public, hostname):
        self.asterisk_ip_private = asterisk_ip_private
        self.asterisk_ip_public = asterisk_ip_public
        self.evolution_hostname = hostname

        def change_ip_db(self):
            cnxn = pyodbc.connect('driver={ODBC Driver 17 for SQL Server};server=' + \
                                   config.get_backup_database_server() + ','+ \
                                   config.get_backup_database_port() + ';database=' + \
                                   config.get_backup_database() + ';uid='+ \
                                   config.get_backup_database_user() + ';pwd=' + \
                                   config.get_backup_database_password())

            cnxn.autocommit = True
            sql = "UPDATE dbo.SIPServers set Server='" + self.asterisk_ip_public + "', AMIServer='" + self. asterisk_ip_private + "' where Name = 'SCM';"

            cursor = cnxn.cursor()
            cursor.execute(sql)
            while cursor.nextset():
                  pass
            cursor.close()
            cnxn.close()

        def write_file_host(self):
            content_file="""127.0.0.1    localhost
127.0.0.1    evo01-spmad
127.0.0.1    {}
::1    localhost
{}    asterisk.ip.private
{}    asterisk.ip.public
            """.format(self.evolution_hostname, self.asterisk_ip_private, self.asterisk_ip_public)
            outfile = open("C:\Windows\System32\drivers\etc\hosts", "w")
            outfile.writelines(content_file)
            outfile.close()

class AsteriskServer(object):

    def __init__(self, evolution_ip_private, evolution_ip_public, hostname):
        self.evolution_ip_private = evolution_ip_private
        self.evolution_ip_public = evolution_ip_public
        self.asterisk_hostname = host_name

    def write_file_host(self):
        content_file="""127.0.0.1 {} localhost localhost.localdomain localhost4
::1 {} localhost localhost6
{} evolution.ip.private
{} evolution.ip.public
        """.format(self.asterisk_hostname, self.asterisk_hostname, self.evolution_ip_private, self.evolution_ip_public)
        outfile = open("/etc/hosts", "w")
        outfile.writelines(content_file)
        outfile.close()

    def change_host_name(self):
        os.system("hostnamectl set-hostname {}".format(self.asterisk_hostname))
