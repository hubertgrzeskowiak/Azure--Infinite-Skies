"""Utilities which don't suit into any other module."""

def sign(number):
    """Return the signature of a number. -1, 0 or 1 for negative, 0 and
    positive numbers respectively."""
    if number < 0:
        return -1
    elif number > 0:
        return 1
    else:
        return 0

class ListInterpolator(object):
    """Defines an interpolated data type."""

    def __init__(self, datap, lowval=None, highval=None):
        """arguments:
        datap -- List or tuple. Each element of which should be a list
                 or tuple with 2 values.
        lowval -- (optional), value to return if requesting y for x less than
                  the lowest given.
        highval -- (optional), value to return if requesting y for x greater
                   than the highest given.
        """
        self.data = list(datap)
        self.data.sort()
        self.lowval = lowval
        self.highval = highval

    def setHigh(self,val):
        """Set high value default."""
        self.highval = val
    def setLow(self,val):
        """Set low value default."""
        self.lowval = val

    def __setitem__(self,x,y):
        """Allows additional values to be placed it the data with syntax like
        values[x] = y.
        """
        self.data.append([x,y])
        self.data.sort()

    def __getitem__(self,x):
        """Returns y values for any value of x in low_x <= x <= high_x."""

        if x < self.data[0][0]:
            if self.lowval is None:
                raise ValueError
            else: return self.lowval
        elif x > self.data[-1][0]:
            if self.highval is None:
                raise ValueError
            else: return self.highval

        # find the neighbouring points
        for d in range(len(self.data)):
            if self.data[d][0] >= x:
                highx,highy = self.data[d]
                if self.data[d][0] == x:
                    return float(highy)
                else:
                    lowx,lowy = self.data[d-1]
                break

        # interpolate between the points
        if lowx == highx:
            return lowy
        else:
            gradient = float(highy - lowy)/(highx - lowx)
        return lowy + gradient*(x - lowx)

if __name__ == '__main__':
    intdata = ListInterpolator([[-1,-1],[0,0],[1,2]],0.0,0.0)

    intdata[3.0] = 3.0;

    for i in (-1.5,-1.0,-0.5,0.0,0.5,1.0,1.5,2.0,2.5,3.0,3.5):
        print intdata[i]


