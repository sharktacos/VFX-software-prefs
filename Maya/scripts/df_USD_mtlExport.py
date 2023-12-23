#--------------------------------------------------------------------------------
'''
 Export Material to USD - materials and bindings sans geometry
 v6 - change extention to .usd (fixes error in USD 0.25)

 call with:
import df_USD_mtlExport
df_USD_mtlExport.main()

 (c) Derek Flood, 2023
 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
#--------------------------------------------------------------------------------

import maya.cmds as mc
import os
from pxr import Usd, UsdGeom, Sdf

def setLatestLoadStageFolder(sceneFolder):
    mc.optionVar ( stringValue=("mayaUsd_LatestLoadStageFolder", sceneFolder) )

def getLatestLoadStageFolder():

    sceneFolder=""
    
    # First check if we've saved a location in the option var
    if mc.optionVar ( exists="mayaUsd_LatestLoadStageFolder"):
        
        sceneFolder = mc.optionVar (q="mayaUsd_LatestLoadStageFolder")
        print (sceneFolder)
    
    # Then check if there is a current Maya scene, if so choose that as
    # a starting point.
    
    if "" == sceneFolder:
        sceneFolder = os.path.dirname(mc.file (q=True, sceneName=True))

    # If we are really starting from scratch then just go with the 
    # current workspace location for scenes.
    if "" == sceneFolder:
        workspaceLocation = mc.workspace (q=True, fn=True)
        scenesFolder = mc.workspace (fileRuleEntry="scene")
        sceneFolder = workspaceLocation + "/" + scenesFolder
    

    return sceneFolder



# Adapted from Jason Coelho's post on Maya-USD Github: https://github.com/Autodesk/maya-usd/discussions/3197
def materials_sans_mesh(root_asset, mtl_file, find_groups):

    # Load in stage from file
    layer_to_edit = mtl_file
    stage = Usd.Stage.Open(layer_to_edit)
    stage_layer = stage.GetRootLayer()
    
    # Replace xforms with scopes for purpose groups
    render_value = find_groups[0]  
    proxy_value = find_groups[1]  
    prim_geo = stage.GetPrimAtPath(root_asset + "/geo")
    prim_geo.SetTypeName("Scope")
    prim_render = stage.GetPrimAtPath(root_asset + "/geo/" + render_value)
    prim_render.SetTypeName("Scope")
    prim_proxy = stage.GetPrimAtPath(root_asset + "/geo/" + proxy_value)
    prim_proxy.SetTypeName("Scope")
    
    # add metadata with Maya scene used to generate asset
    maya_scene = mc.file (q=True, sn=True, shn=True)
    
    prim_path = Sdf.Path(root_asset)
    meta_prim = stage.DefinePrim(prim_path, "Xform")
    meta_prim.SetMetadata("customData", {"Export_from": maya_scene})

    # Traverse the stage and remove any properties that are not related to the Materials and Shaders
    for prim in stage.TraverseAll():

        # Skip Arnold options Prim
        if prim.GetTypeName() == 'ArnoldOptions':
            continue

        if prim.GetTypeName() not in ['Material', 'Shader']:
            for prim_property in prim.GetAuthoredProperties():
                if prim_property.GetName() not in ['material:binding', 'primvars:displayColor']:
                    if prim.GetTypeName() == 'GeomSubset':
                        pass

                    else:
                        prim.RemoveProperty(prim_property.GetName())

    stage_layer.Save()

def main():
    
    sel = mc.ls(sl=True, tr=True)
    if sel:
        geoGrp = mc.listRelatives (sel)
        if geoGrp[0] != "geo":
            mc.confirmDialog (message="Missing \"geo\" group. Structure must be \n\nroot/ (asset name)\n   geo/\n      render/ \n      proxy/\n\nNote that \"geo\" must be the exact name for the geometry scope. The render and proxy purpose scopes can be named as desired based on your studio naming conventions. The root prim is typically given the name of the asset. For example \"fruitBowl\" ", 
                                               button="Got it", icon="warning")
            return

        geoGrpPath = mc.listRelatives (sel, path=True)
        find_groups = mc.listRelatives (geoGrpPath)    
        if len(find_groups) != 2:
            mc.confirmDialog (message="Just two child groups under \"geo\" please. Render and Proxy, in that order", button="Sorry", icon="warning")
            return

        # File export dialog...
        filepath = None
        usdfilter = "USD Export (*.usd *.usda *.usdc)"
        #projDir = mc.workspace(rootDirectory=True, query=True)
        projDir = getLatestLoadStageFolder()


        filepath = mc.fileDialog2(fileFilter=usdfilter, caption="Export Selected to USD with materials and bindings", dialogStyle=2, dir=projDir)

        if filepath is not None:

            USDlayer = filepath[0]
            stripExtension = os.path.splitext(USDlayer)[0]
            mtl_file = stripExtension + '.mtl.usd'
            dag_root = sel[0].replace("|", "")
            root_asset = "/" + dag_root

            # Export selected geo & mtl to USD...
            setLatestLoadStageFolder( os.path.dirname(filepath[0]) )
            mc.file(mtl_file, options=";exportDisplayColor=1;exportColorSets=0;mergeTransformAndShape=1;exportComponentTags=0;defaultUSDFormat=usda;jobContext=[Arnold];materialsScopeName=mtl", typ="USD Export", pr=True, exportSelected=True, f=True)

            # Remove mesh properties, keep materials and bindings
            materials_sans_mesh(root_asset, mtl_file, find_groups)

        else:
            mc.confirmDialog(message='Job canceled by user', button="Yep", icon="info")

    else:
        mc.confirmDialog(message='Oops! Nothing Selected. Select the asset to export in the Outliner.', button="Derp", icon="warning")

if __name__ == "__main__":
    main()
    
#main()