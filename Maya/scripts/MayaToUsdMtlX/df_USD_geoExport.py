#---------------------------------------------------------
'''
 Export geo to USD with support for:
 - Option for Proxy/render display purposes,
 - Reference geometry (.usdc) into payload file (.usda) which is payloaded into Asset file
 - Custom metadata with originating Maya file “exported_from”
 - variant switch to display high res mesh in viewport (with purposes option)
 - switch to "_geo" naming convention for mesh file in crate binary.
 - look file with overs for MaterialX references
 - Support for complex hierarchy under under geo scope (or under render purpose if option selected) 
 - Relative texture file paths for MaterialX docs
 - Export bound MaterialX documents to file (creates in "mat" directory inside save folder)
 - Inherit from class primitive
 - meters to units in metadata (default centimeters)
 - fix mesh name clashes by renaming with unique names.
 - convert .mtlx doc into native USD MaterialX
 - support for native USD MaterialX displacement and mix shaders
 
 v6.2 Export payloaded USD asset with MaterialX reference as native USD.
 (c) Derek Flood, 2025

 call with: 
df_USD_geoExport_UI.mel
(see that file for details)

python calls:
import dfUSD_CreateAsset
dfUSD_CreateAsset.payload_stage(fileName)
dfUSD_CreateAsset.asset_stage(fileName, render_value, proxy_value)

testing:
from importlib import reload
from MayaToUsdMtlX import df_USD_geoExport
reload(df_USD_geoExport)

 
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
import maya.mel as mel
import os
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Kind, Vt
import ufe
import re
from pathlib import Path
import xml.etree.ElementTree as ET
import shutil

from MayaToUsdMtlX import df_mtlx2usd as MtlxToUsd
from importlib import reload
reload(MtlxToUsd)




def make_unique_name(name, existing_names):
    """Generate a unique name by appending a number if necessary."""
    unique_name = name
    suffix = 1
    while unique_name in existing_names:
        unique_name = f"{name}_{suffix}"
        suffix += 1
    return unique_name

def ensure_unique_mesh_names():
    # Get the selected hierarchy root
    selected_roots = mc.ls(selection=True, long=True)
    if not selected_roots:
        mc.warning("No hierarchy selected.")
        return
    
    # Dictionary to track unique names
    existing_names = set()
    
    for root in selected_roots:
        # Get all child transforms of the selected hierarchy
        mesh_transforms = mc.listRelatives(root, allDescendents=True, type='transform', fullPath=True)
        if not mesh_transforms:
            continue

        # Include the root itself in the list of transforms if it's a transform
        if mc.objectType(root) == 'transform':
            mesh_transforms.append(root)

        for transform in mesh_transforms:
            # Check if the transform has a mesh shape
            children = mc.listRelatives(transform, children=True, shapes=True, fullPath=True)
            if not children or not any(mc.objectType(child) == 'mesh' for child in children):
                continue
            
            # Get the short name of the transform
            short_name = transform.split('|')[-1]
            
            # Check if the name already exists
            if short_name in existing_names:
                # Generate a unique name
                unique_name = make_unique_name(short_name, existing_names)
                # Rename the transform
                mc.rename(transform, unique_name)
                print(f"Renamed {transform} to {unique_name}")
            else:
                unique_name = short_name
            
            # Add the name to the set of existing names
            existing_names.add(unique_name)



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



def convert_texture_paths_to_relative(mtlx_file_path):
    """Convert absolute texture file paths to relative paths in a MaterialX document."""
    try:
        # Parse the MaterialX document from the file
        tree = ET.parse(mtlx_file_path)
        root = tree.getroot()
        
        # Get the directory of the .mtlx file
        mtlx_directory = os.path.dirname(mtlx_file_path)
        mtlx_filename = os.path.basename(mtlx_file_path)
        
        '''
        # Function to convert absolute paths to relative paths
        def make_relative_path(path):
            if os.path.isabs(path):
                return os.path.relpath(path, mtlx_directory)
            return path
        '''   
        # Function to convert absolute paths to relative paths
        def make_relative_path(path):
            if os.path.isabs(path):
                # Ensure forward slashes in the file path
                path = path.replace('\\', '/')
                return os.path.relpath(path, mtlx_directory).replace('\\', '/')
            return path.replace('\\', '/')
        
        
        # Traverse the XML tree to find all texture file paths
        for elem in root.iter():
            if elem.tag == 'input' and elem.get('type') == 'filename':
                original_path = elem.get('value')
                
                # Check if the path is already relative
                if not os.path.isabs(original_path):
                    continue
                
                # Convert to relative path
                relative_path = make_relative_path(original_path)
                
                elem.set('value', relative_path)
        
        # Write the updated MaterialX document back to the file
        tree.write(mtlx_file_path, xml_declaration=True, encoding='utf-8')
        #print(f" # Updated MaterialX document with relative texture paths for: {mtlx_file_path}")
    
    except Exception as e:
        print(f"An error occurred with relative texture paths for {mtlx_filename}: {e}")



def localize_texture_paths(mtlx_file_path):
    """
    Find absolute texture file paths, copy these files to ../textures/, 
    and update the paths in the MaterialX document.
    """

    try:
        # Parse the MaterialX document from the file
        tree = ET.parse(mtlx_file_path)
        root = tree.getroot()
        
        # Get the directory of the .mtlx file
        mtlx_directory = os.path.dirname(mtlx_file_path)
        textures_directory = os.path.abspath(os.path.join(mtlx_directory, '..', 'textures'))
        
        # Create the textures directory if it does not exist
        if not os.path.exists(textures_directory):
            os.makedirs(textures_directory)
        
        # Function to convert absolute paths to relative paths
        def make_relative_path(path):
            if os.path.isabs(path):
                # Ensure forward slashes in the file path
                path = path.replace('\\', '/')
                return os.path.relpath(path, mtlx_directory).replace('\\', '/')
            return path.replace('\\', '/')
        
        # Traverse the XML tree to find all texture file paths
        for elem in root.iter():
            if elem.tag == 'input' and elem.get('type') == 'filename':
                original_path = elem.get('value')
                
                # Check if the path is already relative
                if not os.path.isabs(original_path):
                    continue
                
                # Copy the texture file to the textures directory
                texture_filename = os.path.basename(original_path)
                new_texture_path = os.path.join(textures_directory, texture_filename)
                shutil.copy2(original_path, new_texture_path)
                
                # Convert to relative path
                relative_path = make_relative_path(new_texture_path)
                
                elem.set('value', relative_path)
        
        # Write the updated MaterialX document back to the file
        tree.write(mtlx_file_path, xml_declaration=True, encoding='utf-8')
        #print(f" # Updated MaterialX document with new texture paths for: {mtlx_file_path}")
    
    except Exception as e:
        print(f"An error occurred while updating texture paths for {mtlx_file_path}: {e}")
        
        


def get_all_mesh_shapes(render_purp):
    # Function to get all mesh shapes under the given transform
    shapes = mc.listRelatives(render_purp, ad=True, type='mesh', fullPath=True)
    return shapes if shapes else []    

def get_full_path_dict():
    """
    Helper function to get a dictionary of full paths from the Maya hierarchy.
    """
    full_path_dict = {}
    # Get all meshes in the scene with their full paths
    all_meshes = mc.ls(type='mesh', long=True)
    for mesh in all_meshes:
        short_name = mesh.split('|')[-1]
        full_path_dict[short_name] = mesh
    return full_path_dict

def get_relative_path(meshName, render_purp):
    # Get the full path of the mesh
    full_path = mc.ls(meshName, long=True)
    if not full_path:
        raise ValueError(f"Unable to get full path for mesh: {meshName}")
    full_path = full_path[0]
    
    # Get the relative path by removing the render_purp and meshName from the full path
    relative_path = full_path.split(render_purp)[-1]
    relative_path = relative_path.replace(f'|{meshName}', '').strip('|')
    return relative_path






def export_materialX_usd(mtlx_absolute_path, mtlx_docPath, relativePathsEnabled, localizeTexEnabled, nativeUSDEnabled, mtlx_name):

    # Normalize the mtlx_absolute_path to ensure compatibility across different operating systems
    mtlx_absolute_path = os.path.normpath(mtlx_absolute_path)

    # Add extensions
    mtlx_absolute_path_MX = mtlx_absolute_path + ".mtlx"
    mtlx_absolute_path_USD = mtlx_absolute_path + ".usda"
    
    
    nativeUSDEnabled = int(nativeUSDEnabled)
    
    if nativeUSDEnabled:

        try:
            

            # Export materialX doc 
            export_materialX_doc(mtlx_absolute_path_MX, mtlx_docPath)
            
            
            # convert texture paths to relative in mtlx docs.
            #relativePathsEnabled = int(relativePathsEnabled)
            
            if localizeTexEnabled:
                localize_texture_paths(mtlx_absolute_path_MX)
            elif relativePathsEnabled:
                convert_texture_paths_to_relative(mtlx_absolute_path_MX)

            # Convert MaterialX doc to native USD
            MtlxToUsd.materialx_to_usd(mtlx_absolute_path_MX, mtlx_absolute_path_USD, mtlx_name)
            #print(f"# Converting MaterialX doc {mtlx_name}.mtlx to native USD as {mtlx_name}.usda")
            
            # delete the .mtlx file
            os.unlink(mtlx_absolute_path_MX)
            
            
        except FileNotFoundError:
            print(f"Error: MaterialX file not found: {mtlx_absolute_path}")
        except Exception as e:
            print(f"An error occurred creating the native USD MaterialX for {mtlx_name}: {e}")
        
    else:
        export_materialX_doc(mtlx_absolute_path_MX, mtlx_docPath)
        
        # convert texture paths to relative in mtlx docs.
        #relativePathsEnabled = int(relativePathsEnabled)
        if localizeTexEnabled:
            localize_texture_paths(mtlx_absolute_path_MX)
        elif relativePathsEnabled:
            convert_texture_paths_to_relative(mtlx_absolute_path_MX)
            



def export_materialX_doc(mtlx_absolute_path, mtlx_docPath):

    # Normalize the mtlx_absolute_path to ensure compatibility across different operating systems
    #mtlx_absolute_path = os.path.normpath(mtlx_absolute_path)
    
    # Create UFE item and get Context Ops
    docItem = ufe.Hierarchy.createItem(ufe.PathString.path(mtlx_docPath))
    contextOps = ufe.ContextOps.contextOps(docItem)

    # Perform the Export Operation
    operation_result = contextOps.doOp(['MxExportDocument', mtlx_absolute_path])

    


            
def get_mesh_and_material_info(fileName, relativePathsEnabled, localizeTexEnabled, usePurposes, nativeUSDEnabled):
    # Get mesh and material information for all meshes under a given transform.

    usd_directory = os.path.dirname(os.path.abspath(fileName))
    mat_directory = os.path.join(usd_directory, "mat")
    os.makedirs(mat_directory, exist_ok=True)

    long_sel = mc.ls(sl=True, long=True)
    geoGrpPath = mc.listRelatives(long_sel, path=True, fullPath=True)
    
    if usePurposes:
        find_groups = mc.listRelatives(geoGrpPath, path=True, fullPath=True)
        found_render = find_groups[0]
    else:
        found_render = geoGrpPath[0]
    
    mesh_info = []
    error_messages = []
    
    mc.scriptEditorInfo(suppressWarnings=False, suppressInfo=True)

    # Get all mesh shapes under the transform recursively
    shapes = get_all_mesh_shapes(found_render)
    if not shapes:
        return mesh_info

    for shape in shapes:
        try:
            # Get the parent transform of the shape
            meshName = mc.listRelatives(shape, p=True, type='transform')[0]
            
            # Get the relative path of the shape
            relative_path = get_relative_path(meshName, found_render)

            # Get the material shading group connected to the shape
            Maya_SG = mc.listConnections(shape + '.instObjGroups', d=True, s=False)[0]

            # Get the material connected to the shading group
            mtlX_SG = mc.listConnections(Maya_SG + '.surfaceShader', d=False, s=True)[0]

            # Extract the ufePath attribute
            SG_ufePath = mc.getAttr(mtlX_SG + '.ufePath')

            # Extract the material name from the ufePath
            mtlx_docPath = re.sub(r"%[^%]*$", "", SG_ufePath)
            mtlx_name_match = re.search(r"%([^%]*)$", mtlx_docPath)
            if not mtlx_name_match:
                continue
            
            mtlx_name = mtlx_name_match.group(1)
            
            # Construct the absolute path for the MaterialX file sans extention
            mtlx_file = os.path.join("mat", f"{mtlx_name}")
            mtlx_absolute_path = os.path.join(usd_directory, mtlx_file)
            
            # Check if the MaterialX file exists on disk
            if not os.path.exists(mtlx_absolute_path):
                # Export MaterialX Document if it doesn't exist
                export_materialX_usd(mtlx_absolute_path, mtlx_docPath, relativePathsEnabled, localizeTexEnabled, nativeUSDEnabled, mtlx_name)

                
            # Append the meshName, relative path, full path of the MaterialX file, and material name to the list
            mesh_info.append((meshName, relative_path, mtlx_file, mtlx_name, mtlx_absolute_path, mtlX_SG))

        except Exception as e:
            print(f"Warning: The renderable mesh {meshName} is not assigned to a MaterialX material. Skipping in look file. ")
            continue
            
    mc.scriptEditorInfo(suppressWarnings=False, suppressInfo=True)
            

    return mesh_info



    
def get_proxy_mesh_and_material_info(proxy_value, fileName, relativePathsEnabled, nativeUSDEnabled):
    # Get mesh and material information for all proxy meshes under a given transform.

    usd_directory = os.path.dirname(os.path.abspath(fileName))
    mat_directory = os.path.join(usd_directory, "mat")
    os.makedirs(mat_directory, exist_ok=True)
    
    long_sel = mc.ls(sl=True, long=True)
    geoGrpPath = mc.listRelatives(long_sel, path=True, fullPath=True)
    find_groups = mc.listRelatives(geoGrpPath, path=True, fullPath=True)
    found_proxy = find_groups[1]
    
    proxy_info = []
    
    # Get all proxyShapes under the transform
    proxyShapes = mc.listRelatives(found_proxy, ad=True, type='mesh', fullPath=True)
    if not proxyShapes:
        return proxy_info

    for proxyShape in proxyShapes:
    
        try:
            # Get the parent transform of the proxyShape
            proxyMesh = mc.listRelatives(proxyShape, p=True, type='transform')[0]
        
            # Get the relative path of the shape
            px_relative_path = get_relative_path(proxyMesh, found_proxy)

            # Get the material shading group connected to the proxyShape
            pxMaya_SG = mc.listConnections(proxyShape + '.instObjGroups', d=True, s=False)[0]
        
            # Get the material connected to the shading group
            px_mtlX_SG = mc.listConnections(pxMaya_SG + '.surfaceShader', d=False, s=True)[0]

            # Extract the ufePath attribute
            px_SG_ufePath = mc.getAttr(px_mtlX_SG + '.ufePath')

            # Extract the material name from the ufePath
            px_mtlx_docPath = re.sub(r"%[^%]*$", "", px_SG_ufePath)
            px_mtlx_name_match = re.search(r"%([^%]*)$", px_mtlx_docPath)
            if not px_mtlx_name_match:
                continue
            px_mtlx_name = px_mtlx_name_match.group(1)
            
            # Construct the absolute path for the MaterialX file
            px_mtlx_file = os.path.join("mat", f"{px_mtlx_name}")
            px_mtlx_absolute_path = os.path.join(usd_directory, px_mtlx_file)
            
            # Check if the MaterialX file exists on disk
            if not os.path.exists(px_mtlx_absolute_path):
                # Export MaterialX Document if it doesn't exist
                export_materialX_usd(px_mtlx_absolute_path, px_mtlx_docPath, relativePathsEnabled, nativeUSDEnabled, px_mtlx_name)


            # Append the meshName, relative path, full path of the MaterialX file, and material name to the list
            proxy_info.append((proxyMesh, px_mtlx_file, px_mtlx_name, px_mtlx_absolute_path, px_mtlX_SG))
            
        except Exception as e:
            print(f"Warning: The proxy mesh {proxyMesh} is not assigned to a MaterialX material. Skipping in look file.")
            continue
            
    return proxy_info

def geom_stage(fileName, root_asset, render_value, proxy_value, usePurposes):

    stripExtension = os.path.splitext(fileName)[0]
    geom_name = stripExtension + '_geo'

    # Export the geo file
    mc.file(geom_name, options=";exportDisplayColor=1;exportColorSets=0;mergeTransformAndShape=1;exportComponentTags=0;defaultUSDFormat=usdc;materialsScopeName=mtl;exportMaterials=0;sar=0", typ="USD Export", pr=True, ch=True, chn=True, exportSelected=True, f=True)

    # Replace xforms with scopes for purpose groups
    stage = Usd.Stage.Open(geom_name + '.usd')
    prim_geo = stage.GetPrimAtPath(root_asset + "/geo")
    prim_geo.SetTypeName("Scope")
    
    # Extents Hint BBox (not working with unloaded payloads currently in Maya)
    bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ['default', 'render'])    
    root_geom_model_API = UsdGeom.ModelAPI.Apply(prim_geo)
    extentsHint = root_geom_model_API.ComputeExtentsHint(bbox_cache)
    root_geom_model_API.SetExtentsHint(extentsHint)
    
    if usePurposes:
        prim_render = stage.GetPrimAtPath(root_asset + "/geo/" + render_value)
        prim_render.SetTypeName("Scope")
        prim_proxy = stage.GetPrimAtPath(root_asset + "/geo/" + proxy_value)
        prim_proxy.SetTypeName("Scope")

    stage.Save()



def payload_stage(fileName, root_asset):
    stripExtension = os.path.splitext(fileName)[0]
    payload_file = stripExtension + '_payload.usda'
    look_file = stripExtension + '_look.usda'
    geom_file = stripExtension + '_geo.usd'

    # Create USD "payload" stage
    pay_layer = Sdf.Layer.CreateNew(payload_file, args={'format': 'usda'})
    stage: Usd.Stage = Usd.Stage.Open(pay_layer)
    
    # Set the stage metadata
    UsdGeom.SetStageMetersPerUnit(stage, UsdGeom.LinearUnits.centimeters)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)

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
    



def asset_stage(fileName, render_value, proxy_value, root_asset, dag_root, usePurposes):

    maya_scene = mc.file (q=True, sn=True, shn=True)
    stripExtension = os.path.splitext(fileName)[0]
    asset_file = stripExtension + '.usda'
    asset_baseName = os.path.basename(asset_file)
    asset_name = os.path.splitext(asset_baseName)[0]
    
    payName = stripExtension + '_payload.usda'
    payfile_root = "./" + os.path.basename(payName)

    # Create USD "asset" stage
    asset_layer = Sdf.Layer.CreateNew(asset_file, args = {'format':'usda'})
    stage: Usd.Stage = Usd.Stage.Open(asset_layer)
    
    
    # Add class primitive using CreateClassPrim
    class_prim_path = Sdf.Path("/__class__")
    class_prim = stage.CreateClassPrim(class_prim_path)
    
    # Add the default prim to the class
    default_class_prim_path = Sdf.Path("/__class__" + root_asset)
    stage.CreateClassPrim(default_class_prim_path)
    
    # Create class prim for asset
    asset_class_prim_path = class_prim_path.AppendChild(dag_root)
    asset_class_prim = stage.CreateClassPrim(asset_class_prim_path)
    
    # Create and define default prim
    default_prim = UsdGeom.Xform.Define(stage, Sdf.Path(root_asset))
    stage.SetDefaultPrim(default_prim.GetPrim())
    UsdGeom.SetStageMetersPerUnit(stage, UsdGeom.LinearUnits.centimeters)
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

    # Add inherits
    inherit_prim = default_prim.GetPrim()
    inherits_api = inherit_prim.GetInherits()
    inherits_api.AddInherit(asset_class_prim_path, position=Usd.ListPositionFrontOfPrependList)

    # Set kind to component 
    model_API = Usd.ModelAPI(payload_prim)
    model_API.SetKind(Kind.Tokens.component)
    
    # Extents Hint BBox (not working with unloaded payloads currently in Maya)
    bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ['default', 'render'])    
    root_geom_model_API = UsdGeom.ModelAPI.Apply(payload_prim)
    extentsHint = root_geom_model_API.ComputeExtentsHint(bbox_cache)
    root_geom_model_API.SetExtentsHint(extentsHint)
    
    
    if usePurposes:
        
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


def look_stage(fileName, root_asset, render_value, proxy_value, relativePathsEnabled, localizeTexEnabled, usePurposes, nativeUSDEnabled):

    nativeUSDEnabled = int(nativeUSDEnabled)
    
    # Strip the file extension from fileName and create new filename with '_look.usda'
    stripExtension = os.path.splitext(fileName)[0]
    look_file = stripExtension + '_look.usda'

    # Create USD "look" stage
    look_layer = Sdf.Layer.CreateNew(look_file, args={'format': 'usda'})
    stage = Usd.Stage.Open(look_layer)
    
    # default prim is over, not xform 
    default_prim = stage.OverridePrim(Sdf.Path(root_asset))
    stage.SetDefaultPrim(default_prim.GetPrim())
    #default_prim = UsdGeom.Xform.Define(stage, Sdf.Path(root_asset))
    #stage.SetDefaultPrim(default_prim.GetPrim())
    
    # Set stage metadata   
    UsdGeom.SetStageMetersPerUnit(stage, UsdGeom.LinearUnits.centimeters)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    
    # Make 'Materials' scope defined as a def and scope under the 'over' root asset
    materials_scope_path = f'{root_asset}/mtl'
    materials_scope = stage.OverridePrim(materials_scope_path)
    materials_scope.SetSpecifier(Sdf.SpecifierDef)
    materials_scope.GetPrim().SetTypeName('Scope')
    
    # Track created paths to avoid redundancies
    created_paths = set()

    # Get full path dictionary from Maya hierarchy
    full_path_dict = get_full_path_dict()

    # -------- Mesh --------------
    # Process all meshes and materials under the given render purpose
    mesh_material_info = get_mesh_and_material_info(fileName, relativePathsEnabled, localizeTexEnabled, usePurposes, nativeUSDEnabled)
    
    for meshName, relative_path, mtlx_file, mtlx_name, mtlx_absolute_path, mtlX_SG in mesh_material_info:
        
        # Get the full path from the dictionary
        full_path = full_path_dict.get(meshName, relative_path)
        
        # Check if native USD option is enabled for MaterialX
        if nativeUSDEnabled:
            # reference MaterialX as native USD .usda file
            default_prim.GetPrim().GetReferences().AddReference(f'./mat/{mtlx_name}.usda', '/ASSET_MaterialX')
    
        else:
            # reference MaterialX document as .mtlx file
            materials_scope.GetReferences().AddReference(f'./mat/{mtlx_name}.mtlx', '/MaterialX/Materials')

        
        # Split the full path by '|' and create a list of path parts
        path_parts = full_path.strip('|').split('|')
        
        # Initialize the current path with the root asset, 'geo', and the render value if usePurposes is True
        if usePurposes:
            current_path = f'{root_asset}/geo/{render_value}'
        else:
            current_path = f'{root_asset}/geo'

        # Iterate through each part in the path parts list to build the hierarchy
        if full_path:
            for part in path_parts:
                # Update the current path by appending the current part
                current_path = f'{current_path}/{part}'
                # Create the current path in the USD stage if it hasn't been created yet
                if current_path not in created_paths:
                    stage.OverridePrim(current_path)
                    created_paths.add(current_path)
        
        # Define the 'meshName' over under the constructed hierarchy
        mesh_name_path = f'{current_path}/{meshName}'
        
        if mesh_name_path not in created_paths:
            mesh_name_prim = stage.OverridePrim(mesh_name_path)
            mesh_name_prim.SetSpecifier(Sdf.SpecifierOver)
            
            # Apply the MaterialBindingAPI schema on the 'meshName' prim
            UsdShade.MaterialBindingAPI.Apply(mesh_name_prim)
            
            # Define the material binding relationship
            material_binding_rel = mesh_name_prim.CreateRelationship('material:binding', False)
            material_binding_rel.SetTargets([f'{root_asset}/mtl/{mtlX_SG}'])
            created_paths.add(mesh_name_path)
        else:
            # Diagnostic: Print a message if a duplicate mesh name is found
            print(f"Skipping duplicate mesh: {mesh_name_path}")
            
        
    
    # ----------- Proxy ----
    
    if usePurposes:
    
        # ----------- Proxy ----
        # Process all proxy meshes and materials under the given proxy_value
        proxy_material_info = get_proxy_mesh_and_material_info(proxy_value, fileName, relativePathsEnabled, nativeUSDEnabled)
        
        for proxyMesh, px_mtlx_file, px_mtlx_name, px_mtlx_absolute_path, px_mtlX_SG in proxy_material_info:

            try:
                # Get the full path from the dictionary
                full_path = full_path_dict.get(proxyMesh, proxyMesh)
                
                # Check if native USD option is enabled for MaterialX
                if nativeUSDEnabled:
                    # reference MaterialX as native USD .usda file
                    root_xform.GetPrim().GetReferences().AddReference(f'./mat/{px_mtlx_name}.usda', '/ASSET_MaterialX')
    
                else:
                    # reference MaterialX document as .mtlx file
                    materials_scope.GetReferences().AddReference(f'./mat/{px_mtlx_name}.mtlx', '/MaterialX/Materials')
            
                # Define the 'proxy' over under the root asset
                proxy_path = f'{root_asset}/geo/{proxy_value}'
                if proxy_path not in created_paths:
                    proxy_prim = stage.OverridePrim(proxy_path)
                    proxy_prim.SetSpecifier(Sdf.SpecifierOver)
                    created_paths.add(proxy_path)
            
                # Define the 'proxyMesh' over under the 'proxy' over
                mesh_proxy_path = f'{proxy_path}/{proxyMesh}'
                
                if mesh_proxy_path not in created_paths:
                    mesh_proxy_prim = stage.OverridePrim(mesh_proxy_path)
                    mesh_proxy_prim.SetSpecifier(Sdf.SpecifierOver)

                    # Apply the MaterialBindingAPI schema on the 'proxyMesh' prim
                    UsdShade.MaterialBindingAPI.Apply(mesh_proxy_prim)
                
                    # Define the material binding relationship
                    material_binding_rel = mesh_proxy_prim.CreateRelationship('material:binding', False)
                    material_binding_rel.SetTargets([f'{root_asset}/mtl/{px_mtlX_SG}'])
                    created_paths.add(mesh_proxy_path)
                else:
                    # Diagnostic: Print a message if a duplicate proxy mesh name is found
                    print(f"Skipping duplicate proxy mesh: {mesh_proxy_path}")
            except Exception as e:
                print(f"Warning: Skipping proxy mesh {proxyMesh} due to error: {e}")
                continue
            
    # Save the stage
    stage.GetRootLayer().Save()

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



def main(fileName, render_value, proxy_value, relativePathsEnabled, localizeTexEnabled, nativeUSDEnabled, usePurposes):
    sel=mc.ls(sl=True)
    dag_root = sel[0].replace("|", "")
    root_asset = "/" + dag_root
    relativePathsEnabled = int(relativePathsEnabled)
    localizeTexEnabled = int(localizeTexEnabled)
    nativeUSDEnabled = int(nativeUSDEnabled)
    usePurposes = int(usePurposes)
    
    
    # Run the function to ensure unique names
    ensure_unique_mesh_names()
    arnold_subdiv()
    geom_stage(fileName, root_asset, render_value, proxy_value, usePurposes)
    look_stage(fileName, root_asset, render_value, proxy_value, relativePathsEnabled, localizeTexEnabled, usePurposes, nativeUSDEnabled)

    payload_stage(fileName, root_asset)
    asset_stage(fileName, render_value, proxy_value, root_asset, dag_root, usePurposes)


if __name__ == "__main__":
    main()

