
import gdsfactory as gf
import miller_lib as ml
import numpy as np
from matplotlib import pyplot as plt
from functools import partial

gf.gpdk.PDK.activate()



@gf.cell
def shortring_single(radius,gap,buslength=None,cross_section="strip"):
    if buslength is None:
        buslength = radius
        buslength = 2*np.sqrt(1-(1-1.55/radius)**2)*radius # gap # Should I go to double/triple the gap, or gap+lambda_0?
        buslength = 2*radius*(1-np.sqrt(1-1.55**2/radius**2))
        print(buslength)
    c = gf.Component()
    xsec = gf.get_cross_section(cross_section)
    ring = c << gf.components.rings.ring(radius,width=xsec.width,layer=xsec.layer).copy()
    bus = c << gf.components.waveguides.straight(buslength,cross_section=cross_section)
    # marker = c << gf.components.circle(radius=1)
    # ring.movex(-radius)
    bus.rotate(-90)
    ring.movex(-radius-xsec.width-gap)
    bus.movey(buslength/2)
    return c


xs = partial(gf.cross_section.strip,width=1.5,layer=(733,727),port_names=("o1","o2")) # Strip cross-section
radius = 65
gap = 0.3
# radius = 100
gap = 0

c = gf.Component()
ring = c << shortring_single(radius,gap,cross_section=xs)

c.show()

