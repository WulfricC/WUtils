
from rhss_parser_2_7 import Lark_StandAlone, Indenter, Transformer, Tree
import re
import os
from rhss_aliases import aliases
from scriptcontext import doc
import Rhino
import math
import rhinoscriptsyntax as rs
from rhss_helpers import Col 

__commandname__ = "Rhss"

# RunCommand is the called when the user enters the command name in Rhino.
# The command name is defined by the filname minus "_cmd.py"
def RunCommand( is_interactive ):
  
  ### Get file path
  filePath = rs.GetDocumentUserText("rhss.filePath")
  documentDir = rs.DocumentPath()
  if filePath is None and documentDir != None and documentDir != "":
      filePath = documentDir + "style.rhss"
  elif filePath is None:
      filePath = "Open"
  filePath = rs.GetString(
      message = "Layer Settings",
      defaultString = filePath
      )
  if filePath in ["O","o","open","Open"]:
      filePath = rs.OpenFileName(
          title = "Open Layer Settings File",
          filter = "RHSS file (*.rhss)|*.rhss"
          )
  
  # End script in cases where the filepath is invalid
  if filePath == None:
      print('No RHSS file specified.')
      return Rhino.Commands.Result.Cancel

  if not os.path.exists(filePath):
      print('RHSS file not found.')
      return Rhino.Commands.Result.Cancel

  # Load the RHSS file
  layerDataString = ""
  with open(filePath, 'r') as f:
      layerDataString = f.read()
  
  # if we make it this far, save the file path in user text
  rs.SetDocumentUserText("rhss.filePath", filePath)
  
  
  # Parse the RHSS file
  class TreeIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 8

  class Definition:
      def __init__(self, selector, properties):
          self.selector = selector
          self.properties = properties

  class RuleBuilder(Transformer):
      def __init__ (self):
        self.ind = 0
      def number_capture(self, args):
          name = args[0].children[0]
          return r"(?P<" + name + r">[-+]?[0-9]+\.?[0-9]*)"
      def anything(self, args):
          return r"[^:]*?"
      def name_match(self, args):
          return args[0]
      def layer_match(self, args):
          return "".join(args)
      def option(self,args):
          return "(" + "|".join(args) + ")"
      def child(self,args):
          return "(" + "::".join(reversed(args)) + ")"
      def inside(self,args):
          return "(" + "::(.+::)?".join(reversed(args)) + ")"
      def selector(self, args):
          regexpr = "^" + args[0] + "(::|$)"
          try:
              return re.compile(regexpr)
          except re.error:
              raise SyntaxError("invalid rhss selector")
      def property_list(self, args):
          dictionary = {}
          for prop in args:
              dictionary[str(prop.children[0])] = str(prop.children[1])
          return dictionary
      def definition(self, args):
          return Definition(args[0], args[1])
      def stylesheet(self, args):
          return list(args)
      def rooted(self, args):
          if isinstance(args[0], Tree):  
            return "^" + args[1] + "($)"
          else:
            return args[0]
      def number_capture(self, args):
          name = 'float' + str(self.ind) + '_' + args[0]
          self.ind += 1
          return r'(?P<' + name + r'>\d*.?\d+)'

  parser = Lark_StandAlone(postlex=TreeIndenter(), transformer=RuleBuilder())
  print("Z ordering is currently Disabled")
  print("Parsing Style Sheet")
  try:
    definitions = parser.parse(layerDataString)
  except Exception as err:
    print('Malformed RHSS file (or parser).')
    print(err)
    return 0
    
  # fetch all the layers from the file
  layerPaths = rs.LayerNames()

  layerApplications = {}
  print("Compiling Style Sheet")
  # if default layer does not exist exit and print error
  if rs.LayerId('Default') == None:
      print('A layer called "Default" is required for RHSS')
      return 0
  # do cascade
  for definition in definitions:
      for layerPath in layerPaths:
          reversedLayerPath = '::'.join(reversed(layerPath.split('::')))
          match = definition.selector.match(reversedLayerPath)
          if match != None:
            nameCaptures = match.groupdict()
            if layerPath not in layerApplications:
              layerApplications[layerPath] = {}
            if 'vars' not in layerApplications[layerPath]:
              layerApplications[layerPath]['vars'] = {}
            
            # extract all numbers
            for key in nameCaptures.keys():
              match = re.match(r"^float\d+_(?P<name>[\w_]+)",key)
              if match:
                layerApplications[layerPath]['vars'][match.group('name')] = float(nameCaptures[key])

            for property in definition.properties:
              prop = property
              if property in aliases:
                prop = aliases[property]
              layerApplications[layerPath][prop] = definition.properties[property]

  # merge dict function
  def merge(x, y):
    z = x.copy()   # start with keys and values of x
    z.update(y)    # modifies z with keys and values of y
    return z

  def dict_from_module(module):
    context = {}
    for setting in dir(module):
      # you can write your filter here
      if setting.islower() and setting.isalpha():
        context[setting] = getattr(module, setting)
    return context
  
  # domain definition
  def dom(a,b,c,d,val):
    return((val-a)/(b-a))*(d-c)+c
  
  # set main helper functions
  helperFuncs = merge(dict_from_module(math), {"dom":dom})
    
  # linetype functions
  def linetype(*pattern):
      name = 'L{' + ','.join(map(lambda x: str(x), pattern)) + '}'
      patternFloat = map(lambda x: float(x), pattern)
      if doc.Linetypes.Find(name) == -1:
        doc.Linetypes.Add(name,patternFloat)
      return name
  
  # colour functions
  bgCol = Rhino.ApplicationSettings.AppearanceSettings.ViewportBackgroundColor
  print(bgCol.G)
  colFuncs = merge({
    "hsv":Col.fromHSV,
    "xyz":Col.fromXYZ,
    "rgb":Col.fromRGB,
    "grey":Col.greyscale,
    "gray":Col.greyscale,
    "lerp":Col.lerp,

    "White":Col.fromRGB(255,255,255,255),
    "LightGray":Col.fromRGB(230,230,230,255),
    "Gray":Col.fromRGB(190,190,190,255),
    "DarkGray":Col.fromRGB(105,105,105,255),
    "Black":Col.fromRGB(0,0,0,255),
    "Red":Col.fromRGB(255,0,0,255),
    "Brown":Col.fromRGB(191,63,63,255),
    "Orange":Col.fromRGB(255,127,0,255),
    "Gold":Col.fromRGB(255,191,0,255),
    "Yellow":Col.fromRGB(255,255,0,255),
    "Chartreuse":Col.fromRGB(127,255,0,255),
    "Green":Col.fromRGB(0,255,0,255),
    "DarkGreen":Col.fromRGB(0,127,0,255),
    "SeaGreen":Col.fromRGB(63,191,127,255),
    "Aquamarine":Col.fromRGB(127,255,191,255),
    "Cyan":Col.fromRGB(0,255,255,255),
    "Turquoise":Col.fromRGB(63,191,191,255),
    "Lavender":Col.fromRGB(191,191,255,255),
    "Blue":Col.fromRGB(0,0,255,255),
    "DarkBlue":Col.fromRGB(0,0,191,255),
    "Purple":Col.fromRGB(191,63,255,255),
    "Magneta":Col.fromRGB(255,0,255,255),
    "Violet":Col.fromRGB(255,127,255,255),
    "Pink":Col.fromRGB(255,191,191,255),

    "Paper":Col.fromRGB(255,255,255,255),
    "Background":Col.fromRGB(bgCol.R,bgCol.G,bgCol.B,bgCol.A)
    
  }, helperFuncs)

  weightFuncs = merge({
    "NoPrint": -1,
    "Default": 0,
    "Hairline": 0.0001
  }, helperFuncs)
  
  ltFuncs = merge({
    "lt": linetype,
  }, helperFuncs)


  # cached z positions
  zCache = {}
  defaultLayer = 'Default'
  print("Applying Styles")
  # apply properties in order of layer depth to allow parentage to work correctly
  for layer in sorted(layerApplications, key=lambda e: len(e.split('::'))):
    try:
        parent = rs.ParentLayer(layer)
        if parent == None:
            parent = defaultLayer
        if re.search(r"[^:>]+>[^:>]+$", parent):
            parent = rs.ParentLayer(parent)
        if parent == None:
            parent = defaultLayer
        for property in layerApplications[layer]:
            pythonCmd = layerApplications[layer][property]
            vars = layerApplications[layer]['vars']
            #print(vars)
            nameHash = hash(layer)
            name255 = nameHash%255
            name1 = (nameHash%255) / float(255)
            hashes = {'Hash': nameHash, 'H': nameHash, 'H1': name1, 'H255':name255}
            if property == 'LayerColor':
                parentV = Col.fromLC(rs.LayerColor(parent))
                selfV = Col.fromLC(rs.LayerColor(layer))
                locals = {'P': parentV, 'Parent': parentV,'S': selfV, 'Self': selfV}
                locals.update(vars)
                locals.update(hashes)
                try:
                    r = eval(pythonCmd, colFuncs, locals)
                    rs.LayerColor(layer,r.toLC())
                except:
                    pass
            elif property == 'LineType':
                parentV = rs.LayerLinetype(parent)
                selfV = rs.LayerLinetype(layer)
                locals = {'P': parentV, 'Parent': parentV,'S': selfV, 'Self': selfV}
                locals.update(vars)
                locals.update(hashes)
                try:
                    r = eval(pythonCmd, ltFuncs, locals)
                    if type(r) is tuple:
                        r = linetype(*r)
                    rs.LayerLinetype(layer,r)
                except:
                    pass
            elif property == 'Visible':
                parentV = rs.LayerVisible(parent)
                selfV = rs.LayerVisible(layer)
                locals = {'P': parentV, 'Parent': parentV,'S': selfV, 'Self': selfV}
                locals.update(vars)
                locals.update(hashes)
                try:
                    r = eval(pythonCmd, helperFuncs, locals)
                    rs.LayerVisible(layer, r)
                except:
                    pass
            elif property == 'PrintWidth':
                parentV =  rs.LayerPrintWidth(parent)
                selfV = rs.LayerPrintWidth(layer)
                locals = {'P': parentV, 'Parent': parentV,'S': selfV, 'Self': selfV}
                locals.update(vars)
                locals.update(hashes)
                try:
                    r = eval(pythonCmd, weightFuncs, locals)
                    rs.LayerPrintWidth(layer,r)
                except:
                    pass
            elif property == 'PrintColor':
                parentV = Col.fromLC(rs.LayerPrintColor(parent))
                selfV =  Col.fromLC(rs.LayerPrintColor(layer))
                locals = {'P': parentV, 'Parent': parentV,'S': selfV, 'Self': selfV}
                locals.update(vars)
                locals.update(hashes)
                try:
                    r = eval(pythonCmd, colFuncs, locals)
                    rs.LayerPrintColor(layer, r.toLC())
                except:
                    pass
            elif property == 'ZOrder':
                pass
                #zOrder = zCache[parent] if parent in zCache else 0
                #locals = {'P': zOrder, 'Parent': zOrder,'S': 0, 'Self': 0}
                #locals.update(vars)
                #locals.update(hashes)
                #z = eval(pythonCmd, helperFuncs, locals)
                #zCache[layer] = z
                #objs = rs.ObjectsByLayer(layer)
                #if objs: 
                #    for obj in objs:
                #        object = rs.coercerhinoobject(obj)
                #        object.Attributes.DisplayOrder = z
                #        object.CommitChanges()
    except TypeError as err:
        print('Error in formating layer: ', layer, ' parent:', parent)
        print(err)
        return 0

  # apply attributes in parentage order
  print('Successfully applied stylesheet.')
#RunCommand(0)