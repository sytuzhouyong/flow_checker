# coding:utf-8

from utils import *


class Flow(object):
    """一条流表"""
    def __init__(self, text):
        self.text = text
        self.table = 0
        self.priority = 0
        self.match_fields = {}
        self.action_fields = {}

        text = text.strip()
        text = text.replace(', ', ',')
        text = text.replace(' ', ',')
        index = text.find('actions=')
        if index == -1:
            return

        fields_str = text[:index]
        actions_str = text[index + 8:]

        self.parse_match_fields(fields_str)
        self.parse_actions(actions_str)

    def parse_match_fields(self, fields_str):
        keys_values = fields_str.split(',')

        for string in keys_values:
            index = string.find('=')
            if index != -1:
                key = string[:index]
                value = string[index+1:]

                if key == 'table':
                    self.table = int(value)
                    self.match_fields['table'] = int(value)
                elif key == 'priority':
                    self.priority = int(value)
                elif key == 'dl_src' or key == 'arp_sha':
                    self.match_fields['src_mac'] = value
                elif key == 'dl_dst' or key == 'arp_tha':
                    self.match_fields['dst_mac'] = value
                elif key == 'nw_src' or key == 'arp_spa':
                    self.match_fields['src_ip'] = value
                elif key == 'nw_dst' or key == 'arp_tpa':
                    self.match_fields['dst_ip'] = value
                elif key in ['cookie', 'duration', 'n_packets', 'n_bytes', 'idle_age', 'hard_age']:
                    continue
                else:
                    if is_number_string(value):
                        self.match_fields[key] = string_to_number(value)
                    else:
                        self.match_fields[key] = value
            elif string == 'arp':
                self.match_fields['dl_type'] = 0x0806
            elif string == 'ip':
                self.match_fields['dl_type'] = 0x0800

    def parse_actions(self, actions_str):
        actions = actions_str.strip()
        actions = actions.lower()
        actions = actions.replace(', ', ',')
        actions = actions.replace(' ', ',')
        actions = actions.replace('(,', '=')  # 将resubmit变成resubmit=50这种形式

        keys_values = actions.split(',')
        for string in keys_values:
            # print(string) load:0x3->NXM_NX_REG0[0..11]
            if string.startswith('load:'):
                load_str = string[5:].strip()

                index = load_str.find('->')
                load_value = load_str[:index].strip()
                load_key = load_str[index+2:].strip()

                index = load_key.find('[')
                if index != -1:
                    load_key = load_key[:index]
                if load_key.startswith('nxm_nx_'):
                    load_key = load_key[7:].lower()

                # 如果是数字格式就全部转化成int
                if is_number_string(load_value):
                    load_value = string_to_number(load_value)

                self.action_fields[load_key] = load_value

                # print(load_key)
                # print(load_value)
            elif string.startswith('resubmit='):
                load_value = string[9:-1]
                self.action_fields['next_table'] = int(load_value)
            elif string == 'mod_vlan_vid':
                load_value = string_to_number(string[12:])
                self.action_fields['vlan'] = load_value
            elif string == 'strip_vlan':
                self.action_fields['vlan'] = 0
            elif string.startswith('output:'):
                load_value = string_to_number(string[7:])
                self.action_fields['output'] = load_value
            elif string == 'drop':
                self.action_fields['is_drop'] = 1

    def execute(self, ):
        if len(self.action_fields) == 0:
            return self

        for (key, value) in self.action_fields.items():
            self.match_fields[key] = value

        if 'next_table' in self.match_fields:
            self.table = int(self.match_fields['next_table'])
            self.match_fields['table'] = self.match_fields['next_table']
            self.match_fields.pop('next_table')

        self.action_fields.clear()

        return self
