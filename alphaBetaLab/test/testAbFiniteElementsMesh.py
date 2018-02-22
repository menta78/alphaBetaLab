import unittest
import os

import abFiniteElementsMesh

class testAbFiniteElementsMesh(unittest.TestCase):
   
  def testLoadFromGr3File1(self):
    mdldir = os.path.dirname( os.path.abspath(__file__) )
    mshFilePath = os.path.join(mdldir, 'finiteElementsMeshTest/hgridGiamaica.gr3')
    import pdb; pdb.set_trace()
    feMeshSpec = abFiniteElementsMesh.loadFromGr3File(mshFilePath)
    # some random checks
    
    


if __name__ == '__main__':
  unittest.main()
