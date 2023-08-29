import json
import os.path

from constants import MAIN_DIR


class SettingsHandler:
    def __init__(self, file_path):
        self.file_path = os.path.join(MAIN_DIR, "database", file_path)

        self.data = None
        self.load()

    def set(self, key, data):
        """set data to key then save"""
        self.data[key] = data
        self.save()

    def get(self, key):
        try:
            return self.data[key]
        except KeyError:
            return False

    def load(self):
        """load file from file path, fill in if json is empty and make the file if missing"""

        if not os.path.isfile(self.file_path):

            with open(self.file_path, 'w') as outfile:
                json.dump({}, outfile, indent=1)
            self.data = {}

        else:

            with open(self.file_path, 'r') as infile:
                try:
                    self.data = json.load(infile)

                except json.decoder.JSONDecodeError:
                    self.data = {}

    def save(self):
        """save to file"""
        with open(self.file_path, 'w') as outfile:
            json.dump(self.data, outfile, indent=1)
