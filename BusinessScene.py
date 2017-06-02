# coding:utf-8

from FunctionScene import *


class BusinessScene:
    def __init__(self, name, config_file):
        self.name = name
        self.scenes = []
        self.config_manager = ConfigManager(config_file)

    def validate(self,):
        for function_scene in self.scenes:
            result, _ = function_scene.validate()
            if result is not True:
                print "%s validate failed" % function_scene.name
                return False
            print "%s validate success" % function_scene.name
            print ""
        return True


class VXLANScene (BusinessScene):
    def __init__(self, config_file):
        name = "vxlan"
        BusinessScene.__init__(self, name, config_file)
        arp_send = FunctionScene(name, "local", "send", "arp", "request", self.config_manager)
        arp_recv = FunctionScene(name, "local", "recv", "arp", "reply", self.config_manager)
        ip_send = FunctionScene(name, "local", "send", "ip", "request", self.config_manager)
        ip_recv = FunctionScene(name, "local", "recv", "ip", "reply", self.config_manager)
        self.scenes = [arp_send, arp_recv, ip_send, ip_recv]
        # self.scenes = [arp_recv]


class DVRScene (BusinessScene):
    def __init__(self, config_file):
        name = "dvr"
        BusinessScene.__init__(self, name, config_file)
        ip_send = FunctionScene(name, "local", "send", "ip", "request", self.config_manager)
        ip_recv = FunctionScene(name, "local", "recv", "ip", "reply", self.config_manager)
        self.scenes = [ip_send, ip_recv]
