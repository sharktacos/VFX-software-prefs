#import os
# SET UP EXAMPLE ENVIRONMENT
#os.environ['OCIO'] = '/Users/Derek/Documents/GitHub/OpenColorIO-configs/StdX_ACES-ANM/ANM_config.ocio'

  # Add EXR shuffle to read node in User tab: import shuffleLayers
from shuffleLayers import newNode
from shuffleLayers import mylayerPanel


toolbar = nuke.toolbar("Nodes")

toolbar.addCommand( "Studio/Optical Glow", "nuke.createNode('bm_OpticalGlow2')")
toolbar.addCommand( "Studio/Optical Lightwrap", "nuke.createNode('bm_OpticalLightwrap')")
#toolbar.addCommand( "Studio/Night Shift", "nuke.createNode('df_nightShift2')")
toolbar.addCommand( "Studio/mm Color Target", "nuke.createNode('mmColorTarget')")
#toolbar.addCommand( "Gizmos/OpticalZDefocus", "nuke.createNode('OpticalZDefocus')")
toolbar.addCommand( "Studio/bokeh blur", "nuke.createNode('BokehBlur.gizmo')")
toolbar.addCommand( "Studio/FlareFactory", "nuke.createNode('FlareFactory')")
toolbar.addCommand( "Studio/ACES Ref Gamut Compress", "nuke.createNode('ACES_ref_gamut_compress')")

#toolbar.addCommand( "Studio/Burn-In", "nuke.createNode('df_burn_in')")
#toolbar.addCommand( "Studio/Naming Variables", "nuke.createNode('df_nameVars')")
#toolbar.addCommand( "Studio/Read Footage", "nuke.createNode('df_ReadFootage')", 'shift+r' )
toolbar.addCommand( "Studio/Write Dailies", "nuke.createNode('df_WriteDailiesMov')", 'shift+w' )




# ROOT
nuke.knobDefault('Root.project_directory', '[python {nuke.script_directory()}]')
nuke.knobDefault('Root.format', 'HD_1080')

  # Shuffle custom defaults: 
nuke.knobDefault("Shuffle.hide_input", "1")  
nuke.knobDefault("Shuffle.postage_stamp", "1")
nuke.knobDefault("Shuffle.label", "[value in1]") 

# exposure custom defaults
nuke.knobDefault("Exposure.mode", "0") 

  # Cryptomatte custom defaults: 
nuke.knobDefault("Cryptomatte.hide_input", "1")  
#nuke.knobDefault("Cryptomatte.label", "[value matteList]") 

# Write > Default for EXR files: DWAB
nuke.knobDefault("Write.exr.compression","8")  
nuke.knobDefault('Write.create_directories','1')
 


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

