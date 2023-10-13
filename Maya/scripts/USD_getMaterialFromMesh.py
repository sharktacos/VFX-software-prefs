"""
USD Get material from Mesh
Roy Nieterau 
https://gist.github.com/BigRoy/758279a185e4b57b266b2dddca1918de
"""

from maya import cmds
import mayaUsd.ufe
from pxr import Usd, UsdShade


def pairwise(iterable):
    it = iter(iterable)
    return zip(it, it)


def iter_ufe_usd_selection():
    for path in cmds.ls(selection=True, 
                        ufeObjects=True, 
                        long=True,
                        absoluteName=True):
        if "," not in path:
            continue

        node, ufe_path = path.split(",", 1)
        if cmds.nodeType(node) != "mayaUsdProxyShape":
            continue

        yield path
        

def get_ufe_path(proxy, prim):
    prim_path = str(prim.GetPath())
    return "{},{}".format(proxy, prim_path)
    
        
def convert_ufe_paths_to_bound_materials(
    ufe_paths=None,
    material_purpose=UsdShade.Tokens.allPurpose,
    include_subsets=False
):
    """Convert selection or ufe node paths to bound materials
    
    Arguments:
        ufe_paths (Optional[list]): UFE paths to operate on.
            If not provided current selection will be used.
        material_purpose (UsdShade.Token): Material purpose 
            to return bounds for. Defaults to all purposes.
        include_subsets (bool): Whether to include bound
            materials from material bind subsets.
    
    Returns:
        list: UsdShadeMaterial UFE paths.
            
    """
    
    if ufe_paths is None:
        ufe_paths = list(iter_ufe_usd_selection())

    targets = []
    for path in ufe_paths:
        proxy, prim_path = path.split(",", 1)
        prim = mayaUsd.ufe.ufePathToPrim(path)
        if not prim:
            continue
        
        search_from = [prim]
        if include_subsets:
            subsets = UsdShade.MaterialBindingAPI(prim).GetMaterialBindSubsets()
            for subset in subsets:
                search_from.append(subset.GetPrim())
            
        bounds = UsdShade.MaterialBindingAPI.ComputeBoundMaterials(search_from, material_purpose)
        for (material, relationship) in zip(*bounds):
            material_prim = material.GetPrim()
            if material_prim.IsValid():
                material_prim_ufe_path = get_ufe_path(proxy, material_prim)
                targets.append(material_prim_ufe_path)
        
    return targets
        

targets = convert_ufe_paths_to_bound_materials(include_subsets=True)
if targets:
    cmds.select(targets, replace=True, noExpand=True)