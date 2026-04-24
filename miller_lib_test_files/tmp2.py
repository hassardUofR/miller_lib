"""Test file for miller_lib"""



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


def connect_ports_smooth(
    port1,
    port2,
    cross_section="strip",
    npoints=200,
    alpha=0.3,
):
    """
    ChatGPT function: Returns a smooth waveguide between two arbitrary (non-Manhattan) ports.

    Note that this is for a single pair of ports, so it does not prevent collisions.

    Parameters
    ----------
    port1, port2 : gf.Port
        Start and end ports
    cross_section : str or CrossSection
    npoints : int
        Number of interpolation points
    alpha : float
        Controls "tightness" of curve (0.2–0.5 typical)

    Returns
    -------
    Component with smooth connection
    """

    p0 = np.array(port1.center)
    p3 = np.array(port2.center)

    # Direction unit vectors
    def angle_to_vec(angle_deg):
        a = np.deg2rad(angle_deg)
        return np.array([np.cos(a), np.sin(a)])

    t0 = angle_to_vec(port1.orientation)
    t1 = angle_to_vec(port2.orientation+180)

    # distance-based scaling
    d = np.linalg.norm(p3 - p0)

    # control points for the Bezier curve
    L = alpha * d

    p1 = p0 + L * t0
    p2 = p3 - L * t1

    # cubic Bezier curve
    t = np.linspace(0, 1, npoints)
    curve = (
        (1 - t)[:, None] ** 3 * p0
        + 3 * (1 - t)[:, None] ** 2 * t[:, None] * p1
        + 3 * (1 - t)[:, None] * t[:, None] ** 2 * p2
        + t[:, None] ** 3 * p3
    )

    path = gf.Path(curve)
    wg = gf.path.extrude(path, cross_section=cross_section)

    return wg

def neff_index_data(radius):
    """Modeled effective refractive index as a function of ring bend radius (from OptoDesigner library)"""
    A = 0.002083680178277
    B = 4.171450309668357
    n_0 = 1.500287885368830

    neff_model = n_0 + B*np.exp(-A*radius)/radius**2
    return neff_model

@gf.cell
def shortring_single(radius,gap,bus=radius/2,cross_section="strip"):
    ring = gf.components.rings.ring(radius,cross_section=cross_section)
    bus = ring << gf.components.waveguides.straight(2*bus,cross_section=cross_section)
    ring.movex(gap)
    bus.movey(bus)
    return ring

@gf.cell
def ring_BB_single(lambda_um: float = 1.55, m: int = 600, gap: float = 0.9,
    racetrack: float = 0, bend: str = "bend_circular", **kwargs):
    """Builds a single ring resonator (single waveguide) with the OptoDesigner default parameters"""
    # Calculate radius from wavelength, number of waves, and effective index
    # Iterate 3 times to get radius from effective index using a starting estimate of 100 um of ring radius
    # - it should converge to the actual index/radius within 2-3 iterations
    radius = m*lambda_um/2/np.pi/neff_index_data(100)
    for i in range(3):
        neff = neff_index_data(radius)
        radius = m*lambda_um/2/np.pi/neff
    print(radius)
    
    ring = gf.components.rings.ring_single(radius=radius,gap=gap,length_x=racetrack,length_y=0,bend=bend,**kwargs)
    return ring

# Should this leverage ring_single_array instead of building my own array?
@gf.cell
def ring_col_scurve(num: int = 3, ysep: float | list = 400.0, xsep: list | None = None, ds: float = 30,
             cross_section=gf.cross_section.strip(),**kwargs):
    """ Builds a column (vertical channel) of ring resonators. Calls miller_lib.ring_BB_single.
    
    Args:
        num: int, optional (default is 3)
            Number of ring resonators in the channel
        
        ysep: float or list, optional (default is 400 um)
            Vertical separation between adjacent rings in the channel, i.e. [200,200,200] is evenly spaced rings 200 um apart.
            (This spacing is in addition to the thickness of the ring.)
            A single value can be passed for all the rings, or a list of length num-1 will define individual separations.
        
        xsep: list or None, optional (default is None)
            A list (length num) of x displacements from the center ring line. None is equivalent to a list of zeros.

        cross_section: ComponentSpec for rings/bus waveguides

        **kwargs: Keyword arguments for miller_lib.ring_BB_single
            
    Returns: A Component centered on the waveguide of the bottom ring, with a channel of multiple ring resonators.
        Includes input and output ports, but also the intermediate ports for each ring (unfortunately).
    """

    # Typechecking - convert xsep and ysep to lists
    if type(ysep) == float or type(ysep) == int:
        ysep = np.ones(num).astype(float) * ysep
    if xsep is None:
        xsep = np.zeros(num)

    # Define the Component
    c = gf.Component()

    # Add rings 
    for i in range(num):
        ring = c << ring_BB_single(cross_section=cross_section,**kwargs)
        radius = 65.73453642799376
        ring.rotate(-90)
        ring.movey(np.sum(ysep[:i]))
        ring.movex(xsep[i])
        c.add_ports(ring.ports,prefix="ring"+str(i+1)+"_")
        if i > 0:
            port1 = c.ports["ring"+str(i)+"_"+"o1"]
            port2 = c.ports["ring"+str(i+1)+"_"+"o2"]
            mx = 0.5*(port1.x+port2.x)
            my = 0.5*(port1.y+port2.y)
            
            def cosbump(x,wid): # Cosine curve to smoothly vary 
                t = 2*x-1
                def b(t):
                    return 0.5*(1+np.cos(np.pi*t/wid))
                def zero(t):
                    return np.zeros_like(t)
                return np.piecewise(t,[abs(t)<abs(wid)],[b,zero])
            x = np.linspace(0,1,101)
            y = cosbump(x,0.9)*ds*-1
            x *= (ysep[i] - 2*radius - 6) 
            x += ring.y + radius + 3 - ysep[i]
            y += ring.x -radius - 1.2 # gap
            points = list(zip(y,x))
            
            path = gf.path.smooth(points=points,radius=10)
            route = c << gf.path.extrude(path,cross_section=cross_section)
            
            # # route = c << gf.components.bends.bezier(control_points=((port1.x,port1.y),(mx-ds,my),(port2.x,port2.y)),cross_section=cross_section) # Disjointed...
            # route = c << connect_ports_smooth(port1,port2,cross_section=cross_section)
            # # route = gf.routing.route_bundle(c,port1=c.ports["ring"+str(i)+"_"+"o1"],port2=c.ports["ring"+str(i+1)+"_"+"o2"],
            # #                                 cross_section=cross_section)
    # for j,port in enumerate(c.ports):
    #     if j != 0 and j != len(c.ports)-1:
    #         c.remove_port[port.name]
    return c

@gf.cell
def ring_arr_scurve(num=3,channels=6,channel_sep=(50,50),offset=True,offset_sep=300,
             rot_step=-30,odd_voffset=126,cross_section=gf.cross_section.strip,
             rotate=True,**kwargs):
        
    """ Builds an array of ring resonators in multiple columnar channels (calls miller_lib.ring_col_scurve)

    Even if offset is True, the input and output waveguides/ports will be at the same height, with extra straight connections.
    This may result in slightly suboptimal connections (since straight waveguides are included that take space that might
    allow for more gradual bends), but allows for more even connections with less likelihood of collisions if used with a
    routing function such as gf.routing.route_bundle_sbend is used that does not prevent collisions.
    If the staggered IO ports are preferred, use miller_lib.ring_arr.

    Args:
        channels: int, optional (default is 6).
            Number of columns/channels of ring resonators. (Number of iterations to call miller_lib.ring_col_scurve.)

        channel_sep: tuple of floats, optional (default is ()))
            Horizontal separation between channels (waveguides) in um. First number is offset for pairs of ring columns, and second number is offset between pairs.
        
        offset: bool, optional (default is True)
            If True, offsets the rings by offset_sep in each odd column (numbered from 0).
            Intended to step the rings for closer pairing when rotate is True.
        
        offset_sep: float, optional (default is 300)
            Vertical offset between even- and odd-numbered columns (in um) if offset is True.
        
        rotate: bool, optional (Default is True)
            If True, flips across the y-axis each odd column (numbered from 0) for closer packing of channels.

        rot_step: float, optional (default is -30)
            Horizontal displacement of odd (rotated) columns if rotate is True.
            Typically negative to pull rotated and offset odd columns closer to the even ones for tighter ring packing.

        cross_section: ComponentSpec for rings/bus waveguides
        
        **kwargs: Optional keyword arguments for miller_lib.ring_col_scurve

    Returns: A Component of an array of rings. The component is centered at the base port to the lower left ring.
    """
    
    c = gf.Component()
    step = 0 # Step to the right of rotated columns

    def curved_waveguide(port1,offset,ds):
        def cosbump(x,wid): # Cosine curve to smoothly vary 
                t = 2*x-1
                def b(t):
                    return 0.5*(1+np.cos(np.pi*t/wid))
                def zero(t):
                    return np.zeros_like(t)
                return np.piecewise(t,[abs(t)<abs(wid)],[b,zero])
        x1 = port1.y
        # x2 = port2.y
        x2 = port1.y + offset
        y1 = port1.x
        # y2 = port2.x
        y2 = port1.x

        x = np.linspace(0,1,101)
        y = cosbump(x,0.9)*-1*ds
        # x *= (x2-x1)
        x *= offset
        x += x1
        y += y1
        points = list(zip(y,x))
        
        path = gf.path.smooth(points=points,radius=10)
        return gf.path.extrude(path,cross_section=cross_section)

    for i in range(channels):
        col = c << ring_col_scurve(cross_section=cross_section,**kwargs)
        
        x = 0 # Mark center for ports
        y = 0
        h = col.dysize
        
        if rotate is True:
            if i/2 != i//2:
                col.rotate(180)
                # col.movex(col.dxsize)
                col.movey(col.dysize)
                x += col.dxsize
                step += col.dxsize*0 + rot_step
        
        col.movey(-col.dymin)
        col.movex(-gf.get_cross_section(cross_section).width/2-col.dxmin) # Was the 1.5 width
        
        if (i//2)%2 == 1:
            col.movey(odd_voffset) # Offset odd channel-pairs by a certain amount (the middle two for six-channel PICs)


        col.movex(channel_sep[i%2]*i+step)
        x += channel_sep[i%2]*i+step
        if offset is True:
            if i/2 != i//2:
                col.movey(offset_sep)
                y += offset_sep
    
    
        

    # Add the staggered straight waveguides.
        if rotate is True:
            if i/2 == i//2:
                # extra = c << gf.components.waveguides.straight(length=offset_sep,cross_section=cross_section)
                # extra.connect("o1",other=col.ports["ring"+str(num)+"_o1"]) 
                radius_ = 65.73453642799376 #!!!
                offset_ = 400 - 2*radius_ - 6 + odd_voffset
                ds_ = 30

                extra = c << curved_waveguide(col.ports["ring"+str(num)+"_o1"],offset_, ds_)

                # c.add_port("col"+str(i+1)+"_o1",port=col.ports["ring1_o2"])
                # c.add_port("col"+str(i+1)+"_o2",port=extra.ports["o2"])
                c.add_ports(extra.ports,prefix="col"+str(i+1)+"_")
            else:
                # extra = c << gf.components.waveguides.straight(length=offset_sep,cross_section=cross_section)
                # extra.connect("o2",other=col.ports["ring"+str(num)+"_o1"])
                radius_ = 65.73453642799376 #!!!
                offset_ = -(400 - 2*radius_ - 6 + odd_voffset)
                ds_ = -30

                extra = c << curved_waveguide(col.ports["ring"+str(num)+"_o1"],offset_, ds_)
                
                # c.add_port("col"+str(i+1)+"_o2",port=col.ports["ring1_o2"])
                # c.add_port("col"+str(i+1)+"_o1",port=extra.ports["o1"])
                c.add_ports(extra.ports,prefix="col"+str(i+1)+"_")

    return c


m=400
# col = c << ring_arr_scurve(cross_section=xsec)
# col = c << ml.ring_arr_same_heights(m=m,channel_sep=200,offset_sep=250,ysep=500,rot_step=-170,cross_section=xsec)
col = c << ring_arr_scurve(m=m,channel_sep=(200,200),offset_sep=250,ysep=500,rot_step=-170+1.5+0.9,cross_section=xsec)
# col = c << ring_col_scurve(m=m,cross_section=xsec)

col.movex(200)
col.movey(200+1000)

c.show()

