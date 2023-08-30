import json

from constants import MAIN_DIR


def load_user_settings():
    print('loading user settings')
    with open(f'{MAIN_DIR}/detectors/settings/user_settings.json', 'r') as infile:
        settings = json.load(infile)
    if settings is None:
        return {}
    else:
        return settings


def save_user_settings(f_settings):
    print('saving user settings')
    with open(f'{MAIN_DIR}/detectors/settings/user_settings.json', 'w') as outfile:
        json.dump(f_settings, outfile, indent=1)
