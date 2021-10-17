
nuke.pluginAddPath("./denoice")
nuke.pluginAddPath('./rvnuke')
nuke.knobDefault("RotoPaint.toolbox", "brush {{brush ltt 0} {clone ltt 0}}")  

#OLD:
import cryptomatte_utilities
cryptomatte_utilities.setup_cryptomatte()

nuke.pluginAddPath('./Crypto/Cryptomatte-1.2.0/nuke/')
nuke.pluginAddPath("./NukeSurvivalToolkit")

import nuke
nuke.knobDefault("Root.colorManagement", "OCIO")
nuke.knobDefault("Root.floatLut", "reference")
