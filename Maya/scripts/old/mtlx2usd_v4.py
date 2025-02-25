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


def create_nodegraph_nodes(stage, material_path, node_elem):
    """Creates a USD shader from a MaterialX node element."""

    mtlx_node_name = node_elem.get("name")
    mtlx_node_type = node_elem.get("type")

    nodedef_elem = node_elem.find("./nodedef")
    
    
    if nodedef_elem: #If there is a nodedef use that
        nodedef_name = nodedef_elem.get("nodedef")
    else: #If there is no nodedef use the type
        nodedef_name = node_elem.get("type")


    shader_path = f"{material_path}/{mtlx_node_name}"
    usd_shader = UsdShade.Shader.Define(stage, shader_path)
    
    # <--- KEY CHANGE: Construct a proper shader ID
    shader_id = f"ND_{nodedef_name}"  # Or use a more specific namespace if needed
    usd_shader.SetShaderId(shader_id)

    for input_name in usd_shader.GetInputs():
        print(f"  {input_name.GetName()}")

    usd_shader.SetShaderId(nodedef_name)

    for input_elem in node_elem.findall("./input"):
        mtlx_input_name = input_elem.get("name")
        mtlx_input_type = input_elem.get("type")
        mtlx_input_value = input_elem.get("value")
        mtlx_input_nodename = input_elem.get("nodename")
        mtlx_input_output = input_elem.get("output")            
        
        usd_input = usd_shader.GetInput(mtlx_input_name)

        if mtlx_input_nodename and mtlx_input_output: #If there is a connection
            input_nodegraph_path = f"{material_path}/{surface_shader_name}/{mtlx_input_nodegraph}"
            input_nodegraph_prim = stage.GetPrim(input_nodegraph_path)
            if not input_nodegraph_prim:
                input_nodegraph_prim = UsdShade.NodeGraph.Define(stage, input_nodegraph_path)
            input_nodegraph_shader = UsdShade.NodeGraph(input_nodegraph_prim)

            from_usd_node = input_nodegraph_shader #The node we are connecting from is the nodegraph
            from_output = from_usd_node.GetOutput(mtlx_input_output) #The output is the mtlx_input_output
            #from_output = from_usd_node.GetOutput(Tf.Token(mtlx_input_output))  

            if from_output and usd_input:
                usd_input.ConnectToSource(from_output)


        if mtlx_input_value is not None:  # Set constant values
            try:
                usd_input = usd_shader.GetInput(mtlx_input_name) # Get the existing input
                if usd_input: # Check if the input exists (important!)
                    usd_input_type_string = _map_mtlx_type_to_usd(mtlx_input_type)
                    
                else:
                    print(f"Warning: Input '{mtlx_input_name}' not found on shader '{mtlx_node_name}'.")

            except Exception as e:
                print(f"Error setting parameter value for {mtlx_input_name}: {e}")

        if mtlx_input_nodename:  # Handle connections (same as before)
            pass
        

    return usd_shader
    

    

def create_nodegraph(mtlx_filepath, stage, material_path, usd_nodes):

    node_tree = ET.parse(mtlx_filepath)
    node_root = node_tree.getroot()
    
    nodegraph_elem = node_root.find("./nodegraph")
    
    _set_usd_input_connection(usd_shader, usd_type, mtlx_input_name, mtlx_output, nodegraph_shader)  # Call connection function

    
    if nodegraph_elem:
    
        #  Output nodes...
        for out_elem in nodegraph_elem.findall("./output"):  # Iterate through ONLY <output> elements
            out_name = out_elem.get("name")
            out_type = out_elem.get("type")
            out_node = out_elem.get("nodename")
            
            usd_type = _map_mtlx_type_to_usd(out_type)

            if out_node in usd_nodes: #Check if the node exists
                from_usd_node = usd_nodes[out_node]
                from_output = from_usd_node.GetOutput(Token(out_output))

                if from_output:
                    output_path = f"{material_path}/{material_name}_nodes/{out_name}" #Create the output path
                    usd_output = UsdShade.Shader.Define(stage, output_path)
                    usd_output.SetShaderId(usd_type) #Set the shader ID to the correct type

                    usd_output.ConnectToSource(from_output) #Connect the output to the node's output
                else:
                    print(f"Warning: Output '{out_output}' not found on node '{out_node}'.")
            else:
                print(f"Warning: Node '{out_node}' not found for output '{out_name}'.")

        
        # Nodedefs...
        for node_elem in nodegraph_elem.findall("./*"): #Iterate through all elements under nodegraph
            if "nodedef" in node_elem.attrib: #Check if it is a node
                node_name = node_elem.get("name")
                node_type = node_elem.get("type")
                node_def = node_elem.get("nodedef")
               
                # Get inputs for this node
                for input_elem in node_elem.findall("./input"):
                    input_name = input_elem.get("name")
                    input_type = input_elem.get("type")
                    input_attribs_str = ""
                    for key, value in input_elem.attrib.items():
                        key_str = str(key) #Convert key to string
                        if isinstance(value, dict):
                            value_str = str(value)
                        else:
                            value_str = str(value)
                        if key_str != "name" and key_str != "type": #Avoid printing name and type again
                            input_attribs_str += f"{key_str}: {value_str}, "

                    input_attribs_str = input_attribs_str.rstrip(", ")
                    #print(f'  input_{input_name} ({input_attribs_str})')

    
def materialx_to_usd(mtlx_filepath, usd_filepath, material_name):
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
        
        
        # 3. Set Surface Attribute Values
        for input_elem in standard_surface_elem.findall("./input"):
            mtlx_input_name = input_elem.get("name")
            mtlx_input_type = input_elem.get("type")
            mtlx_value = input_elem.get("value")
            mtlx_nodegraph = input_elem.get("nodegraph") #Check if the input is connected
            mtlx_output = input_elem.get("output") 
                    
            usd_input = usd_shader.GetInput(mtlx_input_name)  # Get EXISTING input
            usd_type = _map_mtlx_type_to_usd(mtlx_input_type)
            
            mat.CreateSurfaceOutput().ConnectToSource(usd_shader.ConnectableAPI(), "out")
            # attribute values
            _set_usd_input_value(usd_shader, usd_type, mtlx_value, mtlx_input_name)
            
            
            
        # 4. Connect maps and Create Nodegraph    
        if mtlx_nodegraph and mtlx_output:  # Check for connection FIRST
        
            nodegraph_path = f"{material_path}/{surface_shader_name}/{mtlx_nodegraph}"
            root_prim = stage.GetPseudoRoot() # Get the root prim of the stage
            nodegraph_prim = root_prim.GetPrimAtPath(nodegraph_path)  # Get the prim using the root prim

            if not nodegraph_prim:  # Create ONLY if it DOESN'T exist
                nodegraph_prim = UsdShade.NodeGraph.Define(stage, nodegraph_path)

            nodegraph_shader = UsdShade.NodeGraph(nodegraph_prim)  # Get shader from prim

            _set_usd_input_connection(usd_shader, usd_type, mtlx_input_name, mtlx_output, nodegraph_shader)  # Call connection function

        # 5. NodeGraph Parts
        nodegraph_elem = root.find("./nodegraph")
        usd_nodes = {}
        if nodegraph_elem:
    
            #  Output nodes...
            for out_elem in nodegraph_elem.findall("./output"):  # Iterate through ONLY <output> elements
                out_name = out_elem.get("name")
                out_type = out_elem.get("type")
                out_node = out_elem.get("nodename")
            
                usd_type = _map_mtlx_type_to_usd(out_type)

            if out_node in usd_nodes: #Check if the node exists
                from_usd_node = usd_nodes[out_node]
                from_output = from_usd_node.GetOutput(Token(out_output))

                if from_output:
                    output_path = f"{material_path}/{material_name}_nodes/{out_name}" #Create the output path
                    usd_output = UsdShade.Shader.Define(stage, output_path)
                    usd_output.SetShaderId(usd_type) #Set the shader ID to the correct type

                    usd_output.ConnectToSource(from_output) #Connect the output to the node's output
                else:
                    print(f"Warning: Output '{out_output}' not found on node '{out_node}'.")
            else:
                print(f"Warning: Node '{out_node}' not found for output '{out_name}'.")

        
            # Nodedefs...
            for node_elem in nodegraph_elem.findall("./*"): #Iterate through all elements under nodegraph
                if "nodedef" in node_elem.attrib: #Check if it is a node
                    node_name = node_elem.get("name")
                    node_type = node_elem.get("type")
                    node_def = node_elem.get("nodedef")
                    print(f'node_name: {node_name}')
               
                # Get inputs for this node
                for input_elem in node_elem.findall("./input"):
                    input_name = input_elem.get("name")
                    input_type = input_elem.get("type")
                    input_attribs_str = ""
                    for key, value in input_elem.attrib.items():
                        key_str = str(key) #Convert key to string
                        if isinstance(value, dict):
                            value_str = str(value)
                        else:
                            value_str = str(value)
                        if key_str != "name" and key_str != "type": #Avoid printing name and type again
                            input_attribs_str += f"{key_str}: {value_str}, "

                    input_attribs_str = input_attribs_str.rstrip(", ")
                    #print(f'  input_{input_name} ({input_attribs_str})')


        '''
        # 4. Node Graph and Connections:
        nodegraph_elem = root.find(".//nodegraph[@name='MatName_nodes']")
        if nodegraph_elem is not None:
            usd_nodes = {}
            for node_elem in nodegraph_elem.findall("./*"):
                usd_node = create_materialx_shader(stage, material_path, node_elem)
                usd_nodes[node_elem.get("name")] = usd_node

            #Handle outputs in the nodegraph
            for output_elem in nodegraph_elem.findall("./output"):
                nodegraph_name = output_elem.get("name")
                nodegraph_type = output_elem.get("type")
                nodegraph_nodename = output_elem.get("nodename")
                nodegraph_output_name = output_elem.get("output") #Get the output connected to this nodegraph output


                if nodegraph_nodename in usd_nodes:
                    from_usd_node = usd_nodes[nodegraph_nodename]
                    from_output = from_usd_node.GetOutput(nodegraph_output_name) #Assumes output is named "out"
                    if from_output:
                        nodegraph_connect = nodegraph_shader.CreateOutput(nodegraph_name, _map_mtlx_type_to_usd(nodegraph_type)) #Create the output on the nodegraph
                        nodegraph_connect.ConnectToSource(from_output) #Connect the nodegraph output to the node output

                        #usd_shader.GetInput(nodegraph_name).ConnectTo(from_output) #Get the input and connect it

            # Handle connections in the inputs of the nodes
            for node_elem in nodegraph_elem.findall("./*"):
                for input_elem in node_elem.findall("./input"):
                    mtlx_input_name = input_elem.get("name")
                    mtlx_input_nodename = input_elem.get("nodename")  # Check for nodename (connection)

                    if mtlx_input_nodename:  # Handle connections
                        if mtlx_input_nodename in usd_nodes:
                            from_usd_node = usd_nodes[mtlx_input_nodename]
                            from_output = from_usd_node.GetOutput("out") #Assumes output is named "out"
                            to_usd_node = usd_nodes[node_elem.get("name")]
                            to_input = to_usd_node.GetInput(mtlx_input_name)
                            if from_output and to_input:
                                to_input.ConnectTo(from_output)
            '''
                                


        
            
                
            
    

                

 

    #usd_nodes = {}
    #create_nodegraph(mtlx_file, stage, material_path, usd_nodes)
    
    root_prim = stage.OverridePrim(root_asset)
    root_prim.SetSpecifier(Sdf.SpecifierOver)
    stage.SetDefaultPrim(root_prim)
    
    #print(f"Material written to: {stage.GetRootLayer().GetRealPath()}")
    print_asset = stage.GetRootLayer().ExportToString()
    print(print_asset)

# Example usage:
    
mtlx_file = "/Users/Derek/Downloads/usd_assets/mtlx_test/carBody.mtlx"  # Replace with your MaterialX file
usd_path = "/Users/Derek/Downloads/usd_assets/mtlx_test/carBody.usda"  # Replace with desired USD material path
material_name="carBody_SG"
materialx_to_usd(mtlx_file, usd_path, material_name)
#create_nodegraph(mtlx_file)


