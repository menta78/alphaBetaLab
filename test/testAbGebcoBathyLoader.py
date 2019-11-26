import os
import unittest
import numpy as np
from alphaBetaLab import abGebcoBathyLoader

class testAbGebcoBathyLoader(unittest.TestCase):

  def test0(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    gbFlPth = os.path.join(mdldir, 'gebco_test.nc')
    lon, lat, z = abGebcoBathyLoader.loadBathy(gbFlPth)
    self.assertAlmostEqual(-2431.26, np.min(z), 4)
    self.assertEqual(928, len(lon))
    self.assertEqual(1983, len(lat))
    self.assertEqual((1983, 928), z.shape)

  def test1(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    gbFlPth = os.path.join(mdldir, 'gebco_test.nc')
    lon, lat, z = abGebcoBathyLoader.loadBathy(gbFlPth, llcrnr=[40, 12], urcrnr=[42, 18])
    self.assertAlmostEqual(-2431.26, np.min(z), 4)
    self.assertTrue(np.all(lon >= 40))
    self.assertTrue(np.all(lon <= 42))
    self.assertTrue(np.all(lat >= 12))
    self.assertTrue(np.all(lat <= 18))
    self.assertEqual(480, len(lon))
    self.assertEqual(1440, len(lat))
    self.assertEqual((1440, 480), z.shape)
    self.assertAlmostEqual(-80.21875, z[400, 100], 4)

  def test2(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    gbFlPth = os.path.join(mdldir, 'gebco_test1.nc')
    lon, lat, z = abGebcoBathyLoader.loadBathy(gbFlPth, llcrnr=[179, 8.5], urcrnr=[181, 11.5])
    self.assertAlmostEqual(-6614.5347, np.min(z), 4)
    self.assertTrue(np.all(lon >= 179))
    self.assertTrue(np.all(lon <= 182))
    self.assertTrue(np.all(lat >= 8.5))
    self.assertTrue(np.all(lat <= 11.5))
    self.assertEqual(480, len(lon))
    self.assertEqual(720, len(lat))
    self.assertEqual((720, 480), z.shape)
    self.assertAlmostEqual(-5928.826, z[400, 100], 3)

  def test3(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    gbFlPth = os.path.join(mdldir, 'gebco_test2.nc')
    lon, lat, z = abGebcoBathyLoader.loadBathy(gbFlPth, llcrnr=[179, 8.5], urcrnr=[-179, 11.5])
    self.assertAlmostEqual(-6614.5347, np.min(z), 4)
    self.assertTrue(np.all(np.logical_or(lon <= -179, lon >= 179)))
    self.assertTrue(np.all(lat >= 8.5))
    self.assertTrue(np.all(lat <= 11.5))
    self.assertEqual(480, len(lon))
    self.assertEqual(720, len(lat))
    self.assertEqual((720, 480), z.shape)
    self.assertAlmostEqual(-5928.826, z[400, 100], 3)
    

    

if __name__ == '__main__':
  unittest.main()
