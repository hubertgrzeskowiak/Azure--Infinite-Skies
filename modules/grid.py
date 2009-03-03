"""Module for helper grids."""

from direct.directtools.DirectGeometry import LineNodePath
from pandac.PandaModules import Vec4

# container for all the helpers objects.
helpers_cont = render.attachNewNode("helpers_cont")

class Grid():
    """Generic grid class."""
    # It's still ugly, but should be okay for testing, i guess.

    def makeGrid(self, density=100, scale=500):
        """Draws a grid.
        
        Arguments:
        density -- How many rows (both directions). Defaults to 100.
        scale -- Short for setScale(scale, scale, 1). Default is 500.
                 Scale of 1 means 10x10 panda units or metres.
        """

        self.grid_node = helpers_cont.attachNewNode("grid")

        X1 = Y1 = 5
        X2 = Y2 = -5

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
        for l in range(density):
            l1 = (X2 + d, Y1,     0)
            l2 = (X2 + d, Y2,     0)
            l3 = (X2,     Y2 + d, 0)
            l4 = (X1,     Y2 + d, 0) 

            d += float(X1 - X2) / density
            raster.drawLines([[l1,l2], [l3,l4]])
        raster.create()

        self.grid_node.setScale(scale, scale, 1)
        return self.grid_node
