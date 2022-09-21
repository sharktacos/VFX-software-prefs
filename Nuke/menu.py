  
  # Add EXR shuffle to read node in User tab: import shuffleLayers
from shuffleLayers import newNode
from shuffleLayers import mylayerPanel


toolbar = nuke.toolbar("Nodes")


toolbar.addCommand( "Studio/bm_OpticalGlow", "nuke.createNode('bm_OpticalGlow')")
toolbar.addCommand( "Studio/bm_OpticalLightwrap", "nuke.createNode('bm_OpticalLightwrap')")
toolbar.addCommand( "Studio/mmColorTarget", "nuke.createNode('mmColorTarget')")
#toolbar.addCommand( "Gizmos/OpticalZDefocus", "nuke.createNode('OpticalZDefocus')")
#toolbar.addCommand( "Gizmos/bokeh_blur", "nuke.createNode('bokeh_blur')")
toolbar.addCommand( "Studio/ACES Ref Gamut Compress", "nuke.createNode('ACES_ref_gamut_compress')")
toolbar.addCommand( "Studio/Write Dailies Movie", "nuke.createNode('WriteDailiesMov')")


# obsolete
'''
#toolbar.addCommand( "Gizmos/bokeh_blur_jb_v03_1", "nuke.createNode('bokeh_blur_jb_v03_1')")
#toolbar.addCommand( "Gizmos/CalibrateMacbeth", "nuke.createNode('CalibrateMacbeth')")
#toolbar.addCommand( "Gizmos/Offset", "nuke.createNode('Offset')")
#toolbar.addCommand( "Gizmos/exr_extract", "nuke.createNode('exr_extract')")

def writeDir():
 import os
 file = nuke.filename(nuke.thisNode())
 dir = os.path.dirname(file)
 osdir = nuke.callbacks.filenameFilter(dir)
 try:
  os.makedirs(osdir)
 except OSError:
  pass

  # OCIO Shot Look custom defaults: 

def _setOCIODisplayContext():
    node = nuke.thisNode()
    node.knob('key1').setValue("SHOW")
    node.knob('key2').setValue("SHOT")
    node.knob('key3').setValue("VER")
    node.knob('key4').setValue("SHAPER")
    
    node.knob('value1').setValue("DSOM")
    node.knob('value2').setValue("022") 
    node.knob('value3').setValue("v02")
    node.knob('value4').setValue("ACEScct")
    
nuke.addOnCreate(_setOCIODisplayContext, nodeClass="OCIODisplay")
'''


  # Shuffle custom defaults: 
nuke.knobDefault("Shuffle.hide_input", "1")  
nuke.knobDefault("Shuffle.postage_stamp", "1")
#nuke.knobDefault("Shuffle.label", "[value in]") 

  # Cryptomatte custom defaults: 
nuke.knobDefault("Cryptomatte.hide_input", "1")  
#nuke.knobDefault("Cryptomatte.label", "[value matteList]") 

# Write > Default for EXR files: DWAB
nuke.knobDefault("Write.exr.compression","8")  
#nuke.knobDefault('Write.beforeRender','writeDir()')

  # OCIO Color Space custom defaults: 
nuke.knobDefault("OCIOColorSpace.label", "[value in_colorspace]\n[value out_colorspace]") 

#-------------------- Custom Merge Function -------------------------------#
'''More info on callbacks here:
 http://docs.thefoundry.co.uk/nuke/90/pythondevguide/callbacks.html'''

def MergeNodeAfterKnobChange():
  if nuke.thisKnob().name() == "operation":
    outputRGB = [ "plus", "minus", "screen", "multiply", "divide", "difference", "hypot" ]
    outputRGBA = [ "over", "under" , "disjoint-over" , "conjoint-over", "in", "out", "overlay", "stencil", "mask", "matte", "copy" ]
    if nuke.thisKnob().value() in outputRGB:
        nuke.thisNode()[ "output" ].setValue( "rgb" ) 
    elif nuke.thisKnob().value() in outputRGBA:
        nuke.thisNode()[ "output" ].setValue( "rgba" )

nuke.addKnobChanged( MergeNodeAfterKnobChange, nodeClass="Merge2" )
