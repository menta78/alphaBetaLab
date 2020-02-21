import numpy as np
from shapely import geometry as g

from .abUtils import *

dxtol = .0001
dytol = .0001

class abHighResAlphaMatrix:
  def __init__(self, xs, ys, alphas, freqs = None):
    """
    abHighResAlphaMatrix: class representing the high resolution matrix of alpha.
    Alpha must be defined on a regular matrix.
    """
    if len(ys) != alphas.shape[0]:
      raise ValueError('ys list and alpha matrix are not compatible')
    if len(xs) != alphas.shape[1]:
      raise ValueError('xs list and alpha matrix are not compatible')
    self.xs = np.array(xs)
    self.ys = np.array(ys)
    self.alphas = np.array(alphas)
    self.hasFreqs = True if not freqs is None else False
    self.freqs = freqs if self.hasFreqs else None
    self.polygon = None
    self.polygonCrds = []
    self.dx = np.mean(xs[1:] - xs[:-1]) if len(xs) > 1 else None
    self.dy = np.mean(ys[1:] - ys[:-1]) if len(xs) > 1 else None
    if self.dx is None or self.dy is None:
      self.xs = np.array([])
      self.ys = np.array([])
      self.alphas = np.array([])

  def wrapAroundDateline(self, bufferSizeDeg=5):
    if self.dx < 0:
      raise abException('abHighResAlphaMatrix.wrapAroundDateline: xs must be in ascendent order')
    xbuffRight = max(self.xs) + self.dx + np.arange(0, bufferSizeDeg, self.dx)
    nbuffRight = len(xbuffRight)
    alphabuffRight = self.alphas[:, :nbuffRight]
    xbuffLeft = min(self.xs) - np.arange(bufferSizeDeg, 0, -self.dx)
    nbuffLeft = len(xbuffLeft)
    alphabuffLeft = self.alphas[:, -nbuffLeft:]
    xs = np.concatenate([xbuffLeft, self.xs, xbuffRight])
    alphas = np.concatenate([alphabuffLeft, self.alphas, alphabuffRight], axis=1)
    self.xs = xs
    self.alphas = alphas

  def getExtendedXY(self):
    """
    getExtendedXY: self.xs, self.ys only contain the ids of the high
    resolution cells, that is the left-bottom vertex.
    This method adds the right-top margins.
    """
    xs_ = self.xs
    dx = self.dx
    xsl = xs_[-1] + dx
    exs = np.concatenate([xs_, np.array([xsl])])
    ys_ = self.ys
    dy = self.dy
    ysl = ys_[-1] + dy
    eys = np.concatenate([ys_, np.array([ysl])])
    return exs, eys

  def getDownUpXYs(self):
    """
    getDownUpXYs
    returns the left and right borders of all the cells
    in x and y
    """
    def _getDownUp(vec):
      v1 = vec[:-1]
      v2 = vec[1:]
      dn, upp = (v1, v2) if v1[0] < v2[0] else (v2, v1)
      return dn, upp
    extxs, extys = self.getExtendedXY()
    downxs, upxs = _getDownUp(extxs)
    downys, upys = _getDownUp(extys)
    return downxs, upxs, downys, upys

  def getAlphaSubMatrix(self, polygon):
    """
    getAlphaSubMatrix:
    Estimates the submatrix covering the polygon passed as argument.
    It returns a new instance of abHighResAlphaMatrix,
    which has the variable polygon poited to the polygon argument of
    this method.
    """
    downxs, upxs, downys, upys = self.getDownUpXYs()

    envlp = polygon.envelope
    crds = list(envlp.exterior.coords)
    exs = [c[0] for c in crds]
    minx, maxx = min(exs) - dxtol, max(exs) + dxtol
    xindxs = np.where(np.logical_and((minx <= upxs), (downxs <= maxx)))[0]
    submtxxs = self.xs[xindxs]
    eys = [c[1] for c in crds]
    miny, maxy = min(eys) - dytol, max(eys) + dxtol
    yindxs = np.where(np.logical_and((miny <= upys), (downys <= maxy)))[0]
    submtxys = self.ys[yindxs]
    
    if self.hasFreqs:
      xmtx, ymtx, freqs = np.meshgrid(xindxs, yindxs, self.freqs)
      alps = self.alphas[ymtx, xmtx, freqs]
    else:
      xmtx, ymtx = np.meshgrid(xindxs, yindxs)
      freqs = None
      alps = self.alphas[ymtx, xmtx]
    aMtx = abHighResAlphaMatrix(submtxxs, submtxys, alps, freqs)
    singlePolygon = polygon.boundary.__class__ == g.LineString
    aMtx.polyon = polygon
    aMtx.polygonCrds =  [list(polygon.boundary.coords)] if singlePolygon else [list(b.coords) for b in polygon.boundary]
    aMtx.dx = self.dx
    aMtx.dy = self.dy
    return aMtx

  def coversPoly(self):
    if self.isNull():
      return False
    crds = self.polygonCrds[0] if len(self.polygonCrds) <= 1 else reduce(lambda crdtot, crdi: list(crdtot).extend(crdi), self.polygonCrds)
    px = [c[0] for c in crds]
    py = [c[1] for c in crds]
    minpx, maxpx = min(px), max(px)
    minpy, maxpy = min(py), max(py)
    minx, maxx = min(self.xs), max(self.xs) + self.dx
    miny, maxy = min(self.ys), max(self.ys) + self.dy
    return lesserClose(minx, minpx) and greaterClose(maxx, maxpx)\
        and lesserClose(miny, minpy) and greaterClose(maxy, maxpy)
      

  def getAlpha(self, ix, iy, freq):
    if self.hasFreqs:
      ifreq = self.freqs.index(freq)
      return self.alphas[iy, ix, ifreq]
    else:
      return self.alphas[iy, ix]

  def isNull(self):
    return len(self.xs) == 0 or len(self.ys) == 0
 
  def empty(self):
    return np.allclose(self.alphas, 1)

  def nullOrEmpty(self):
    return self.isNull() or self.empty()

  def onLand(self):
    return np.allclose(self.alphas, 0)

