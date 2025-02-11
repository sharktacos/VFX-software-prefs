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