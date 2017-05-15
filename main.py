# coding:utf-8

from BusinessScene import *


if __name__ == "__main__":
    vxlan = VXLANScene()
    vxlan.validate()

    dvr = DVRScene()
    dvr.validate()
