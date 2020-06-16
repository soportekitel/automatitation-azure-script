import os
import json


class Config(object):
    json_data = {}

    def __init__(self):
        self.configfile = os.path.splitext(__file__)[0] + ".json"
        self.load()

    def load(self):
        with open(self.configfile) as json_data_file:
            self.json_data = json.load(json_data_file)

    def save(self):
        with open(self.configfile, "w") as json_file:
            json.dump(self.json_data, json_file)
            json_file.close()

    def get_account(self):
        return self.json_data.get('backup_account_name')

    def get_key(self):
        return self.json_data.get('backup_account_key')

    def get_connection(self):
        return self.json_data.get('backup_account_connection')

    def get_container_record(self):
        return self.json_data.get('backup_container_record')

    def get_day_record(self):
        return self.json_data.get('backup_day_record')

    def get_directory_record(self):
        return self.json_data.get('backup_directory_record')

    def get_container_backup(self):
        return self.json_data.get('backup_container_backup')

    def get_directory_backup(self):
        return self.json_data.get('backup_directory_backup')

    def get_container_cdr(self):
        return self.json_data.get('backup_container_cdr')

    def get_day_cdr(self):
        return self.json_data.get('backup_day_cdr')

    def get_directory_cdr(self):
        return self.json_data.get('backup_directory_cdr')

    def get_notification_mailalert(self):
        return self.json_data.get('backup_mail_alert')

    def set_account(self, values):
        self.json_data['backup_account_name'] = values
        self.save()

    def set_key(self, values):
        self.json_data['backup_account_key'] = values
        self.save()

    def set_connection(self, values):
        self.json_data['backup_account_connection'] = values
        self.save()
