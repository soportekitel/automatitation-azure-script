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

    def get_mailfrom(self):
        return self.json_data.get('mailfrom')

    def get_mailuser(self):
        return self.json_data.get('mailuser')

    def get_mailpassword(self):
        return self.json_data.get('mailpassword')

    def get_mailserver(self):
        return self.json_data.get('mailserver')

    def get_mailserver_port(self):
        return self.json_data.get('mailserver_port')

    def get_notification_mailalert(self):
        return self.json_data.get('mail_alert')
