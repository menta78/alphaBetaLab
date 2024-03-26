from __future__ import annotations
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
    # boundary index -> node index
    self.landBoundaries = {}
    # boundary index -> boundary type: 0=main boundary, 1=island
    self.landBoundaryType = {}
    # node index -> land boundary id
    self.landBoundaryNodes = {}
    # node index in the order they are loaded from the file
    self.landBoundaryOrdered = []
    # open boundary id -> node index
    self.openBoundaries = {}
    # node index -> open boundary id
    self.openBoundaryNodes = {}

  def getCellPolygons(self, excludeLandBoundary=True, excludeOpenBoundary=False):
    """
    getCellPolygons: returns an approximate cental median cell for each non-land-boundary node
    """
    print('        building the triangular mesh polygons (may take a while ...)')
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
      if (nid in self.landBoundaryNodes) and excludeLandBoundary:
        continue
      if (nid in self.openBoundaryNodes) and excludeOpenBoundary:
        continue
      ccc.append(self.nodes[nid])
      ccc = adjustCrossDatelineVertices(ccc)
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
        bndTyp = self.landBoundaryType[bndId]
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
      bndTyp = self.landBoundaryType[bndId]
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

  def saveAsGr3(self, filePath, bathyFactor=-1):
    m = self
    fl = open(filePath, 'w')
    fl.write('\n')
    nodeCount = len(m.nodes.keys())
    connPlysCount = len(m.connectionPolygons.keys())
    ln = str(connPlysCount) + '   ' + str(nodeCount) + '\n'
    fl.write(ln)
    
    # saving the nodes
    for inode in range(nodeCount):
      nodeId = inode + 1
      lon, lat = m.nodes[nodeId]
      dpth = m.nodeBathy[nodeId]
      ln = '  '.join([str(nodeId), str(lon), str(lat), str(dpth*bathyFactor)]) + '\n'
      fl.write(ln)

    # saving the connection polygons
    connPlysCount = len(m.connectionPolygons.keys())
    for ipl in range(connPlysCount):
      connPolyId = ipl + 1
      nodeIds = m.connectionPolygons[connPolyId]
      nsides = len(nodeIds)
      ln = str(connPolyId) + '  ' + str(nsides) + '  ' + '  '.join([str(n) for n in nodeIds]) + '\n'
      fl.write(ln)

    # saving the open boundaries
    nOpenBoundary = len(self.openBoundaries.keys())
    if nOpenBoundary == 0:
      print('WARINING: no open boundary found. Beware, if this mesh was loaded from a msh, the open boundary was not loaded')
    ln = str(nOpenBoundary) + ' Number of open boundaries\n'
    fl.write(ln)
    nbndnodes = int(np.sum([len(itm[1]) for itm in m.openBoundaries.items()]))
    ln = str(nbndnodes) + ' Total number of open boundary nodes\n'
    fl.write(ln)
    for ibnd in range(nOpenBoundary):
      bndId = ibnd + 1
      obnds = m.openBoundaries[bndId]
      ln = str(len(obnds)) + ' Number of nodes for open boundary ' + str(bndId) + '\n'
      fl.write(ln)
      for nodeId in obnds:
        ln = str(nodeId) + '\n'
        fl.write(ln)

    # saving the land boundaries
    nLandBoundary = len(self.landBoundaries.keys())
    ln = str(nLandBoundary) + ' Number of land boundaries\n'
    fl.write(ln)
    nbndnodes = int(np.sum([len(itm[1]) for itm in m.landBoundaries.items()]))
    ln = str(nbndnodes) + ' Total number of land boundary nodes\n'
    fl.write(ln)
    for ibnd in range(nLandBoundary):
      bndId = ibnd + 1
      obnds = m.landBoundaries[bndId]
      bndTyp = m.landBoundaryType[bndId]
      ln = str(len(obnds)) + ' ' + str(bndTyp) + ' Number of nodes for open boundary ' + str(bndId) + '\n'
      fl.write(ln)
      for nodeId in obnds:
        ln = str(nodeId) + '\n'
        fl.write(ln)

    fl.close()

  def getNodesDataframe(self):
    import pandas as pd
    dfcrds = pd.DataFrame.from_dict(self.nodes, orient='index', columns=['x', 'y'])
    dfbathy = pd.DataFrame.from_dict(self.nodeBathy, orient='index', columns=['bathy'])
    return dfcrds.join(dfbathy)

  def clipToPolygon(self, xsPolygon, ysPolygon) -> _abTriMeshSpec:
    """
    Reduces a mesh to the nodes/elements contained in a polygon.
    All the information on land and open boundary are lost in the process.
    """
    import copy
    out = copy.deepcopy(self)
    # the output mesh has no land or open boundary set
    out.landBoundaries = {}
    out.landBoundaryType = {}
    out.landBoundaryNodes = {}
    out.landBoundaryOrdered = []
    out.openBoundaries = {}
    out.openBoundaryNodes = {}

    # mapping the connection polygons by node
    def mapPolygonsByNode():
      plyByNode = {}
      for plyId in out.connectionPolygons:
        ply = out.connectionPolygons[plyId]
        for nodeId in ply:
          plys = plyByNode.get(nodeId, [])
          plyByNode[nodeId] = plys
          plys.append(plyId)
      return plyByNode
    plyByNode = mapPolygonsByNode()

    # creating the polygon
    polygon = g.Polygon([p for p in zip(xsPolygon, ysPolygon)])

    # removing everything that is outside of the polygon
    for nodeId in self.nodes:
      crds = self.nodes[nodeId]
      if not polygon.contains(g.Point(crds[0], crds[1])):
        # removing the node
        del out.nodes[nodeId]
        # removing the bathymetry
        del out.nodeBathy[nodeId]
        # removing all the connection polygons containing the node
        plys = plyByNode[nodeId]
        for plyId in plys:
          out.connectionPolygons.pop(plyId, None)

    # remapping the node ids
    plyByNode = mapPolygonsByNode()
    newNodeIds = range(1, len(out.nodes)+1)
    oldNodeIds = [k for k in out.nodes.keys()]
    oldNodeIds.sort()
    newNodes = {}
    newNodeBathy = {}
    for nodeIdOld, nodeIdNew in zip(oldNodeIds, newNodeIds):
      # coordinates of the new node
      newNodes[nodeIdNew] = out.nodes[nodeIdOld]
      # bathy of the new node
      newNodeBathy[nodeIdNew] = out.nodeBathy[nodeIdOld]
      # propagating the new id the polygons
      plyIds = plyByNode[nodeIdOld]
      for plyId in plyIds:
        ply = out.connectionPolygons[plyId]
        newPly = []
        for nid in ply:
          nidnew = nodeIdNew if nid == nodeIdOld else nid
          newPly.append(nidnew)
        out.connectionPolygons[plyId] = newPly
    out.nodes = newNodes
    out.nodeBathy = newNodeBathy

    # remapping the connection polygon ids
    newPlyIds = range(1, len(out.connectionPolygons)+1)
    oldPlyIds = [k for k in out.connectionPolygons.keys()]
    oldPlyIds.sort()
    newConnectionPolygons = {}
    for plyIdOld, plyIdNew in zip(oldPlyIds, newPlyIds):
      newConnectionPolygons[plyIdNew] = out.connectionPolygons[plyIdOld]
    out.connectionPolygons = newConnectionPolygons

    return out










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
    bndId = ibnd + 1
    obnds = m.openBoundaries[bndId] if bndId in m.openBoundaries else []
    m.openBoundaries[bndId] = obnds
    for ind in range(nNodes):
      line = fl.readline().strip('\n\t\r ')
      nodeId = int(line)
      m.openBoundaryNodes[nodeId] = bndId
      obnds.append(nodeId)
    
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

    bndId = ibnd + 1
    lbnds = m.landBoundaries[bndId] if bndId in m.landBoundaries else []
    m.landBoundaries[bndId] = lbnds
    m.landBoundaryType[bndId] = bndTyp
    for ind in range(nNodes):
      line = fl.readline().strip('\n\t\r ')
      nodeId = int(line)
      m.landBoundaryNodes[nodeId] = bndId
      m.landBoundaryOrdered.append(nodeId)
      lbnds.append(nodeId)

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
      m.landBoundaryType[ibnd] = bndType
      m.landBoundaryOrdered.append(nodeId)
    elif elmtyp == 2: # 2: triangle 
      nodeIds = [int(s) for s in vlsstr[6:]]
      connPolyId = int(vlsstr[4])
      m.connectionPolygons[connPolyId] = nodeIds
  
  #AFAIK the open boundary is not included in the file

  fl.close()
  return m


def adjustCrossDatelineVertices(vertices):
  xs = np.array([v[0] for v in vertices])
  ys = np.array([v[1] for v in vertices])

  dff = np.abs(xs - xs[0])
  ratioCloseToFirstPt = np.sum(dff <= 180)/len(xs)
  if np.abs(ratioCloseToFirstPt - 1) < .0000001:
    # the polygon does not cross the dateline.
    return vertices
  if ratioCloseToFirstPt > .5:
    x0 = xs[0]
  else:
    ii = np.where(dff >= 180)[0][0]
    x0 = xs[ii]
  for ix in range(len(xs)):
    x = xs[ix]
    if x - x0 > 180:
      x = x - 360
    elif x - x0 < -180:
      x = x + 360
    xs[ix] = x

  vertices = [vrtx for vrtx in zip(xs, ys)]
  return vertices


