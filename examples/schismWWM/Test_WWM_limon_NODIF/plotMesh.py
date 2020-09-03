from alphaBetaLab import abTriangularMesh as trmsh
from matplotlib import pyplot as plt

msh = trmsh.loadFromGr3File('hgrid.gr3')
xs = [msh.nodes[k][0] for k in msh.nodes.keys()]
ys = [msh.nodes[k][1] for k in msh.nodes.keys()]

plt.triplot(xs, ys, linewidth=.1, color='k')

# obstructed node
obsNodeId = 329
xnd, ynd = msh.nodes[obsNodeId][:]
plt.plot(xnd, ynd, 'o', color='k')

# shadowed node 1
obsNodeId = 1344
xnd, ynd = msh.nodes[obsNodeId][:]
plt.plot(xnd, ynd, 'o', color='b')

# shadow node 2
obsNodeId = 1000
xnd, ynd = msh.nodes[obsNodeId][:]
plt.plot(xnd, ynd, 'o', color='g')

# shadow node 3
obsNodeId = 1414
xnd, ynd = msh.nodes[obsNodeId][:]
plt.plot(xnd, ynd, 'o', color='y')

plt.show()

