import gdsfactory as gf
import miller_lib as ml
import numpy as np
from matplotlib import pyplot as plt

# Instantiate a component and set up the die
c = gf.Component()
die = c << gf.components.die((1000,4000),die_name=None)#"Hello, world")
die.movex(500) # Shift origin to corner of die
die.movey(2000)
# print(c.layers)
xsec = gf.cross_section.strip(width=1.5,layer=(733,727)) # Strip cross-section

# Add input and output grating couplers
input = c << ml.UCSB_grating_1550(False,False)
input.rotate(-90)
input.movex(500) # Make sure to get the y value right!!!
input.movey(350)
c.add_ports(input.ports,prefix="input_") # Include ports for coupling waveguides
# print(c.layers)

# output_order = [5,2,7,4,3,6]
# output_order = [1=,2=,3=,4=,5=,6=]
output = c << ml.array_UCSB_grating_1550(fid=False,bs_fid=False)
output.rotate(0)
output.movey(3500) # May need to adjust y value
output.movex(500)
c.add_ports(output.ports,prefix="output_")
# print()
# print(output.ports)
# print()

# MMI
# MMI = c << ml.myMMI1x6(cross_section=xsec)
MMI = c << ml.myMMI1x6()
# print(MMI.ports)
# print()
MMI.rotate(90)
# MMI.movex(500)
# MMI.movey(600)
MMI.connect("o1",input.ports["o1"],allow_layer_mismatch=True)
# print(MMI.ports)
# print(input.ports)


# Ring resonator column variables
yshift = 1320
xshift = 170 # 150 for m=600
rotatey = 1400
rotatex = 180
offset = 200
x_col = 250
m = 400

# Add ring resonators and connect with waveguides
# rings = c << ml.ring_arr(m=500,channel_sep=50,offset_sep=250,ysep=500) # channel_sep = 20 for m=600???
rings = c << ml.ring_arr_same_heights(m=500,channel_sep=200,offset_sep=250,ysep=500,rot_step=-170,port_layer=(733,727))
rings.movey(yshift)
rings.movex(xshift)
c.add_ports(rings.ports,prefix="rings_")

ring_ports = [c.ports["rings_col"+str(i+1)+"_o1"] for i in range(6)]
mmi_ports = [MMI.ports["o"+str(i+2)] for i in range(6)]

# connect = gf.routing.route_bundle(c,mmi_ports,ring_ports,allow_width_mismatch=False,
#                                 #   route_width=1.5,layer=(0,1),
#                                   cross_section=xsec,
#                                 #   radius=100,
#                                   bboxes=[rings.bbox()])
# _sbend
# allow_layer_mismatch=True,
connect = gf.routing.route_bundle_sbend(c,mmi_ports,ring_ports,allow_width_mismatch=False,
                                allow_layer_mismatch=True)
                                #   cross_section=xsec,
                                #   radius=100,
                                #   bboxes=[rings.bbox()])


ring_bank_ports = [c.ports["rings_col"+str(i+1)+"_o2"] for i in range(6)]
# output_order = [5,2,7,4,3,6]
output_order = [6,3,7,4,2,5]
output_ports = [c.ports["output_grating_"+str(n)+"_o1"] for n in output_order]
connect2 = gf.routing.route_bundle_sbend(c,ring_bank_ports,output_ports,allow_layer_mismatch=True,enforce_port_ordering=True)


# Plot the result 
# print()
# print(c.ports)
# c.draw_ports()
# c.write_gds(r"C:\Users\bhassard\Downloads\tmpgds.gds")
c.plot()
plt.show()

