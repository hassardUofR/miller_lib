import gdsfactory as gf
import miller_lib as ml
import numpy as np
from matplotlib import pyplot as plt
from functools import partial

gf.gpdk.PDK.activate()

# Instantiate a component and set up the die
c = gf.Component()

xsec = partial(gf.cross_section.strip,width=1.5,layer=(733,727),port_names=("o1","o2")) # Strip cross-section
# rings = c << ml.ring_arr_same_heights(m=500,channel_sep=200,offset_sep=250,ysep=500,rot_step=-170,port_layer=(733,727),cross_section=xsec)
# rings = c << ml.ring_col(m=500,ysep=500,cross_section=xsec)


rings = c << ml.ring_arr_same_heights(m=500,ysep=500,channel_sep=200,offset_sep=250,cross_section=xsec)

c.add_ports(rings.ports,prefix="rings_")

# Save the output
# c.write_gds(r"D:\blmgrp\Downloads\tmpgds.gds")
c.show()
