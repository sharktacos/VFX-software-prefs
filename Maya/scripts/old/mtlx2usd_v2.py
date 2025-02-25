from pxr import Usd, UsdShade, Sdf, Gf
import xml.etree.ElementTree as ET
import os

'''
#OLDER
def _connect_and_set_value(usd_shader, mtlx_input_name, usd_type_name, mtlx_value, vec_type=None):
    """Connects ports and sets value (common logic)."""

    input_name_token = Sdf.Path.TokenizeIdentifier(mtlx_input_name)[0]

    internal_port = usd_shader.CreateInput(input_name_token, usd_type_name)
    exposed_port = usd_shader.CreateInput(input_name_token, usd_type_name)
    internal_port.ConnectToSource(exposed_port)

    if mtlx_value is not None:
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
'''
#NEW
def _connect_and_set_value(usd_shader, mtlx_input_name, usd_type_name, mtlx_value, vec_type=None):
    """Connects ports and sets value (common logic)."""

    input_name_token = Sdf.Path.TokenizeIdentifier(mtlx_input_name)[0]
    internal_port = usd_shader.CreateInput(input_name_token, usd_type_name)
    exposed_port = usd_shader.CreateInput(input_name_token, usd_type_name)
    internal_port.ConnectToSource(exposed_port)  

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



'''
#OLD
def _set_usd_input_value(usd_shader, usd_input, usd_type, mtlx_value, mtlx_input_name):
    if usd_type == "color3":
        usd_type_name = Sdf.ValueTypeNames.Color3f
        vec_type = Gf.Vec3f
        _connect_and_set_value(usd_shader, mtlx_input_name, usd_type_name, mtlx_value, vec_type)

    elif usd_type == "vector3":
        usd_type_name = Sdf.ValueTypeNames.Float3 #Vector3f
        vec_type = Gf.Vec3f
        _connect_and_set_value(usd_shader, mtlx_input_name, usd_type_name, mtlx_value, vec_type)

    elif usd_type == "float":
        usd_type = usd_type.capitalize()
        usd_type_name = getattr(Sdf.ValueTypeNames, usd_type)
        _connect_and_set_value(usd_shader, mtlx_input_name, usd_type_name, mtlx_value)

    elif usd_type == "filename":
        usd_type_name = Sdf.ValueTypeNames.String
        _connect_and_set_value(usd_shader, mtlx_input_name, usd_type_name, mtlx_value)

    # ... (rest of the type handling) ...
    else:
        print(f"Warning: Setting value for unsupported type: {usd_type}")
'''        
        
        

#NEW        
def _set_usd_input_value(usd_shader, usd_input, usd_type, mtlx_value, mtlx_input_name):
    """Sets USD input value (called ONLY for value inputs)."""
    if usd_type == "color3":
        usd_type_name = Sdf.ValueTypeNames.Color3f
        vec_type = Gf.Vec3f
    elif usd_type == "vector3":
        usd_type_name = Sdf.ValueTypeNames.Float3  # Vector3f
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

    _connect_and_set_value(usd_shader, mtlx_input_name, usd_type_name, mtlx_value, vec_type)





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

'''
def _set_usd_input_value(usd_shader, usd_input, usd_type, mtlx_value, mtlx_input_name):

    if usd_type == "color3":
        parts = [float(x.strip()) for x in mtlx_value.split(",")]  # Parse comma-separated values
        usd_input.Set(pxr.Gf.Vec3f(parts[0], parts[1], parts[2]))
        
    elif usd_type == "float":
    
        usd_type = usd_type.capitalize()
        usd_type_name = getattr(Sdf.ValueTypeNames, usd_type)
        input_name_token = Sdf.Path.TokenizeIdentifier(mtlx_input_name)[0]  # Use TokenizeIdentifier

        internal_port = usd_shader.CreateInput(input_name_token, usd_type_name)  # Correct: Name and Type
        exposed_port = usd_shader.CreateInput(input_name_token, usd_type_name)  # Correct: Name and Type
        exposed_port.Set(float(mtlx_value))
        internal_port.ConnectToSource(exposed_port) #Connect the two inputs

                
    elif usd_type == "vector3":
        parts = [float(x.strip()) for x in mtlx_value.split(",")]
        usd_input.Set(pxr.Gf.Vec3f(parts[0], parts[1], parts[2]))
    elif usd_type == "filename":
        usd_input.Set(mtlx_value)
    # Add more type handling as necessary
    else:
        print(f"Warning: Setting value for unsupported type: {usd_type}")
'''

def create_materialx_shader(stage, material_path, node_elem):
    """Creates a USD shader from a MaterialX node element."""

    mtlx_node_name = node_elem.get("name")
    mtlx_node_type = node_elem.get("type")

    nodedef_elem = node_elem.find("./nodedef")
    if nodedef_elem is None:
        nodedef_elem = node_elem
        print("No nodedef found. Using node tag.")

    nodedef_name = nodedef_elem.get("nodedef")
    if nodedef_name is None:
        nodedef_name = node_elem.get("type")
        print("No nodedef found. Using node type.")

    shader_path = f"{material_path}/{mtlx_node_name}"
    usd_shader = pxr.UsdShade.Shader.Define(stage, shader_path)
    print(f"Shader Path: {shader_path}")  # Print the path for reference
    print(f"Available Inputs for {surface_shader_name}:")
    for input_name in usd_shader.GetInputs():
        print(f"  {input_name.GetName()}")

    usd_shader.SetShaderId(nodedef_name)

    for input_elem in node_elem.findall("./input"):
        mtlx_input_name = input_elem.get("name")
        mtlx_input_type = input_elem.get("type")
        mtlx_input_value = input_elem.get("value")
        mtlx_input_nodename = input_elem.get("nodename")

        if mtlx_value is not None:  # Set constant values
            try:
                usd_input = usd_shader.GetInput(mtlx_input_name) # Get the existing input
                if usd_input: # Check if the input exists (important!)
                    usd_input_type_string = _map_mtlx_type_to_usd(mtlx_input_type)
                    if usd_type:
                        _set_usd_input_value(usd_shader, usd_input, usd_type, mtlx_value, mtlx_input_name)
                else:
                    print(f"Warning: Input '{mtlx_input_name}' not found on shader '{mtlx_node_name}'.")

            except Exception as e:
                print(f"Error setting parameter value for {mtlx_input_name}: {e}")

        if mtlx_input_nodename:  # Handle connections (same as before)
            pass

    return usd_shader
    

    
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

    stage = pxr.Usd.Stage.CreateNew(usd_filepath)  # File path for the USD file


    # Create Over for the root asset
    root_asset = "/ASSET_MaterialX"

    # Make 'Materials' scope defined as a def and scope under the 'over' root asset
    materials_scope_path = f'{root_asset}/mtl'
    materials_scope = stage.OverridePrim(materials_scope_path)
    materials_scope.SetSpecifier(Sdf.SpecifierDef)
    materials_scope.GetPrim().SetTypeName('Scope')
    
    material_path = f"{materials_scope_path}/{material_name}"  # Prim path *inside* the USD stage
    mat = pxr.UsdShade.Material.Define(stage, material_path)    
    
    # 1. Surface Material
    surface_material_elem = root.find(".//surfacematerial")
    if surface_material_elem is not None:
        surface_shader_input = surface_material_elem.find("./input[@name='surfaceshader']")
        if surface_shader_input is not None:
            surface_shader_name = surface_shader_input.get("nodename")
            #print(f'surface_shader_name: {surface_shader_name}')

            # 2. Standard Surface Shader
            standard_surface_elem = root.find(f".//standard_surface[@name='{surface_shader_name}']")
            if standard_surface_elem is not None:
                shader_path = f"{material_path}/{surface_shader_name}"  # Prim path *under* the material
                #print(f'shader_path: {shader_path}')
                usd_shader = pxr.UsdShade.Shader.Define(stage, shader_path)
                #print(f'usd_shader: {usd_shader}')
                usd_shader.SetShaderId("ND_standard_surface_surfaceshader")  # Or use nodedef if available
                

                # 3. Set Standard Surface Inputs (Parameters):
                for input_elem in standard_surface_elem.findall("./input"):
                    mtlx_input_name = input_elem.get("name")
                    mtlx_input_type = input_elem.get("type")
                    mtlx_value = input_elem.get("value")
                    mtlx_input_nodegraph = input_elem.get("nodegraph") #Check if the input is connected
                    mtlx_input_output = input_elem.get("output") 


                    #usd_input = usd_shader.GetInput(mtlx_input_name)  # Get EXISTING input
                    
                    if mtlx_input_output is not None and mtlx_input_nodegraph is not None:  # Connection case
                        print(f"Handling connection for {mtlx_input_name} from nodegraph {mtlx_input_nodegraph} output {mtlx_input_output}")
                        # Connection logic will be handled later in the main materialx_to_usd function

                    elif mtlx_value is not None:  # Set constant values (if present)
            
                        try:
                            usd_input = usd_shader.GetInput(mtlx_input_name)  # Get EXISTING input
                            #print(f'seting {mtlx_value} for {mtlx_input_name}')
                            usd_type = _map_mtlx_type_to_usd(mtlx_input_type)
                            #print(f'usd_type: {usd_type}')
                            _set_usd_input_value(usd_shader, usd_input, usd_type, mtlx_value, mtlx_input_name)
                            #print(f'SET usd_input: {usd_input}')
                        except Exception as e:
                            print(f"Error setting parameter value for {mtlx_input_name}: {e}")
                    else:
                        print(f"Input {mtlx_input_name} has neither value nor connection information.")
             
 
                # 4. Node Graph and Connections:
                nodegraph_elem = root.find(".//nodegraph[@name='MatName_nodes']")
                if nodegraph_elem is not None:
                    usd_nodes = {}
                    for node_elem in nodegraph_elem.findall("./*"):
                        usd_node = create_materialx_shader(stage, material_path, node_elem)
                        usd_nodes[node_elem.get("name")] = usd_node

                    #Handle outputs in the nodegraph
                    for output_elem in nodegraph_elem.findall("./output"):
                        output_name = output_elem.get("name")
                        output_type = output_elem.get("type")
                        output_nodename = output_elem.get("nodename")

                        if output_nodename in usd_nodes:
                            from_usd_node = usd_nodes[output_nodename]
                            from_output = from_usd_node.GetOutput("out") #Assumes output is named "out"
                            if from_output:
                                # Connect the output (do NOT create it):
                                usd_shader.GetInput(output_name).ConnectTo(from_output) #Get the input and connect it

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
                            
                            
                mat.CreateSurfaceOutput().ConnectToSource(usd_shader.ConnectableAPI(), "out")
                #mat.CreateSurfaceOutput().ConnectToSource(usd_shader.ConnectableAPI(), "surface")
                usd_input = usd_shader.GetInput("base") 
                #print(usd_input)
                
    
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







