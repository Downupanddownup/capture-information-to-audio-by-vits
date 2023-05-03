import configparser

class ConfigFile:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file_path)
        self.config_data = dict(self.config.items(self.config.sections()[0]))

    def get(self, key):
        return self.config_data.get(key)

    def set(self, key, value):
        self.config.set(self.config.sections()[0], key, value)
        with open(self.config_file_path, 'w') as configfile:
            self.config.write(configfile)
        self.config_data = dict(self.config.items(self.config.sections()[0]))

    def delete(self, key):
        self.config.remove_option(self.config.sections()[0], key)
        with open(self.config_file_path, 'w') as configfile:
            self.config.write(configfile)
        self.config_data = dict(self.config.items(self.config.sections()[0]))

    def show_all(self):
        return self.config_data
