# coding:utf-8

from BusinessScene import *


def default_l2_l3_scene():
    vxlan = VXLANScene('config-default.ini')
    vxlan.validate()

    dvr = DVRScene('config-default.ini')
    dvr.validate()


if __name__ == "__main__":
    default_l2_l3_scene()
