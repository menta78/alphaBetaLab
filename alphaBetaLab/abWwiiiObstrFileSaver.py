import numpy as np

class abWwiiiObstrFileSaver:

  def __init__(self, locCoords, locGeoCoords, locAlphas, locBetas, locSizesKm,\
                     shdCoords, shdGeoCoords, shdAlphas, shdBetas, shdSizesKm):
    """
    abWwiiiObstrFileSaver: saves the wwiii input file for the advanced 
    parameterization of unresolved obstacles.
    """
    self.locCoords = locCoords
    self.locGeoCoords = locGeoCoords
    self.locAlphas = locAlphas
    self.locBetas = locBetas
    self.locSizesKm = locSizesKm
    self.shdCoords = shdCoords
    self.shdGeoCoords = shdGeoCoords
    self.shdAlphas = shdAlphas
    self.shdBetas = shdBetas
    self.shdSizesKm = shdSizesKm

  def _saveFile(self, fileName, header, coords, geoCoords, alphaList, betaList, sizesKm):
    fl = open(fileName, 'w')
    fl.write(header + '\n')
    fl.write(str(len(coords)) + '\n')
    for icrd, crd, alpha, beta, size in zip(range(len(coords)), coords, alphaList, betaList, sizesKm):
      if geoCoords != None:
        [lon, lat] = geoCoords[icrd]
        fl.write('$ ilon ilat of the cell. lon: ' + str(lon) + ', ' + str(lat) + '\n')
      ln = '   '.join(str(c + 1) for c in crd) + '\n'
      fl.write(ln)
      fl.write('$ sizes of the cell in km\n')
      ln = '   '.join('{:10.3f}'.format(s) for s in size) + '\n'
      fl.write(ln)
      fl.write('$ mean alpha: ' + str(np.mean(alpha)) + '\n')
      fl.write('$ mean beta: ' + str(np.mean(beta)) + '\n')
      fl.write('$alpha by ik, ith\n')
      for ak in alpha:
        ln = '  '.join('{:1.2f}'.format(a) for a in ak) + '\n'
        fl.write(ln)
      fl.write('$beta by ik, ith\n')
      for bk in beta:
        ln = '  '.join('{:1.2f}'.format(b) for b in bk) + '\n'
        fl.write(ln)
    fl.close()

  def saveLocFile(self, locFileName):
    self._saveFile(locFileName, '$WAVEWATCH III LOCAL OBSTRUCTIONS',\
            self.locCoords, self.locGeoCoords, self.locAlphas, self.locBetas, self.locSizesKm)

  def saveShdFile(self, shdFileName):
    self._saveFile(shdFileName, '$WAVEWATCH III SHADOW OBSTRUCTIONS',\
            self.shdCoords, self.shdGeoCoords, self.shdAlphas, self.shdBetas, self.shdSizesKm)

  def saveFiles(self, locFileName, shadowFileName):
    self.saveLocFile(locFileName)
    self.saveShdFile(shadowFileName)
