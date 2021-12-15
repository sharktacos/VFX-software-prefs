
nuke.pluginAddPath("./denoice")
nuke.pluginAddPath('./rvnuke')
#nuke.knobDefault("RotoPaint.toolbox", "brush {{brush ltt 0} {clone ltt 0}}")  


import nuke
nuke.knobDefault("Root.colorManagement", "OCIO")
nuke.knobDefault("Root.floatLut", "reference")
