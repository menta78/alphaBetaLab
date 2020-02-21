import numpy as np
from shapely import geometry as g

landBoundaryExteriorType = 0
landBoundaryIslandType = 1

class _abTriMeshSpec:

  def __init__(self):
    """
    _abTriMeshSpec: class representing the logical structure of a triangular mesh
    (used for example in a finite elemets numerical scheme)
    """
    # node index -> node coordinates
    self.nodes = {}
    # node index -> node depth
    self.nodeBathy = {}
    # polygon index -> vertice nodes indices
    self.connectionPolygons = {}
    # boundary index -> boundary type: 0=main boundary, 1=island
    self.landBoundaries = {}
    # node index -> land boundary id
    self.landBoundaryNodes = {}
    # node index in the order they are loaded from the file
    self.landBoundaryOrdered = []
    # node index -> open boundary id
    self.openBoundaryNodes = {}

  def getCellPolygons(self, excludeLandBoundary=True, excludeOpenBoundary=False):
    """
    getCellPolygons: returns an approximate cental median cell for each non-land-boundary node
    """
    plIds = list(self.connectionPolygons.keys())
    plIds.sort()
    centroidsByNode = {}
    for plId in plIds:
      vrtxsNodes = self.connectionPolygons[plId]
      vrtxs = [self.nodes[nid] for nid in vrtxsNodes]
      vrtxs = adjustCrossDatelineVertices(vrtxs)
      connPoly = g.Polygon(vrtxs)
      centroid = connPoly.centroid.coords[:][0]
      for nid in vrtxsNodes:
        nodeCentroids = centroidsByNode.get(nid, [])
        nodeCentroids.append(centroid)
        centroidsByNode[nid] = nodeCentroids
    
    cellPlys = []
    nodeIds = []
    nodeIds0 = list(centroidsByNode.keys())
    nodeIds0.sort()
    npts = [g.Point(self.nodes[nid]) for nid in nodeIds0]
    for nid, npt in zip(nodeIds0, npts):
      ccc = centroidsByNode[nid]
      if nid in self.landBoundaryNodes:
        if excludeLandBoundary:
          continue
        else:
          ccc.append(self.nodes[nid])
      if nid in self.openBoundaryNodes:
        if excludeOpenBoundary:
          continue
        else:
          ccc.append(self.nodes[nid])
      ccc.append(self.nodes[nid])
      vrtxs = g.LineString(ccc)
      approxCell = vrtxs.convex_hull
      if not isinstance(vrtxs.convex_hull, g.Polygon):
        continue
      cellPlys.append(approxCell)
      nodeIds.append(nid)
    return nodeIds, cellPlys

  def createSchismWWMBndFile(self, schismWWMBndFilePath):
    fl = open(schismWWMBndFilePath, 'w')
    fl.write('schism WWM boundary TEST file\n')
    fl.write('*\n')
    nodeIds = self.nodes.keys()
    for nid in nodeIds:
      nodeIds
      if nid in self.landBoundaryNodes:
        bndId = self.landBoundaryNodes[nid]
        bndTyp = self.landBoundaries[bndId]
        if bndTyp == landBoundaryExteriorType:
          bndtyp = 1
        else:
          bndtyp = -1
      elif nid in self.openBoundaryNodes:
        bndtyp = 2
      else:
        bndtyp = 0
      ln = '  '.join([str(nid), str(bndtyp), str(bndtyp), str(bndtyp)]) + '\n'
      fl.write(ln)
    fl.write('')
    fl.close()

  def saveAsMsh(self, filePath, bathyFactor=-1):
    fl = open(filePath, 'w')
    fl.write('$MeshFormat\n2 0 8\n$EndMeshFormat\n$Nodes\n')
    nodeIds = list(self.nodes.keys())
    nds = len(nodeIds)
    fl.write(str(nds).rjust(12) + '\n')
    nodeIds.sort()
    for nd in nodeIds:
      lon, lat = self.nodes[nd]
      dpt = self.nodeBathy[nd]*bathyFactor
      ln = str(nd).rjust(10) + '{a:5.10}'.format(a=lon).rjust(22)\
                  + '{a:5.10}'.format(a=lat).rjust(22) + '{a:5.10}'.format(a=dpt).rjust(22) + '\n'
      fl.write(ln)
    fl.write('$EndNodes\n$Elements\n')
    bndNodeIds = self.landBoundaryOrdered
    connPolyIds = sorted(self.connectionPolygons.keys())
    elmCnt = len(bndNodeIds) + len(connPolyIds)
    fl.write(str(elmCnt).rjust(12) + '\n')
    elmTypStr = '15'.rjust(10)
    ntagStr = '2'.rjust(10)
    for bndNodeId, ibnd in zip(bndNodeIds, range(1,len(bndNodeIds)+1)):
      bndId = self.landBoundaryNodes[bndNodeId]
      bndTyp = self.landBoundaries[bndId]
      ln = str(ibnd).rjust(10) + elmTypStr + ntagStr + str(bndTyp).rjust(10)\
                           + '0'.rjust(10) + str(bndNodeId).rjust(10) + '\n' 
      fl.write(ln)
    mxBnd = len(bndNodeIds)
    elmTypStr = '2'.rjust(10)
    ntagStr = '3'.rjust(10)
    for connPolyId, elmId in zip(connPolyIds, range(mxBnd+1, mxBnd+len(connPolyIds)+1)):
      ln = str(elmId).rjust(8) + elmTypStr + ntagStr + '0'.rjust(8)\
             + str(connPolyId).rjust(8) + '0'.rjust(8)\
             + ''.join([str(nd).rjust(8) for nd in self.connectionPolygons[connPolyId]]) + '\n'
      fl.write(ln)
    fl.write('$EndElements')
    fl.close()
 


def loadFromGr3File(gr3FilePath):
  """
  loadFromGr3File: loads an instance of _abTriMeshSpec from a gr3 file 
  (format used, for example in model schism).
  """
  m = _abTriMeshSpec()
  fl = open(gr3FilePath)
  fl.readline()

  # getting nodes and polygons count
  cntln = fl.readline().strip('\n\t\r ')
  connPlysCount, nodeCount = (int(vstr) for vstr in cntln.split() if vstr)

  # loading nodes
  for inode in range(nodeCount):
    nodeline = fl.readline().strip('\n\t\r ')
    vlsstr = [s for s in nodeline.split() if s]
    nodeId = int(vlsstr[0])
    lon = float(vlsstr[1])
    lat = float(vlsstr[2])
    dpth = float(vlsstr[3])
    
    m.nodes[nodeId] = (lon, lat)
    m.nodeBathy[nodeId] = dpth
  
  # loading connection polygons
  for ipl in range(connPlysCount):
    polyline = fl.readline().strip('\n\t\r ')
    vlsstr = [s for s in polyline.split() if s]
    connPolyId = int(vlsstr[0])
    nodeIds = [int(s) for s in vlsstr[2:]]
    
    m.connectionPolygons[connPolyId] = nodeIds
    
  # loading open boundary
  line = fl.readline().strip('\n\t\r ')
  vlsstr = [s for s in line.split() if s]
  nOpenBoundary = int(vlsstr[0])
  fl.readline()
  for ibnd in range(nOpenBoundary):
    line = fl.readline().strip('\n\t\r ')
    vlsstr = [s for s in line.split() if s]
    nNodes = int(vlsstr[0])
    for ind in range(nNodes):
      line = fl.readline().strip('\n\t\r ')
      nodeId = int(line)
      m.openBoundaryNodes[nodeId] = ibnd + 1
    
  # loading land boundary
  line = fl.readline().strip('\n\t\r ')
  vlsstr = [s for s in line.split() if s]
  nLandBoundary = int(vlsstr[0])
  fl.readline()
  for ibnd in range(nLandBoundary):
    line = fl.readline().strip('\n\t\r ')
    vlsstr = [s for s in line.split() if s]
    nNodes = int(vlsstr[0])

    bndTyp = int(vlsstr[1])
    if bndTyp == 20:
      bndTyp = landBoundaryExteriorType
    if bndTyp == 21:
      bndTyp = landBoundaryIslandType

    m.landBoundaries[ibnd + 1] = bndTyp
    for ind in range(nNodes):
      line = fl.readline().strip('\n\t\r ')
      nodeId = int(line)
      m.landBoundaryNodes[nodeId] = ibnd + 1
      m.landBoundaryOrdered.append(nodeId)

  fl.close()
  return m
 


def loadFromMshFile(mshFilePath):
  """
  loadFromMshFile: loads an instance of _abTriMeshSpec from a msh file 
  (format used, for example in model ww3).
  """
  m = _abTriMeshSpec()
  fl = open(mshFilePath)
  fl.readline()
  fl.readline()
  fl.readline()
  fl.readline()

  # getting nodes and polygons count
  cntln = fl.readline().strip('\n\t\r ')
  nodeCount = int(cntln)

  # loading nodes
  for inode in range(nodeCount):
    nodeline = fl.readline().strip('\n\t\r ')
    vlsstr = [s for s in nodeline.split() if s]
    nodeId = int(vlsstr[0])
    lon = float(vlsstr[1])
    lat = float(vlsstr[2])
    dpth = float(vlsstr[3])
    
    m.nodes[nodeId] = (lon, lat)
    m.nodeBathy[nodeId] = dpth
  
  fl.readline()
  fl.readline()

  cntln = fl.readline().strip('\n\t\r ')
  connPlysCount = int(cntln)
  # loading connection polygons
  for ipl in range(connPlysCount):
    polyline = fl.readline().strip('\n\t\r ')
    vlsstr = [s for s in polyline.split() if s]
    elementId = int(vlsstr[0])
    ntag = int(vlsstr[2])
    elmtyp = int(vlsstr[1])

    if elmtyp == 15: # 15: single point element
      # is a boundary node. Loading it as land boundary
      ibnd = elementId
      nodeId = int(vlsstr[-1])
      bndType = int(vlsstr[3])
      m.landBoundaryNodes[nodeId] = ibnd
      m.landBoundaries[ibnd] = bndType
      m.landBoundaryOrdered.append(nodeId)
    elif elmtyp == 2: # 2: triangle 
      nodeIds = [int(s) for s in vlsstr[6:]]
      connPolyId = int(vlsstr[4])
      m.connectionPolygons[connPolyId] = nodeIds
  
  #AFAIK the open boundary is not included in the file

  fl.close()
  return m


def adjustCrossDatelineVertices(vertices):
  """
  THIS WORKS ONLY WITH TRIANGLES
  Kevin Martin's fix to close the mesh at the
  dateline: understand whether an element has a single node
  isolated on the other side, and bring it
  back. This approach does nothing with the element
  that contains the pole.
  """
  x = np.array([v[0] for v in vertices])
  y = np.array([v[1] for v in vertices])
  if   ( (x[1]-x[0])>180 and (x[2]-x[0])>180 ):
    # In this case, x0 is 'isolated' to the East of the dateline; we "bring it back" towards the West
    x[0] = x[0] + 360
  elif ( (x[0]-x[1])>180 and (x[2]-x[1])>180 ):
    # In this case, x1 is 'isolated' to the East of the dateline; we "bring it back" towards the West
    x[1] = x[1] + 360
  elif ( (x[0]-x[2])>180 and (x[1]-x[2])>180 ):
    # In this case, x2 is 'isolated' to the East of the dateline; we "bring it back" towards the West
    x[2] = x[2] + 360
  elif ( (x[0]-x[1])>180 and (x[0]-x[2])>180 ):
    # In this case, x0 is 'isolated' to the West of the dateline; we "bring it back" towards the East
    x[0] = x[0] - 360
  elif ( (x[1]-x[0])>180 and (x[1]-x[2])>180 ):
    # In this case, x1 is 'isolated' to the West of the dateline; we "bring it back" towards the East
    x[1] = x[1] - 360
  elif ( (x[2]-x[0])>180 and (x[2]-x[1])>180 ):
    # In this case, x2 is 'isolated' to the West of the dateline; we "bring it back" towards the East
    x[2] = x[2] - 360

  vertices = [vrtx for vrtx in zip(x, y)]
  return vertices


