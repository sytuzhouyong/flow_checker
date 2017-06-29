# coding:utf-8

import fileinput
import re
from utils import *

default_bridge = 'br-int'


class Config(object):
    def __init__(self):
        self.br_name = ''
        self.br_ip = ''
        self.vxlan_port = 0
        self.vm_port = 0
        self.vm_ip = ''
        self.vm_mac = ''
        self.vlanif10_ip = ''
        self.vlanif10_mac = ''
        self.vlanif100_mac = ''
        self.tun_id_l2 = 0
        self.tun_id_l3 = 0


class ConfigManager(object):
    def __init__(self, config_file_path):
        self.config_file = config_file_path
        self.side_configs_dict = self.read_config_file(config_file_path)

    @staticmethod
    def read_config_file(config_file_path):
        configs_dict = {}

        config_name = ''
        for line in fileinput.input(config_file_path):
            line = line.strip()

            if len(line) == 0 or line[0] == '#':
                continue

            if re.match('^\[[a-zA-Z.]+\]$', line):
                config_name = line[1:-1]
                if config_name not in configs_dict:
                    configs_dict[config_name] = {}
                continue

            index = line.find('=')
            if index == 0:
                continue

            key = line[0:index].strip()
            value = line[index+1:].strip()
            configs_dict[config_name][key] = value

        side_configs = {}
        for side, side_config_dict in configs_dict.items():
            config = Config()

            for key, value in side_config_dict.items():
                if hasattr(config, key) is not None:
                    if isinstance(getattr(config, key), int):
                        setattr(config, key, string_to_number(value))
                    else:
                        setattr(config, key, value)

            side_configs[side] = config

        return side_configs

    def get_config(self, scene_name, direction):
        key = '%s.%s' % (scene_name, direction)
        if key in self.side_configs_dict:
            return self.side_configs_dict[key]
        else:
            print 'not find config:%s in configfile: %s' % (key, self.config_file)
            return None


if __name__ == "__main__":
    side_configs_dict = ConfigManager.read_config_file("config.ini")
    print side_configs_dict
