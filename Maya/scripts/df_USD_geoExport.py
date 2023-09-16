#---------------------------------------------------------
'''
 Export geo to USD with support for:
 - Proxy/render display purposes,
 - Reference geometry (.usdc) into payload file (.usda) which is payloaded into Asset file
 - Custom metadata with originating Maya file “exported_from”
 
 v3 called from Mel with filedialog options for render & proxy purpse
 (c) Derek Flood, 2023

 call with: 
df_USD_geoExport_UI.mel

python calls:
import dfUSD_CreateAsset
dfUSD_CreateAsset.payload_stage(fileName)
dfUSD_CreateAsset.asset_stage(fileName, render_value, proxy_value)
 
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
from pxr import Usd, UsdGeom, Sdf, Gf, Kind, Vt

# variables:

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

def geom_stage(fileName, root_asset, render_value, proxy_value):

    stripExtension = os.path.splitext(fileName)[0]
    geom_name = stripExtension + '.geom'

    # Export the geo file
    mc.file(geom_name, options=";exportDisplayColor=1;exportColorSets=0;mergeTransformAndShape=1;exportComponentTags=0;defaultUSDFormat=usdc;jobContext=[Arnold];materialsScopeName=mtl", typ="USD Export", pr=True, ch=True, chn=True, exportSelected=True, f=True)
    
    # Replace xforms with scopes for purpose groups
    stage = Usd.Stage.Open(geom_name + '.usd')
    prim_geo = stage.GetPrimAtPath(root_asset + "/geo")
    prim_geo.SetTypeName("Scope")
    
    prim_render = stage.GetPrimAtPath(root_asset + "/geo/" + render_value)
    prim_render.SetTypeName("Scope")
    prim_proxy = stage.GetPrimAtPath(root_asset + "/geo/" + proxy_value)
    prim_proxy.SetTypeName("Scope")

    stage.Save()


    
def payload_stage(fileName, root_asset):

    stripExtension = os.path.splitext(fileName)[0]
    asset_file = stripExtension + '.usda'
    asset_baseName = os.path.basename(asset_file)
    asset_name = os.path.splitext(asset_baseName)[0]

    geom_name = stripExtension + '.geom'
    payload_file = stripExtension + '_payload.usda'
    geom_root = "./" + os.path.basename(geom_name + '.usd')
    
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
    #print("===============PAYLOAD FILE ======================================")
    #print(print_payload)
    
    # save to file
    stage.GetRootLayer().Save()


def asset_stage(fileName, render_value, proxy_value, root_asset):

    maya_scene = mc.file (q=True, sn=True, shn=True)
    stripExtension = os.path.splitext(fileName)[0]
    asset_file = stripExtension + '.usda'
    asset_baseName = os.path.basename(asset_file)
    asset_name = os.path.splitext(asset_baseName)[0]
    payName = stripExtension + '_payload.usda'
    payfile_root = "./" + os.path.basename(payName)

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

    # Create an xform to hold payload file as a payload
    payload_prim: Usd.Prim = UsdGeom.Xform.Define(stage, Sdf.Path(root_asset)).GetPrim()
    add_payload(payload_prim, payfile_root, Sdf.Path(root_asset))
    
    # Add custom metadata for Maya fie. 
    payload_prim.SetMetadata("customData", {"Exported_from": maya_scene})

    # Set kind to component 
    model_API = Usd.ModelAPI(payload_prim)
    model_API.SetKind(Kind.Tokens.component)

    # Overs with render and proxy purposes
    render_path = Sdf.Path(root_asset + "/geo/" + render_value)
    render_prim = stage.DefinePrim(render_path)
    render_prim.SetSpecifier(Sdf.SpecifierOver)
    render_purpose = UsdGeom.Imageable(render_prim).CreatePurposeAttr()
    render_purpose.Set(UsdGeom.Tokens.render)
    
    proxy_path = Sdf.Path(root_asset + "/geo/" + proxy_value)
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



def main(fileName, render_value, proxy_value):

    sel=mc.ls(sl=True)
    dag_root = sel[0].replace("|", "")
    root_asset = "/" + dag_root

    geom_stage(fileName, root_asset, render_value, proxy_value)
    payload_stage(fileName, root_asset)
    asset_stage(fileName, render_value, proxy_value, root_asset)


if __name__ == "__main__":
    main()

