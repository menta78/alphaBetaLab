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
    # node index -> open boundary id
    self.openBoundaryNodes = {}

  def getCellPolygons(self, excludeLandBoundary=True, excludeOpenBoundary=False):
    """
    getCellPolygons: returns an approximate cental median cell for each non-land-boundary node
    """
    plIds = self.connectionPolygons.keys()
    plIds.sort()
    centroidsByNode = {}
    for plId in plIds:
      vrtxsNodes = self.connectionPolygons[plId]
      vrtxs = [self.nodes[nid] for nid in vrtxsNodes]
      connPoly = g.Polygon(vrtxs)
      centroid = connPoly.centroid.coords[:][0]
      for nid in vrtxsNodes:
        nodeCentroids = centroidsByNode.get(nid, [])
        nodeCentroids.append(centroid)
        centroidsByNode[nid] = nodeCentroids
    
    cellPlys = []
    nodeIds = []
    nodeIds0 = centroidsByNode.keys()
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
    connPolyId = int(vlsstr[0])

    if len(vlsstr) == 6:
      # is a boundary node. Loading it as land boundary
      ibnd = connPolyId
      nodeId = int(vlsstr[-1])
      m.landBoundaryNodes[nodeId] = ibnd
    else:  
      nodeIds = [int(s) for s in vlsstr[6:]]
      
      m.connectionPolygons[connPolyId] = nodeIds

  return m



