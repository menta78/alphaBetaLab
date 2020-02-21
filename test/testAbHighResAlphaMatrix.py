import unittest
import numpy as np
import alphaBetaLab.abHighResAlphaMatrix as hram

class testAbHighResAlphaMatrix(unittest.TestCase):

  def testWrapAroundDateline(self):
    xs = np.arange(-180, 180, 1)
    ys = np.arange(-90, 90, 1)
    alphas = np.zeros((len(ys), len(xs)))
    alphas[:,1] = 1
    alphas[:,4] = .9
    alphas[:,-1] = .7
    alphas[:,356] = .5
    ha = hram.abHighResAlphaMatrix(xs, ys, alphas)
    self.assertEqual(360, len(ha.xs))
    self.assertEqual(180, len(ha.ys))
    self.assertEqual((180, 360), ha.alphas.shape)
    ha.wrapAroundDateline()
    self.assertEqual(370, len(ha.xs))
    self.assertEqual(180, len(ha.ys))
    self.assertEqual((180, 370), ha.alphas.shape)
    self.assertTrue(np.all(ha.alphas[1,:10] == ha.alphas[1,-10:]))
    self.assertEqual(.5, ha.alphas[10, 1])
    self.assertEqual(.7, ha.alphas[20, 4])
    self.assertEqual(1, ha.alphas[20, 6])
    self.assertEqual(.9, ha.alphas[20, 9])
    

if __name__ == '__main__':
  unittest.main()

