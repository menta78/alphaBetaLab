import unittest
import numpy as np
from shapely import geometry as g
from shapely import affinity as a
from alphaBetaLab.abCellSize import abCellSize, _computeAvgDir

class testAbCellSize(unittest.TestCase):

  def testComputeAvgDir(self):
    crds = [[0,0], [1,0], [1,2], [0,2], [0,0]]
    cell0 = g.Polygon(crds)

    cell = cell0 
    avgDir = _computeAvgDir(cell)
    self.assertAlmostEqual(0, avgDir)

    cell = a.rotate(cell0, np.pi/6, use_radians=True)
    avgDir = _computeAvgDir(cell)
    self.assertAlmostEqual(np.pi/6, avgDir)

    cell = a.rotate(cell0, -np.pi/6, use_radians=True)
    avgDir = _computeAvgDir(cell)
    self.assertAlmostEqual(np.pi/2-np.pi/6, avgDir)

    cell = a.rotate(cell0, np.pi/3, use_radians=True)
    avgDir = _computeAvgDir(cell)
    self.assertAlmostEqual(np.pi/3, avgDir)

    cell = a.rotate(cell0, np.pi/2, use_radians=True)
    avgDir = _computeAvgDir(cell)
    self.assertAlmostEqual(0, avgDir)


  def testComputeAvgDir_romboidCell(self):
    crds = [[0, -2], [1, 0], [0, 2], [-1, 0], [0, -2]]
    cell0 = g.Polygon(crds)
    angle0 = np.arctan2(2,1)

    cell = cell0
    avgDir = _computeAvgDir(cell)
    self.assertAlmostEqual(angle0, avgDir)

    cell = a.rotate(cell0, np.pi/6, use_radians=True)
    avgDir = _computeAvgDir(cell)
    self.assertAlmostEqual(angle0 + np.pi/6 - np.pi/2, avgDir)

    cell = a.rotate(cell0, -np.pi/6, use_radians=True)
    avgDir = _computeAvgDir(cell)
    self.assertAlmostEqual(angle0-np.pi/6, avgDir)


  def test1(self):
    crds = [[0,0], [1,0], [1,2], [0,2], [0,0]]
    expd0 = 1.
    expdPi_2 = 2.
    expdPi_4 = (1. + 5.**.5)/2.
    ang2 = np.arctan(4.)
    expdang20 = 2.118034;
    expdang21 = 1.154508497

    cell = g.Polygon(crds)
    cs = abCellSize(cell)

    d0 = cs.computeSize(0.)
    d1 = cs.computeSize(np.pi/2.)
    d2 = cs.computeSize(np.pi)
    d3 = cs.computeSize(np.pi*3./2.)
    d4 = cs.computeSize(2.*np.pi)
    self.assertAlmostEqual(d0, expd0)
    self.assertAlmostEqual(d2, expd0)
    self.assertAlmostEqual(d1, expdPi_2)
    self.assertAlmostEqual(d3, expdPi_2)

    dPi_40 = cs.computeSize(np.pi/4)
    dPi_41 = cs.computeSize(np.pi/4 + np.pi/2.)
    dPi_42 = cs.computeSize(np.pi/4 + np.pi)
    dPi_43 = cs.computeSize(np.pi/4 + np.pi*3./2.)
    self.assertAlmostEqual(dPi_40, expdPi_4)
    self.assertAlmostEqual(dPi_41, expdPi_4)
    self.assertAlmostEqual(dPi_42, expdPi_4)
    self.assertAlmostEqual(dPi_43, expdPi_4)

    dang20 = cs.computeSize(ang2)
    dang21 = cs.computeSize(ang2 + np.pi/2.)
    dang22 = cs.computeSize(ang2 + np.pi)
    dang23 = cs.computeSize(ang2 + np.pi*3./2.)
    self.assertAlmostEqual(dang20, expdang20)
    self.assertAlmostEqual(dang21, expdang21)
    self.assertAlmostEqual(dang22, expdang20)
    self.assertAlmostEqual(dang23, expdang21)


  def test2(self):
    crds = [[0,0], [1,0], [1,2], [0,2], [0,0]]
    rotangle = np.pi/6
    expd0 = 1.
    expdPi_2 = 2.
    expdPi_4 = (1. + 5.**.5)/2.
    ang2 = rotangle + np.arctan(4.)
    expdang20 = 2.118034;
    expdang21 = 1.154508497

    cell = g.Polygon(crds)
    cell = a.rotate(cell, rotangle, use_radians = True)
    cs = abCellSize(cell)

    d0 = cs.computeSize(0. + rotangle)
    d1 = cs.computeSize(np.pi/2. + rotangle)
    d2 = cs.computeSize(np.pi + rotangle)
    d3 = cs.computeSize(np.pi*3./2. + rotangle)
    d4 = cs.computeSize(2.*np.pi + rotangle)
    self.assertAlmostEqual(d0, expd0)
    self.assertAlmostEqual(d2, expd0)
    self.assertAlmostEqual(d1, expdPi_2)
    self.assertAlmostEqual(d3, expdPi_2)

    dPi_40 = cs.computeSize(np.pi/4 + rotangle)
    dPi_41 = cs.computeSize(np.pi/4 + np.pi/2. + rotangle)
    dPi_42 = cs.computeSize(np.pi/4 + np.pi + rotangle)
    dPi_43 = cs.computeSize(np.pi/4 + np.pi*3./2. + rotangle)
    self.assertAlmostEqual(dPi_40, expdPi_4)
    self.assertAlmostEqual(dPi_41, expdPi_4)
    self.assertAlmostEqual(dPi_42, expdPi_4)
    self.assertAlmostEqual(dPi_43, expdPi_4)

    dang20 = cs.computeSize(ang2)
    dang21 = cs.computeSize(ang2 + np.pi/2.)
    dang22 = cs.computeSize(ang2 + np.pi)
    dang23 = cs.computeSize(ang2 + np.pi*3./2.)
    self.assertAlmostEqual(dang20, expdang20)
    self.assertAlmostEqual(dang21, expdang21)
    self.assertAlmostEqual(dang22, expdang20)
    self.assertAlmostEqual(dang23, expdang21)


  def test3(self):
    crds = [[0,0], [1,0], [1,2], [0,2], [0,0]]
    rotangle = np.pi/5
    expd0 = 1.
    expdPi_2 = 2.
    expdPi_4 = (1. + 5.**.5)/2.
    ang2 = rotangle + np.arctan(4.)
    expdang20 = 2.118034;
    expdang21 = 1.154508497

    cell = g.Polygon(crds)
    cell = a.rotate(cell, rotangle, use_radians = True)
    cs = abCellSize(cell)

    d0 = cs.computeSize(0. + rotangle)
    d1 = cs.computeSize(np.pi/2. + rotangle)
    d2 = cs.computeSize(np.pi + rotangle)
    d3 = cs.computeSize(np.pi*3./2. + rotangle)
    d4 = cs.computeSize(2.*np.pi + rotangle)
    self.assertAlmostEqual(d0, expd0)
    self.assertAlmostEqual(d2, expd0)
    self.assertAlmostEqual(d1, expdPi_2)
    self.assertAlmostEqual(d3, expdPi_2)

    dPi_40 = cs.computeSize(np.pi/4 + rotangle)
    dPi_41 = cs.computeSize(np.pi/4 + np.pi/2. + rotangle)
    dPi_42 = cs.computeSize(np.pi/4 + np.pi + rotangle)
    dPi_43 = cs.computeSize(np.pi/4 + np.pi*3./2. + rotangle)
    self.assertAlmostEqual(dPi_40, expdPi_4)
    self.assertAlmostEqual(dPi_41, expdPi_4)
    self.assertAlmostEqual(dPi_42, expdPi_4)
    self.assertAlmostEqual(dPi_43, expdPi_4)

    dang20 = cs.computeSize(ang2)
    dang21 = cs.computeSize(ang2 + np.pi/2.)
    dang22 = cs.computeSize(ang2 + np.pi)
    dang23 = cs.computeSize(ang2 + np.pi*3./2.)
    self.assertAlmostEqual(dang20, expdang20)
    self.assertAlmostEqual(dang21, expdang21)
    self.assertAlmostEqual(dang22, expdang20)
    self.assertAlmostEqual(dang23, expdang21)
    

if __name__ == '__main__':
  unittest.main()

