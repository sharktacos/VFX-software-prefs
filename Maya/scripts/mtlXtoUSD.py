import os
from pxr import Usd, UsdShade, Sdf
import maya.cmds as mc

def convert_mtlx_to_usd(mtlx_doc, usd_file_path):
    # Create a new USD stage
    stage = Usd.Stage.CreateNew(usd_file_path)
    
    # Parse the MaterialX document
    materials = mc.ls(type='materialXNode')
    
    for material in materials:
        material_name = mc.getAttr(f"{material}.name")
        material_path = f"/Materials/{material_name}"
        
        # Define the Material in USD
        usd_material = UsdShade.Material.Define(stage, material_path)
        
        # Iterate over all shader nodes in the MaterialX document
        shaders = mc.listConnections(material, type='MaterialXShaderNode')
        if shaders:
            for shader in shaders:
                shader_name = mc.getAttr(f"{shader}.name")
                shader_path = f"{material_path}/{shader_name}"
                
                # Define the Shader in USD
                usd_shader = UsdShade.Shader.Define(stage, shader_path)
                node_type = mc.nodeType(shader)
                usd_shader.CreateIdAttr(f"MaterialX/{node_type}")
                
                # Iterate over all inputs of the shader node
                inputs = mc.listAttr(shader, k=True)
                for input in inputs:
                    input_value = mc.getAttr(f"{shader}.{input}")
                    input_type = mc.getAttr(f"{shader}.{input}", type=True)
                    
                    # Map Maya type to USD type
                    usd_type = Sdf.ValueTypeNames.String
                    if input_type == "float":
                        usd_type = Sdf.ValueTypeNames.Float
                    elif input_type == "float3":
                        usd_type = Sdf.ValueTypeNames.Color3f
                    elif input_type == "double3":
                        usd_type = Sdf.ValueTypeNames.Float3
                    elif input_type == "double2":
                        usd_type = Sdf.ValueTypeNames.Float2
                    elif input_type == "string":
                        usd_type = Sdf.ValueTypeNames.Asset
                    # Add more type mappings as needed
                    
                    # Create the input attribute in USD
                    usd_shader.CreateInput(input, usd_type).Set(input_value)
                
                # Bind the shader to the material
                usd_material.CreateSurfaceOutput().ConnectToSource(usd_shader.ConnectableAPI(), "out")
    
    # Iterate over all nodegraphs in the MaterialX document
    nodegraphs = mc.ls(type='materialXNodeGraph')
    for nodegraph in nodegraphs:
        nodegraph_name = mc.getAttr(f"{nodegraph}.name")
        nodegraph_path = f"/NodeGraphs/{nodegraph_name}"
        
        # Define the NodeGraph in USD
        usd_nodegraph = UsdShade.NodeGraph.Define(stage, nodegraph_path)
        
        # Iterate over all nodes in the nodegraph
        nodes = mc.listConnections(nodegraph, type='MaterialXShaderNode')
        if nodes:
            for node in nodes:
                node_name = mc.getAttr(f"{node}.name")
                node_path = f"{nodegraph_path}/{node_name}"
                
                # Define the Node in USD
                usd_node = UsdShade.Shader.Define(stage, node_path)
                node_type = mc.nodeType(node)
                usd_node.CreateIdAttr(f"MaterialX/{node_type}")
                
                # Iterate over all inputs of the node
                inputs = mc.listAttr(node, k=True)
                for input in inputs:
                    input_value = mc.getAttr(f"{node}.{input}")
                    input_type = mc.getAttr(f"{node}.{input}", type=True)
                    
                    # Map Maya type to USD type
                    usd_type = Sdf.ValueTypeNames.String
                    if input_type == "float":
                        usd_type = Sdf.ValueTypeNames.Float
                    elif input_type == "float3":
                        usd_type = Sdf.ValueTypeNames.Color3f
                    elif input_type == "double3":
                        usd_type = Sdf.ValueTypeNames.Float3
                    elif input_type == "double2":
                        usd_type = Sdf.ValueTypeNames.Float2
                    elif input_type == "string":
                        usd_type = Sdf.ValueTypeNames.Asset
                    # Add more type mappings as needed
                    
                    # Create the input attribute in USD
                    usd_node.CreateInput(input, usd_type).Set(input_value)
                
                # Iterate over all outputs of the node
                outputs = mc.listAttr(node, m=True)
                for output in outputs:
                    output_type = mc.getAttr(f"{node}.{output}", type=True)
                    
                    # Map Maya type to USD type
                    usd_type = Sdf.ValueTypeNames.String
                    if output_type == "float":
                        usd_type = Sdf.ValueTypeNames.Float
                    elif output_type == "float3":
                        usd_type = Sdf.ValueTypeNames.Color3f
                    elif output_type == "double3":
                        usd_type = Sdf.ValueTypeNames.Float3
                    elif output_type == "double2":
                        usd_type = Sdf.ValueTypeNames.Float2
                    # Add more type mappings as needed
                    
                    # Create the output attribute in USD
                    usd_node.CreateOutput(output, usd_type)
    
    # Save the USD stage
    stage.GetRootLayer().Save()

def export_materialx_to_usd(materialx_stack_name, output_file_path):
    # Get the MaterialX document from the stack in Maya
    materialx_doc = mc.getAttr(f"{materialx_stack_name}.materialXDocument")

    if not materialx_doc:
        raise ValueError(f"No MaterialX document found on stack {materialx_stack_name}")

    # Convert the MaterialX document to USD and save it on disk
    convert_mtlx_to_usd(materialx_doc, output_file_path)

# Example usage:
materialx_stack = "materialXStack1"  # Replace with the name of your MaterialX stack in Maya
output_usda_path = "C:/path/to/output_materialx.usda"  # Replace with your desired output file path

export_materialx_to_usd(materialx_stack, output_usda_path)




########################

import os
import MaterialX as mx
from pxr import Usd, UsdShade, Sdf, Gf

def convert_mtlx_to_usd(mtlx_file_path, usd_file_path):
    # Load the MaterialX document
    doc = mx.createDocument()
    mx.readFromXmlFile(doc, mtlx_file_path)

    # Create a new USD stage
    stage = Usd.Stage.CreateNew(usd_file_path)
    
    # Iterate over all materials in the MaterialX document
    for material in doc.getMaterials():
        material_name = material.getName()
        material_path = f"/Materials/{material_name}"
        
        # Define the Material in USD
        usd_material = UsdShade.Material.Define(stage, material_path)
        
        # Iterate over all shader nodes in the MaterialX document
        for shader_ref in material.getShaderRefs():
            shader_name = shader_ref.getName()
            shader_path = f"{material_path}/{shader_name}"
            
            # Define the Shader in USD
            usd_shader = UsdShade.Shader.Define(stage, shader_path)
            usd_shader.CreateIdAttr(f"MaterialX/{shader_ref.getNodeString()}")
            
            # Iterate over all inputs of the shader node
            for input in shader_ref.getInputs():
                input_name = input.getName()
                input_value = input.getValue()
                input_type = input.getType()
                
                # Map MaterialX type to USD type
                usd_type = Sdf.ValueTypeNames.String
                if input_type == "float":
                    usd_type = Sdf.ValueTypeNames.Float
                elif input_type == "color3":
                    usd_type = Sdf.ValueTypeNames.Color3f
                elif input_type == "vector3":
                    usd_type = Sdf.ValueTypeNames.Float3
                elif input_type == "vector2":
                    usd_type = Sdf.ValueTypeNames.Float2
                elif input_type == "filename":
                    usd_type = Sdf.ValueTypeNames.Asset
                # Add more type mappings as needed
                
                # Create the input attribute in USD
                usd_shader.CreateInput(input_name, usd_type).Set(input_value)
            
            # Bind the shader to the material
            usd_material.CreateSurfaceOutput().ConnectToSource(usd_shader.ConnectableAPI(), "out")

    # Iterate over all nodegraphs in the MaterialX document
    for nodegraph in doc.getNodeGraphs():
        nodegraph_name = nodegraph.getName()
        nodegraph_path = f"/NodeGraphs/{nodegraph_name}"
        
        # Define the NodeGraph in USD
        usd_nodegraph = UsdShade.NodeGraph.Define(stage, nodegraph_path)
        
        # Iterate over all nodes in the nodegraph
        for node in nodegraph.getNodes():
            node_name = node.getName()
            node_path = f"{nodegraph_path}/{node_name}"
            
            # Define the Node in USD
            usd_node = UsdShade.Shader.Define(stage, node_path)
            usd_node.CreateIdAttr(f"MaterialX/{node.getCategory()}")
            
            # Iterate over all inputs of the node
            for input in node.getInputs():
                input_name = input.getName()
                input_value = input.getValue()
                input_type = input.getType()
                
                # Map MaterialX type to USD type
                usd_type = Sdf.ValueTypeNames.String
                if input_type == "float":
                    usd_type = Sdf.ValueTypeNames.Float
                elif input_type == "color3":
                    usd_type = Sdf.ValueTypeNames.Color3f
                elif input_type == "vector3":
                    usd_type = Sdf.ValueTypeNames.Float3
                elif input_type == "vector2":
                    usd_type = Sdf.ValueTypeNames.Float2
                elif input_type == "filename":
                    usd_type = Sdf.ValueTypeNames.Asset
                # Add more type mappings as needed
                
                # Create the input attribute in USD
                usd_node.CreateInput(input_name, usd_type).Set(input_value)
            
            # Iterate over all outputs of the node
            for output in node.getOutputs():
                output_name = output.getName()
                output_type = output.getType()
                
                # Map MaterialX type to USD type
                usd_type = Sdf.ValueTypeNames.String
                if output_type == "float":
                    usd_type = Sdf.ValueTypeNames.Float
                elif output_type == "color3":
                    usd_type = Sdf.ValueTypeNames.Color3f
                elif output_type == "vector3":
                    usd_type = Sdf.ValueTypeNames.Float3
                elif output_type == "vector2":
                    usd_type = Sdf.ValueTypeNames.Float2
                # Add more type mappings as needed
                
                # Create the output attribute in USD
                usd_node.CreateOutput(output_name, usd_type)
    
    # Save the USD stage
    stage.GetRootLayer().Save()

# Example usage
mtlx_file_path = "path/to/your/material.mtlx"
usd_file_path = "path/to/your/material.usda"
convert_mtlx_to_usd(mtlx_file_path, usd_file_path)

#############

import os
import maya.cmds as cmds
from pxr import Usd, UsdShade, Sdf, MaterialX

def materialx_to_usd(materialx_doc, output_path):
    # Create a new USD stage
    stage = Usd.Stage.CreateNew(output_path)

    # Create a MaterialX context
    mtlx = MaterialX.createDocument()

    # Load the MaterialX document
    MaterialX.readFromXmlString(mtlx, materialx_doc)

    # Iterate through the nodes in the MaterialX document
    for node in mtlx.getNodes():
        # Create a USD Shader for each node
        shader_path = Sdf.Path(f"/{node.getName()}")
        shader = UsdShade.Shader.Define(stage, shader_path)
        shader.SetSourceCode(MaterialX.writeToXmlString(node), UsdShade.Tokens.universalSourceType)

        # Set the shader ID
        shader.SetShaderId(node.getCategory())

    # Save the USD stage
    stage.GetRootLayer().Save()

    print(f"MaterialX document has been converted to USD and saved to {output_path}")

def export_materialx_to_usd(materialx_stack_name, output_file_path):
    # Get the MaterialX document from the stack in Maya
    materialx_doc = cmds.getAttr(f"{materialx_stack_name}.materialXDocument")

    if not materialx_doc:
        raise ValueError(f"No MaterialX document found on stack {materialx_stack_name}")

    # Convert the MaterialX document to USD and save it on disk
    materialx_to_usd(materialx_doc, output_file_path)

# Example usage:
materialx_stack = "materialXStack1"  # Replace with the name of your MaterialX stack in Maya
output_usda_path = "C:/path/to/output_materialx.usda"  # Replace with your desired output file path

export_materialx_to_usd(materialx_stack, output_usda_path)