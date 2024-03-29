# Nuke
## Installation
Place contents in the .nuke folder of your $HOME directory (if at the school lab that's your Z drive). 

**Windows**

You can find the $HOME folder by typing %HOME% or %USERPROFILE% in an Explorer Browser.

**MacOS**

In the finder menu select **go>home**. This folder is hidden by default. To show it Press CMD+Shift+Period in the Finder.

# Tools/Gizmos

- **Shuffle EXR** <br> [Created by Nacho Igea](http://www.nukepedia.com/python/import/export/shufflelayers). The older EXR shuffle was incompatible with Nuke 13. The new one has options to extract all AOVs or select the AOVs to extract. <br>Located in the ```User``` tab of a ```Read``` node.

![img](img/nuke_shuffle.jpg)

- **bm Optical Glow** <br> [Created by Ben McEwan](https://github.com/BenMcEwan/nuke_public). Adds exponentially-increasing blurs together to produce a more optically-correct, natural glow. <br>Located in the ```Studio``` menu.

- **bm Optical Light Wrap** <br> [Created by Ben McEwan](https://github.com/BenMcEwan/nuke_public). Adds exponentially-increasing blurs together to produce a more optically-correct, natural light wrap. <br>Located in the ```Studio``` menu.

- **Optical Z Defocus** <br> [Created by Jed Smith](https://gist.github.com/jedypod/50a3b68f9b5bbe487e1a). A physically accurate ZDefocus, which controls circle of confusion (coc) size based on lens geometry using the depth of field equation. Set your lens and film-back characteristics, your focus distance, and adjust the size of your bokeh with the aperture size, just like a real lens. <br>Located in the ```Studio``` menu.

- **df Night Adaptation** <br> Created by Derek Flood. Simulate perceptual loss of color and blue-shift in low-light conditions by desaturating and color balancing low luminance colors. Based on ZoneSat and ZoneGrade tools by Jed Smith. <br>Located in the ```Studio``` menu.

- **Write dailies mov** <br> Created by Derek Flood. Writes a JPG image sequence for dailies with options for resizing and auto-generated burn-in text (text includes script name, output color space, and frame count). Burn-in text placement is based on resolution in project settings. <br> Usage: Set desired resize scale, file path, and Output Transform. Click "render movie"<br>Located in the ```Studio``` menu. 

![img](img/nuke_dailies.jpg)

- **ACES Ref Gamut Compress** <br> [Created by the ACES Gamut Mapping Workgroup](https://github.com/ampas/aces-vwg-gamut-mapping-2020). See the [ACES Ref Gamut Compression](https://sharktacos.github.io/OpenColorIO-configs/docs/gamut.html) page for details. <br>Located in the ```Studio``` menu.

- **mm Color Target** <br> [Created by Marco Myer](https://www.marcomeyer-vfx.de/posts/mmcolortarget-nuke-gizmo/). Neutralize film footage with a Macbeth color chart to a target color space. <br>Located in the ```Gizmos``` menu. Note that this Giszmo requires NumPy. For Windows you can unzip the included numpy_win_python3.7.zip file and place it in your .nuke folder. See the video below for an example. <br>Located in the ```Studio``` menu.

<iframe width="560" height="315" src="https://www.youtube.com/embed/-LsSpV0ftCw" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>






