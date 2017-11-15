import unittest
import numpy as np
import os
import pickle
import abBathyDataGridder
from abUtils import *

import loadBathy_testGridder

class testAbBathyDataGridder(unittest.TestCase):

  def createMockBathy1(self):
    x1 = np.arange(0,15,.1)
    y1 = np.arange(0,10,.1)
    xm1, ym1 = np.meshgrid(x1, y1)
    xm1 = xm1.flatten()
    ym1 = ym1.flatten()
    z1 = xm1*0 + 100

    x2 = np.arange(0,5,.05)
    y2 = np.arange(0,3,.05)
    xm2, ym2 = np.meshgrid(x2, y2)
    xm2 = xm2.flatten()
    ym2 = ym2.flatten()
    z2 = xm2*0 + 50

    xs = np.concatenate((xm1, xm2))
    ys = np.concatenate((ym1, ym2))
    zs = np.concatenate((z1, z2))
    return xs, ys, zs
 
  def createBathyGridder1(self):
    xs, ys, zs = self.createMockBathy1()
    btGridder = abBathyDataGridder.abBathyDataGridder(xs, ys, zs, verbose = True)
    btGridder.nxInterpSteps = 8
    btGridder.nyInterpSteps = 12
    btGridder.nxInterpExtraSteps = 2
    btGridder.nyInterpExtraSteps = 2
    return btGridder


  def testReduceXYZ(self):
    btGridder = self.createBathyGridder1()
    btGridder._reduceXYZ(1, 10, .1, 1, 8, .1)
    redx, redy, redz, grdx, grdy =\
                btGridder.redx, btGridder.redy, btGridder.redz, btGridder.grdx, btGridder.grdy
    self.assertEqual(6269, len(redx))
    self.assertAlmostEqual(.9, min(redx))
    self.assertAlmostEqual(10, max(redx))
    self.assertEqual(6269, len(redy))
    self.assertAlmostEqual(.9, min(redy))
    self.assertAlmostEqual(8.05, max(redy))

    rdxarr = np.array(redx)
    rdxarr.sort()
    rdxarr = np.unique(rdxarr)
    self.assertAlmostEqual(.9, rdxarr[0])
    self.assertAlmostEqual(.925, rdxarr[1])
    self.assertAlmostEqual(10., rdxarr[-1])
    self.assertAlmostEqual(9.9, rdxarr[-2])

    rdyarr = np.array(redy)
    rdyarr.sort()
    rdyarr = np.unique(rdyarr)
    self.assertAlmostEqual(.9, rdyarr[0])
    self.assertAlmostEqual(.925, rdyarr[1])
    self.assertAlmostEqual(8.05, rdyarr[-1])
    self.assertAlmostEqual(7.9, rdyarr[-2])

    self.assertEqual(90, len(grdx))
    self.assertAlmostEqual(1, min(grdx))
    self.assertAlmostEqual(9.9, max(grdx))
    self.assertEqual(70, len(grdy))
    self.assertAlmostEqual(1, min(grdy))
    self.assertAlmostEqual(7.9, max(grdy))
 
    rdzarr = np.unique(redz)
    rdzarr.sort()
    self.assertAlmostEqual(50., rdzarr[0])
    self.assertAlmostEqual(62.5, rdzarr[1])
    self.assertAlmostEqual(66.66666666666, rdzarr[2])
    self.assertAlmostEqual(100., rdzarr[3])
    
  def testGetNXNYInterpPatch(self):
    btGridder = self.createBathyGridder1()
    btGridder._reduceXYZ(1, 10, .1, 1, 8, .1)
    nx, ny = btGridder.getNXNYInterpPatch()
    self.assertEqual(11, nx)
    self.assertEqual(5, ny)
    btGridder.nyInterpSteps = 11
    nx, ny = btGridder.getNXNYInterpPatch()
    self.assertEqual(6, ny)
    

  def testGetInterpPatch(self):
    btGridder = self.createBathyGridder1()
    btGridder._reduceXYZ(1, 10, .1, 1, 8, .1)
 
    predx, predy, predz, pgrdx, pgrdy = btGridder.getInterpPatch(0, 0)
    self.assertAlmostEqual(.925, min(predx), 1)
    self.assertAlmostEqual(1.925, max(predx), 1)
    self.assertAlmostEqual(.925, min(predy), 1)
    self.assertAlmostEqual(2.325, max(predy), 1)
    self.assertTrue(np.all(predz == 62.5))
    self.assertEqual(8, len(pgrdx))
    self.assertAlmostEqual(1., pgrdx[0], 1)
    self.assertAlmostEqual(1.7, pgrdx[-1], 1)
    self.assertAlmostEqual(12, len(pgrdy), 1)
    self.assertAlmostEqual(1., pgrdy[0], 1)
    self.assertAlmostEqual(2.1, pgrdy[-1], 1)

    predx, predy, predz, pgrdx, pgrdy = btGridder.getInterpPatch(1, 1)
    self.assertAlmostEqual(1.625, min(predx), 1)
    self.assertAlmostEqual(2.8, max(predx), 1)
    self.assertAlmostEqual(2.025, min(predy), 1)
    self.assertAlmostEqual(3.6, max(predy), 1)
    upz = np.unique(predz)
    self.assertEqual(2, len(upz))
    self.assertAlmostEqual(62.5, min(upz), 1)
    self.assertAlmostEqual(100., max(upz), 1)
    self.assertEqual(8, len(pgrdx))
    self.assertAlmostEqual(1.8, pgrdx[0], 1)
    self.assertAlmostEqual(2.5, pgrdx[-1], 1)
    self.assertAlmostEqual(12, len(pgrdy), 1)
    self.assertAlmostEqual(2.2, pgrdy[0], 1)
    self.assertAlmostEqual(3.3, pgrdy[-1], 1)
    
    predx, predy, predz, pgrdx, pgrdy = btGridder.getInterpPatch(10, 5)
    self.assertAlmostEqual(8.9, min(predx), 1)
    self.assertAlmostEqual(10.0, max(predx), 1)
    self.assertAlmostEqual(6.9, min(predy), 1)
    self.assertAlmostEqual(8.05, max(predy), 1)
    self.assertTrue(np.all(predz == 100.))
    self.assertEqual(10, len(pgrdx))
    self.assertAlmostEqual(9., pgrdx[0], 1)
    self.assertAlmostEqual(9.9, pgrdx[-1], 1)
    self.assertAlmostEqual(10, len(pgrdy), 1)
    self.assertAlmostEqual(7., pgrdy[0], 1)
    self.assertAlmostEqual(7.9, pgrdy[-1], 1)
  
    btGridder.nyInterpSteps = 11
    predx, predy, predz, pgrdx, pgrdy = btGridder.getInterpPatch(10, 5)
    self.assertAlmostEqual(8.9, min(predx), 1)
    self.assertAlmostEqual(10., max(predx), 1)
    self.assertAlmostEqual(6.4, min(predy), 1)
    self.assertAlmostEqual(8.05, max(predy), 1)
    self.assertTrue(np.all(predz == 100.))
    self.assertEqual(10, len(pgrdx))
    self.assertAlmostEqual(9., pgrdx[0], 1)
    self.assertAlmostEqual(9.9, pgrdx[-1], 1)
    self.assertAlmostEqual(15, len(pgrdy), 1)
    self.assertAlmostEqual(6.5, pgrdy[0], 1)
    self.assertAlmostEqual(7.9, pgrdy[-1], 1)

  def testDoGridSerial(self):
    btGridder = self.createBathyGridder1()
    grdx, grdy, grdz = btGridder.doGridSerial(1, 10, .1, 1, 8, .1)
    self.assertEqual(90, len(grdx))
    self.assertEqual(70, len(grdy))
    self.assertEqual((70, 90), grdz.shape)
    self.assertAlmostEqual(1., grdx[0])
    self.assertAlmostEqual(9.9, grdx[-1])
    self.assertTrue(((grdx[1:]-grdx[:-1]) - .1 < .00001).all())
    self.assertAlmostEqual(1., grdy[0])
    self.assertAlmostEqual(7.9, grdy[-1])
    self.assertTrue(((grdy[1:]-grdy[:-1]) - .1 < .00001).all())

    self.assertAlmostEqual(62.5, grdz[0, 0])
    self.assertAlmostEqual(100., grdz[0, -1])
    self.assertAlmostEqual(62.5, grdz[18, 0])
    self.assertAlmostEqual(100., grdz[18, -1])
    self.assertAlmostEqual(100., grdz[-1, 0])
    self.assertAlmostEqual(100., grdz[-1, -1])

  def testDoGridParallel(self):
    btGridder = self.createBathyGridder1()
    grdx, grdy, grdz = btGridder.doGridParallel(1, 10, .1, 1, 8, .1)
    self.assertEqual(90, len(grdx))
    self.assertEqual(70, len(grdy))
    self.assertEqual((70, 90), grdz.shape)
    self.assertAlmostEqual(1., grdx[0])
    self.assertAlmostEqual(9.9, grdx[-1])
    self.assertTrue(((grdx[1:]-grdx[:-1]) - .1 < .00001).all())
    self.assertAlmostEqual(1., grdy[0])
    self.assertAlmostEqual(7.9, grdy[-1])
    self.assertTrue(((grdy[1:]-grdy[:-1]) - .1 < .00001).all())

    self.assertAlmostEqual(62.5, grdz[0, 0])
    self.assertAlmostEqual(100., grdz[0, -1])
    self.assertAlmostEqual(62.5, grdz[18, 0])
    self.assertAlmostEqual(100., grdz[18, -1])
    self.assertAlmostEqual(100., grdz[-1, 0])
    self.assertAlmostEqual(100., grdz[-1, -1])

  def testDoGrid(self):
    btGridder = self.createBathyGridder1()
    grdx, grdy, grdz = btGridder.doGrid(1, 10, .1, 1, 8, .1)
    self.assertEqual(90, len(grdx))
    self.assertEqual(70, len(grdy))
    self.assertEqual((70, 90), grdz.shape)
    self.assertAlmostEqual(1., grdx[0])
    self.assertAlmostEqual(9.9, grdx[-1])
    self.assertTrue(((grdx[1:]-grdx[:-1]) - .1 < .00001).all())
    self.assertAlmostEqual(1., grdy[0])
    self.assertAlmostEqual(7.9, grdy[-1])
    self.assertTrue(((grdy[1:]-grdy[:-1]) - .1 < .00001).all())

    self.assertAlmostEqual(62.5, grdz[0, 0])
    self.assertAlmostEqual(100., grdz[0, -1])
    self.assertAlmostEqual(62.5, grdz[18, 0])
    self.assertAlmostEqual(100., grdz[18, -1])
    self.assertAlmostEqual(100., grdz[-1, 0])
    self.assertAlmostEqual(100., grdz[-1, -1])

  def testDoGridWithLand(self):
    btGridder = self.createBathyGridder1()
    btGridder.nParallelWorker = 4
    dd = .001
    land1 = [[2. + dd, 2. + dd], [3. - dd, 2. + dd], [3. - dd, 3. - dd], [2. + dd, 3. - dd]]
    land2 = [[4. + dd, 2. + dd], [5. - dd, 2. + dd], [5. - dd, 3. - dd], [4. + dd, 3. - dd]]
    btGridder.setLandPolygons([land1, land2])
    grdx, grdy, grdz = btGridder.doGrid(1, 10, .1, 1, 8, .1)
    self.assertEqual(90, len(grdx))
    self.assertEqual(70, len(grdy))
    self.assertEqual((70, 90), grdz.shape)
    self.assertAlmostEqual(1., grdx[0])
    self.assertAlmostEqual(9.9, grdx[-1])
    self.assertTrue(((grdx[1:]-grdx[:-1]) - .1 < .00001).all())
    self.assertAlmostEqual(1., grdy[0])
    self.assertAlmostEqual(7.9, grdy[-1])
    self.assertTrue(((grdy[1:]-grdy[:-1]) - .1 < .00001).all())

    self.assertAlmostEqual(62.5, grdz[0, 0])
    self.assertAlmostEqual(100., grdz[0, -1])
    self.assertAlmostEqual(62.5, grdz[18, 0])
    self.assertAlmostEqual(100., grdz[18, -1])
    self.assertAlmostEqual(100., grdz[-1, 0])
    self.assertAlmostEqual(100., grdz[-1, -1])
    self.assertEqual(200, len(grdz[np.isnan(grdz)]))
    self.assertTrue(\
        (np.concatenate(( np.arange(2, 3, .1), np.arange(4, 5, .1)))\
        - np.unique( grdx[np.where(np.isnan(grdz))[1]]) < .001).all() )
    self.assertTrue(\
        (np.arange(2, 3, .1)\
        - np.unique( grdx[np.where(np.isnan(grdz))[0]]) < .001).all() )

  def testGridLaSpezia(self):
    xyz = loadBathy_testGridder.loadBathy()
    xs, ys, zs = xyz[:,0], xyz[:,1], xyz[:,2]
    minx, maxx, dx = 9.7, 10.4, .001
    miny, maxy, dy = 43.96, 44.13, .001
    grdr = abBathyDataGridder.abBathyDataGridder(xs, ys, zs)
    grdx, grdy, grdz = grdr.doGrid(minx, maxx, dx, miny, maxy, dy)
    self.assertEqual((167, 350), grdz.shape)
    self.assertTrue(13500 < len(grdz[np.isnan(grdz)]) < 14000)
    grdz[np.isnan(grdz)] = 0
    self.assertTrue(min(grdz.flatten()) < -220)

  def testGridLaSpeziaFine(self):
    xyz = loadBathy_testGridder.loadBathy()
    xs, ys, zs = xyz[:,0], xyz[:,1], xyz[:,2]
    minx, maxx, dx = 9.7, 10.4, .0005
    miny, maxy, dy = 43.96, 44.13, .0005
    grdr = abBathyDataGridder.abBathyDataGridder(xs, ys, zs, nParallelWorker = 4)
    grdr.nxInterpSteps = 100
    grdr.nyInterpSteps = 100
    grdx, grdy, grdz = grdr.doGrid(minx, maxx, dx, miny, maxy, dy)
    self.assertEqual((331, 699), grdz.shape)
    self.assertTrue(65000 < len(grdz[np.isnan(grdz)]) < 66000)
    grdz[np.isnan(grdz)] = 0
    self.assertTrue(min(grdz.flatten()) < -220)

  def testGridLaSpeziaWithException(self):
    xyz = loadBathy_testGridder.loadBathy()
    xs, ys, zs = xyz[:,0], xyz[:,1], xyz[:,2]
    minx, maxx, dx = 9.7, 10.4, .0005
    miny, maxy, dy = 43.96, 44.13, .0005
    grdr = abBathyDataGridder.abBathyDataGridder(xs, ys, zs, nParallelWorker = 4)
    grdr.nxInterpSteps = 10
    grdr.nyInterpSteps = 10
    excRaised = False
    try:
      grdx, grdy, grdz = grdr.doGrid(minx, maxx, dx, miny, maxy, dy)
    except abException as e:
      excRaised = True
      print(e.message)
    self.assertTrue(excRaised)
      
  def testGridLaSpeziaFineWithCoastLine(self):
    xyz = loadBathy_testGridder.loadBathy()
    cstFlDir = os.path.dirname(os.path.abspath(__file__))
    cstFlPth = os.path.join(cstFlDir, 'testGridder_coast.pckl')
    fl = open(cstFlPth)
    cstln = pickle.load(fl)
    fl.close()
    xs, ys, zs = xyz[:,0], xyz[:,1], xyz[:,2]
    minx, maxx, dx = 9.7, 10.4, .0005
    miny, maxy, dy = 43.96, 44.13, .0005
    grdr = abBathyDataGridder.abBathyDataGridder(xs, ys, zs,\
      landPolygons = cstln, verbose = True, nParallelWorker = 4)
    grdr.nxInterpSteps = 200
    grdr.nyInterpSteps = 200
    grdx, grdy, grdz = grdr.doGrid(minx, maxx, dx, miny, maxy, dy)
    self.assertEqual((331, 699), grdz.shape)
    self.assertTrue(81000 < len(grdz[np.isnan(grdz)]) < 82000)
    grdz[np.isnan(grdz)] = 0
    self.assertTrue(min(grdz.flatten()) < -220)

  def testGridLaSpeziaFineWithCoastLine2(self):
    xyz = loadBathy_testGridder.loadBathy()
    cstFlDir = os.path.dirname(os.path.abspath(__file__))
    cstFlPth = os.path.join(cstFlDir, 'testGridder_coast.pckl')
    fl = open(cstFlPth)
    cstln = pickle.load(fl)
    fl.close()
    xs, ys, zs = xyz[:,0], xyz[:,1], xyz[:,2]
    minx, maxx, dx = 9.7, 10.4, .0005
    miny, maxy, dy = 43.96, 44.13, .0005
    grdr = abBathyDataGridder.abBathyDataGridder(xs, ys, zs,\
      landPolygons = cstln, verbose = True, nParallelWorker = 4)
    grdr.nxInterpSteps = 100
    grdr.nyInterpSteps = 100
    grdx, grdy, grdz = grdr.doGrid(minx, maxx, dx, miny, maxy, dy)
    self.assertEqual((331, 699), grdz.shape)
    self.assertTrue(81000 < len(grdz[np.isnan(grdz)]) < 82000)
    grdz[np.isnan(grdz)] = 0
    self.assertTrue(min(grdz.flatten()) < -220)

  def testGridLaSpeziaFineWithCoastLine3(self):
    xyz = loadBathy_testGridder.loadBathy()
    cstFlDir = os.path.dirname(os.path.abspath(__file__))
    cstFlPth = os.path.join(cstFlDir, 'testGridder_coast.pckl')
    fl = open(cstFlPth)
    cstln = pickle.load(fl)
    fl.close()
    xs, ys, zs = xyz[:,0], xyz[:,1], xyz[:,2]
    minx, maxx, dx = 9.7, 10.4, .0005
    miny, maxy, dy = 43.96, 44.13, .0005
    grdr = abBathyDataGridder.abBathyDataGridder(xs, ys, zs,\
      landPolygons = cstln, verbose = True, nParallelWorker = 4)
    grdr.nxInterpSteps = 50
    grdr.nyInterpSteps = 50
    grdx, grdy, grdz = grdr.doGrid(minx, maxx, dx, miny, maxy, dy)
    self.assertEqual((331, 699), grdz.shape)
    self.assertTrue(81000 < len(grdz[np.isnan(grdz)]) < 82000)
    grdz[np.isnan(grdz)] = 0
    self.assertTrue(min(grdz.flatten()) < -220)


if __name__ == '__main__':
  unittest.main()
