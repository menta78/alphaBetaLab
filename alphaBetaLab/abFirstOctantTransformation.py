import numpy as np
from shapely import geometry as g, affinity as a

from abHighResAlphaMatrix import abHighResAlphaMatrix as hrmtx

class abFirstOctantTransformation:

  def __init__(self, alphaMtx, cellPolygon):
    self.alphaMtx = alphaMtx
    self.cell = cellPolygon

  def transform(self, theta):
    """
    theta is the propagation direction in radiants.
    if theta > pi/2, theta and highResCellGrid are rotated by n*pi/2
    so that they get within pi/2
    """
    highResCellGrid, xs, ys = self.alphaMtx.alphas, self.alphaMtx.xs, self.alphaMtx.ys
    dx, dy = self.alphaMtx.dx, self.alphaMtx.dy
    if self.alphaMtx.hasFreqs:
      rtheta, rmtx = self.mtx3DTransformToFirstOctant(theta, highResCellGrid)
    else:
      rtheta, rmtx = self.mtx2DTransformToFirstOctant(theta, highResCellGrid)
    rtheta, xs, ys, dx, dy = self.coordsTransformToFirstOctant\
             (theta, xs, ys, dx, dy)
    rtheta, rcell = self.polygonTransformToFirstOctant(theta, self.cell)
    rmtx = hrmtx(xs, ys, rmtx, self.alphaMtx.freqs)
    rmtx.dx = dx
    rmtx.dy = dy
    rmtx.polygon = rcell
    return rtheta, rmtx, rcell
    
  def mtx2DTransformToFirstQuarter(self, theta, highResCellGrid):
    """
    mtx2DTransformToFirstQuarter: transforms to first quarter a 2D matrix
    (use this if your high resolution alpha matrix does not depend from frequency)
    """
    theta = theta % (2.*np.pi)
    if theta <= np.pi/2:
      return theta, highResCellGrid
    elif theta <= np.pi:
      return theta - np.pi/2., highResCellGrid.transpose()
    elif theta <= 3./2.*np.pi:
      return theta - np.pi, highResCellGrid
    else:
      return theta - 3./2.*np.pi, highResCellGrid.transpose()

  def _mtx2DTransformToFirstOctant(self, theta, highResCellGrid):
    """
    transforms to first octant a 2D matrix.
    theta must be between 0 and pi.
    if theta > pi/4 theta1 = pi/2 - theta
    and highResCellGrid1 = highResCellGrid.transpose()
    """
    if theta <= np.pi/4:
      return theta, highResCellGrid
    elif np.pi/4 < theta <= np.pi:
      return np.pi/2 - theta, highResCellGrid.transpose()
    else:
      raise ValueError('theta must be between 0 and pi. theta = ' + str(theta))
  
  def mtx2DTransformToFirstOctant(self, theta, highResCellGrid):
    """
    mtx2DTransformToFirstOctant: transforms to first octant a 2D matrix
    (use this if your high resolution alpha matrix does not depend from frequency)
    """
    theta, highResCellGrid = self.mtx2DTransformToFirstQuarter(theta, highResCellGrid)
    return self._mtx2DTransformToFirstOctant(theta, highResCellGrid)
    
  def mtx3DTransformToFirstQuarter(self, theta, highResCellGrid):
    """
    mtx3DTransformToFirstQuarter: transforms to first quarter a 3D matrix
    (use this if your high resolution alpha matrix depends from frequency)
    """
    theta = theta % (2.*np.pi)
    if theta <= np.pi/2:
      return theta, highResCellGrid
    elif theta <= np.pi:
      return theta - np.pi/2., highResCellGrid.transpose((1,0,2))
    elif theta <= 3./2.*np.pi:
      return theta - np.pi, highResCellGrid
    else:
      return theta - 3./2.*np.pi, highResCellGrid.transpose((1,0,2))

  def _mtx3DTransformToFirstOctant(self, theta, highResCellGrid):
    """
    transforms to first octant a 3D matrix.
    theta must be between 0 and pi.
    if theta > pi/4 theta1 = pi/2 - theta
    and highResCellGrid1 = highResCellGrid.transpose()
    """
    if theta <= np.pi/4:
      return theta, highResCellGrid
    elif np.pi/4 < theta <= np.pi:
      return np.pi/2 - theta, highResCellGrid.transpose((1,0,2))
    else:
      raise ValueError('theta must be between 0 and pi. theta = ' + str(theta))
  
  def mtx3DTransformToFirstOctant(self, theta, highResCellGrid):
    """
    mtx3DTransformToFirstOctant: transforms to first octant a 3D matrix
    (use this if your high resolution alpha matrix depends from frequency)
    """
    theta, highResCellGrid = self.mtx3DTransformToFirstQuarter(theta, highResCellGrid)
    return self._mtx3DTransformToFirstOctant(theta, highResCellGrid)

  def coordsTransformToFirstQuarter(self, theta, xs, ys, dx, dy):
    """
    coordsTransformToFirstQuarter: transform xs, ys coords to first quarter
    """
    theta = theta % (2.*np.pi)
    if theta <= np.pi/2:
      return theta, xs, ys, dx, dy
    elif theta <= np.pi:
      return theta - np.pi/2., ys, -xs, dy, -dx
    elif theta <= 3./2.*np.pi:
      return theta - np.pi, -xs, -ys, -dx, -dy
    else:
      return theta - 3./2.*np.pi, -ys, xs, -dy, dx

  def _coordsTransformToFirstOctant(self, theta, xs, ys, dx, dy):
    """
    transforms to first octant xs, ys coords.
    theta must be between 0 and pi.
    if theta > pi/4 theta1 = pi/2 - theta
    and highResCellGrid1 = highResCellGrid.transpose()
    """
    if theta <= np.pi/4:
      return theta, xs, ys, dx, dy
    elif np.pi/4 < theta <= np.pi:
      return np.pi/2 - theta, ys, xs, dy, dx
    else:
      raise ValueError('theta must be between 0 and pi. theta = ' + str(theta))

  def coordsTransformToFirstOctant(self, theta, xs, ys, dx, dy):
    """
    coordsTransformToFirstOctant: transform xs, ys coords to first octant
    """
    theta, xs, ys, dx, dy =\
           self.coordsTransformToFirstQuarter(theta, xs, ys, dx, dy)
    return self._coordsTransformToFirstOctant(theta, xs, ys, dx, dy)

  def polygonTransformToFirstQuarter(self, theta, poly):
    """
    polygonTransformToFirstQuarter: transform poly to first quarter
    """
    theta = theta % (2.*np.pi)
    if theta <= np.pi/2:
      return theta, poly
    elif theta <= np.pi:
      return theta - np.pi/2., a.rotate(poly, -90, origin=(0,0))
    elif theta <= 3./2.*np.pi:
      return theta - np.pi, a.rotate(poly, -180, origin=(0,0))
    else:
      return theta - 3./2.*np.pi, a.rotate(poly, -270, origin=(0,0))

  def _polygonTransformToFirstOctant(self, theta, poly):
    """
    transforms to first octant a polygon.
    theta must be between 0 and pi.
    if theta > pi/4 theta1 = pi/2 - theta
    and highResCellGrid1 = highResCellGrid.transpose()
    """
    if theta <= np.pi/4:
      return theta, poly
    elif np.pi/4 < theta <= np.pi:
      reflPolyCoords = [(c[1], c[0]) for c in list(poly.boundary.coords)]
      reflpoly = g.Polygon(reflPolyCoords)
      return np.pi/2 - theta, reflpoly
    else:
      raise ValueError('theta must be between 0 and pi. theta = ' + str(theta))

  def polygonTransformToFirstOctant(self, theta, poly):
    """
    polygonTransformToFirstOctant: transform poly to first octant
    """
    theta, poly = self.polygonTransformToFirstQuarter(theta, poly)
    return self._polygonTransformToFirstOctant(theta, poly)


