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

    def get_ddns(self):
        return self.json_data.get('ddns')

    def get_security_group_name(self):
        return self.json_data.get('security_group_name')

    def get_resource_group_name(self):
        return self.json_data.get('resource_group_name')

    def get_subscription_id(self):
        return self.json_data.get('subscription_id')

    def get_client_id(self):
        return self.json_data.get('client_id')

    def get_tenant(self):
        return self.json_data.get('tenant')

    def get_secret(self):
        return self.json_data.get('secret')

    def get_os_system(self):
        return self.json_data.get('os_system')

    def get_evolution(self, values):
        return self.json_data.get('evolution')

    def get_asterisk(self, values):
        return self.json_data.get('asterisk')

    def set_os_system(self, values):
        self.json_data['os_system'] = values
        self.save()

    def set_ddns(self, values):
        self.json_data['ddns'] = values
        self.save()

    def set_security_group_name(self, values):
        self.json_data['security_group_name'] = values
        self.save()

    def set_resource_group_name(self, values):
        self.json_data['resource_group_name'] = values
        self.save()

    def set_asterisk(self, values):
        self.json_data['asterisk'] = values
        self.save()

    def set_evolution(self, values):
        self.json_data['evolution'] = values
        self.save()
