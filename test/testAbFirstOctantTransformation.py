import unittest
import numpy as np

from alphaBetaLab.abHighResAlphaMatrix import abHighResAlphaMatrix as alphaMtx
from alphaBetaLab.abFirstOctantTransformation import *

plotResults = False
if plotResults:
  from matplotlib import pyplot as plt
  from alphaBetaLab.abHighResAlphaMatrixPlot.plot import plotHiResAlphaMtx as plot

class testAbFirstOctantTransformation(unittest.TestCase):


  def test_noTransform2D(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[3, :] = 0
    highResCellGrid[1, 1] = 0
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4)) + yoff
    freqs = None
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid, freqs = freqs)

    lowresDx = 1.3
    lowresDy = 3.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    direction = 20./180.*np.pi
   
    trfrm = abFirstOctantTransformation(hiResAlphaMtx, cellPoly)
    rtheta, rmtx, rcell = trfrm.transform(direction)
    
    expdir = direction
    self.assertAlmostEqual(expdir, rtheta)
    
    expcoord = list(cellPoly.boundary.coords)
    rcellcoord = list(rcell.boundary.coords)
    for ec, rc in zip(expcoord, rcellcoord):
      self.assertAlmostEqual(ec, rc)
    
    exprtmtx = hiResAlphaMtx
    self.assertTrue(np.allclose(exprtmtx.alphas, rmtx.alphas))
    self.assertIs(exprtmtx.polygon, rmtx.polygon)
    self.assertTrue(np.allclose(exprtmtx.xs, rmtx.xs))
    self.assertTrue(np.allclose(exprtmtx.ys, rmtx.ys))
    self.assertEqual(exprtmtx.hasFreqs, rmtx.hasFreqs)
    self.assertIs(freqs, rmtx.freqs)
    self.assertTrue(rmtx.xs[0] < rmtx.xs[-1])
    self.assertTrue(rmtx.ys[0] < rmtx.ys[-1])


  def test_noTransform3D(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[3, :] = 0
    highResCellGrid[1, 1] = 0
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4)) + yoff
    highResCellGrid = np.dstack((highResCellGrid, highResCellGrid, highResCellGrid))
    freqs = np.array([.1,.2,.3])
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid, freqs)

    lowresDx = 1.3
    lowresDy = 3.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    direction = 20./180.*np.pi
   
    trfrm = abFirstOctantTransformation(hiResAlphaMtx, cellPoly)
    rtheta, rmtx, rcell = trfrm.transform(direction)
    
    expdir = direction
    self.assertAlmostEqual(expdir, rtheta)
    
    expcoord = list(cellPoly.boundary.coords)
    rcellcoord = list(rcell.boundary.coords)
    for ec, rc in zip(expcoord, rcellcoord):
      self.assertAlmostEqual(ec, rc)
    
    exprtmtx = hiResAlphaMtx
    self.assertTrue(np.allclose(exprtmtx.alphas, rmtx.alphas))
    self.assertIs(exprtmtx.polygon, rmtx.polygon)
    self.assertTrue(np.allclose(exprtmtx.xs, rmtx.xs))
    self.assertTrue(np.allclose(exprtmtx.ys, rmtx.ys))
    self.assertEqual(exprtmtx.hasFreqs, rmtx.hasFreqs)
    #self.assertTrue(rmtx.xs[0] < rmtx.xs[-1])
    #self.assertTrue(rmtx.ys[0] < rmtx.ys[-1])


  def test_octantReflection2D(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[3, :] = 0
    highResCellGrid[1, 1] = 0
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4)) + yoff
    freqs = None
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid, freqs = freqs)

    lowresDx = 1.3
    lowresDy = 3.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    direction = 60./180.*np.pi
   
    trfrm = abFirstOctantTransformation(hiResAlphaMtx, cellPoly)
    rtheta, rmtx, rcell = trfrm.transform(direction)

    if plotResults:
      plot('original', hiResAlphaMtx, direction)
      plot('transformed', rmtx, rtheta)
      plt.show()
    
    expdir = 30./180.*np.pi
    self.assertAlmostEqual(expdir, rtheta)
    
    crds = list(cellPoly.boundary.coords)
    expcoord = [(c[1], c[0]) for c in crds]
    rcellcoord = list(rcell.boundary.coords)
    for ec, rc in zip(expcoord, rcellcoord):
      self.assertAlmostEqual(ec, rc)
    
    expalpha = highResCellGrid.transpose()
    exprtmtx = alphaMtx(ys, xs, expalpha, freqs = freqs)
    exprtmtx.polygon = rcell
    self.assertTrue(np.allclose(exprtmtx.alphas, rmtx.alphas))
    self.assertIs(exprtmtx.polygon, rmtx.polygon)
    self.assertTrue(np.allclose(exprtmtx.xs, rmtx.xs))
    self.assertTrue(np.allclose(exprtmtx.ys, rmtx.ys))
    self.assertEqual(exprtmtx.hasFreqs, rmtx.hasFreqs)
    self.assertIs(freqs, rmtx.freqs)
    #self.assertTrue(rmtx.xs[0] < rmtx.xs[-1])
    #self.assertTrue(rmtx.ys[0] < rmtx.ys[-1])


  def test_octantReflection3D(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[3, :] = 0
    highResCellGrid[1, 1] = 0
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4)) + yoff
    highResCellGrid = np.dstack((highResCellGrid, highResCellGrid, highResCellGrid))
    freqs = np.array([.1,.2,.3])
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid, freqs = freqs)

    lowresDx = 1.3
    lowresDy = 3.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    direction = 60./180.*np.pi
   
    trfrm = abFirstOctantTransformation(hiResAlphaMtx, cellPoly)
    rtheta, rmtx, rcell = trfrm.transform(direction)

    if plotResults:
      plot('original', hiResAlphaMtx, direction)
      plot('transformed', rmtx, rtheta)
      plt.show()
    
    expdir = 30./180.*np.pi
    self.assertAlmostEqual(expdir, rtheta)
    
    crds = list(cellPoly.boundary.coords)
    expcoord = [(c[1], c[0]) for c in crds]
    rcellcoord = list(rcell.boundary.coords)
    for ec, rc in zip(expcoord, rcellcoord):
      self.assertAlmostEqual(ec, rc)
    
    expalpha = highResCellGrid.transpose((1,0,2))
    exprtmtx = alphaMtx(ys, xs, expalpha, freqs = freqs)
    exprtmtx.polygon = rcell
    self.assertTrue(np.allclose(exprtmtx.alphas, rmtx.alphas))
    self.assertIs(exprtmtx.polygon, rmtx.polygon)
    self.assertTrue(np.allclose(exprtmtx.xs, rmtx.xs))
    self.assertTrue(np.allclose(exprtmtx.ys, rmtx.ys))
    self.assertEqual(exprtmtx.hasFreqs, rmtx.hasFreqs)
    self.assertIs(freqs, rmtx.freqs)
    #self.assertTrue(rmtx.xs[0] < rmtx.xs[-1])
    #self.assertTrue(rmtx.ys[0] < rmtx.ys[-1])


  def test_90degRotation2D(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[3, :] = 0
    highResCellGrid[1, 1] = 0
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4)) + yoff
    freqs = None
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid, freqs = freqs)

    lowresDx = 1.3
    lowresDy = 3.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    direction = 110./180.*np.pi
   
    trfrm = abFirstOctantTransformation(hiResAlphaMtx, cellPoly)
    rtheta, rmtx, rcell = trfrm.transform(direction)

    if plotResults:
      plot('original', hiResAlphaMtx, direction)
      plot('transformed', rmtx, rtheta)
      plt.show()
    
    expdir = 20./180.*np.pi
    self.assertAlmostEqual(expdir, rtheta)
    
    crds = list(cellPoly.boundary.coords)
    expcoord = [(c[1], -c[0]) for c in crds]
    rcellcoord = list(rcell.boundary.coords)
    for ec, rc in zip(expcoord, rcellcoord):
      self.assertAlmostEqual(ec, rc)
    
    expalpha = highResCellGrid.transpose()
    exprtmtx = alphaMtx(ys, -xs, expalpha, freqs = freqs)
    exprtmtx.polygon = rcell
    self.assertTrue(np.allclose(exprtmtx.alphas, rmtx.alphas))
    self.assertIs(exprtmtx.polygon, rmtx.polygon)
    self.assertTrue(np.allclose(exprtmtx.xs, rmtx.xs))
    self.assertTrue(np.allclose(exprtmtx.ys, rmtx.ys))
    self.assertEqual(exprtmtx.hasFreqs, rmtx.hasFreqs)
    self.assertIs(freqs, rmtx.freqs)
    #self.assertTrue(rmtx.xs[0] < rmtx.xs[-1])
    #self.assertTrue(rmtx.ys[0] < rmtx.ys[-1])


  def test_90degRotation3D(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[3, :] = 0
    highResCellGrid[1, 1] = 0
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4)) + yoff
    highResCellGrid = np.dstack((highResCellGrid, highResCellGrid, highResCellGrid))
    freqs = np.array([.1,.2,.3])
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid, freqs = freqs)

    lowresDx = 1.3
    lowresDy = 3.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    direction = 110./180.*np.pi
   
    trfrm = abFirstOctantTransformation(hiResAlphaMtx, cellPoly)
    rtheta, rmtx, rcell = trfrm.transform(direction)

    if plotResults:
      plot('original', hiResAlphaMtx, direction)
      plot('transformed', rmtx, rtheta)
      plt.show()
    
    expdir = 20./180.*np.pi
    self.assertAlmostEqual(expdir, rtheta)
    
    crds = list(cellPoly.boundary.coords)
    expcoord = [(c[1], -c[0]) for c in crds]
    rcellcoord = list(rcell.boundary.coords)
    for ec, rc in zip(expcoord, rcellcoord):
      self.assertAlmostEqual(ec, rc)
    
    expalpha = highResCellGrid.transpose((1,0,2))
    exprtmtx = alphaMtx(ys, -xs, expalpha, freqs = freqs)
    exprtmtx.polygon = rcell
    self.assertTrue(np.allclose(exprtmtx.alphas, rmtx.alphas))
    self.assertIs(exprtmtx.polygon, rmtx.polygon)
    self.assertTrue(np.allclose(exprtmtx.xs, rmtx.xs))
    self.assertTrue(np.allclose(exprtmtx.ys, rmtx.ys))
    self.assertEqual(exprtmtx.hasFreqs, rmtx.hasFreqs)
    self.assertIs(freqs, rmtx.freqs)
    #self.assertTrue(rmtx.xs[0] < rmtx.xs[-1])
    #self.assertTrue(rmtx.ys[0] < rmtx.ys[-1])


  def test_180degRotation2D(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[3, :] = 0
    highResCellGrid[1, 1] = 0
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4)) + yoff
    freqs = None
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid, freqs = freqs)

    lowresDx = 1.3
    lowresDy = 3.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    direction = 200./180.*np.pi
   
    trfrm = abFirstOctantTransformation(hiResAlphaMtx, cellPoly)
    rtheta, rmtx, rcell = trfrm.transform(direction)

    if plotResults:
      plot('original', hiResAlphaMtx, direction)
      plot('transformed', rmtx, rtheta)
      plt.show()
    
    expdir = 20./180.*np.pi
    self.assertAlmostEqual(expdir, rtheta)
    
    crds = list(cellPoly.boundary.coords)
    expcoord = [(-c[0], -c[1]) for c in crds]
    rcellcoord = list(rcell.boundary.coords)
    for ec, rc in zip(expcoord, rcellcoord):
      self.assertAlmostEqual(ec, rc)
    
    expalpha = highResCellGrid
    exprtmtx = alphaMtx(-xs, -ys, expalpha, freqs = freqs)
    exprtmtx.polygon = rcell
    self.assertTrue(np.allclose(exprtmtx.alphas, rmtx.alphas))
    self.assertIs(exprtmtx.polygon, rmtx.polygon)
    self.assertTrue(np.allclose(exprtmtx.xs, rmtx.xs))
    self.assertTrue(np.allclose(exprtmtx.ys, rmtx.ys))
    self.assertEqual(exprtmtx.hasFreqs, rmtx.hasFreqs)
    self.assertIs(freqs, rmtx.freqs)
    #self.assertTrue(rmtx.xs[0] < rmtx.xs[-1])
    #self.assertTrue(rmtx.ys[0] < rmtx.ys[-1])


  def test_180degRotation3D(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[3, :] = 0
    highResCellGrid[1, 1] = 0
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4)) + yoff
    highResCellGrid = np.dstack((highResCellGrid, highResCellGrid, highResCellGrid))
    freqs = np.array([.1,.2,.3])
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid, freqs = freqs)

    lowresDx = 1.3
    lowresDy = 3.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    direction = 200./180.*np.pi
   
    trfrm = abFirstOctantTransformation(hiResAlphaMtx, cellPoly)
    rtheta, rmtx, rcell = trfrm.transform(direction)

    if plotResults:
      plot('original', hiResAlphaMtx, direction)
      plot('transformed', rmtx, rtheta)
      plt.show()
    
    expdir = 20./180.*np.pi
    self.assertAlmostEqual(expdir, rtheta)
    
    crds = list(cellPoly.boundary.coords)
    expcoord = [(-c[0], -c[1]) for c in crds]
    rcellcoord = list(rcell.boundary.coords)
    for ec, rc in zip(expcoord, rcellcoord):
      self.assertAlmostEqual(ec, rc)
    
    expalpha = highResCellGrid
    exprtmtx = alphaMtx(-xs, -ys, expalpha, freqs = freqs)
    exprtmtx.polygon = rcell
    self.assertTrue(np.allclose(exprtmtx.alphas, rmtx.alphas))
    self.assertIs(exprtmtx.polygon, rmtx.polygon)
    self.assertTrue(np.allclose(exprtmtx.xs, rmtx.xs))
    self.assertTrue(np.allclose(exprtmtx.ys, rmtx.ys))
    self.assertEqual(exprtmtx.hasFreqs, rmtx.hasFreqs)
    self.assertIs(freqs, rmtx.freqs)
    #self.assertTrue(rmtx.xs[0] < rmtx.xs[-1])
    #self.assertTrue(rmtx.ys[0] < rmtx.ys[-1])


  def test_270degRotation2D(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[3, :] = 0
    highResCellGrid[1, 1] = 0
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4)) + yoff
    freqs = None
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid, freqs = freqs)

    lowresDx = 1.3
    lowresDy = 3.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    direction = 290./180.*np.pi
   
    trfrm = abFirstOctantTransformation(hiResAlphaMtx, cellPoly)
    rtheta, rmtx, rcell = trfrm.transform(direction)

    if plotResults:
      plot('original', hiResAlphaMtx, direction)
      plot('transformed', rmtx, rtheta)
      plt.show()
    
    expdir = 20./180.*np.pi
    self.assertAlmostEqual(expdir, rtheta)
    
    crds = list(cellPoly.boundary.coords)
    expcoord = [(-c[1], c[0]) for c in crds]
    rcellcoord = list(rcell.boundary.coords)
    for ec, rc in zip(expcoord, rcellcoord):
      self.assertAlmostEqual(ec, rc)
    
    expalpha = highResCellGrid.transpose()
    exprtmtx = alphaMtx(-ys, xs, expalpha, freqs = freqs)
    exprtmtx.polygon = rcell
    self.assertTrue(np.allclose(exprtmtx.alphas, rmtx.alphas))
    self.assertIs(exprtmtx.polygon, rmtx.polygon)
    self.assertTrue(np.allclose(exprtmtx.xs, rmtx.xs))
    self.assertTrue(np.allclose(exprtmtx.ys, rmtx.ys))
    self.assertEqual(exprtmtx.hasFreqs, rmtx.hasFreqs)
    self.assertIs(freqs, rmtx.freqs)
    #self.assertTrue(rmtx.xs[0] < rmtx.xs[-1])
    #self.assertTrue(rmtx.ys[0] < rmtx.ys[-1])


  def test_270degRotation3D(self):
    xoff = 20.
    yoff = 10.

    highResCellGrid = np.ones((4, 2))
    highResCellGrid[3, :] = 0
    highResCellGrid[1, 1] = 0
    xs = np.array(range(2)) + xoff
    ys = np.array(range(4)) + yoff
    highResCellGrid = np.dstack((highResCellGrid, highResCellGrid, highResCellGrid))
    freqs = np.array([.1,.2,.3])
    hiResAlphaMtx = alphaMtx(xs, ys, highResCellGrid, freqs = freqs)

    lowresDx = 1.3
    lowresDy = 3.3
    cellPoly = g.Polygon(\
                [[xoff, yoff], [xoff + lowresDx, yoff],\
                [xoff + lowresDx, yoff + lowresDy], [xoff, yoff + lowresDy]])
    hiResAlphaMtx.polygon = cellPoly

    direction = 290./180.*np.pi
   
    trfrm = abFirstOctantTransformation(hiResAlphaMtx, cellPoly)
    rtheta, rmtx, rcell = trfrm.transform(direction)

    if plotResults:
      plot('original', hiResAlphaMtx, direction)
      plot('transformed', rmtx, rtheta)
      plt.show()
    
    expdir = 20./180.*np.pi
    self.assertAlmostEqual(expdir, rtheta)
    
    crds = list(cellPoly.boundary.coords)
    expcoord = [(-c[1], c[0]) for c in crds]
    rcellcoord = list(rcell.boundary.coords)
    for ec, rc in zip(expcoord, rcellcoord):
      self.assertAlmostEqual(ec, rc)
    
    expalpha = highResCellGrid.transpose((1,0,2))
    exprtmtx = alphaMtx(-ys, xs, expalpha, freqs = freqs)
    exprtmtx.polygon = rcell
    self.assertTrue(np.allclose(exprtmtx.alphas, rmtx.alphas))
    self.assertIs(exprtmtx.polygon, rmtx.polygon)
    self.assertTrue(np.allclose(exprtmtx.xs, rmtx.xs))
    self.assertTrue(np.allclose(exprtmtx.ys, rmtx.ys))
    self.assertEqual(exprtmtx.hasFreqs, rmtx.hasFreqs)
    self.assertIs(freqs, rmtx.freqs)
    #self.assertTrue(rmtx.xs[0] < rmtx.xs[-1])
    #self.assertTrue(rmtx.ys[0] < rmtx.ys[-1])


if __name__ == '__main__':
  unittest.main()
