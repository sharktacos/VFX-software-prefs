from pxr import Usd, UsdShade, Sdf, Gf, Tf
import xml.etree.ElementTree as ET
import os



def _set_usd_input_connection(usd_shader, usd_type, mtlx_input_name, mtlx_output, nodegraph_shader):
    """Sets USD input connection."""

    vec_type=None

    if usd_type == "color3f":
        usd_type_name = Sdf.ValueTypeNames.Color3f
        vec_type = Gf.Vec3f
    elif usd_type == "vector3f":
        usd_type_name = Sdf.ValueTypeNames.Vector3f  # Vector3f
        vec_type = Gf.Vec3f
    elif usd_type == "float":
        usd_type = usd_type.capitalize()
        usd_type_name = getattr(Sdf.ValueTypeNames, usd_type)
        vec_type = None  # No vector type for float
    elif usd_type == "filename":
        usd_type_name = Sdf.ValueTypeNames.String
        vec_type = None
    else:
        print(f"Warning: Setting value for unsupported type: {usd_type}")
        return  # Important: Exit early if type is unsupported
    
    outPort = nodegraph_shader.CreateOutput(mtlx_output, usd_type_name)
    surfaceTerminal = usd_shader.CreateOutput(mtlx_input_name, usd_type_name)
    surfaceTerminal.ConnectToSource(outPort)
    
    
def _set_usd_filepaths(usd_shader, usd_type, mtlx_input_name, filepath, nodegraph_shader):
    """Sets USD input connection."""

    vec_type=None

    if usd_type == "color3f":
        usd_type_name = Sdf.ValueTypeNames.Color3f
        vec_type = Gf.Vec3f
    elif usd_type == "vector3f":
        usd_type_name = Sdf.ValueTypeNames.Vector3f  # Vector3f
        vec_type = Gf.Vec3f
    elif usd_type == "float":
        usd_type = usd_type.capitalize()
        usd_type_name = getattr(Sdf.ValueTypeNames, usd_type)
        vec_type = None  # No vector type for float
    elif usd_type == "filename":
        usd_type_name = Sdf.ValueTypeNames.String
        vec_type = None
    else:
        print(f"Warning: Setting value for unsupported type: {usd_type}")
        return  # Important: Exit early if type is unsupported

    #outPort = nodegraph_shader.CreateOutput(filepath, usd_type_name)
    #surfaceTerminal = usd_shader.CreateOutput(mtlx_input_name, usd_type_name)
    #surfaceTerminal.ConnectToSource(outPort)
    diffuseTextureSampler = UsdShade.Shader.Define(stage,'/TexModel/boardMat/diffuseTexture')

    diffuseTextureSampler.CreateInput('file', Sdf.ValueTypeNames.Asset).Set("USDLogoLrg.png")
    
    diffuseTextureSampler.CreateOutput('rgb', Sdf.ValueTypeNames.Float3)
    pbrShader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(diffuseTextureSampler.ConnectableAPI(), 'rgb')
    
    connectable_api = UsdShade.ConnectableAPI(usd_node_shader) #Get the connectable API                     
    connectable_api.CreateInput(input_name, usd_type).Set(input_value) #Create the input and set the value
                            

    
def _set_usd_input_value(usd_shader, usd_type, mtlx_value, mtlx_input_name):
    """Sets USD input value (called ONLY for value inputs)."""
    input_name_token = Sdf.Path.TokenizeIdentifier(mtlx_input_name)[0]
    vec_type=None

    if usd_type == "color3f":
        usd_type_name = Sdf.ValueTypeNames.Color3f
        vec_type = Gf.Vec3f
    elif usd_type == "vector3f":
        usd_type_name = Sdf.ValueTypeNames.Vector3f  # Vector3f
        vec_type = Gf.Vec3f
    elif usd_type == "float":
        usd_type = usd_type.capitalize()
        usd_type_name = getattr(Sdf.ValueTypeNames, usd_type)
        vec_type = None  # No vector type for float
    elif usd_type == "filename":
        usd_type_name = Sdf.ValueTypeNames.String
        vec_type = None
    else:
        print(f"Warning: Setting value for unsupported type: {usd_type}")
        return  # Important: Exit early if type is unsupported
   
    input_name_token = Sdf.Path.TokenizeIdentifier(mtlx_input_name)[0]
    internal_port = usd_shader.CreateInput(input_name_token, usd_type_name)
    exposed_port = usd_shader.CreateInput(input_name_token, usd_type_name)

    if mtlx_value is not None:  # Only set value if it exists
        try:
            if vec_type:  # Handle vector/color types
                parts = [float(x.strip()) for x in mtlx_value.split(",")]
                exposed_port.Set(vec_type(parts[0], parts[1], parts[2]))
            elif usd_type_name == Sdf.ValueTypeNames.Float:
                exposed_port.Set(float(mtlx_value))
            elif usd_type_name == Sdf.ValueTypeNames.Int:
                exposed_port.Set(int(mtlx_value))
            elif usd_type_name == Sdf.ValueTypeNames.String:
                exposed_port.Set(mtlx_value)
            # Add handling for other types as needed
        except ValueError:
            print(f"Error: Could not convert {mtlx_value} to {usd_type_name}")

def _map_mtlx_type_to_usd(mtlx_type):
    """Maps MaterialX types to USD types."""
    if mtlx_type == "color3":
        return "color3f"  # Or "color"
    elif mtlx_type == "float":
        return "float"
    elif mtlx_type == "vector3":
        return "vector3f"
    elif mtlx_type == "filename":
        return "string"  # File paths are strings in USD
    # Add more mappings as needed...
    else:
        print(f"Warning: Unsupported MaterialX type: {mtlx_type}")
        return None



    


    
def materialx_to_usd(mtlx_filepath, usd_filepath, material_name, asset_name):
    """Translates a MaterialX file to a USD file."""

    try:
        tree = ET.parse(mtlx_filepath)
        root = tree.getroot()
    except FileNotFoundError:
        print(f"Error: MaterialX file not found: {mtlx_filepath}")
        return
    except ET.ParseError as e:
        print(f"Error parsing MaterialX file: {e}")
        return

    stage = Usd.Stage.CreateNew(usd_filepath)  # File path for the USD file

    # Set the stage metadata
    stage.SetMetadata("defaultPrim", asset_name)
    stage.SetMetadata('metersPerUnit', 0.01)
    stage.SetMetadata('upAxis', 'Y')

    
    # Create Over for the root asset
    root_asset = "/ASSET_MaterialX"
    

    # Make 'Materials' scope defined as a def and scope under the 'over' root asset
    materials_scope_path = f'{root_asset}/mtl'
    materials_scope = stage.OverridePrim(materials_scope_path)
    materials_scope.SetSpecifier(Sdf.SpecifierDef)
    materials_scope.GetPrim().SetTypeName('Scope')
    
    material_path = f"{materials_scope_path}/{material_name}"  # Prim path *inside* the USD stage
    mat = UsdShade.Material.Define(stage, material_path)  
    
    # 1. Surface Material
    surface_material_elem = root.find("./surfacematerial")
    if surface_material_elem is not None:
        
        # 2. Standard Surface Shader (Corrected and Simplified):
        standard_surface_elem = root.find("./standard_surface")  # <--- Direct access
        if standard_surface_elem is None:
            raise ValueError("No <standard_surface> element found at the root level.")

        surface_shader_name = standard_surface_elem.get("name") #Get the name of the standard surface
        shader_path = f"{material_path}/{surface_shader_name}"  # Prim path *under* the material
        #usd_shader = create_materialx_shader(stage, material_path, standard_surface_elem)  # Call for shader ONLY
        usd_shader = UsdShade.Shader.Define(stage, shader_path)
        usd_shader.SetShaderId("ND_standard_surface_surfaceshader")  # Or use nodedef if available
        
        
        # 3. Set Standard Surface Inputs (Parameters):
        for input_elem in standard_surface_elem.findall("./input"):
            mtlx_input_name = input_elem.get("name")
            mtlx_input_type = input_elem.get("type")
            mtlx_value = input_elem.get("value")
            mtlx_nodegraph = input_elem.get("nodegraph") #Check if the input is connected
            mtlx_output = input_elem.get("output") 
                    
            usd_input = usd_shader.GetInput(mtlx_input_name)  # Get EXISTING input
            usd_type = _map_mtlx_type_to_usd(mtlx_input_type)
                    
            if mtlx_nodegraph and mtlx_output:  # Check for connection FIRST
                    
                nodegraph_path = f"{material_path}/{surface_shader_name}/{mtlx_nodegraph}"
                root_prim = stage.GetPseudoRoot() # Get the root prim of the stage
                nodegraph_prim = root_prim.GetPrimAtPath(nodegraph_path)  # Get the prim using the root prim

                if not nodegraph_prim:  # Create ONLY if it DOESN'T exist
                    nodegraph_prim = UsdShade.NodeGraph.Define(stage, nodegraph_path)

                nodegraph_shader = UsdShade.NodeGraph(nodegraph_prim)  # Get shader from prim
                  
                mat.CreateSurfaceOutput().ConnectToSource(usd_shader.ConnectableAPI(), "out")                
                _set_usd_input_connection(usd_shader, usd_type, mtlx_input_name, mtlx_output, nodegraph_shader)  # Call connection function
                #_set_usd_input_value(usd_shader, usd_type, mtlx_value, mtlx_input_name)
                
        # 5. NodeGraph Assembly
        nodegraph_elem = root.find("./nodegraph")
        
        if nodegraph_elem:
        
            # 5a. Get Nodedefs...
            usd_nodes = {}
            for node_elem in nodegraph_elem.findall("./*"): #Iterate through all elements under nodegraph
                if "nodedef" in node_elem.attrib: # Check if it has a nodedef attribute
                    node_name = node_elem.get("name")
                    #usd_node_name = usd_nodes[node_name] #Get the usd node
                    node_type = node_elem.get("type")
                    node_def = node_elem.get("nodedef")
                    
                    # Create USD node and add to usd_nodes dictionary
                    node_path = f"{material_path}/{mtlx_nodegraph}/{node_name}"
                    usd_node_shader = UsdShade.Shader.Define(stage, node_path)
                    
                    
                    usd_node_shader.SetShaderId(node_def)
                    usd_nodes[node_def] = usd_node_shader # Add the node to the dictionary
                    usd_node_type = _map_mtlx_type_to_usd(node_type)
                    

                # 5b. Get their inputs...
                for input_elem in node_elem.findall("./input"):
                    if "nodedef" in node_elem.attrib:
                        input_name = input_elem.get("name")
                        input_type = input_elem.get("type")
                        input_value = input_elem.get("value")
                        input_nodegraph = input_elem.get("nodegraph")
                        input_output = input_elem.get("output")
                        input_attribs_str = ""
                        
                        for key, value in input_elem.attrib.items():
                            key_str = str(key) #Convert key to string
                            if isinstance(value, dict):
                                value_str = str(value)
                            else:
                                value_str = str(value)
                            if key_str != "name" and key_str != "type": #Avoid printing name and type again
                                input_attribs_str += f"{key_str}: {value_str}, "
                        
                        # file textures
                        if input_type == "filename" and key_str == "value":
                            input_file = value_str
                            #--------------
                            
                            #--------------
                            #_set_usd_input_connection(usd_node_shader, node_type, input_name, input_file, nodegraph_shader)
                            
                        elif key_str == "value":
                            input_value = value_str
                            _set_usd_input_value(usd_node_shader, usd_node_type, input_value, input_name)
                        
                            #print(f'{node_name}: input_value is {input_value}')
                            
                        
    
            # 5c. Finally we do the Output Nodes...
            for out_elem in nodegraph_elem.findall("./output"):  # Iterate through ONLY <output> elements
                out_name = out_elem.get("name")
                out_type = out_elem.get("type")
                out_node = out_elem.get("nodename")
                
                usd_out_type = _map_mtlx_type_to_usd(out_type)
                
                from_output = None
                if out_node in usd_nodes:  # check if the NODE exists
                    #print('outputs block C...')
                    output_path = f"{material_path}/{mtlx_nodegraph}/{out_name}"
                    output_prim = stage.GetPrimAtPath(output_path) 
                    if output_prim:
                        from_usd_out_node = usd_nodes[out_node]
                        from_output = from_usd_out_node.GetOutput(out_name)
                    else:
                        print(f"Warning: NodeGraph prim {out_name} not found at path: {output_path}")


                    if from_output:
                        print('outputs block D...')
                    
                        usd_output = UsdShade.Shader.Define(stage, output_path)
                        usd_output.SetShaderId(usd_out_type)

                        usd_output.ConnectToSource(from_output)
                    else:
                        print(f"Warning: Output '{out_name}' not found on node '{out_node}'.")
                else:
                    print(f"Warning: Node '{out_node}' not found for output '{out_name}'.")

            

            
    
    
    
    
    root_prim = stage.OverridePrim(root_asset)
    root_prim.SetSpecifier(Sdf.SpecifierOver)
    #stage.SetDefaultPrim(root_prim)
    
    #print(f"Material written to: {stage.GetRootLayer().GetRealPath()}")
    print_asset = stage.GetRootLayer().ExportToString()
    print(print_asset)

# Example usage:
asset_name = "carBody"
mtlx_file = "/Users/Derek/Downloads/usd_assets/mtlx_test/carBody3.mtlx"  # Replace with your MaterialX file
usd_path = "/Users/Derek/Downloads/usd_assets/mtlx_test/carBody.usda"  # Replace with desired USD material path
material_name="carBody_SG"
materialx_to_usd(mtlx_file, usd_path, material_name, asset_name)
#create_nodegraph(mtlx_file)


