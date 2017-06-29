# coding:utf-8

is_test = 1


test_flows = {'0': """cake
table=0, priority=105,udp,nw_src=7.0.0.4,tp_dst=4789 actions=output:2
table=0, priority=105,ip,nw_src=7.0.0.4,nw_proto=47 actions=output:2
table=0, priority=105,udp,nw_dst=7.0.0.4,tp_dst=4789 actions=LOCAL
table=0, priority=100,arp,arp_spa=7.0.0.4 actions=output:2
table=0, priority=100,arp,arp_tpa=7.0.0.4 actions=LOCAL
table=0, priority=100,tun_id=0x4e20,in_port=1 actions=load:0x1->NXM_NX_REG1[],load:0x2->NXM_NX_REG2[],mod_vlan_vid:1,resubmit(,80)
table=0, priority=100,tun_id=0x4e30,in_port=1 actions=load:0x2->NXM_NX_REG1[],load:0x2->NXM_NX_REG2[],resubmit(,80)
table=0, priority=100,in_port=3 actions=load:0x3->NXM_NX_REG0[0..11],load:0x4e->NXM_NX_TUN_ID[],load:0x1->NXM_NX_REG2[],resubmit(,50)""",
              '50': """cake
table=50, priority=100,ip,in_port=3,dl_src=52:54:00:00:73:03,nw_src=1.2.3.3 actions=resubmit(,60)
table=50, priority=100,arp,in_port=3,arp_spa=1.2.3.3,arp_sha=52:54:00:00:73:03 actions=resubmit(,60)
table=50, priority=100,ip,in_port=3,dl_src=52:54:00:00:74:03,nw_src=1.2.3.9 actions=resubmit(,60)
table=50, priority=100,arp,in_port=3,arp_spa=1.2.3.9,arp_sha=52:54:00:00:74:03 actions=resubmit(,60)
table=50, priority=95,udp,tp_dst=67 actions=resubmit(,60)
table=50, priority=90,in_port=3 actions=drop""",
              '60': """cake
table=60, priority=80 actions=resubmit(,70)""",
              '70': """cake
table=70, priority=80 actions=resubmit(,80)""",
              '80': """cake
table=80, priority=120,arp,arp_spa=0.0.0.0 actions=drop
table=80, priority=100 actions=resubmit(,85)""",
              '85': """cake
table=85, priority=120,udp,reg2=0x2,tun_id=0x4e20,tp_src=67,tp_dst=68 actions=drop
table=85, priority=120,udp,reg2=0x2,tun_id=0x4e20,tp_src=68,tp_dst=67 actions=drop
table=85, priority=80 actions=resubmit(,100)""",
              '100': """cake
table=100, priority=120,arp,tun_id=0x4e,arp_tpa=1.2.4.1 actions=resubmit(,115)
table=100, priority=100,ip,tun_id=0x4e,nw_dst=1.2.4.1 actions=resubmit(,115)
table=100, priority=100,arp,dl_dst=ff:ff:ff:ff:ff:ff actions=resubmit(,110)
table=100, priority=80 actions=resubmit(,120)""",
              '110': """cake
table=110, priority=100,arp,tun_id=0x4e,arp_tpa=1.2.3.9 actions=load:0x4e20->NXM_NX_TUN_ID[],load:0x7000003->NXM_NX_TUN_IPV4_DST[],load:0x7000004->NXM_NX_TUN_IPV4_SRC[],output:1
table=110, priority=100,arp,tun_id=0x4e20,arp_tpa=1.2.3.3 actions=strip_vlan,output:3""",
              '120': """cake
table=120, priority=120,reg2=0x1,tun_id=0x4e,dl_dst=52:54:01:02:03:01 actions=load:0x4e30->NXM_NX_TUN_ID[],load:0x2->NXM_NX_REG1[],mod_dl_src:52:54:01:02:04:02,resubmit(,140)
table=120, priority=120,reg1=0x2,reg2=0x2 actions=resubmit(,140)
table=120, priority=100,tun_id=0x4e20,dl_dst=52:54:00:00:73:03 actions=strip_vlan,output:3
table=120, priority=100,tun_id=0x4e,dl_dst=52:54:00:00:74:03 actions=load:0x4e20->NXM_NX_TUN_ID[],load:0x7000003->NXM_NX_TUN_IPV4_DST[],load:0x7000004->NXM_NX_TUN_IPV4_SRC[],output:1
table=120, priority=80 actions=resubmit(,130)""",
              '140': """cake
table=140, priority=80 actions=resubmit(,150)""",
              '150': """cake
table=150, priority=100,ip,tun_id=0x4e30,nw_dst=1.2.3.3 actions=mod_dl_dst:52:54:01:02:03:02,load:0x7000003->NXM_NX_TUN_IPV4_DST[],load:0x7000004->NXM_NX_TUN_IPV4_SRC[],output:1
table=150, priority=100,ip,tun_id=0x4e30,nw_dst=1.2.4.3 actions=mod_dl_dst:52:54:00:00:74:03,mod_dl_src:52:54:01:02:04:01,output:3""",
              }
