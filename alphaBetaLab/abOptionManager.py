class abOptions:                                                                                                                                                                  
  def __init__(self, **kwargs):                                                                                                                                                       
    for k in kwargs.keys():
      setattr(self, k, kwargs[k])


_opts = {}
def printOpts():
  print('OPTIONS:')
  optNms = list(_opts.keys())
  optNms.sort()
  for opt in optNms:
    print(' ' + opt + ': ' + str(_opts[opt]))


def getOption(abOptObj, optName, defaultValue):
  try:
    val = getattr(abOptObj, optName)
  except:
    val = defaultValue
  _opts[optName] = val
  return val

