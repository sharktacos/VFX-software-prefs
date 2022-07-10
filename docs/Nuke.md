<h1>Installation</h1>
Place contents in the .nuke folder of your $HOME directory (if at the school lab that's your Z drive). 
<h2>Windows</h2>
  You can find the $HOME folder by typing %HOME% or %USERPROFILE% in an Explorer Browser.
<h2>MacOS</h2>
  In the finder menu select <b>go>home</b>. This folder is hidden by default. To show it Press CMD+Shift+Period in the Finder.

## Tools/Gizmos

- **Shuffle EXR** </br> [Created by Nacho Igea](http://www.nukepedia.com/python/import/export/shufflelayers). The older EXR shuffle was incompatible with Nuke 13. The new one has options to extract all AOVs or select the AOVs to extract. </br>Located in the ```User``` tab of a ```Read``` node.
- **bm Optical Glow** </br> [Created by Ben McEwan](https://github.com/BenMcEwan/nuke_public). Adds exponentially-increasing blurs together to produce a more optically-correct, natural glow. </br>Located in the ```Gizmos``` menu.
- **bm Optical Light Wrap** </br> [Created by Ben McEwan](https://github.com/BenMcEwan/nuke_public). Adds exponentially-increasing blurs together to produce a more optically-correct, natural light wrap. </br>Located in the ```Gizmos``` menu.
- **Optical Z Defocus** </br> [Created by Jed Smith](https://gist.github.com/jedypod/50a3b68f9b5bbe487e1a). A physically accurate ZDefocus, which controls circle of confusion (coc) size based on lens geometry using the depth of field equation. Set your lens and film-back characteristics, your focus distance, and adjust the size of your bokeh with the aperture size, just like a real lens. </br>Located in the ```Gizmos``` menu.
- **mm Color Target** </br> [Created by Marco Myer](https://www.marcomeyer-vfx.de/posts/mmcolortarget-nuke-gizmo/). Neutralize film footage with a Macbeth color chart to a target color space. </br>Located in the ```Gizmos``` menu. Note that this Giszmo requires NumPy. For Windows you can unzip the included numpy_win_python3.7.zip file and place it in your .nuke folder.
- **df Night Adaptation** </br> Created by Derek Flood. Simulate perceptual loss of color and blue-shift in low-light conditions by desaturating and color balancing low luminance colors. Based on ZoneSat and ZoneGrade tools by Jed Smith.
- **ACES Ref Gamut Compress** </br> [Created by the ACES Gamut Mapping Workgroup](https://github.com/ampas/aces-vwg-gamut-mapping-2020). </br>Located in ```Color > OCIO``` menu

*The video below shows the usage of mm Color Target to neutralize a film plate for VFX work* </br>
<div style="padding:56.31% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/727228662?h=6d5cbf799a&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;" title="Plate Neutralization for CG integration"></iframe></div><script src="https://player.vimeo.com/api/player.js"></script>


