# coding:utf-8

from FunctionScene import *


class BusinessScene:
    def __init__(self, name):
        self.name = name
        self.scenes = []

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
    def __init__(self):
        name = "vxlan"
        BusinessScene.__init__(self, name)
        arp_send = FunctionScene(name, "local", "send", "arp", "request")
        arp_recv = FunctionScene(name, "local", "recv", "arp", "reply")
        ip_send = FunctionScene(name, "local", "send", "ip", "request")
        ip_recv = FunctionScene(name, "local", "recv", "ip", "reply")
        self.scenes = [arp_send, arp_recv, ip_send, ip_recv]
        # self.scenes = [arp_recv]


class DVRScene (BusinessScene):
    def __init__(self):
        name = "dvr"
        BusinessScene.__init__(self, name)
        ip_send = FunctionScene(name, "local", "send", "ip", "request")
        ip_recv = FunctionScene(name, "local", "recv", "ip", "reply")
        self.scenes = [ip_send, ip_recv]

