#---------------------------------------------------------
'''
 Export geo to USD with support for:
 - Proxy/render display purposes,
 - Payload geometry (.usdc) into asset file (.usda)
 - Custom metadata with originating Maya file “exported_from”
 
  v01 with two file workflow (geom and asset file)
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
#---------------------------------------------------------

import maya.cmds as mc
import os
from pxr import Usd, UsdGeom, Sdf, Gf

def add_payload(prim: Usd.Prim, payload_asset_path: str, payload_target_path: Sdf.Path) -> None:
    payloads: Usd.Payloads = prim.GetPayloads()
    payloads.AddPayload(
        assetPath=payload_asset_path,
        primPath=payload_target_path # OPTIONAL: Payload a specific target prim. Otherwise, uses the payloadd layer's defaultPrim.
    )


def asset_stage(asset_file, root_asset, geom_root):

    # Create USD "asset" stage, then create and define default prim
    asset_layer = Sdf.Layer.CreateNew(asset_file, args = {'format':'usda'})
    stage: Usd.Stage = Usd.Stage.Open(asset_layer)
    default_prim = UsdGeom.Xform.Define(stage, Sdf.Path(root_asset))
    stage.SetDefaultPrim(default_prim.GetPrim())
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    
    # draw modes for bounding box
    '''
    set_prim = stage.GetPrimAtPath(root_asset)
    set_geom_model_API = UsdGeom.ModelAPI.Apply(set_prim)
    set_geom_model_API.GetModelDrawModeAttr().Set(UsdGeom.Tokens.bounds) # bounds, cards
    set_geom_model_API.GetModelCardGeometryAttr().Set(UsdGeom.Tokens.cross) # cross, box
    '''
    
    # Create an xform to hold geo file as a payload
    payload_prim: Usd.Prim = UsdGeom.Xform.Define(stage, Sdf.Path(root_asset)).GetPrim()
    add_payload(payload_prim, geom_root, Sdf.Path(root_asset))
    
    # Add custom metadata for Maya fie. 
    payload_prim.SetMetadata("customData", {"Exported_from": maya_scene})

    # Set kind to component (for bounding box from parent needs to be higher)
    model_API = Usd.ModelAPI(payload_prim)
    model_API.SetKind(Kind.Tokens.component)

    

    # Overs with render and proxy purposes
    # This assumes "GEO" and "GEO_PROXY" naming, otherwise will result in orphaned overs. CBB.
    render_path = Sdf.Path(root_asset+"/GEO")
    render_prim = stage.DefinePrim(render_path)
    render_prim.SetSpecifier(Sdf.SpecifierOver)
    render_purpose = UsdGeom.Imageable(render_prim).CreatePurposeAttr()
    render_purpose.Set(UsdGeom.Tokens.render)
    
    proxy_path = Sdf.Path(root_asset+"/GEO_PROXY")
    proxy_prim = stage.DefinePrim(proxy_path)
    proxy_prim.SetSpecifier(Sdf.SpecifierOver)
    proxy_purpose = UsdGeom.Imageable(proxy_prim).CreatePurposeAttr()
    proxy_purpose.Set(UsdGeom.Tokens.proxy)  

    # diagnositic
    print_asset = stage.GetRootLayer().ExportToString()
    #print("===============ASSET FILE ======================================")
    #print(print_asset)
    
    # save to file
    stage.GetRootLayer().Save()
    



sel=mc.ls(sl=True)
if sel:

    # Export selected to USD
    usdfilter = "USD Export (*.usd *.usdc *.usda)"
    filepath = mc.fileDialog2(fileFilter=usdfilter, caption="Export selected to USD with geometry payloaded into asset file", dialogStyle=2)
    
    # variables
    fileName = filepath[0]
    stripExtension = os.path.splitext(fileName)[0]
    geoName = stripExtension + '.geom.usdc'
    dag_root = sel[0].replace("|", "")
    root_asset = "/" + dag_root
    geom_root = "./" + os.path.basename(geoName)
    asset_file = stripExtension + '.usda'
    asset_root = os.path.basename(asset_file)
    maya_scene = mc.file (q=True, sn=True, shn=True)
    
    # Export the geo file
    mc.file(geoName, options=";exportDisplayColor=1;exportColorSets=0;mergeTransformAndShape=1;exportComponentTags=0;defaultUSDFormat=usdc;jobContext=[Arnold];materialsScopeName=mtl", typ="USD Export", pr=True, ch=True, chn=True, exportSelected=True, f=True)

    # Export asset file with geo payload
    asset_stage(asset_file, root_asset, geom_root)
    



else:
    mc.confirmDialog(t="Oops! Nothing Selected", icon="warning")


