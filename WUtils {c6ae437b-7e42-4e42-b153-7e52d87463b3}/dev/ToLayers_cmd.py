import rhinoscriptsyntax as rs

__commandname__ = "ToLayers"

# RunCommand is the called when the user enters the command name in Rhino.
# The command name is defined by the filname minus "_cmd.py"
def RunCommand( is_interactive ):
  geometry = rs.SelectedObjects()
  if len(geometry) == 0:
    geometry = rs.GetObjects()
  toLayer = rs.GetLayer()
  if geometry: 
    for item in geometry:
      layer = rs.ObjectLayer(item)
      path = layer.split('::')
      path[0] = toLayer
      layername = '::'.join(path)
      print('::'.join(path))
      if not rs.IsLayer(layername): 
        rs.AddLayer(layername)
      rs.ObjectLayer(item, layername)
  
  
  # you can optionally return a value from this function
  # to signify command result. Return values that make
  # sense are
  #   0 == success
  #   1 == cancel
  # If this function does not return a value, success is assumed
  return 0
