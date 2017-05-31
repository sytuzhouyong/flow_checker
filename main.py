# coding:utf-8

from BusinessScene import *


def default_l2_l3_scene():
    vxlan = VXLANScene()
    vxlan.validate()

    dvr = DVRScene()
    dvr.validate()
    
    
if __name__ == "__main__":
    default_l2_l3_scene()
