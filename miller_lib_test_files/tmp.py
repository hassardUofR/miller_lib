import miller_lib as ml
import gdsfactory as gf
import matplotlib.pyplot as plt
import numpy as np

C = gf.Component()

ring = C << ml.ring_arr()
# C.add_ports(ring.ports,prefix="ring_")
# C.draw_ports()
# print(C.ports)

C.plot()
plt.show()
