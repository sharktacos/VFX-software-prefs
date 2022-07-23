# Substance 3D Painter to Maya (Arnold)

Tool to automatically connect Substance 3D Painter textures to Maya shaders. Based on [the original script by Tristan Le Granche](https://github.com/Strangenoise/SubstancePainterToMaya). This version has been updated for Python 3 (required for Maya 2022 and up). 

## Usage

Click the shelf button to launch the GUI. 

![img](img/sp2m_gui1.jpg)

The first field will default to the texture directory defined in your Maya project settings. If your textures are in a sub folder, you can navigate there. 

In the second field put one of the textureSets (i.e. the shader name) included in your texture's file name. When Substance exports textures it includes the name of the shader you assigned in Maya, calling this a "textureSet" in Substance Painter. The script will match up the shader name in your Maya file to this part of the filename on your texture. 

In the third field put one of the texture map types you have. Here the "dif" map is selected referring to a diffuse map (base color). 

Click  the "Launch" button and the script will search your textures for matches.

![img](img/sp2m_gui2.jpg)

Select the desired options, and click the "Proceed" button. If you have the (default) option "use all found texture sets" the script will assign the texture maps to all the shaders it finds. If you only want to assign textures to one shader use the "use only specified texture set" option.


## Limitations
 - Only the Arnold renderer is supported. I have not had a chance to test this out in Renderman or Vray. Maybe some day.
 - Color Correct mode has been disabled.

## Enhancements

### Specular Roughness mix network
 
As you can see below, in addition to color, bump, normal, and metalness texture maps, specular roughness maps are connected with a blend that allows artists to use the texture as a mask to define regions that are remaped to two roughness sliders (color1 and color2 shown in the Attribute Editor below). This provides artistic control, rather than having the roughness slider locked off with a texture map.

![img](img/sp2m_roughness.jpg)

Note that this workflow is also included in the roughness section of my "UberShader" Smartmaterial included in the [Substance tools](Substance.md). The technique is also shown here:

<div style="padding:56.25% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/326948120?h=da9e609785&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;" title="Substance Painter: A better way to export roughness maps for artistic control"></iframe></div><script src="https://player.vimeo.com/api/player.js"></script><br>


### Layer Shader network
 
If a layer map is found (naming: 'Layer', 'layer', 'lyr') the aiStandardSurface shader is duplicated with all of its input connections, and these two shaders are then connected to a layerShader. Finally the layer texture map is input into the layer mix. 
 
![img](img/sp2m_layer.jpg)
   


