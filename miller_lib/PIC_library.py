import gdsfactory as gf
import numpy as np
from matplotlib import pyplot as plt
from functools import partial

from time import time




@gf.cell # This decorator helps gdsfactory with its strict no-duplicate naming requirements if multiple instances are called
def UCSB_grating_1550(fid=False,bs_fid=False,
                      gds_library_path = "./miller_lib/gds_files/"): # C:/Users/bhassard/Box/BLMGroup/Layouts/RACER_5/URMC_SPT/library
    """Imports the 1550 nm grating coupler from the Meinhart lab at UCSB
    
    Args:
        fid, bs_fid: bool, optional (default is False)
            Include front- and back-side fiducials

        gds_library_path: str, optional (default is "C:/Users/bhassard/Box/BLMGroup/Layouts/RACER_5/URMC_SPT/library")
            Path to the /URMC_SPT/library directory where the UCSB GDS files are located.
            I should make this a local directory...

    Returns:
        A GDSFactory Component of the grating coupler in two (FN/SN) layers: (733/727) and (735/727)
    """

    c = gf.Component()
    # Access the GDS file from UCSB/Carl Meinhart
    if fid is True:
        gds_filename_fn = gds_library_path+"/coupler_1550nm__fx_174pt73429um_fz_500_um_LayerFN_NJ_V2.gds"
    else:
        gds_filename_fn = gds_library_path+"/coupler_1550nm__fx_174pt73429um_fz_500_um_LayerFN_NJ_V2_noFiducials.gds"
    gds_filename_sn = gds_library_path+"/coupler_1550nm__fx_174pt73429um_fz_500_um_LayerSN_NJ_V3.gds"

    fn = c << gf.import_gds(gds_filename_fn)
    sn = c << gf.import_gds(gds_filename_sn)

    # Add port
    c.add_port(name="o1",center=(-100,0),width=1.5,orientation=180,layer=c.layers[-2])

    c.movex(-180) # This appears to center the gds for rotation around the actual grating (i.e. for building the grating array)
    return c

@gf.cell # This decorator helps gdsfactory with its strict no-duplicate naming requirements if multiple instances are called
def UCSB_grating_1550_straightened(grating_angle=0,output_angle=90,radius=50,euler_part=0.2,straight1=10,straight2=10,**kwargs): # C:/Users/bhassard/Box/BLMGroup/Layouts/RACER_5/URMC_SPT/library
    """Calls UCSB_grating_1550 but adds an extruded Path to make the port at 180 degrees.
    """

    c = gf.Component()

    grating = c << UCSB_grating_1550(**kwargs)
    grating.rotate(grating_angle)



    path1 = gf.path.straight(length=straight1)
    path2 = gf.path.euler(radius=radius,angle=output_angle-grating_angle,p=euler_part)
    path3 = gf.path.straight(length=straight2)

    p = path1+path2+path3

    # xsec = gf.cross_section.strip(width=1.5,layer=(733,727),port_names=("in","out"))
    xsec = partial(gf.cross_section.strip,width=1.5,layer=(733,727),port_names=("in","out"))
    
    curve = c << gf.path.extrude(p,cross_section=xsec)
    curve.connect("in",other=grating.ports["o1"])

    c.add_ports(curve.ports) # Include ports for coupling waveguides
    c.flatten()
    return c


@gf.cell
def array_UCSB_grating_1550(gratings: list = [2,3,4,5,6,7],rotations: list = [-104,-104,-76,-77,-90,-90,-103],**kwargs):
    """Imports an up-to-7-plex array of UCSB 1550 nm grating couplers meant to map to a fiber bundle.

    Args:
        Gratings: list-like array of integers marking which of the gratings will be included, optional (default is [2,3,4,5,6,7]).
            Only gratings listed will be included in the grating bundle.

        Rotations: Optional list-like array of floats (default is [-104,-104,-76,-77,-90,-90,-103])
            Rotations to be applied before x/y shifts. Default angles were taken from OptoDesigner 1x4 mm PICs.

        **kwargs: Optional keyword arguments for UCSB_grating_1550(**kwargs)


    Gratings numbering:
           1
      3         2
           4
      6         5
           7

           
    Returns: A Component with the listed gratings included at the rotation angles.
    """
    array = gf.Component()

    # Lists of the x and y shifts needed for each grating
    xvals = [0,-300-1,300+1,0+1,-300,300,0-1]
    yvals = [-346.410,-173.205,-173.205,0,173.205,173.205,346.410]
    # [90,104,76,77,90,90,103]
    for grating in gratings:
        add = array << UCSB_grating_1550(**kwargs) # Add a grating into the array
        add.rotate(rotations[grating-1])
        add.movey(yvals[grating-1]) # Shift grating to correct location (Python indexing from 0)
        add.movex(xvals[grating-1])
        array.add_ports(add.ports,prefix="grating_"+str(grating)+"_")
    
    
    array.rotate(180) # Originally built upside down to match Michael's OptoDesigner setup
    array.flatten()
    return array

@gf.cell
def array_UCSB_grating_1550_straight(gratings: list = [2,3,4,5,6,7],rotations: list = [-104,-104,-76,-77,-90,-90,-103],**kwargs):
    """Uses UCSB_grating_1550_straightened to make straight output ports.

    Args:
        Gratings: list-like array of integers marking which of the gratings will be included, optional (default is [2,3,4,5,6,7]).
            Only gratings listed will be included in the grating bundle.

        Rotations: Optional list-like array of floats (default is [-104,-104,-76,-77,-90,-90,-103])
            Rotations to be applied before x/y shifts. Default angles were taken from OptoDesigner 1x4 mm PICs.

        **kwargs: Optional keyword arguments for UCSB_grating_1550(**kwargs)


    Gratings numbering: 
           1
      3         2
           4
      6         5
           7

           
    Returns: A Component with the listed gratings included at the rotation angles.
    """
    array = gf.Component()

    # Lists of the x and y shifts needed for each grating
    xvals = [0,-300-1,300+1,0+1,-300,300,0-1]
    yvals = [-346.410,-173.205,-173.205,0,173.205,173.205,346.410]
    # [90,104,76,77,90,90,103]
    for grating in gratings:
        add = array << UCSB_grating_1550_straightened(
            grating_angle=rotations[grating-1],output_angle=-90,radius=50,euler_part=0.2,straight1=10,straight2=10,
            **kwargs) # Add a grating into the array
        
        add.movey(yvals[grating-1]) # Shift grating to correct location (Python indexing from 0)
        add.movex(xvals[grating-1])
        array.add_port("grating_"+str(grating)+"_",port=add.ports["out"])
        # array.add_ports(add.ports,prefix="grating_"+str(grating)+"_")
    
    
    array.rotate(180) # Originally built upside down to match Michael's OptoDesigner setup
    array.flatten()
    return array


@gf.cell
def myMMI1x6(width: float = 1.5, width_taper: float = 4.0, width_mmi: float = 45.0,
           length_mmi: float = 225, length_taper: float = 25, gap_input_tapers: float = 4.0,
           gap_output_tapers: float = 4,**kwargs):
    """1x6 MMI splitter with Miller lab 2025 default dimensions. Calls gf.components.mmi with the updated default arguments."""

    return gf.components.mmi(outputs=6,width=width,width_taper=width_taper,length_taper=length_taper,length_mmi=length_mmi,width_mmi=width_mmi,gap_input_tapers=gap_input_tapers,gap_output_tapers=gap_output_tapers,**kwargs)

# Is this necessary? And how to include the effects of getTechnology() and &techAPSUNY/AIM???
@gf.cell
def passiveDieBase(Length: int = 6000, Width: int = 8500,die_name=None,**kwargs):
    return gf.components.die(Size = (Width,Length),die_name=die_name,**kwargs)

def neff_index_data(radius):
    """Modeled effective refractive index as a function of ring bend radius (from OptoDesigner library)"""
    A = 0.002083680178277
    B = 4.171450309668357
    n_0 = 1.500287885368830

    neff_model = n_0 + B*np.exp(-A*radius)/radius**2
    return neff_model

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
    
    ring = gf.components.rings.ring_single(radius=radius,gap=gap,length_x=racetrack,length_y=0,bend="bend_circular",**kwargs)
    return ring

@gf.cell
def ring_col(num: int = 3, ysep: float | list = 400.0, xsep: list | None = None, 
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

        cross_section: GDSFactory CrossSection, optional (default is gf.cross_section.strip() - change?!!!)
            Cross-section for both rings and waveguide.

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
        ring.rotate(-90)
        ring.movey(np.sum(ysep[:i]))
        ring.movex(xsep[i])
        c.add_ports(ring.ports,prefix="ring"+str(i+1)+"_")
        if i > 0:
            # route = gf.routing.route_single(c,port1=c.ports["ring"+str(i)+"_"+"o1"],port2=c.ports["ring"+str(i+1)+"_"+"o2"], #!!! This is where I am getting the UserWarning.
            #                                 cross_section=cross_section)
            route = gf.routing.route_bundle(c,port1=c.ports["ring"+str(i)+"_"+"o1"],port2=c.ports["ring"+str(i+1)+"_"+"o2"], #!!! This is where I am getting the UserWarning.
                                            cross_section=cross_section)
    # for j,port in enumerate(c.ports):
    #     if j != 0 and j != len(c.ports)-1:
    #         c.remove_port[port.name]
    return c

@gf.cell
def ring_arr(num=3,channels=6,channel_sep=50,offset=True,offset_sep=300,
             rot_step=-30,
             rotate=True, port_width=1.5,port_layer=(0,1),**kwargs):
    """ Builds an array of ring resonators in multiple columnar channels (calls miller_lib.ring_col)

    Unlike ring_arr_same_heights, if offset is True, the input and output ports for even and odd channels will be staggered
    in height. This is probably preferable in the sense that it leaves more space for connecting waveguides to bend more
    gradually, but can cause problems if a routing function such as gf.routing.route_bundle_sbend is used that might allow 
    collisions with one of the rings.

    Args:
        channels: int, optional (default is 6).
            Number of columns/channels of ring resonators. (Number of iterations to call miller_lib.ring_col.)

        channel_sep: float, optional (default is 50)
            Horizontal separation between channels (waveguides) in um.
        
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
        
        port_width: float, optional (default is 1.5)
            Width of input and output ports in um.
        
        port_layer: 2-tuple of ints, optional (default is (0,1)).
            Layer where the input and output ports will be placed.
        
        **kwargs: Optional keyword arguments for miller_lib.ring_col

    Returns: A Component of an array of rings. The component is centered at the base port to the lower left ring.
        
    """
    
    c = gf.Component()
    step = 0 # Step to the right of rotated columns
    for i in range(channels):
        col = c << ring_col(**kwargs)
        col.movey(-col.dymin)
        col.movex(-port_width/2-col.dxmin)
        x = 0 # Mark center for ports
        y = 0
        h = col.dysize
        
        if rotate is True:
            if i/2 != i//2:
                col.rotate(180)
                # col.movex(col.dxsize)
                col.movey(col.dysize)
                # x += col.dxsize
                step += col.dxsize + rot_step
                c.add_port("col"+str(i+1)+"_o2",port=col.ports["ring1_o2"])
                c.add_port("col"+str(i+1)+"_o1",port=col.ports["ring"+str(num)+"_o1"])
            else:
                c.add_port("col"+str(i+1)+"_o1",port=col.ports["ring1_o2"])
                c.add_port("col"+str(i+1)+"_o2",port=col.ports["ring"+str(num)+"_o1"])
        col.movex(channel_sep*i+step)
        x += channel_sep*i+step
        if offset is True:
            if i/2 != i//2:
                col.movey(offset_sep)
                y += offset_sep
        
        # c.add_port(name="col"+str(i+1)+"_o1",width=port_width,orientation=-90,center=(x,y),layer=port_layer)
        # c.add_port(name="col"+str(i+1)+"_o2",width=port_width,orientation=90,center=(x,y+h),layer=port_layer)
    return c
    
@gf.cell
def ring_arr_same_heights(num=3,channels=6,channel_sep=50,offset=True,offset_sep=300,
             rot_step=-30,cross_section="strip",
             rotate=True, port_width=1.5,port_layer=(0,1),**kwargs):
        
    """ Builds an array of ring resonators in multiple columnar channels (calls miller_lib.ring_col)

    Even if offset is True, the input and output waveguides/ports will be at the same height, with extra straight connections.
    This may result in slightly suboptimal connections (since straight waveguides are included that take space that might
    allow for more gradual bends), but allows for more even connections with less likelihood of collisions if used with a
    routing function such as gf.routing.route_bundle_sbend is used that does not prevent collisions.
    If the staggered IO ports are preferred, use miller_lib.ring_arr.

    Args:
        channels: int, optional (default is 6).
            Number of columns/channels of ring resonators. (Number of iterations to call miller_lib.ring_col.)

        channel_sep: float, optional (default is 50)
            Horizontal separation between channels (waveguides) in um.
        
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
        
        port_width: float, optional (default is 1.5)
            Width of input and output ports in um.
        
        port_layer: 2-tuple of ints, optional (default is (0,1)).
            Layer where the input and output ports will be placed.
        
        **kwargs: Optional keyword arguments for miller_lib.ring_col

    Returns: A Component of an array of rings. The component is centered at the base port to the lower left ring.
    """
    
    c = gf.Component()
    step = 0 # Step to the right of rotated columns
    for i in range(channels):
        col = c << ring_col(cross_section=cross_section,**kwargs)
        
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
        col.movex(-0/2-col.dxmin) # Was the 1.5 width
        


        col.movex(channel_sep*i+step)
        x += channel_sep*i+step
        if offset is True:
            if i/2 != i//2:
                col.movey(offset_sep)
                y += offset_sep
        
    # Add the staggered straight waveguides.
        if rotate is True:
            if i/2 == i//2:
                extra = c << gf.components.waveguides.straight(length=offset_sep,cross_section=cross_section)
                extra.connect("o1",other=col.ports["ring"+str(num)+"_o1"]) #!!! Need to fix the number of rings passed in
                # extra.rotate(90)
                # extra.movex(step+channel_sep*i+extra.dxsize/2)
                # extra.movey(col.dysize-extra.dxsize/2)
                c.add_port("col"+str(i+1)+"_o1",port=col.ports["ring1_o2"])
                c.add_port("col"+str(i+1)+"_o2",port=extra.ports["o2"])
            else:
                extra = c << gf.components.waveguides.straight(length=offset_sep,cross_section=cross_section)
                extra.connect("o2",other=col.ports["ring"+str(num)+"_o1"])
                # extra.rotate(90)
                # extra.movex(step+channel_sep*i-extra.dxsize/2+col.dxsize)
                # extra.movey(extra.dxsize/2)
                # y -= extra.dysize
                c.add_port("col"+str(i+1)+"_o2",port=col.ports["ring1_o2"])
                c.add_port("col"+str(i+1)+"_o1",port=extra.ports["o1"])
            # h += extra.dysize
    return c
    

# @gf.cell
class PIC_1x4(gf.Component):
    """A gf.Component subclass to build a 1x4mm-style PIC ring resonator sensor
    
    Would this be better as a function? I need to make it so the kwargs for the different functions can be modified if needed.
    """
    def __init__(self,
                 size=(1000,4000),input=UCSB_grating_1550,output=array_UCSB_grating_1550,
                 splitter=myMMI1x6,ringbank=ring_arr_same_heights,outorder=[6,3,7,4,2,5],
                 connect_1=gf.routing.route_bundle_sbend,connect_2=gf.routing.route_bundle_sbend
                #  ,**kwargs
                 ):
        """
        Size: tuple of (x,y) die size in um
        input,output,splitter,ringbank,connect_1,connect_2: functions to create components used to build each of those pieces
            (Should be able to access/shift the component as eg self.input.movex(500))
        Outorder: order of output gratings to be matched with the channel ports
        """
        super().__init__()
        self.size = size
        self.input = input()
        self.output = output()
        self.splitter = splitter()
        self.ringbank = ringbank()
        self.connect_1 = connect_1
        self.connect_2 = connect_2

        self.outorder = outorder

        # self.rebuild() # Build the component - this doesn't do anything here actually...
    
    def rebuild(self):
        """Rebuilds the component with any updates"""
        # How to make the movements variable??? kwargs for here???

        c = gf.Component()
        die = c << gf.components.die(self.size,die_name=None)
        die.movex(500) # Shift origin to corner of die
        die.movey(2000)

        input = c << self.input
        input.rotate(-90)
        input.movex(500)
        input.movey(350)
        c.add_ports(input.ports,prefix="input")

        output = c << self.output
        output.rotate(0)
        output.movey(3500) # May need to adjust y value
        output.movex(500)
        c.add_ports(output.ports,prefix="output_")

        mmi = c << self.splitter
        mmi.rotate(90)
        mmi.connect("o1",input.ports["o1"],allow_layer_mismatch=True) #!!! Will want to change that line once I get the layers right 

        rings = c << self.ringbank
        rings.movey(1320)
        rings.movex(170)
        c.add_ports(rings.ports,prefix="rings_")

        ring_ports = [c.ports["rings_col"+str(i+1)+"_o1"] for i in range(6)]
        mmi_ports = [mmi.ports["o"+str(i+2)] for i in range(6)]

        connect = self.connect_1(c,mmi_ports,ring_ports,allow_width_mismatch=False,
                                allow_layer_mismatch=True)

        ring_bank_ports = [c.ports["rings_col"+str(i+1)+"_o2"] for i in range(6)]
        output_ports = [c.ports["output_grating_"+str(n)+"_o1"] for n in self.outorder]
        connect2 = self.connect_2(c,ring_bank_ports,output_ports,allow_layer_mismatch=True,enforce_port_ordering=True)

        return c
    
    def save_gds(self,location="",filename="tmp.gds"):
        """Save a gds of self.rebuild() to the location"""
        self.rebuild().write_gds(location+filename)

    def plot(self):
        """Plot the GDS in matplotlib"""
        self.rebuild().plot()
        plt.show()



