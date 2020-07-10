"""
Develop by Jose Rojas rojasrjosee@gmail.com
Script for update IP pbx on Evolution or IP Evolution on pbx
"""

import os

from backup_windows_config import Config

config = Config()


class EvolutionServer(object):

    def __init__(self, asterisk_ip_private, asterisk_ip_public, instance_dict):
        self.asterisk_ip_private = asterisk_ip_private
        self.asterisk_ip_public = asterisk_ip_public
        self.evolution_dns = ""
        if "hostname" in instance_dict:
            self.evolution_hostname = instance_dict["hostname"]
        if "midns" in instance_dict:
            self.evolution_dns = "{}    {}".format(instance_dict["ip_lan"],
                                                   instance_dict["midns"])

    def change_ip_db(self):
        import pyodbc
        cnxn_string = ';server={},{};database={};uid={};pwd={}'\
                      .format(config.get_backup_database_server(),
                              config.get_backup_database_port(),
                              config.get_backup_database(),
                              config.get_backup_database_user(),
                              config.get_backup_database_password())

        cnxn = pyodbc.connect('driver={ODBC Driver 17 '
                              'for SQL Server};' + cnxn_string)

        cnxn.autocommit = True
        sql = "UPDATE dbo.SIPServers set Server='{}', AMIServer='{}'"\
              "where Name = 'SCM';".format(self.asterisk_ip_public,
                                           self.asterisk_ip_private)

        cursor = cnxn.cursor()
        cursor.execute(sql)
        while cursor.nextset():
            pass
        cursor.close()
        cnxn.close()

    def write_file_host(self):
        content_file = """127.0.0.1    localhost
127.0.0.1    {}
::1    localhost
{}    asterisk.ip.private
{}    asterisk.ip.public
{}
        """.format(self.evolution_hostname,
                   self.asterisk_ip_private,
                   self.asterisk_ip_public,
                   self.evolution_dns)

        outfile = open("C:\\Windows\\System32\\drivers\\etc\\hosts", "w")
        outfile.writelines(content_file)
        outfile.close()


class AsteriskServer(object):

    def __init__(self, evolution_ip_private, evolution_ip_public, instance_dict):
        self.evolution_ip_private = evolution_ip_private
        self.evolution_ip_public = evolution_ip_public
        self.asterisk_dns = ""
        if "hostname" in instance_dict:
            self.asterisk_hostname = instance_dict["hostname"]
        if "midns" in instance_dict:
            self.asterisk_dns = "{} {}".format(instance_dict["ip_lan"],
                                               instance_dict["midns"])

    def write_file_host(self):
        content_file = """127.0.0.1 {} localhost localhost.localdomain localhost4
::1 {} localhost localhost6
{} evolution.ip.private
{} evolution.ip.public
{}
        """.format(self.asterisk_hostname,
                   self.asterisk_hostname,
                   self.evolution_ip_private,
                   self.evolution_ip_public,
                   self.asterisk_dns)

        outfile = open("/etc/hosts", "w")
        outfile.writelines(content_file)
        outfile.close()

    def change_host_name(self):
        os.system("hostnamectl set-hostname {}".format(self.asterisk_hostname))
