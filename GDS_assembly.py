import gdsfactory as gf


def insert_design(file,origin=(0,0),dim=(1000,4000),tiling=(1,1),rotate=0):
    """ Insert a design into the overall component. Plots in (x,y) square grid.
    
    file: str
      Relative path in overall folder to the design GDS file.
      
    origin: tuple
      (x,y) shift (in um) for the set of repeated designs. Default is (0,0).
      
    dim: tuple
      (x,y) dimensions (in um) of the component. Default is (1000,4000) (1x4 mm PIC).
      
    tiling: tuple
      (x,y) number of repetitions of the design. IF ANY ARE 0, NO DESIGNS WILL 
      BE INSERTED. Default is (1,1) - a single instance of the design.
    
    Rotate: float 
      Rotation (in degrees) to be applied before moving in x and y.
      Intended to be 0, 90, 180, or 270 degrees - this is a square tiling. Can include other rotations,
      but only automatically adjusts x and y placement for those rotations (positive or negative).
    
    Returns: A component of the inserted designs.


    TODO: Apparently this is NOT the GDSFactory preferred method of tiling (calling a single PCell repeatedly).
    Rewrite this function in the preferred form to avoid the slow looping.
    (Using this to tile GDS files into a single reticle layout is likely few enough tilings to not be too slow.)
    """

    c = gf.Component() # Define the component for the inserted grid of designs
    
    #!!! Had problems with 2501 Weiss file... How to fix?
    design = gf.import_gds(folder+"/"+file,rename_duplicated_cells=True) # Import the design GDS file. 

    if rotate == 90 or rotate == -270:
        rotx = dim[1]
        roty = 0
    elif rotate == 180 or rotate == -180:
        rotx = dim[0]
        roty = dim[1]
    elif rotate == 270 or rotate == -90:
        rotx = 0
        roty = dim[1]
    else:
        rotx = 0
        roty = 0
    
    for i in range(tiling[0]): # Loop in x and y to insert the grid of designs
        for j in range(tiling[1]):
            d_inst = c << design # A single instance of the inserted design
            d_inst.rotate(rotate)
            d_inst.movex(origin[0]+dim[0]*i+rotx) # Shift in x
            d_inst.movey(origin[1]+dim[1]*j+roty) # Shift in y
    
    
    return c