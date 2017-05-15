# coding:utf-8

from Flow import *
from FlowRule import *
from FunctionScene import *

flow0_send_str = 'table=0, priority=100, in_port=%d, ' \
                 'actions=load:0x1->NXM_NX_REG2[], load:0x6e->NXM_NX_TUN_ID[],resubmit(,50)'
flow0_recv_str = 'table=0,priority=100,tun_id=%s,in_port=%d ' \
                 'actions=load:%d->NXM_NX_REG1[],load:2->NXM_NX_REG2[],mod_vlan_vid:0x1,resubmit(,80)'
flow50_arp_send_str = 'table=50,priority=100,in_port=%d,arp,arp_sha=%s,arp_spa=%s,actions=resubmit(,60)'
flow50_ip_send_str = 'table=50,priority=100,in_port=%d,ip,dl_src=%s,nw_src=%s,actions=resubmit(,60)'
flow60 = Flow('table=60,priority=80,actions=resubmit(,70)')
flow70 = Flow('table=70,priority=80,actions=resubmit(,80)')
flow80 = Flow('table=80,priority=100,actions=resubmit(,85)')
flow85 = Flow('table=85,priority=80,actions=resubmit(,100)')
flow100_arp = Flow('table=100,priority=100,arp,dl_dst=ff:ff:ff:ff:ff:ff,actions=resubmit(,110)')
flow100_default = Flow('table=100,priority=80,actions=resubmit(,120)')
flow120_recv_to_l3 = Flow('table=120,priority=120,reg1=2,reg2=2,actions=resubmit(,140)')
flow140_default = Flow('table=140,priority=80,actions=resubmit(,150)')


class FunctionSceneFactory:
    def __init__(self):
        pass

    @staticmethod
    def vxlan_arp_send(local, remote):
        flow0_send = Flow(flow0_send_str % local.vm_port)
        flow50_arp_send = Flow(flow50_arp_send_str % (local.vm_port, local.vm_mac, local.vm_ip))
        flow110_arp_send = \
            Flow("table=110,priority=100,tun_id=0x6e,arp,arp_tpa=%s,actions=load:0x6e20->NXM_NX_TUN_ID[],"
                 "load:%s->NXM_NX_TUN_IPV4_DST[],load:%s->NXM_NX_TUN_IPV4_SRC[],output:%d"
                 % (remote.vm_ip, ip_hex_string(remote.br_ip), ip_hex_string(local.br_ip), local.vxlan_port))

        flows = [flow0_send, flow50_arp_send, flow60, flow70, flow80, flow85, flow100_arp, flow110_arp_send]
        rules = FlowRule.parse_rules_str('table0.action.tun_id == table110.match.tun_id')
        return flows, rules

    @staticmethod
    def vxlan_arp_recv(local, _):
        flow0_recv = Flow(flow0_recv_str % (l2_tun_id, local.vxlan_port, 1))
        flow120_arp_recv = \
            Flow('table=120,priority=100,tun_id=%s,arp,dl_dst=%s actions=strip_vlan,output:%d'
                 % (l2_tun_id, local.vm_mac, local.vm_port))

        flows = [flow0_recv, flow80, flow85, flow100_default, flow120_arp_recv]
        # rules = FlowRule.parse_rules_str('table0.match.tun_id != 0')
        return flows, []

    @staticmethod
    def vxlan_ip_send(local, remote):
        flow0_send = Flow(flow0_send_str % local.vm_port)
        flow50_ip_send = Flow(flow50_ip_send_str % (local.vm_port, local.vm_mac, local.vm_ip))
        flow120_ip_send = \
            Flow('table=120,priority=100,dl_dst=%s,tun_id=0x6e actions=load:0x6e20->NXM_NX_TUN_ID[],'
                 'load:%s->NXM_NX_TUN_IPV4_DST[],load:%s->NXM_NX_TUN_IPV4_SRC[],output:%d'
                 % (remote.vm_mac, ip_hex_string(remote.br_ip), ip_hex_string(local.br_ip), local.vxlan_port))

        flows = [flow0_send, flow50_ip_send, flow60, flow70, flow80, flow85, flow100_default, flow120_ip_send]
        rules = FlowRule.parse_rules_str('table0.action.tun_id == table120.match.tun_id')
        return flows, rules

    @staticmethod
    def vxlan_ip_recv(local, _):
        flow0_recv = Flow(flow0_recv_str % (l2_tun_id, local.vxlan_port, 1))
        flow120_ip_recv = Flow('table=120,priority=100,tun_id=%s,dl_dst=%s actions=strip_vlan,output:%d'
                               % (l2_tun_id, local.vm_mac, local.vm_port))

        flows = [flow0_recv, flow80, flow85, flow100_default, flow120_ip_recv]
        # rules = FlowRule.parse_rules_str('table0.match.tun_id != 0')
        return flows, []

    @staticmethod
    def dvr_ping_gateway(self, local, remote):
        pass

    @staticmethod
    def dvr_ip_send(local, remote):
        flow0_send = Flow(flow0_send_str % local.vm_port)
        flow50_ip_send = Flow(flow50_ip_send_str % (local.vm_port, local.vm_mac, local.vm_ip))
        flow120_to_gateway = Flow('table=120, priority=120,reg2=1,tun_id=0x6e,dl_dst=%s, actions='
                                  'load:0x6e30->NXM_NX_TUN_ID[],load:0x02->NXM_NX_REG1[],mod_dl_src:%s,resubmit(,140)'
                                  % (local.vlanif10_mac, local.vlanif100_mac))
        flow150 = Flow('table=150, priority=100,ip,tun_id=0x6e30,nw_dst=%s, actions='
                       'mod_dl_dst:%s,load:%s->NXM_NX_TUN_IPV4_DST[],load:%s->NXM_NX_TUN_IPV4_SRC[],output:%d'
                       % (remote.vm_ip, remote.vlanif100_mac, ip_hex_string(remote.br_ip),
                          ip_hex_string(local.br_ip), local.vxlan_port))
        flows = [flow0_send, flow50_ip_send, flow60, flow70, flow80, flow85, flow100_default, flow120_to_gateway,
                 flow140_default, flow150]
        rules = FlowRule.parse_rules_str('table0.action.tun_id == table120.match.tun_id '
                                         '&& table120.action.tun_id == table150.match.tun_id')
        return flows, rules

    @staticmethod
    def dvr_ip_recv(local, _):
        flow0_recv = Flow(flow0_recv_str % (l3_tun_id, local.vxlan_port, 2))
        flow150 = Flow('table=150,priority=100,ip,tun_id=%s,nw_dst=%s,actions=mod_dl_dst:%s,mod_dl_src:%s,output:%d'
                       % (l3_tun_id, local.vm_ip, local.vm_mac, local.vlanif10_mac, local.vm_port))
        flows = [flow0_recv, flow80, flow85, flow100_default, flow120_recv_to_l3, flow140_default, flow150]
        # rules = FlowRule.parse_rules_str('table0.match.tun_id != 0')
        return flows, []
