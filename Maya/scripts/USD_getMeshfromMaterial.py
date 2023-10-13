"""
USD Get mesh from material
https://gist.github.com/BigRoy/d3f982819176291dd5ec1a88898c3313
Roy Nieterau 

"""

from maya import cmds
import mayaUsd.ufe
from pxr import Usd, UsdShade
from collections import defaultdict


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
    
        
def convert_ufe_paths_to_bound_geo(
    ufe_paths=None,
    material_purpose=UsdShade.Tokens.allPurpose
):
    """Convert USD material selection or ufe material node paths to bound objects.
    
    Arguments:
        ufe_paths (Optional[list]): UFE material paths to operate on.
            If not provided current selection will be used.
        material_purpose (UsdShade.Token): Material purpose 
            to return bounds for. Defaults to all purposes.
    
    Returns:
        list: UsdShadeMaterial UFE paths.
            
    """
    
    if ufe_paths is None:
        ufe_paths = list(iter_ufe_usd_selection())
    
    targets = []
    prims_per_proxy = defaultdict(set)
    for path in ufe_paths:
        prim = mayaUsd.ufe.ufePathToPrim(path)
        if not prim:
            continue
        
        proxy, _prim_path = path.split(",", 1)
        prims_per_proxy[proxy].add(prim)
        
    bindings = defaultdict(set)
    for proxy, prims in prims_per_proxy.items():
        
        stage = next(iter(prims)).GetStage()
        stage_prims = list(stage.Traverse())
        bounds = UsdShade.MaterialBindingAPI.ComputeBoundMaterials(stage_prims, material_purpose)
        for stage_prim, material, relationship in zip(stage_prims, *bounds):
            material_prim = material.GetPrim()
            if not material_prim.IsValid():
                continue
                
            bindings[material_prim].add(stage_prim)
            
        for prim in prims:
            for geo_prim in bindings.get(prim, []):
                ufe_path = get_ufe_path(proxy, geo_prim)
                targets.append(ufe_path)
    
    return targets
    

targets = convert_ufe_paths_to_bound_geo()
if targets:
    cmds.select(targets, replace=True, noExpand=True)