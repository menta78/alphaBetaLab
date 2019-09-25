import unittest
import os
import shutil
import pickle

from alphaBetaLab import abWwiiiGridFilesCompiler

class testAbWwiiiGridFilesCompiler(unittest.TestCase):

  def testCompileWwiiiGridFiles(self):
    currdir = os.path.dirname(os.path.abspath(__file__))
    grdBathyFlPath = os.path.join(currdir, 'bathyForWwiiiFilesCompilation.pkl')
    fl = open(grdBathyFlPath, 'rb')
    grdx, grdy, grdz = pickle.load(fl, encoding='bytes')
    fl.close()
    testdir = os.path.join(currdir, 'testgrid')
    try:
      os.mkdir(testdir)
    except:
      pass

    try:
      wwiiiGrdComp = abWwiiiGridFilesCompiler.abWwiiiGridFilesCompiler(grdx, grdy, grdz)
      wwiiiGrdComp.generateFiles('test', 9.75, 10.035, .003, 43.97, 44.12, .003, testdir)
      fls = os.listdir(testdir)
    finally:
      shutil.rmtree(testdir)
    self.assertEqual(4, len(fls))



if __name__ == '__main__':
  unittest.main()
