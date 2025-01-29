#---------------------------------------------------------
'''
 Export geo to USD with support for:
 - Proxy/render display purposes,
 - Reference geometry (.usdc) into payload file (.usda) which is payloaded into Asset file
 - Custom metadata with originating Maya file “exported_from”
 - variant switch to display high res mesh in viewport
 - switch to "_geo" naming convention for mesh file in crate binary.
 - Look file with overs for MaterialX references.
 
 v5 Export payloaded USD asset with MaterialX reference
 (c) Derek Flood, 2025

 call with: 
df_USD_geoExport_UI.mel
(see that file for details)

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
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Kind, Vt
import re



def compute_bbox(prim: Usd.Prim) -> Gf.Range3d:
    """
    Compute Bounding Box using ComputeWorldBound at UsdGeom.Imageable
    See https://graphics.pixar.com/usd/release/api/class_usd_geom_imageable.html

    Args:
        prim: A prim to compute the bounding box.
    Returns: 
        A range (i.e. bounding box), see more at: https://graphics.pixar.com/usd/release/api/class_gf_range3d.html
    """
    imageable = UsdGeom.Imageable(prim)
    time = Usd.TimeCode.Default() # The time at which we compute the bounding box
    bound = imageable.ComputeWorldBound(time, UsdGeom.Tokens.default_)
    bound_range = bound.ComputeAlignedBox()
    return bound_range
    

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
    
def find_mtlx_file(directory, mtlx_name):
    """
    Search recursively for a MaterialX file within a given directory.
    Returns the relative path combined with the file name if found, otherwise None.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == f"{mtlx_name}.mtlx":
                relative_path = os.path.relpath(root, directory)
                # Combine relative path and file name
                if relative_path == ".":
                    return file
                else:
                    return os.path.join(relative_path, file)
    return None

def get_mesh_and_material_info(render_value, fileName):
    """
    Get mesh and material information for all meshes under a given transform.
    Returns a list of tuples containing meshName and mtlx_name.
    """
    # Determine the directory where the USD file is being written
    usd_directory = os.path.dirname(os.path.abspath(fileName))
    
    # Get the child group names under selected to populate purpose fields
    long_sel = mc.ls(sl=True, long=True)
    geoGrpPath = mc.listRelatives(long_sel, path=True, fullPath=True)
    find_groups = mc.listRelatives(geoGrpPath, path=True, fullPath=True)
    found_render = find_groups[0]
    
    mesh_info = []
    error_messages = []
    print("")
    
    # Get all shapes under the transform
    shapes = mc.listRelatives(found_render, ad=True, type='mesh', fullPath=True)
    if not shapes:
        return mesh_info

    for shape in shapes:
        try:
            # Get the parent transform of the shape
            meshName = mc.listRelatives(shape, p=True, type='transform')[0]

            # Get the material shading group connected to the shape
            Maya_SG = mc.listConnections(shape + '.instObjGroups', d=True, s=False)[0]
        
            # Get the material connected to the shading group
            mtlX_SG = mc.listConnections(Maya_SG + '.surfaceShader', d=False, s=True)[0]
        
            # Extract the ufePath attribute
            SG_ufePath = mc.getAttr(mtlX_SG + '.ufePath')
        
            # Extract the material name from the ufePath
            mtlx_docPath = re.sub(r"%[^%]*$", "", SG_ufePath)
            mtlx_name = re.search(r"%([^%]*)$", mtlx_docPath).group(1)
        
            # Search recursively for the MaterialX file in the USD directory
            mtlx_file = find_mtlx_file(usd_directory, mtlx_name)
            if not mtlx_file:
                warning_message = (f"Warning: The MaterialX file {mtlx_name}.mtlx for render mesh {meshName} does not exist in\n"
                                   f"directory: {usd_directory}.\n"
                                   f"Please save it either with Export MaterialX Document or Export Documents in MaterialX Stack.")
                print(warning_message)
                error_messages.append(warning_message)
                continue
            
            # Append the meshName and the full path of the MaterialX file
            mesh_info.append((meshName, mtlx_file, mtlx_name))
        
        except Exception as e:
            warning_message = f"Warning: The renderable mesh {meshName} is not assigned to a MaterialX material. Skipping in look file."
            print(warning_message)
            error_messages.append(warning_message)
            continue
            
    # Check if there were any errors and show a single dialog if so
    if error_messages:
        mc.confirmDialog(
            title='Missing some MaterialX materials or bindings',
            message='Process completed with errors. See Script Editor for details.',
            button=['Oh My!'],
            defaultButton='Oh My!',
            cancelButton='Oh My!',
            dismissString='Oh My!'
        )  
    return mesh_info


    
def get_proxy_mesh_and_material_info(proxy_value, fileName):
    """
    Get mesh and material information for all meshes under a given transform.
    Returns a list of tuples containing proxyMesh and px_mtlx_name.
    """
    # Determine the directory where the USD file is being written
    usd_directory = os.path.dirname(os.path.abspath(fileName))
    
    # Get the child group names under selected to populate purpose fields
    long_sel = mc.ls(sl=True, long=True)
    geoGrpPath = mc.listRelatives(long_sel, path=True, fullPath=True)
    find_groups = mc.listRelatives(geoGrpPath, path=True, fullPath=True)
    #found_render = find_groups[0]
    found_proxy = find_groups[1]
    
    proxy_info = []
    
    # Get all proxyShapes under the transform
    proxyShapes = mc.listRelatives(found_proxy, ad=True, type='mesh', fullPath=True)
    if not proxyShapes:
        return proxy_info

    for proxyShape in proxyShapes:
        # Get the parent transform of the proxyShape
        proxyMesh = mc.listRelatives(proxyShape, p=True, type='transform')[0]

        # Get the material shading group connected to the proxyShape
        pxMaya_SG = mc.listConnections(proxyShape + '.instObjGroups', d=True, s=False)[0]
        
        # Get the material connected to the shading group
        px_mtlX_SG = mc.listConnections(pxMaya_SG + '.surfaceShader', d=False, s=True)[0]
        
        try:
            # Extract the ufePath attribute
            px_SG_ufePath = mc.getAttr(px_mtlX_SG + '.ufePath')

            # Extract the material name from the ufePath
            px_mtlx_docPath = re.sub(r"%[^%]*$", "", px_SG_ufePath)
            px_mtlx_name = re.search(r"%([^%]*)$", px_mtlx_docPath).group(1)


            # Search recursively for the MaterialX file in the USD directory
            px_mtlx_file = find_mtlx_file(usd_directory, px_mtlx_name)
            if not px_mtlx_file:
                warning_message = (f"Warning: The MaterialX file {px_mtlx_name}.mtlx for proxy mesh {proxyMesh} does not exist in\n"
                                   f"directory: {usd_directory}.\n"
                                   f"Please save it either with Export MaterialX Document or Export Documents in MaterialX Stack.")
                print(warning_message)
                continue
            
            proxy_info.append((proxyMesh, px_mtlx_file, px_mtlx_name))  # Append the tuple with mesh name and combined path
            
        except Exception as e:
            print(f"Warning: The proxy mesh {proxyMesh} is not assigned to a MaterialX material.")
            continue
            
    return proxy_info

def geom_stage(fileName, root_asset, render_value, proxy_value):

    stripExtension = os.path.splitext(fileName)[0]
    geom_name = stripExtension + '_geo'

    # Export the geo file
    #mc.file(geom_name, options=";exportDisplayColor=1;exportColorSets=0;mergeTransformAndShape=1;exportComponentTags=0;defaultUSDFormat=usdc;jobContext=[None];materialsScopeName=mtl", typ="USD Export", pr=True, ch=True, chn=True, exportSelected=True, f=True)
    mc.file(geom_name, options=";exportDisplayColor=1;exportColorSets=0;mergeTransformAndShape=1;exportComponentTags=0;defaultUSDFormat=usdc;materialsScopeName=mtl", typ="USD Export", pr=True, ch=True, chn=True, exportSelected=True, f=True)
    
    # Replace xforms with scopes for purpose groups
    stage = Usd.Stage.Open(geom_name + '.usd')
    prim_geo = stage.GetPrimAtPath(root_asset + "/geo")
    prim_geo.SetTypeName("Scope")
    
    # Extents Hint BBox (not working with unloaded payloads currently in Maya)
    bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ['default', 'render'])    
    root_geom_model_API = UsdGeom.ModelAPI.Apply(prim_geo)
    extentsHint = root_geom_model_API.ComputeExtentsHint(bbox_cache)
    root_geom_model_API.SetExtentsHint(extentsHint)
    
    prim_render = stage.GetPrimAtPath(root_asset + "/geo/" + render_value)
    prim_render.SetTypeName("Scope")
    prim_proxy = stage.GetPrimAtPath(root_asset + "/geo/" + proxy_value)
    prim_proxy.SetTypeName("Scope")

    stage.Save()


    
def payload_stageOLD(fileName, root_asset):

    stripExtension = os.path.splitext(fileName)[0]
    asset_file = stripExtension + '.usda'
    asset_baseName = os.path.basename(asset_file)
    asset_name = os.path.splitext(asset_baseName)[0]

    geom_name = stripExtension + '_geo'
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
    
    
def payload_stage(fileName, root_asset):
    stripExtension = os.path.splitext(fileName)[0]
    payload_file = stripExtension + '_payload.usda'
    look_file = stripExtension + '_look.usda'
    geom_file = stripExtension + '_geo.usd'

    # Create USD "payload" stage
    pay_layer = Sdf.Layer.CreateNew(payload_file, args={'format': 'usda'})
    stage: Usd.Stage = Usd.Stage.Open(pay_layer)
    
    # Set the stage metadata
    stage.SetMetadata('metersPerUnit', 0.01)
    stage.SetMetadata('upAxis', 'Y')
    
    # Set the subLayers with relative paths
    relative_look_file = f"./{os.path.basename(look_file)}"
    relative_geom_file = f"./{os.path.basename(geom_file)}"
    pay_layer.subLayerPaths = [relative_look_file, relative_geom_file]
    
    # Set the default prim
    default_prim = stage.DefinePrim(root_asset)
    stage.SetDefaultPrim(default_prim.GetPrim())

    # Diagnostic
    print_asset = stage.GetRootLayer().ExportToString()
    #print("===============PAYLOAD FILE ======================================")
    #print(print_asset)
    
    # Save the stage
    stage.GetRootLayer().Save()
    





def asset_stage(fileName, render_value, proxy_value, root_asset):

    maya_scene = mc.file (q=True, sn=True, shn=True)
    stripExtension = os.path.splitext(fileName)[0]
    asset_file = stripExtension + '.usda'
    asset_baseName = os.path.basename(asset_file)
    asset_name = os.path.splitext(asset_baseName)[0]
    
    payName = stripExtension + '_payload.usda'
    #payName = stripExtension + '_geo.usd'
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
    
    # Create an xform to hold geo file as a payload
    payload_prim: Usd.Prim = UsdGeom.Xform.Define(stage, Sdf.Path(root_asset)).GetPrim()
    add_payload(payload_prim, payfile_root, Sdf.Path(root_asset))
    
    # Add custom metadata for Maya fie. 
    payload_prim.SetMetadata("customData", {"Exported_from": maya_scene})

    # Set kind to component 
    model_API = Usd.ModelAPI(payload_prim)
    model_API.SetKind(Kind.Tokens.component)
    
    # Extents Hint BBox (not working with unloaded payloads currently in Maya)
    bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ['default', 'render'])    
    root_geom_model_API = UsdGeom.ModelAPI.Apply(payload_prim)
    extentsHint = root_geom_model_API.ComputeExtentsHint(bbox_cache)
    root_geom_model_API.SetExtentsHint(extentsHint)
    
    # Create display variants
    variant_sets = payload_prim.GetVariantSets().AddVariantSet('geo_vis')

    variant_sets.AddVariant("high_res")
    variant_sets.SetVariantSelection("high_res")
    with variant_sets.GetVariantEditContext():
        # Overs with default and guide purposes (for display of high res mesh)
        render_path = Sdf.Path(root_asset + "/geo/" + render_value)
        render_prim = stage.DefinePrim(render_path)
        render_prim.SetSpecifier(Sdf.SpecifierOver)
        render_purpose = UsdGeom.Imageable(render_prim).CreatePurposeAttr()
        render_purpose.Set(UsdGeom.Tokens.default_)
    
        proxy_path = Sdf.Path(root_asset + "/geo/" + proxy_value)
        proxy_prim = stage.DefinePrim(proxy_path)
        proxy_prim.SetSpecifier(Sdf.SpecifierOver)
        proxy_purpose = UsdGeom.Imageable(proxy_prim).CreatePurposeAttr()
        proxy_purpose.Set(UsdGeom.Tokens.guide)  
        
    variant_sets.AddVariant("preview")
    variant_sets.SetVariantSelection("preview")
    with variant_sets.GetVariantEditContext():
        # Overs with render and proxy purposes (for viewport preview)
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




def look_stage(fileName, root_asset, render_value, proxy_value):
    # Strip the file extension from fileName and create new filename with '_look.usda'
    stripExtension = os.path.splitext(fileName)[0]
    look_file = stripExtension + '_look.usda'

    # Create USD "look" stage
    look_layer = Sdf.Layer.CreateNew(look_file, args={'format': 'usda'})
    stage: Usd.Stage = Usd.Stage.Open(look_layer)
    
    # Set stage metadata
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    
    # Check if root_asset is valid
    if not root_asset or not root_asset.startswith('/'):
        raise ValueError("The root_asset path must be a non-empty absolute path starting with '/'.")
    
    # Override the root asset
    root_prim = stage.OverridePrim(root_asset)
    root_prim.SetSpecifier(Sdf.SpecifierOver)
    stage.SetDefaultPrim(root_prim)
    
    # Define the 'Materials' scope under the root asset as an over
    materials_scope_path = f'{root_asset}/mtl'
    materials_scope = stage.OverridePrim(materials_scope_path)
    
    # Ensure the 'Materials' scope is defined as a def and scope under the 'over' root asset
    materials_scope.SetSpecifier(Sdf.SpecifierDef)
    materials_scope.GetPrim().SetTypeName('Scope')
    
    # Process all meshes and materials under the given render_value
    mesh_material_info = get_mesh_and_material_info(render_value, fileName)
    
    #for meshName, mtlx_name in mesh_material_info:
    for meshName, mtlx_file, mtlx_name in mesh_material_info:
        
        # Add a reference to the MaterialX file in the 'Materials' scope
        materials_scope.GetReferences().AddReference(f'./{mtlx_file}', '/MaterialX/Materials')
        
        # Define the 'render' over under the root asset
        render_path = f'{root_asset}/geo/{render_value}'
        render_prim = stage.OverridePrim(render_path)
        render_prim.SetSpecifier(Sdf.SpecifierOver)
        
        # Define the 'meshName' over under the 'render' over
        mesh_name_path = f'{render_path}/{meshName}'
        mesh_name_prim = stage.OverridePrim(mesh_name_path)
        mesh_name_prim.SetSpecifier(Sdf.SpecifierOver)

        # Apply the MaterialBindingAPI schema on the 'meshName' prim
        UsdShade.MaterialBindingAPI.Apply(mesh_name_prim)
        
        # Define the material binding relationship
        material_binding_rel = mesh_name_prim.CreateRelationship('material:binding', False)
        material_binding_rel.SetTargets([f'{root_asset}/mtl/{mtlx_name}_SG'])


    
    # Process all proxy meshes and materials under the given proxy_value
    proxy_material_info = get_proxy_mesh_and_material_info(proxy_value, fileName)
    
    for proxyMesh, px_mtlx_file, px_mtlx_name in proxy_material_info:
        try:
            # Add a reference to the MaterialX file in the 'Materials' scope
            materials_scope.GetReferences().AddReference(f'./{px_mtlx_file}', '/MaterialX/Materials')
        
            # Define the 'proxy' over under the root asset
            proxy_path = f'{root_asset}/geo/{proxy_value}'
            proxy_prim = stage.OverridePrim(proxy_path)
            proxy_prim.SetSpecifier(Sdf.SpecifierOver)
        
            # Define the 'proxyMesh' over under the 'proxy' over
            mesh_proxy_path = f'{proxy_path}/{proxyMesh}'
            mesh_proxy_prim = stage.OverridePrim(mesh_proxy_path)
            mesh_proxy_prim.SetSpecifier(Sdf.SpecifierOver)

            # Apply the MaterialBindingAPI schema on the 'proxyMesh' prim
            UsdShade.MaterialBindingAPI.Apply(mesh_proxy_prim)
        
            # Define the material binding relationship
            material_binding_rel = mesh_proxy_prim.CreateRelationship('material:binding', False)
            material_binding_rel.SetTargets([f'{root_asset}/mtl/{px_mtlx_name}_SG'])
        except Exception as e:
            print(f"Warning: Skipping proxy mesh {proxyMesh} due to error: {e}")
            continue
            
    # Save the stage
    stage.GetRootLayer().Save()
    
    '''
    # Check for orphaned overs
    print("Checking for orphaned overs...")
    orphaned_overs = list(prim for prim in stage.TraverseAll() if not prim.IsDefined())
    if orphaned_overs:
        print("Found orphaned overs:")
        for orphan in orphaned_overs:
            print(orphan.GetPath())
    else:
        print("No orphaned overs found.")
    '''
    
    # Diagnostic
    print_asset = stage.GetRootLayer().ExportToString()
    #print("===============LOOK FILE ======================================")
    #print(print_asset)   
    

def arnold_subdiv():

    shapesInSel = mc.ls(dag=1,objectsOnly=1,long=1,selection=1,geometry=True)
    for shape_node in shapesInSel:
        # Check if Smooth Mesh Preview is on
        if mc.attributeQuery('displaySmoothMesh', node=shape_node, exists=True):
            smooth_preview_on = mc.getAttr(shape_node + ".displaySmoothMesh")
        else:
            # If the attribute doesn't exist, assume it's off
            smooth_preview_on = False

        # Set the Arnold subdiv type to catclark if Maya smooth mesh preview is on
        if smooth_preview_on:
            mc.setAttr(shape_node + ".aiSubdivType", 1)



def main(fileName, render_value, proxy_value):

    sel=mc.ls(sl=True)
    dag_root = sel[0].replace("|", "")
    root_asset = "/" + dag_root
    
    arnold_subdiv()
    geom_stage(fileName, root_asset, render_value, proxy_value)
    look_stage(fileName, root_asset, render_value, proxy_value)
    payload_stage(fileName, root_asset)
    asset_stage(fileName, render_value, proxy_value, root_asset)


if __name__ == "__main__":
    main()

