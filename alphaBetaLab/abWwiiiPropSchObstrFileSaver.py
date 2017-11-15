import numpy as np

class abWwiiiPropSchObstrFileSaver:

  def __init__(self, grid, dirs, locCoords, locAlphas):
    """
    abWwiiiPropSchObstrFileSaver: saves the wwiii input file for the parameterization 
    of unresolved obstacles based on propagation scheme.
    """
    self.grid = grid
    self.dirs = dirs
    self.locCoords = locCoords
    self.locAlphas = locAlphas

  def saveFile(self, filePath):
    dirs = self.dirs
    dirsa = np.array(self.dirs)

    xdirs = dirsa[np.abs(dirsa) < 1. / 100.]
    if len(xdirs) == 0:
      raise ValueError('x direction not found')
    xdirIndx = list(dirs).index(xdirs[0])

    ydirs = dirsa[np.abs(dirsa - np.pi/2) < np.pi/2 / 100.]
    if len(ydirs) == 0:
      raise ValueError('y direction not found')
    ydirIndx = list(dirs).index(ydirs[0])

    try:
      nx = self.grid.nx
      ny = self.grid.ny
    except Exception as e:
      msg = e.message
      raise ValueError('Maybe grid is not regular? Original exception message ' + msg)

    coordsDict = dict((tuple(c[0]), c[1]) for c in zip(self.locCoords, range(len(self.locCoords))))
    fl = open(filePath, 'w')

    print('writing x obstrs')
    for iy in range(ny)[::-1]:
      ln = '';
      for ix in range(nx):
        if (ix, iy) in coordsDict:
          ialpha = coordsDict[(ix, iy)]
          alpha = np.array(self.locAlphas[ialpha])
          avgAlpha = np.mean(alpha[:, xdirIndx])
          aobstr = 1 - avgAlpha
        else:
          aobstr = 0
        ln += '    {a:1.0f} '.format(a = aobstr*100)
      ln += '\n'
      fl.write(ln)

    print('writing y obstrs')
    for iy in range(ny)[::-1]:
      ln = '';
      for ix in range(nx):
        if (ix, iy) in coordsDict:
          ialpha = coordsDict[(ix, iy)]
          alpha = np.array(self.locAlphas[ialpha])
          avgAlpha = np.mean(alpha[:, ydirIndx])
          aobstr = 1 - avgAlpha
        else:
          aobstr = 0
        ln += '    {a:1.0f} '.format(a = aobstr*100)
      ln += '\n'
      fl.write(ln)
    fl.close()
    

