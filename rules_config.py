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


    def get_all(self):
        return self.json_data.get('all')


    def get_sip(self):
        return self.json_data.get('sip')
