""" v0008
FuelBot config tools
"""
import configparser
import os


class Config:
    config = configparser.ConfigParser()
    config_file_path = 'fuelbot.cfg'

    def __init__(self, config_file_path='fuelbot.cfg'):
        self.config_file_path = os.path.expanduser(config_file_path)
        self.load_config()

    def load_config(self):
        # Load configuration parameters
        if os.path.exists(self.config_file_path):
            self.config.read(self.config_file_path)
        else:
            self.set_default_config()

    def set_default_config(self):
        # Set default configuration'
        self.config['telegram'] = {}
        self.config['telegram']['bot_token'] = '102896sfghsfghsfgnsfgnsVhGzTnMsznT7OUjgrzU1MjgY'
        self.config['tg_admins'] = {}
        self.config['tg_admins']['263255207'] = '263255207'
        self.config['tg_admins']['297360613'] = '297360613'
        self.config['tg_admins']['421392418'] = '421392418'
        self.config['tg_admins']['696626950'] = '696626950'
        self.config['tg_admins']['158450093'] = '158450093'
        self.config['tg_admins']['429032923'] = '429032923'
        self.config['tg_admins']['340851561'] = '340851561'
        self.config['tg_drivers'] = {}
        self.config['tg_drivers']['1270451600'] = '1270451600'

        with open(self.config_file_path, 'w') as config_file:
            self.config.write(config_file)

    def get(self):
        # Obtain configuration
        return self.config
