'''
v11 with support for Displacement and Mix shaders (note that Mix shaders do not currently render in Arnold)
'''


from pxr import Usd, UsdShade, Sdf, Gf
import xml.etree.ElementTree as ET
import os



def set_usd_input_connection(usd_destination, sdf_type, mtlx_input_slot, mtlx_output_slot, usd_source):
    '''
    usd_destination: the node recieving the connection (the input). eg "carBody_mtl"
    sdf_type:  sdf format. eg: "color3f"
                         
    mtlx_input_slot: the parameter being connected to (input). eg: "base_color" or -- in = name
    mtlx_output_slot: the channel being connected from (output). eg: 
                         
    usd_source: the node the connection is going out of (the output) ie coming from.  eg: "carBody_dif"
    
    example output:
        color3f inputs:base_color.connect = </ASSET_MaterialX/mtl/carBody_SG/carBody_nodes.outputs:outColor>
    '''  


    vec_type=None
    known_string_types = {"filename", "surfaceshader"}  # Add more types as needed

    # Tokenize input name:
    mtlx_input_name_token = Sdf.Path.TokenizeIdentifier(mtlx_input_slot)[0]

    outPort = usd_source.GetOutput(mtlx_output_slot) # Get output
    if not outPort: #Create if it doesn't exist
        outPort = usd_source.CreateOutput(mtlx_output_slot, sdf_type)

    surfaceTerminal = usd_destination.GetInput(mtlx_input_name_token)  # Use tokenized name
    if surfaceTerminal:  # Check if the input exists
        surfaceTerminal.ConnectToSource(outPort)  # connect outPort into surfaceTerminal
    else:
        print(f"Warning: Input '{mtlx_input_slot}' not found on shader {usd_destination.GetPath()}")
    


    
def set_usd_input_value(usd_destination, sdf_type, mtlx_value, mtlx_SourceName):
    """Sets USD input value (called ONLY for value inputs)."""
    token_sourceName = Sdf.Path.TokenizeIdentifier(mtlx_SourceName)[0]
    vec_type=None
    known_string_types = {"filename", "surfaceshader"}  # Add more types as needed

    if sdf_type == "color3f":
        vec_type = Gf.Vec3f
    elif sdf_type == "vector3f":
    #elif sdf_type == "float3":
        vec_type = Gf.Vec3f
    elif sdf_type == "float2":
        vec_type = Gf.Vec2f
        
        
    token_sourceName = Sdf.Path.TokenizeIdentifier(mtlx_SourceName)[0] # name the port (eg: 'base color')
    internal_port = usd_destination.CreateInput(token_sourceName, sdf_type) # create input
    exposed_port = usd_destination.CreateInput(token_sourceName, sdf_type) # create input

    if mtlx_value is not None:  # Only set value if it exists
        try:
            #if vec_type:  # Handle vector/color types
            #    parts = [float(x.strip()) for x in mtlx_value.split(",")]
            #    exposed_port.Set(vec_type(parts[0], parts[1], parts[2]))
                
            if vec_type:  # Handle vector/color types
                parts = [float(x.strip()) for x in mtlx_value.split(",")]
                if len(parts) == 3:
                    exposed_port.Set(vec_type(parts[0], parts[1], parts[2]))
                elif len(parts) == 2 and vec_type == Gf.Vec2f:
                    exposed_port.Set(Gf.Vec2f(parts[0], parts[1]))
                else:
                    print(f"Error: Incorrect number of components for {vec_type}: {mtlx_value}")
                
            elif sdf_type == Sdf.ValueTypeNames.Float:
                exposed_port.Set(float(mtlx_value))
            elif sdf_type == Sdf.ValueTypeNames.Int:
                exposed_port.Set(int(mtlx_value))
            elif sdf_type == Sdf.ValueTypeNames.String:
                exposed_port.Set(mtlx_value)
            # Add handling for other types as needed
        except ValueError:
            print(f"Error: Could not convert {mtlx_value} to {sdf_type}")


        
def map_mtlx_type_to_sdf(mtlx_type):
    """Maps MaterialX types to USD types."""
    known_string_types = {"filename", "surfaceshader"}  # Add more types as needed
        
    if mtlx_type == "color3":
        return Sdf.ValueTypeNames.Color3f
    elif mtlx_type == "float":
        return Sdf.ValueTypeNames.Float
    elif mtlx_type == "vector3":
        #return Sdf.ValueTypeNames.Float3
        return Sdf.ValueTypeNames.Vector3f
    elif mtlx_type == "vector2":
        return Sdf.ValueTypeNames.Float2 
    elif mtlx_type == "filename":
        return Sdf.ValueTypeNames.String # File paths are strings in USD
    elif mtlx_type == "surfaceshader":
        return Sdf.ValueTypeNames.Token 
    elif mtlx_type == "displacementshader":
        return Sdf.ValueTypeNames.Token     
    else:
        print(f"Warning: Setting value for unsupported type: {mtlx_type}")
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

    # create stage
    try:
        mtlx_layer = Sdf.Layer.CreateNew(usd_filepath, args={'format': 'usda'})
    except Exception as e:
        print(f"Warning: Failed to create new layer at '{usd_filepath}': {e}")
        print("Attempting to open existing layer from cache...")
        mtlx_layer = Sdf.Layer.FindOrOpen(usd_filepath)
        if not mtlx_layer:
            print(f"Error: Failed to open cached layer at '{usd_filepath}'.")
            return

    if not mtlx_layer:
        print(f"Error: Unable to create or open layer at '{usd_filepath}'.")
        return

    stage = Usd.Stage.Open(mtlx_layer)



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
    
    
    #-------------
    

    # 1. Get Material (SG)
    surface_material_elem = root.find("./surfacematerial") 
    if surface_material_elem is None:
        raise ValueError("No <surfacematerial> element found at the root level.")
    
    material_name = surface_material_elem.get("name")
    material_def = surface_material_elem.get("nodedef") 
    if not material_def:
        material_def = "ND_surfacematerial"
        print("Warning: No node defintion found in MaterialX file for material. Setting to ND_surfacematerial")
    material_path = f"{materials_scope_path}/{material_name}" 
    usd_material = UsdShade.Material.Define(stage, material_path) 
    
    # Get the material inputs
    for mat_input in surface_material_elem:
        material_input_name = mat_input.get("name")
        material_input_nodename = mat_input.get("nodename")
        
        # 2. Get Surface Shaders  
        surface_shaders = root.findall("./*[@type='surfaceshader']")

        
        for surface in surface_shaders:
            surface_name = surface.get("name")
            surface_def = surface.get("nodedef")
            if not surface_def:
                #surface_def = "ND_standard_surface_surfaceshader"
                surface_def = f"ND_{surface.tag}_surfaceshader"
                print(f"Warning: No node defintion found in MaterialX file for surfaceshader. Setting to ND_{surface.tag}_surfaceshader")
                # todo: query element name for other surfaceshader types.
                
            surface_path = f"{material_path}/{surface_name}"  # Prim path *under* the material
            usd_surface = UsdShade.Shader.Define(stage, surface_path)
            usd_surface.SetShaderId(surface_def)
        
            # check for the right connection to the material
            if surface_name == material_input_nodename:
                # Check for the "out" output before attempting to get its type
                if not usd_surface.GetOutput("out"):
                    usd_surface.CreateOutput("out", Sdf.ValueTypeNames.Token)  
                # add mtlx namespace to output in the Material (SG)
                mtlx_surface_output = usd_material.CreateOutput("mtlx:surface", usd_surface.GetOutput("out").GetTypeName())
                mtlx_surface_output.ConnectToSource(usd_surface.ConnectableAPI(), "out")
                # token outputs:mtlx:surface.connect = </ASSET_MaterialX/mtl/carBody_SG/carBody_mtl.outputs:out>

    
    
            # 3. Set Standard Surface Inputs (Parameters):
            surf_attributes = surface.findall("./input")  # Find input elements within the current surface
            for surf_attr in surf_attributes:
                mtlx_input_name = surf_attr.get("name")
                mtlx_input_type = surf_attr.get("type")
                mtlx_input_value = surf_attr.get("value")
                mtlx_nodegraph = surf_attr.get("nodegraph") 
                mtlx_surf_output = surf_attr.get("output") 
                mtlx_surf_nodename = surf_attr.get("nodename") 
            
                # populate surface parameter values
                sdf_surf_type = map_mtlx_type_to_sdf(mtlx_input_type)
                set_usd_input_value(usd_surface, sdf_surf_type, mtlx_input_value, mtlx_input_name) 

    
                # 4. Create Node Graph
                if mtlx_nodegraph:  # Check for connections to surface
          
                    nodegraph_path = f"{material_path}/{mtlx_nodegraph}"  # eg: /ASSET_MaterialX/mtl/carBody_SG/carBody_nodes

                    root_prim = stage.GetPseudoRoot() # Get the root prim of the stage
                    nodegraph_prim = root_prim.GetPrimAtPath(nodegraph_path)  # Get the prim using the root prim

                    if not nodegraph_prim:  # Create ONLY if it DOESN'T exist
                        nodegraph_prim = UsdShade.NodeGraph.Define(stage, nodegraph_path)
                    nodegraph_shader = UsdShade.NodeGraph(nodegraph_prim)  # Get shader from prim

                # Connect maps from Node Graph to the surface
                if mtlx_surf_output:
                    set_usd_input_connection(usd_surface, sdf_surf_type, mtlx_input_name, mtlx_surf_output, nodegraph_shader)
                
                # Connect mix shaders if any
                if mtlx_surf_nodename:
                    set_usd_input_connection(usd_surface, sdf_surf_type, mtlx_input_name, "out", nodegraph_shader)
  

            # 5. Populate outputs for Nodegraph terminal            
            nodegraph_elem = root.find("./nodegraph")  # Find the specific nodegraph
            if nodegraph_elem is not None:
                for output_elem in nodegraph_elem.findall("./output"):  # Directly find <output> elements
                    output_name = output_elem.get("name")
                    output_type = output_elem.get("type")
                    output_nodename = output_elem.get("nodename") 
                
                    if output_nodename:
                        output_path = f"{nodegraph_path}/{output_nodename}"  # path to nodes. 
                    output_prim = stage.GetPrimAtPath(output_path) #Get the prim
                    if not output_prim:  
                        output_prim = UsdShade.Shader.Define(stage, output_path)
                    usd_output = UsdShade.Shader(output_prim)  
                           
                    sdf_output_type = map_mtlx_type_to_sdf(output_type) # convert type to sdf
                    outNode = usd_output.CreateOutput('out', sdf_output_type)  #creates out from texture
                            
                    NodeGraph_hub = nodegraph_shader.CreateOutput(output_name, sdf_output_type) # creates output in graph terminal
                    NodeGraph_hub.ConnectToSource(outNode) # connects to nodegraph hub

                    # check for displacement, add output to Material (SG)
                    if output_type == "displacementshader":
                
                        # add output to material SG
                        displace_path = f"{nodegraph_path}/{output_nodename}"  
                        usd_displace = UsdShade.Shader.Define(stage, displace_path)
                        # Create the output with the 'mtlx' namespace. Then connect it to source
                        mtlx_displacement_output = usd_material.CreateOutput("mtlx:displacement", usd_displace.GetOutput("out").GetTypeName())
                        mtlx_displacement_output.ConnectToSource(usd_displace.ConnectableAPI(), "out")

                        #usd_material.CreateDisplacementOutput().ConnectToSource(usd_displace.ConnectableAPI(), "out")
                        # token outputs:displacement.connect = </ASSET_MaterialX/mtl/surf_SG/surf_nodes.outputs:outDisplace>
                       

                # 6. Add Nodes in Nodegraph...
                nodegraph_elem = root.find("./nodegraph")
                if not nodegraph_elem:
                    return
                
                usd_nodes = {}
                for node_elem in nodegraph_elem.findall("./*"): # Iterate through all elements under nodegraph
                    
                    if node_elem.tag not in ["output", "input"]:
                    #if "nodedef" in node_elem.attrib: # Check if it has a nodedef attribute (i.e. that it is a node)
                        node_name = node_elem.get("name")
                        node_type = node_elem.get("type")
                        #node_def = node_elem.get("nodedef")
                        if node_elem.tag == "normalmap":
                            node_def = f"ND_{node_elem.tag}"
                        else:
                            node_def = f"ND_{node_elem.tag}_{node_type}" 
                            
                        node_output = node_elem.get("output")
                    
                        # Create USD node from path
                        node_path = f"{nodegraph_path}/{node_name}"
                        node_prim = stage.GetPrimAtPath(node_path) #Get the prim
                        if not node_prim:  
                            node_prim = UsdShade.Shader.Define(stage, node_path)
                        usd_node_shader = UsdShade.Shader(node_prim)  
                        usd_node_shader.SetShaderId(node_def)
                        usd_nodes[node_def] = usd_node_shader # Add the node to the dictionary
                    
                        # add node output
                        sdf_node_type = map_mtlx_type_to_sdf(node_type) # also used to add values to nodes below
                        nodeOut = usd_node_shader.CreateOutput("out", sdf_node_type)

            
                    # 7. Get node inputs...
                    for input_elem in node_elem.findall("./input"):
                        #if "nodedef" not in node_elem.attrib:
                        #if input_elem.tag not in ["output", "input"]:
                        #    continue
                        input_name = input_elem.get("name")
                        input_type = input_elem.get("type")
                        input_value = input_elem.get("value")
                        input_nodename = input_elem.get("nodename")
                        
                        # make usd shaders for nodename and type
                        if input_nodename:
                            input_nodename_path = f"{nodegraph_path}/{input_nodename}"  # path to nodes. 
                            input_nodenam_prim = stage.GetPrimAtPath(input_nodename_path) #Get the prim
                            if not input_nodenam_prim:  
                                input_nodenam_prim = UsdShade.Shader.Define(stage, input_nodename_path)
                           
                            usd_input_nodename = UsdShade.Shader(input_nodenam_prim) # nodename shader 
                            sdf_input_type = map_mtlx_type_to_sdf(input_type) 

                        # Add values to nodes
                        if input_type != "filename":
                            if input_value: 
                                set_usd_input_value(usd_node_shader, sdf_node_type, input_value, input_name)
                               
                        # Add texture filepaths to nodes
                        if input_type == "filename": 
                            usd_node_shader.CreateInput('file', Sdf.ValueTypeNames.Asset).Set(input_value)
                            #        asset inputs:file = @../textures/carBody_met_Beetle_forMtlx.jpg@

    
                        # Node Connections
                        if input_nodename:
                            #using node type from 6 - nodegraph outputs. need sdf_input_type
                            set_usd_input_value(usd_node_shader, sdf_input_type, input_value, input_name) # adds inputs without values to receive connections
                            set_usd_input_connection(usd_node_shader, sdf_input_type, input_name, "out", usd_input_nodename)
                            #          vector3f inputs:in.connect = </ASSET_MaterialX/mtl/MatName_SG/MatName_nodes/MatName_nor.outputs:out>
    
                
    root_prim = stage.OverridePrim(root_asset)
    root_prim.SetSpecifier(Sdf.SpecifierOver)
    
    # diagnositic
    print_asset = stage.GetRootLayer().ExportToString()
    #print("=============== MATERIALX FILE ======================================")
    #print(print_asset)
    
    # save to file
    stage.GetRootLayer().Save()
    
    


'''
# Example usage:
asset_name = "carBody_mix"
mtlx_file = "/Users/Derek/Downloads/usd_assets/mtlx_test/carBody_mix.mtlx"  # Replace with your MaterialX file
usd_path = "/Users/Derek/Downloads/usd_assets/mtlx_test/surf_dsp.usda"  # Replace with desired USD material path
#material_name="carBody_SG"
materialx_to_usd(mtlx_file, usd_path, asset_name)
'''


