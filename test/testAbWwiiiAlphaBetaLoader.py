import unittest
import os
from alphaBetaLab import abWwiiiAlphaBetaLoader

class testAbWwiiiAlphaBetaLoader(unittest.TestCase):
  
  def testLoad(self):
    filedir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(filedir, 'obstrTest.in')
    nfreq = 25
    ldr = abWwiiiAlphaBetaLoader.abWwiiiAlphaBetaLoader(nfreq)
    ab = ldr.load(filepath)
    self.assertEqual(125, len(ab.alphaList))
    self.assertEqual(125, len(ab.betaList))
    self.assertEqual(125, len(ab.geoCoords))
    self.assertEqual(125, len(ab.sizeKm))
    
    i = 30
    self.assertEqual((64, 62), ab.coords[i])
    self.assertEqual((-84.75, 22.25), ab.geoCoords[i])
    expSize = (154.538, 172.635, 195.402, 227.38, 202.99, 184.424,166.792, 184.424, 202.99, 227.38, 195.402, 172.635, 154.538, 172.635, 195.402, 227.38, 202.99, 184.424, 166.792, 184.424, 202.99, 227.38, 195.402, 172.635, 154.538)
    self.assertEqual(expSize, tuple(ab.sizeKm[i]))
    aa = ab.alphaList[i]
    self.assertEqual((25, 25), aa.shape)
    expAlpha = ( 0.36,  0.45,  0.55,  0.64,  0.55,  0.46,  0.37,  0.38,  0.39, 0.39,  0.38,  0.37,  0.36,  0.45,  0.55,  0.64,  0.55,  0.46, 0.37,  0.38,  0.39,  0.39,  0.38,  0.37,  0.36 )
    self.assertEqual(expAlpha, tuple(aa[0,:]))
    self.assertEqual(expAlpha, tuple(aa[2,:]))
    bb = ab.betaList[i]
    self.assertEqual((25, 25), bb.shape)
    expBeta = ( 0.77,  0.76,  0.76,  0.75,  0.67,  0.58,  0.49,  0.47,  0.44, 0.42,  0.4 ,  0.39,  0.37,  0.46,  0.54,  0.63,  0.63,  0.63, 0.63,  0.64,  0.65,  0.67,  0.7 ,  0.73,  0.77)
    self.assertEqual(expBeta, tuple(bb[0,:]))
    self.assertEqual(expBeta, tuple(bb[2,:]))
    
    

if __name__ == '__main__':
  unittest.main()
