"""This is a test design using miller_lib to recreate a 1x4 18-plex ring resonator sensor.

My goal is to make the miller_lib functions able to 100% replicate a RACER 5 sensor  (including grating location for coupling, ring location for SX printing, and nitride fill).
"""


import gdsfactory as gf
import miller_lib as ml
import numpy as np
from matplotlib import pyplot as plt
from functools import partial

gf.gpdk.PDK.activate()

# Instantiate a component and set up the die
c = gf.Component()
die = c << gf.components.die((1000,4000),die_name=None,layer=(726,727),bbox_layer=None)
die.movex(500) # Shift origin to corner of die
die.movey(2000)


xsec = partial(gf.cross_section.strip,width=1.5,layer=(733,727),port_names=("o1","o2")) # Strip cross-section


# Add input and output grating couplers
input = c << ml.UCSB_grating_1550(False,False)
input.rotate(-90)
input.movex(500) 
input.movey(350+50-5) # Make sure to get the y value right!!!
c.add_ports(input.ports,prefix="input_") # Include ports for coupling waveguides


# output = c << ml.array_UCSB_grating_1550(fid=False,bs_fid=False)
output = c << ml.array_UCSB_grating_1550_straight() # Using fixed/straightened function.
output.rotate(0)
output.movey(3500+105) # May need to adjust y values here too
output.movex(500)
c.add_ports(output.ports,prefix="output_")

# MMI
MMI = c << ml.myMMI1x6(cross_section=xsec)
MMI.rotate(90)
MMI.connect("o1",input.ports["o1"],allow_layer_mismatch=True)


# Ring resonator column variables
yshift = 1320
xshift = 170 # 150 for m=600
rotatey = 1400
rotatex = 180
offset = 200
x_col = 250
m = 400

# # Add ring resonators and connect with waveguides
# # rings = c << ml.ring_arr(m=500,channel_sep=50,offset_sep=250,ysep=500) # channel_sep = 20 for m=600???
rings = c << ml.ring_arr_same_heights(m=500,channel_sep=200,offset_sep=250,ysep=500,rot_step=-170,cross_section=xsec)
rings.movey(yshift)
rings.movex(xshift)
c.add_ports(rings.ports,prefix="rings_")

ring_ports = [c.ports["rings_col"+str(i+1)+"_o1"] for i in range(6)]
mmi_ports = [MMI.ports["o"+str(i+2)] for i in range(6)]

connect = gf.routing.route_bundle_sbend(c,mmi_ports,ring_ports,cross_section=xsec)


ring_bank_ports = [c.ports["rings_col"+str(i+1)+"_o2"] for i in range(6)]
output_order = [6,3,7,4,2,5]
output_ports = [c.ports["output_grating_"+str(n)+"_"] for n in output_order]
connect2 = gf.routing.route_bundle_sbend(c,ring_bank_ports,output_ports,cross_section=xsec,enforce_port_ordering=True) #allow_layer_mismatch=False


# Plot or save the result 
# c.write_gds(r"D:\blmgrp\Downloads\tmpgds.gds") # Save the file as a GDS

# # These translations/rotations move the PIC to line up with Michael's RACER 5 GDS files for comparison of locations.
# c.rotate(180)
# c.movex(-100+1000)
# c.movey(-100+4000)

c.show() # Open the design in KLayout
