# coding:utf-8

l2_tun_id = '0x4e20'
l3_tun_id = '0x4e30'


class Config(object):
    def __init__(self):
        self.br_ip = ''
        self.vxlan_port = 0
        self.vm_port = 0
        self.vm_ip = ''
        self.vm_mac = ''
        self.vlanif10_ip = ''
        self.vlanif10_mac = ''
        self.vlanif100_mac = ''

    @staticmethod
    def vxlan_config1():
        config = Config()
        config.br_ip = '7.0.0.3'
        config.vxlan_port = 1  # ofport_of_device
        config.vm_port = 3  # ofport_of_device
        config.vm_ip = '1.2.3.3'
        config.vm_mac = '52:54:00:00:73:03'
        return config

    @staticmethod
    def vxlan_config2():
        config = Config()
        config.br_ip = '7.0.0.4'
        config.vxlan_port = 1  # ofport_of_device
        config.vm_port = 3  # ofport_of_device
        config.vm_ip = '1.2.3.9'
        config.vm_mac = '52:54:00:00:74:03'
        return config

    @staticmethod
    def dvr_config1():
        config = Config()
        config.br_ip = '7.0.0.3'
        config.vxlan_port = 1  # ofport_of_device
        config.vm_port = 3  # ofport_of_device
        config.vm_ip = '1.2.3.3'
        config.vm_mac = '52:54:00:00:73:03'
        config.vlanif10_ip = '1.2.3.1'
        config.vlanif10_mac = '52:54:01:02:03:01'
        config.vlanif100_mac = '52:54:01:02:03:02'
        return config

    @staticmethod
    def dvr_config2():
        config = Config()
        config.br_ip = '7.0.0.4'
        config.vxlan_port = 1  # ofport_of_device
        config.vm_port = 3  # ofport_of_device
        config.vm_ip = '1.2.4.3'
        config.vm_mac = '52:54:00:00:74:03'
        config.vlanif10_ip = '1.2.4.1'
        config.vlanif10_mac = '52:54:01:02:04:01'
        config.vlanif100_mac = '52:54:01:02:04:02'
        return config


class ConfigManager(object):
    def __init__(self):
        pass

    # scene_name = vxlan
    @staticmethod
    def local_config(scene_name):
        function = ConfigManager.function_of_config_with_scene_name(scene_name, "config1")
        if function is not None:
            local_config = function()

        function = ConfigManager.function_of_config_with_scene_name(scene_name, "config2")
        if function is not None:
            remote_config = function()

        return local_config, remote_config

    @staticmethod
    def remote_config(scene_name):
        function = ConfigManager.function_of_config_with_scene_name(scene_name, "config2")
        if function is not None:
            local_config = function()

        function = ConfigManager.function_of_config_with_scene_name(scene_name, "config1")
        if function is not None:
            remote_config = function()

        return local_config, remote_config

    @staticmethod
    def function_of_config_with_scene_name(scene_name, config_name):
        config = "%s_%s" % (scene_name, config_name)
        function = getattr(Config, config)
        if function is None:
            print "Config does not have function named %s" % config

        return function
