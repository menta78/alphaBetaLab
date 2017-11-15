import re
import numpy as np


class abAlphaBetaLoadObj:
  def __init__(self):
    self.coords = []
    self.geoCoords = []
    self.alphaList = []
    self.betaList = []
    self.sizeKm = []


class abWwiiiAlphaBetaLoader():

  def __init__(self, nfreq = 25):
    """
    abWwiiiAlphaBetaLoader: utility class to load alpha and beta from files saved by abWwiiiObstrFileSaver
    """
    self.nfreq = nfreq

  def load(self, abFilePath):
    o = abAlphaBetaLoadObj()

    nfreq = self.nfreq

    fl = open(abFilePath)
    fl.readline()
    npt = int(fl.readline().strip(' \n\r\t'))
    for ipt in range(npt):
      ln = fl.readline().strip(' \n\r\t')
      mtch = re.match('(.*) ([-0-9\.]*), ([-0-9\.]*)', ln)
      grps = mtch.groups()
      lon = float(grps[-2])
      lat = float(grps[-1])
      o.geoCoords.append((lon, lat))

      ln = fl.readline().strip(' \n\r\t')
      vls = [int(v) for v in ln.split() if v != '']
      ilon = vls[0]
      ilat = vls[1]
      o.coords.append((ilon, ilat))
   
      fl.readline()

      szln = fl.readline().strip(' \n\r\t')
      sizes = np.array([float(v) for v in szln.split() if v != ''])
      o.sizeKm.append(sizes)

      fl.readline()
      fl.readline()
      fl.readline()
      alpha = []
      for ifreq in range(nfreq):
        ln = fl.readline().strip(' \n\r\t')
        a = [float(v) for v in ln.split() if v != '']
        alpha.append(a)
      alpha = np.array(alpha)
      o.alphaList.append(alpha)
      
      fl.readline()
      beta = []
      for ifreq in range(nfreq):
        ln = fl.readline().strip(' \n\r\t')
        b = [float(v) for v in ln.split() if v != '']
        beta.append(b)
      beta = np.array(beta)
      o.betaList.append(beta)
      
    return o

