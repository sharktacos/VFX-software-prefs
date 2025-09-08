nuke.pluginAddPath("./denoice")
nuke.pluginAddPath('./rvnuke')
#nuke.knobDefault("RotoPaint.toolbox", "brush {{brush ltt 0} {clone ltt 0}}")  


import nuke
nuke.pluginAddPath('pixelfudger3')
nuke.knobDefault("Root.colorManagement", "OCIO")
#nuke.knobDefault("Root.floatLut", "reference")

# default color spaces for Writes for 8-bit images and movies
# ------------------
nuke.knobDefault('Write.exr.colorspace', 'ACEScg')

#nuke.knobDefault('Write.png.colorspace', 'ACES 1.0 (sRGB Display)')
nuke.knobDefault('Write.png.transformType', 'display')
nuke.knobDefault('Write.png.ocioDisplay', 'sRGB Display')
nuke.knobDefault('Write.png.ocioView', 'VFX - ACES 1.0')

#nuke.knobDefault('Write.jpeg.colorspace', 'ACES 1.0 (sRGB Display)')
nuke.knobDefault('Write.jpeg.transformType', 'display')
nuke.knobDefault('Write.jpeg.ocioDisplay', 'sRGB Display')
nuke.knobDefault('Write.jpeg.ocioView', 'VFX - ACES 1.0')

#nuke.knobDefault('Write.mov.colorspace', 'ACES 1.0 SDR-video (Rec.709 - Display)')
nuke.knobDefault('Write.mov.transformType', 'display')
nuke.knobDefault('Write.mov.ocioDisplay', 'Rec.709 Display')
nuke.knobDefault('Write.mov.ocioView', 'VFX - ACES 1.0')

#nuke.knobDefault('Write.mxf.colorspace', 'ACES 1.0 SDR-video (Rec.709 - Display)') 
nuke.knobDefault('Write.mxf.transformType', 'display')
nuke.knobDefault('Write.mxf.ocioDisplay', 'Rec.709 Display')
nuke.knobDefault('Write.mxf.ocioView', 'VFX - ACES 1.0')

# -----------------------


# default mov to h.254 
#nuke.knobDefault('Write.mov.mov64_codec', '4')

# set MXF and MOV (Prores) to video range and proxy
nuke.knobDefault('Write.mov.mov_prores_codec_profile', '5')
nuke.knobDefault('Write.mxf.mxf_codec_profile_knob', '4')
nuke.knobDefault('Write.mov.dataRange', '1')
nuke.knobDefault('Write.mxf.dataRange', '1')












