def generateTestPolymeshRandFile(x0, nx, dx, y0, ny, dy, zbottom):
  outfilepath = 'rand.dat'
  
  ofl = open(outfilepath, 'w')
  ofl.write('C boundary points\n')  

  x, y, ipt = x0, y0, 1

  for i1 in range(nx):
    ln = '   '.join([str(ipt), str(x), str(y), str(zbottom)]) + '\n'
    ofl.write(ln)
    x += dx
    ipt += 1

  for i1 in range(ny):
    ln = '   '.join([str(ipt), str(x), str(y), str(zbottom)]) + '\n'
    ofl.write(ln)
    y += dy
    ipt += 1

  for i1 in range(nx):
    ln = '   '.join([str(ipt), str(x), str(y), str(zbottom)]) + '\n'
    ofl.write(ln)
    x -= dx
    ipt += 1

  for i1 in range(ny):
    ln = '   '.join([str(ipt), str(x), str(y), str(zbottom)]) + '\n'
    ofl.write(ln)
    y -= dy
    ipt += 1

  ofl.write('-1')
  ofl.close()
  
  
def generateTestPolymeshXYZFile(x0, nx, dx, y0, ny, dy, zbottom):
  outfilepath = 'xyz.dat'
  
  ofl = open(outfilepath, 'w')
  ofl.write(str(nx*ny) + '\n')
  
  for ix in range(nx):
    for iy in range(ny):
      x = x0 + ix*dx
      y = y0 + iy*dy
      ln = '   '.join([str(x), str(y), str(zbottom)]) + '\n'
      ofl.write(ln)

  ofl.close()

