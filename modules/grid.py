"""Module for helper grids."""

from direct.directtools.DirectGeometry import LineNodePath
from pandac.PandaModules import Vec4

class Grid():
    """Generic grid class."""

    def __init__(self):
        pass

    def makeGrid(self):
        """Draws a grid and returns the nodepath."""

        self.grid_node = render.attachNewNode("grid")

        # size
        X1 = Y1 = 10
        X2 = Y2 = -10

        # X axis
        Xaxis = LineNodePath(self.grid_node, "Xaxis", 1, Vec4(1, 0, 0, 1))

        x1 = (X2, 0, 0)
        x2 = (X1, 0, 0)

        Xaxis.drawLines([[x1, x2]])
        Xaxis.create()

        # Y axis
        Yaxis = LineNodePath(self.grid_node, "Yaxis", 1, Vec4(0, 1, 0, 1))

        x3 = (0, Y2, 0)
        x4 = (0, Y1, 0)

        Yaxis.drawLines([[x3, x4]])
        Yaxis.create()

        # outer borders
        border = LineNodePath(self.grid_node, 'border', 1, Vec4(.6, .6, .6, 1))

        q1 = (X1, Y1, 0)
        q2 = (X1, Y2, 0)
        q3 = (q2)
        q4 = (X2, Y2, 0)
        q5 = (q4)
        q6 = (X2, Y1, 0)
        q7 = (q6)
        q8 = (X1, Y1, 0)

        border.drawLines([[q1,q2], [q3,q4], [q5,q6], [q7,q8]])
        border.create()

        # thin lines
        raster = LineNodePath(self.grid_node, 'raster', .2, Vec4(.5, .5, .5, 1))

        d = 0
        for l in range (X1-Y2):
            l1 = (X2 + d, Y1,     0)
            l2 = (X2 + d, Y2,     0)
            l3 = (X2,     Y2 + d, 0)
            l4 = (X1,     Y2 + d, 0) 
            d += 1
            raster.drawLines([[l1,l2], [l3,l4]])
        raster.create()

        return self.grid_node
