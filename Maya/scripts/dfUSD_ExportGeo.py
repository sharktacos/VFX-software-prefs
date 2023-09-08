#---------------------------------------------------------
'''
 Export geo to USD with support for:
 - Proxy/render display purposes,
 - Reference geometry (.usdc) into payload file (.usda) which is payloaded into Asset file
 - Custom metadata with originating Maya file “exported_from”
 
 v2 with Pixar style asset, payload, and geom files.
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
from pxr import Usd, UsdGeom, Sdf, Gf, Vt

def add_payload(prim: Usd.Prim, payload_asset_path: str, payload_target_path: Sdf.Path) -> None:
    payloads: Usd.Payloads = prim.GetPayloads()
    payloads.AddPayload(
        assetPath=payload_asset_path,
        primPath=payload_target_path # OPTIONAL: Payload a specific target prim. Otherwise, uses the payloadd layer's defaultPrim.
    )

def add_ext_reference(prim: Usd.Prim, ref_asset_path: str, ref_target_path: Sdf.Path) -> None:
    references: Usd.References = prim.GetReferences()
    references.AddReference(
        assetPath=ref_asset_path,
        primPath=ref_target_path # OPTIONAL: Reference a specific target prim. Otherwise, uses the referenced layer's defaultPrim.
    )

def payload_stage(asset_file, payload_file, root_asset, geom_root):

    asset_baseName = os.path.basename(asset_file)
    asset_name = os.path.splitext(asset_baseName)[0]
    
    # Create USD "payload" stage, then create and define default prim
    pay_layer = Sdf.Layer.CreateNew(payload_file, args = {'format':'usda'})
    stage: Usd.Stage = Usd.Stage.Open(pay_layer)
    default_prim = UsdGeom.Xform.Define(stage, Sdf.Path(root_asset))
    stage.SetDefaultPrim(default_prim.GetPrim())
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    
    # asset idenitfiers
    prim_path = Sdf.Path(root_asset)
    prim = stage.DefinePrim(prim_path, "Xform")
    prim.SetMetadata("assetInfo", {"identifier": Sdf.AssetPath(asset_baseName)})
    prim.SetAssetInfoByKey("name", asset_name)
    
    # Create an xform to hold geo file as a reference
    ref_prim: Usd.Prim = UsdGeom.Xform.Define(stage, Sdf.Path(root_asset)).GetPrim()
    add_ext_reference(ref_prim, geom_root, Sdf.Path(root_asset))
    
    # diagnositic
    print_payload = stage.GetRootLayer().ExportToString()
    print("===============PAYLOAD FILE ======================================")
    print(print_payload)
    
    # save to file
    stage.GetRootLayer().Save()
    

def asset_stage(asset_file, root_asset, payfile_root):

    asset_baseName = os.path.basename(asset_file)
    asset_name = os.path.splitext(asset_baseName)[0]

    # Create USD "asset" stage, then create and define default prim
    asset_layer = Sdf.Layer.CreateNew(asset_file, args = {'format':'usda'})
    stage: Usd.Stage = Usd.Stage.Open(asset_layer)
    default_prim = UsdGeom.Xform.Define(stage, Sdf.Path(root_asset))
    stage.SetDefaultPrim(default_prim.GetPrim())
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    
    # asset idenitfiers
    prim_path = Sdf.Path(root_asset)
    prim = stage.DefinePrim(prim_path, "Xform")
    prim.SetMetadata("assetInfo", {"identifier": Sdf.AssetPath(asset_baseName)})
    prim.SetAssetInfoByKey("name", asset_name)
    
    # bounding box 
    '''   
    bbox_cache = UsdGeom.BBoxCache(1, [UsdGeom.Tokens.default_, UsdGeom.Tokens.render],
                               useExtentsHint=False, ignoreVisibility=False)
    bbox = bbox_cache.ComputeUntransformedBound(prim)
    root_geom_model_API = UsdGeom.ModelAPI.Apply(prim)   
    extentsHint = root_geom_model_API.ComputeExtentsHint(bbox_cache)
    root_geom_model_API.SetExtentsHint(extentsHint)
    
    set_prim = stage.GetPrimAtPath(root_asset)
    set_geom_model_API = UsdGeom.ModelAPI.Apply(set_prim)
    set_geom_model_API.GetModelDrawModeAttr().Set(UsdGeom.Tokens.bounds) # bounds, cards
    set_geom_model_API.GetModelCardGeometryAttr().Set(UsdGeom.Tokens.cross) # cross, box
    '''
    
    # Create an xform to hold payload file as a payload
    payload_prim: Usd.Prim = UsdGeom.Xform.Define(stage, Sdf.Path(root_asset)).GetPrim()
    add_payload(payload_prim, payfile_root, Sdf.Path(root_asset))
    
    # Add custom metadata for Maya fie. 
    payload_prim.SetMetadata("customData", {"Exported_from": maya_scene})

    # Set kind to component 
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
    print("===============ASSET FILE ======================================")
    print(print_asset)
    
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
    geoName = stripExtension + '.geom'
    payName = stripExtension + '_payload.usda'
    dag_root = sel[0].replace("|", "")
    root_asset = "/" + dag_root
    asset_file = stripExtension + '.usda'
    payload_file = stripExtension + '_payload.usda'
    geom_root = "./" + os.path.basename(geoName + '.usd')
    payfile_root = "./" + os.path.basename(payName)
    maya_scene = mc.file (q=True, sn=True, shn=True)
    
    # Export the geo file
    mc.file(geoName, options=";exportDisplayColor=1;exportColorSets=0;mergeTransformAndShape=1;exportComponentTags=0;defaultUSDFormat=usdc;jobContext=[Arnold];materialsScopeName=mtl", typ="USD Export", pr=True, ch=True, chn=True, exportSelected=True, f=True)

    # Export asset file with geo payload
    payload_stage(asset_file, payload_file, root_asset, geom_root)
    asset_stage(asset_file, root_asset, payfile_root)



else:
    mc.confirmDialog(t="Oops! Nothing Selected", icon="warning")


