#--------------------------------------------------------------------------------
# Export Material to USD - materials and bindings sans geometry

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
#--------------------------------------------------------------------------------

import maya.cmds as mc
import os
from pxr import Usd, UsdGeom, Sdf


sel=mc.ls(sl=True, tr=True)
if sel:

    # File export dialog...
    usdfilter = "USD Export (*.usd *.usda *.usdc)"
    filepath = mc.fileDialog2(fileFilter=usdfilter, caption="Export Selected to USD with materials and bindings", dialogStyle=2)
    
    # Variables
    USDlayer = filepath[0]
    stripExtension = os.path.splitext(USDlayer)[0]
    mtl_file = stripExtension + '.usda'
    maya_scene = mc.file (q=True, sn=True, shn=True)
    
    # Export selected geo & mtl to USD...
    mc.file(mtl_file, options=";exportDisplayColor=1;exportColorSets=0;mergeTransformAndShape=1;exportComponentTags=0;defaultUSDFormat=usda;jobContext=[Arnold];materialsScopeName=mtl", typ="USD Export", pr=True, exportSelected=True, f=True)


    # From Jason Coelho's post on Maya-USD Github: https://github.com/Autodesk/maya-usd/discussions/3197
    #----------------------------------------------------------------------------------------------------
    
    # Load in stage from file
    layer_to_edit = mtl_file
    stage = Usd.Stage.Open(layer_to_edit)
    stage_layer = stage.GetRootLayer()

    # Traverse the stage and remove any properties that are not related to the Materials and Shaders
    for prim in stage.TraverseAll():

        # Ignore Arnold options Prim, I'm assuming you are using Arnold
        if prim.GetTypeName() == 'ArnoldOptions':
            continue

        if prim.GetTypeName() not in ['Material', 'Shader']:
            for prim_property in prim.GetAuthoredProperties():
                if prim_property.GetName() not in ['material:binding', 'primvars:displayColor']:
                    if prim.GetTypeName() == 'GeomSubset':
                        pass

                    else:
                        prim.RemoveProperty(prim_property.GetName())

        if prim.GetTypeName() == 'ArnoldOptions':
            prim.RemoveProperty()

    # add metadata with Maya scene used to generate asset
    prim_path = Sdf.Path(root_asset)
    meta_prim = stage.DefinePrim(prim_path, "Xform")
    meta_prim.SetMetadata("customData", {"Export_from": maya_scene})

    stage_layer.Save()


else:
    mc.confirmDialog(t="Oops! Nothing Selected", message='Oops! Nothing Selected. Select the asset to export in the Outliner.', icon="warning")
