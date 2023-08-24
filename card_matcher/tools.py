import os
import json

main_dir = os.path.dirname(os.path.abspath(__file__))


def load_user_settings():
    print('loading user settings')
    with open(f'{main_dir}/settings/user_settings.json', 'r') as infile:
        settings = json.load(infile)
    if settings is None:
        return {}
    else:
        return settings


def save_user_settings(f_settings):
    print('saving user settings')
    with open(f'{main_dir}/settings/user_settings.json', 'w') as outfile:
        json.dump(f_settings, outfile, indent=1)
