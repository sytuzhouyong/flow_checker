# coding:utf-8

from Config import *
from Scene import *
from FunctionSceneFactory import *


class FunctionScene (Scene):
    def __str__(self):
        return self.name

    # config_type: local / remote
    # direction: send / recv
    # pkt_type: request / reply
    def __init__(self, scene_name, config_type, direction, dl_type, pkt_type, config_manager):
        name = "%s_%s_%s" % (scene_name, dl_type, direction)
        Scene.__init__(self, name)
        self.scene_name = scene_name
        self.dl_type = dl_type
        self.direction = direction
        self.pkt_type = pkt_type
        self.config_manager = config_manager
        self.jump_flow = Flow('')

        local_config, remote_config = self.init_config(scene_name, config_type)
        self.local_config = local_config
        self.remote_config = remote_config

        self.init_flow()
        self.init_flows_and_rules(name)

    def init_config(self, scene_name, config_type):
        config_send = self.config_manager.get_config(scene_name, 'send')
        config_recv = self.config_manager.get_config(scene_name, 'recv')

        if config_type == "local":
            return config_send, config_recv

        if config_type == "remote":
            return config_recv, config_send

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

        updated_fields = {}
        if 'vxlan' in self.scene_name and self.dl_type == 'arp':
            if self.direction == 'send':
                if self.pkt_type == 'request':
                    updated_fields.update({'dst_mac': 'FF:FF:FF:FF:FF:FF'.lower(), 'src_mac': self.local_config.vm_mac})
                elif self.pkt_type == 'reply':
                    updated_fields.update({'dst_mac': self.remote_config.vm_mac, 'src_mac': self.local_config.vm_mac})
            elif self.direction == 'recv':
                if self.pkt_type == 'request':
                    updated_fields.update({'dst_mac': 'FF:FF:FF:FF:FF:FF'.lower(), 'src_mac': self.remote_config.vm_mac})
                elif self.pkt_type == 'reply':
                    updated_fields .update({'dst_mac': self.local_config.vm_mac, 'src_mac': self.remote_config.vm_mac})

        if 'dvr' in self.scene_name:
            updated_fields.update({'dst_mac': self.local_config.vlanif10_mac, })
        
        if self.direction == 'recv':
            if 'vxlan' in self.scene_name:
                updated_fields.update({'tun_id': l2_tun_id})
            else:
                updated_fields.update({'tun_id': l3_tun_id})

        self.jump_flow.match_fields.update(updated_fields)

    # vxlan_arp_send
    def init_flows_and_rules(self, function_name):
        function = getattr(FunctionSceneFactory, function_name)
        if function is None:
            print "factory does not have function name: %s" % function_name
            return None

        flows, rules = function(self.local_config, self.remote_config)
        self.flows = flows
        self.rules = rules
