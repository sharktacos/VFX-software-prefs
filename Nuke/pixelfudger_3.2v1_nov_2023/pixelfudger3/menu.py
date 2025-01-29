#############################################################
# menu.py
# Add Pixelfuger menu to Nuke's Nodes menu.
# (C) 2023 - Xavier Bourque - www.pixelfudger.com
#############################################################

import nuke

nuke.pluginAddPath('icons')

aboutMsg = 'Pixelfudger 3.2 \n2023/11\nCreated by: Xavier Bourque\nwww.pixelfudger.com\n(c) 2011-2023'

t=nuke.menu("Nodes")
u=t.addMenu("Pixelfudger3", icon="PxF_Menu3.png")
 
u.addCommand( "PxF_Bandpass", "nuke.createNode('PxF_Bandpass')", icon="PxF_Bandpass.png" ) 
u.addCommand( "PxF_ChromaBlur", "nuke.createNode('PxF_ChromaBlur')", icon="PxF_ChromaBlur.png")
u.addCommand( "PxF_DeepFade", "nuke.createNode('PxF_DeepFade')", icon="PxF_DeepFade.png")
u.addCommand( "PxF_DeepMask", "nuke.createNode('PxF_DeepMask')", icon="PxF_DeepMask.png")
u.addCommand( "PxF_DeepResample", "nuke.createNode('PxF_DeepResample')", icon="PxF_DeepResample.png")
v = u.addMenu("PxF_Defocus", icon="PxF_IDefocus.png")
v.addCommand( "PxF_DeepDefocus", "nuke.createNode('PxF_DeepDefocus')", icon="PxF_IDefocus.png") 
v.addCommand( "PxF_IDefocus", "nuke.createNode('PxF_IDefocus')", icon="PxF_IDefocus.png")
v.addCommand( "PxF_ZDefocus", "nuke.createNode('PxF_ZDefocus')", icon="PxF_IDefocus.png")
u.addCommand( "PxF_Distort", "nuke.createNode('PxF_Distort')", icon="PxF_Distort.png") 
u.addCommand( "PxF_Erode", "nuke.createNode('PxF_Erode')", icon="PxF_Erode.png")
u.addCommand( "PxF_Filler", "nuke.createNode('PxF_Filler')", icon="PxF_Filler.png") 
u.addCommand( "PxF_Grain", "nuke.createNode('PxF_Grain')", icon="PxF_Grain.png") 
u.addCommand( "PxF_HueSat", "nuke.createNode('PxF_HueSat')", icon="PxF_HueSat.png")  
u.addCommand( "PxF_KillSpill", "nuke.createNode('PxF_KillSpill')", icon="PxF_KillSpill.png")
w = u.addMenu("PxF_Lights", icon="PxF_Lights.png")
w.addCommand( "PxF_AreaLight", "nuke.createNode('PxF_AreaLight')", icon="PxF_AreaLight.png" )
w.addCommand( "PxF_EnvLight", "nuke.createNode('PxF_EnvLight')", icon="PxF_EnvLight.png" )
w.addCommand( "PxF_GeoLight", "nuke.createNode('PxF_GeoLight')", icon="PxF_GeoLight.png" )
w.addCommand( "PxF_RingLight", "nuke.createNode('PxF_RingLight')", icon="PxF_RingLight.png" )
w.addCommand( "PxF_TubeLight", "nuke.createNode('PxF_TubeLight')", icon="PxF_TubeLight.png" )
u.addCommand( "PxF_Line", "nuke.createNode('PxF_Line')", icon="PxF_Line.png" ) 
u.addCommand( "PxF_MergeWrap", "nuke.createNode('PxF_MergeWrap')", icon="PxF_MergeWrap.png" )
u.addCommand( "PxF_Nukebench", "nuke.createNode('PxF_Nukebench')", icon="PxF_Nukebench.png" )
u.addCommand( "PxF_ScreenClean", "nuke.createNode('PxF_ScreenClean')", icon="PxF_ScreenClean.png")
u.addCommand( "PxF_SmokeBox", "nuke.createNode('PxF_SmokeBox')", icon="PxF_SmokeBox.png")
u.addCommand( "PxF_Smoother", "nuke.createNode('PxF_Smoother')", icon="PxF_Smoother.png")
u.addCommand( "PxF_TimeMerge", "nuke.createNode('PxF_TimeMerge')", icon="PxF_TimeMerge.png")
u.addCommand( "PxF_VectorEdgeBlur", "nuke.createNode('PxF_VectorEdgeBlur')", icon="PxF_VectorEdgeBlur.png")
u.addSeparator()
u.addCommand("About Pixelfudger...", "nuke.message(aboutMsg)", icon="PxF_Menu3.png")
