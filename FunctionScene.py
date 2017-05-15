# coding:utf-8

from Config import *
from Scene import *
from FunctionSceneFactory import *


class FunctionScene (Scene):
    def __str__(self):
        return self.name

    def __init__(self, scene_name, dl_type, direction, env_type):
        name = "%s_%s_%s" % (scene_name, dl_type, direction)
        Scene.__init__(self, name)
        self.scene_name = scene_name
        self.dl_type = dl_type
        self.direction = direction
        self.jump_flow = Flow('')

        local_config, remote_config = FunctionScene.init_config(scene_name, env_type)
        self.local_config = local_config
        self.remote_config = remote_config

        self.init_flow()
        self.init_flows_and_rules(name)

    @staticmethod
    def init_config(scene_name, env_type):
        if env_type == "local":
            return ConfigManager.local_config(scene_name)

        if env_type == "remote":
            return ConfigManager.remote_config(scene_name)

    # TODO: 各个场景下的初始化属性
    def init_flow(self,):
        self.jump_flow.match_fields['table'] = 0

        if self.direction == 'send':
            self.jump_flow.match_fields.update(
                {'in_port': self.local_config.vm_port,
                 'src_ip':  self.local_config.vm_ip,
                 'src_mac': self.local_config.vm_mac,
                 'dst_ip':  self.remote_config.vm_ip,
                 'dst_mac': self.remote_config.vm_mac, })
        elif self.direction == 'recv':
            self.jump_flow.match_fields.update(
                {'in_port': self.local_config.vxlan_port,
                 'src_ip':  self.remote_config.vm_ip,
                 'src_mac': self.remote_config.vm_mac,
                 'dst_ip':  self.local_config.vm_ip,
                 'dst_mac': self.local_config.vm_mac, })

        if self.dl_type == 'arp':
            self.jump_flow.match_fields.update({'dl_type': int(0x0806), })
        elif self.dl_type == 'ip':
            self.jump_flow.match_fields.update({'dl_type': int(0x0800), })

        if self.direction == 'send':
            if self.scene_name == 'vxlan' and self.dl_type == 'arp':
                self.jump_flow.match_fields.update({'dst_mac': 'FF:FF:FF:FF:FF:FF'.lower(), })
            elif self.scene_name == 'dvr':
                self.jump_flow.match_fields.update({'dst_mac': self.local_config.vlanif10_mac, })
        elif self.direction == 'recv':
            if self.scene_name == 'vxlan':
                self.jump_flow.match_fields.update({'tun_id': l2_tun_id, })
            else:
                self.jump_flow.match_fields.update({'tun_id': l3_tun_id })

    # vxlan_arp_send
    def init_flows_and_rules(self, function_name):
        function = getattr(FunctionSceneFactory, function_name)
        if function is None:
            print "factory does not have function name: %s" % function_name
            return None

        flows, rules = function(self.local_config, self.remote_config)
        self.flows = flows
        self.rules = rules
