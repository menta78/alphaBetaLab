from shapely import geometry as g


class _abFeMeshSpec:

  def __init__(self):
    """
    _abFeMeshSpec: class representing the logical structure of a finite elemets mesh
    """
    # node index -> node coordinates
    self.nodes = {}
    # node index -> node depth
    self.nodeBathy = {}
    # polygon index -> vertice nodes indices
    self.connectionPolygons = {}
    # node indes -> land boundary id
    self.landBoundaryNodes = {}
    # node indes -> open boundary id
    self.openBoundaryNodes = {}

  def getCellPolygons(self, excludeLandBoundary=True):
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
      centroid = cpl.centroid.coords[:][0]
      for nid in vrtxsNodes:
        if excludeLandBoundary and (nid in self.landBoundaryNodes):
          continue
        nodeCentroids = centroidsByNode.get(nid, [])
        nodeCentroids.append(centroid)
        centroidsByNode[nid] = nodeCentroids
    
    cellPlys = []
    nodeIds = centroidsByNode.keys()
    nodeIds.sort()
    for nid in nodeIds:
      vrtxs = g.LineString(nodeCentroids[nid])
      approxCell = vrtxs.convex_hull
      cellPlys.append(approxCell)
    return nodeIds, cellPlys
 


def loadFromGr3File(gr3FilePath):
  """
  loadFromGr3File: loads an instance of _abFeMeshSpec from a gr3 file 
  (format used, for example in model schism).
  """
  m = _abFeMeshSpec()
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
    for ind in range(nNodes):
      line = fl.readline().strip('\n\t\r ')
      nodeId = int(line)
      m.landBoundaryNodes[nodeId] = ibnd + 1

  return m


