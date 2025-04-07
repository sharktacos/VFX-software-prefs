
nuke.pluginAddPath("./denoice")
nuke.pluginAddPath('./rvnuke')
#nuke.knobDefault("RotoPaint.toolbox", "brush {{brush ltt 0} {clone ltt 0}}")  


import nuke
nuke.pluginAddPath('pixelfudger3')
nuke.knobDefault("Root.colorManagement", "OCIO")
#nuke.knobDefault("Root.floatLut", "reference")

# default color spaces for Writes for img and mov
nuke.knobDefault('Write.exr.colorspace', 'ACEScg')
nuke.knobDefault('Write.png.colorspace', 'ACES 1.0 SDR-video (Gamma 2.2 - Display)')
nuke.knobDefault('Write.jpeg.colorspace', 'ACES 1.0 SDR-video (Gamma 2.2 - Display)')
nuke.knobDefault('Write.mov.colorspace', 'ACES 1.0 SDR-video (Rec.709 - Display)')
nuke.knobDefault('Write.mxf.colorspace', 'ACES 1.0 SDR-video (Rec.709 - Display)')

# default mov to h.254 
#nuke.knobDefault('Write.mov.mov64_codec', '4')

# set MXF and MOV (Prores) to video range and proxy
nuke.knobDefault('Write.mov.mov_prores_codec_profile', '5')
nuke.knobDefault('Write.mxf.mxf_codec_profile_knob', '4')
nuke.knobDefault('Write.mov.dataRange', '1')
nuke.knobDefault('Write.mxf.dataRange', '1')




