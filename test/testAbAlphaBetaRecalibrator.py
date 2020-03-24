import unittest
import numpy as np
from shapely import geometry as g
from shapely import affinity as a

from alphaBetaLab import abUtils, abAlphaBetaRecalibrator

class testAbAlphaBetaRecalibrator(unittest.TestCase):

  def testGetDefaultFactors(self):
    locRecFct, shdRecFct = abAlphaBetaRecalibrator.getDefaultFactors(abUtils.MESHTYPE_REGULAR)
    self.assertEqual(1., locRecFct)
    self.assertEqual(1.2, shdRecFct)
    locRecFct, shdRecFct = abAlphaBetaRecalibrator.getDefaultFactors(abUtils.MESHTYPE_TRIANGULAR)
    self.assertAlmostEqual(1.1547, locRecFct, 4)
    self.assertAlmostEqual(1.38564, shdRecFct, 4)

  def testRecalibrator(self):
    rclb = abAlphaBetaRecalibrator.abAlphaBetaRecalibrator(obstFactor=1.2)
    self.assertEqual(1.2, rclb.obstFactor)
    calpha = rclb.recalibrate(.5)
    self.assertAlmostEqual(.4, calpha)
    calpha = rclb.recalibrate(.2)
    self.assertAlmostEqual(.04, calpha)
    calpha = rclb.recalibrate(.1)
    self.assertAlmostEqual(0, calpha)


if __name__ == '__main__':
  unittest.main()

