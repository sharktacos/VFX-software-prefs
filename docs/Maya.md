<h2>Project template</h2>
Zip file containing Maya project folders for an animation studio pipeline.
<h2>Turntable Setup</h2>
Maya files for look development turntable setup.
<h2>scripts</h2>
Python and Mel scripts. Place these in your Maya scripts folder. Python scripts updated for Python3 used by Maya 2022.

<h2>Maya shelf</h2>
A Maya shelf containing the above scripts and some other goodies. This goes in your Maya prefs folder. 

| OS | Location
|----|----
| Windows: | %USERPROFILE%\Documents\maya\2022\prefs\
| Mac OS X: |  /Users/[username]/Library/Preferences/Autodesk/maya/2022/prefs/

There are two shelves: 
*shelf_DF_docs.mel* points to the above Windows location for custom icons.
*shelf_DF_zdrive.mel* points to the Windows location on the network drive of our school computers.
If your prefs directory is in a different location you can edit the file to point to that location.

![img](img/maya_shelf.jpg)

Shelf items shown above are oranized into three sections:
 - **Lights**
   - *custom point light*<br>
     This creates a point light with a templated sphere showing the size (radius) of the light.
   - *custom area light (Arnold)*
   - *custom directional light*
   - *custom dome light (Arnold)*
 - **scripts**
   - *Material Transfer GUI*<br>
     Used to transfer shader assignments from a lookdev asset to its corresponding Alembic cache. [Watch a video](https://vimeo.com/252241167) showing the use of this GUI. 
   - *UV Transfer GUI*
   - *Create Light Group AOVs* 
   - *Remove Light Group AOVs* 
   - *Renderman MakeTX GUI*
     GUI for MakeTx to convert textures to mipmap TX files with an OCIO config in Renderman. See the [doc page](https://docs.sharktacos.com/texture/mipmap.html) for usage.
 - **Arnold**
   - *Arnold Render View*
   - *Custom Layout (node editor & persp view)*
   - *Create Texture File Node*
   - *Create Arnold Standard Shader*
   
   
