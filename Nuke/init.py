
nuke.pluginAddPath("./denoice")
nuke.pluginAddPath('./rvnuke')
#nuke.knobDefault("RotoPaint.toolbox", "brush {{brush ltt 0} {clone ltt 0}}")  


import nuke
nuke.knobDefault("Root.colorManagement", "OCIO")
#nuke.knobDefault("Root.floatLut", "reference")
#nuke.knobDefault('Write.mov.colorspace', 'ACES 1.0 SDR-video (Rec.709 - Display)')
nuke.knobDefault('Write.mov.mov_prores_codec_profile', '5')


