from pxr import Usd, UsdShade, Sdf, Gf
import xml.etree.ElementTree as ET
import os



def set_usd_input_connection(usd_shader, usd_type, mtlx_input_name, mtlx_output, nodegraph_shader):
    '''
    usd_shader: The node being connected (the output). eg: "carBody_dif"
    usd_type:  usd which is converted to sdf. eg: "color3f"
                         
    mtlx_input_name: the channel being connected to (to/output). eg: "base_color" or -- in = name
    mtlx_output: the output channel being connected (from/input). eg: 
                         
    nodegraph_shader: the node recieving the connection (the input). eg "carBody_mtl"
    #color3f inputs:base_color.connect = </ASSET_MaterialX/mtl/carBody_SG/carBody_nodes.outputs:outColor>
    '''  

    vec_type=None

    # convert usd types into Sdf
    if usd_type == "color3f":
        usd_type_name = Sdf.ValueTypeNames.Color3f
        vec_type = Gf.Vec3f
    elif usd_type == "vector3f":
        usd_type_name = Sdf.ValueTypeNames.Vector3f  # Vector3f
        vec_type = Gf.Vec3f
    elif usd_type == "float":
        usd_type_name = Sdf.ValueTypeNames.Float
        vec_type = None  # No vector type for float
    elif usd_type == "filename":
        usd_type_name = Sdf.ValueTypeNames.String
        vec_type = None
    else:
        print(f"Warning: Setting value for unsupported type: {usd_type}")
        return  # Important: Exit early if type is unsupported
    
   
    # Tokenize input name:
    mtlx_input_name_token = Sdf.Path.TokenizeIdentifier(mtlx_input_name)[0]

    outPort = nodegraph_shader.GetOutput(mtlx_output) # Get output
    if not outPort: #Create if it doesn't exist
        outPort = nodegraph_shader.CreateOutput(mtlx_output, usd_type_name)

    surfaceTerminal = usd_shader.GetInput(mtlx_input_name_token)  # Use tokenized name
    if surfaceTerminal:  # Check if the input exists
        surfaceTerminal.ConnectToSource(outPort)  # connect outPort into surfaceTerminal
    else:
        print(f"Warning: Input '{mtlx_input_name}' not found on shader {usd_shader.GetPath()}")
    


    
def set_usd_input_value(usd_shader, usd_type, mtlx_value, mtlx_input_name):
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
   
    input_name_token = Sdf.Path.TokenizeIdentifier(mtlx_input_name)[0] # name the port (eg: 'base color')
    internal_port = usd_shader.CreateInput(input_name_token, usd_type_name) # create input
    exposed_port = usd_shader.CreateInput(input_name_token, usd_type_name) # create input

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

def map_mtlx_type_to_usd(mtlx_type):
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
        
def map_mtlx_type_to_sdf(mtlx_type):
    """Maps MaterialX types to USD types."""
    if mtlx_type == "color3":
        return Sdf.ValueTypeNames.Color3f
    elif mtlx_type == "float":
        return Sdf.ValueTypeNames.Float
    elif mtlx_type == "vector3":
        return Sdf.ValueTypeNames.Vector3f 
    elif mtlx_type == "filename":
        return Sdf.ValueTypeNames.String # File paths are strings in USD
    else:
        print(f"Warning: Setting value for unsupported type: {usd_type}")
        return  # Important: Exit early if type is unsupported


    

    
def materialx_to_usd(mtlx_filepath, usd_filepath, asset_name):
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
    
    
    # 1. Surface Material (SG)
    surface_material_elem = root.find("./surfacematerial") 
    if surface_material_elem is None:
        raise ValueError("No <surfacematerial> element found at the root level.")
        
    material_name = surface_material_elem.get("name")
    material_path = f"{materials_scope_path}/{material_name}"  
    surfacematerial = UsdShade.Material.Define(stage, material_path) 

    
    # 2. Standard Surface Shader 
    standard_surface_elem = root.find("./standard_surface")  
    if standard_surface_elem is None:
        raise ValueError("No <standard_surface> element found at the root level.")

    surface_name = standard_surface_elem.get("name") #Get the name of the standard surface
    surface_path = f"{material_path}/{surface_name}"  # Prim path *under* the material
    usd_surface = UsdShade.Shader.Define(stage, surface_path)
    
    # connect surface to material (SG)
    surfacematerial.CreateSurfaceOutput().ConnectToSource(usd_surface.ConnectableAPI(), "out") 
    
    # 3. Set Standard Surface Inputs (Parameters):
    for surf_elem in standard_surface_elem.findall("./input"):
        mtlx_input_name = surf_elem.get("name")
        mtlx_input_type = surf_elem.get("type")
        mtlx_input_value = surf_elem.get("value")
        mtlx_surf_def = surf_elem.get("nodedef")
        mtlx_nodegraph = surf_elem.get("nodegraph") 
        mtlx_surf_output = surf_elem.get("output") 
        
        if mtlx_surf_def is not None:
            usd_surface.SetShaderId(mtlx_surf_def)
        else:  
            usd_surface.SetShaderId("ND_standard_surface_surfaceshader") 
        usd_surf_type = map_mtlx_type_to_usd(mtlx_input_type)
        
        set_usd_input_value(usd_surface, usd_surf_type, mtlx_input_value, mtlx_input_name) # surface parameter values
        
        # 4. Create Node Graph
        if mtlx_nodegraph and mtlx_surf_output:  # Check for connections to surface
            
            nodegraph_path = f"{material_path}/{mtlx_nodegraph}"  # eg: /ASSET_MaterialX/mtl/carBody_SG/carBody_nodes

            root_prim = stage.GetPseudoRoot() # Get the root prim of the stage
            nodegraph_prim = root_prim.GetPrimAtPath(nodegraph_path)  # Get the prim using the root prim

            if not nodegraph_prim:  # Create ONLY if it DOESN'T exist
                nodegraph_prim = UsdShade.NodeGraph.Define(stage, nodegraph_path)
            nodegraph_shader = UsdShade.NodeGraph(nodegraph_prim)  # Get shader from prim
            
            # Connect maps from Node Graph to the surface
            set_usd_input_connection(usd_surface, usd_surf_type, mtlx_input_name, mtlx_surf_output, nodegraph_shader) 
            
            
        # 5. Populate outputs for Nodegraph terminal            
        nodegraph_elem = root.find("./nodegraph")  # Find the specific nodegraph
        if nodegraph_elem is not None:
            for output_elem in nodegraph_elem.findall("./output"):  # Directly find <output> elements
                output_name = output_elem.get("name")
                output_type = output_elem.get("type")
                output_nodename = output_elem.get("nodename") 
                
                output_path = f"{nodegraph_path}/{output_nodename}"  # path to nodes. 
                output_prim = stage.GetPrimAtPath(output_path) #Get the prim
                if not output_prim:  
                    output_prim = UsdShade.Shader.Define(stage, output_path)
                usd_output = UsdShade.Shader(output_prim)  
                            
                sdf_output_type = map_mtlx_type_to_sdf(output_type) # convert type to sdf
                outNode = usd_output.CreateOutput('out', sdf_output_type)  #creates out from texture
                            
                NodeGraph_hub = nodegraph_shader.CreateOutput(output_name, sdf_output_type) # creates output in graph terminal
                NodeGraph_hub.ConnectToSource(outNode) # connects to nodegraph hub
                
            
            # 6. Add Nodes in Nodegraph...
            nodegraph_elem = root.find("./nodegraph")
            if not nodegraph_elem:
                return
                
            usd_nodes = {}
            for node_elem in nodegraph_elem.findall("./*"): # Iterate through all elements under nodegraph
                if "nodedef" in node_elem.attrib: # Check if it has a nodedef attribute (i.e. that it is a node)
                    node_name = node_elem.get("name")
                    node_type = node_elem.get("type")
                    node_def = node_elem.get("nodedef")
                    node_output = node_elem.get("output")
                    
                    # Create USD node from path
                    node_path = f"{nodegraph_path}/{node_name}"
                    node_prim = stage.GetPrimAtPath(node_path) #Get the prim
                    if not node_prim:  
                        node_prim = UsdShade.Shader.Define(stage, node_path)
                    usd_node_shader = UsdShade.Shader(node_prim)  
                    
                    #usd_node_name = usd_nodes[node_name] #Get the usd node
                    usd_node_type = map_mtlx_type_to_usd(node_type)
                    usd_node_shader.SetShaderId(node_def)
                    usd_nodes[node_def] = usd_node_shader # Add the node to the dictionary
                    
                    # add node output
                    sdf_node_type = map_mtlx_type_to_sdf(node_type)
                    nodeOut = usd_node_shader.CreateOutput("out", sdf_node_type)

            
                # 7. Get node inputs...
                for input_elem in node_elem.findall("./input"):
                    if "nodedef" not in node_elem.attrib:
                        continue
                    input_name = input_elem.get("name")
                    input_type = input_elem.get("type")
                    input_value = input_elem.get("value")
                    input_nodename = input_elem.get("nodename")
                        
                    # make usd shader for nodename
                    if input_nodename:
                        input_nodename_path = f"{nodegraph_path}/{input_nodename}"  # path to nodes. 
                        input_nodenam_prim = stage.GetPrimAtPath(input_nodename_path) #Get the prim
                        if not input_nodenam_prim:  
                            input_nodenam_prim = UsdShade.Shader.Define(stage, input_nodename_path)
                        usd_input_nodename = UsdShade.Shader(input_nodenam_prim)  
                        
                        
                    # Add values to nodes
                    if input_type != "filename":
                        if input_value: 
                            set_usd_input_value(usd_node_shader, usd_node_type, input_value, input_name)
                               
                    # Add texture filepaths to nodes
                    if input_type == "filename": 
                        usd_node_shader.CreateInput('file', Sdf.ValueTypeNames.Asset).Set(input_value)
                        #        asset inputs:file = @../textures/carBody_met_Beetle_forMtlx.jpg@
                        
                    # Node Connections
                    if input_nodename:
                        set_usd_input_value(usd_node_shader, usd_node_type, input_value, input_name) # adds inputs without values to receive connections
                        set_usd_input_connection(usd_node_shader, usd_node_type, input_name, "out", usd_input_nodename)
                        #          vector3f inputs:in.connect = </ASSET_MaterialX/mtl/MatName_SG/MatName_nodes/MatName_nor.outputs:out>
                            

                                   
  
    
    root_prim = stage.OverridePrim(root_asset)
    root_prim.SetSpecifier(Sdf.SpecifierOver)

    
    #print(f"Material written to: {stage.GetRootLayer().GetRealPath()}")
    print_asset = stage.GetRootLayer().ExportToString()
    print(print_asset)

# Example usage:
asset_name = "carBody"
mtlx_file = "/Users/Derek/Downloads/usd_assets/mtlx_test/carBody3.mtlx"  # Replace with your MaterialX file
usd_path = "/Users/Derek/Downloads/usd_assets/mtlx_test/carBody.usda"  # Replace with desired USD material path
material_name="carBody_SG"
materialx_to_usd(mtlx_file, usd_path, asset_name)


