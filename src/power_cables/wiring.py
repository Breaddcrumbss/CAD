import Part
import FreeCAD as App
from FreeCAD import Base


#TODO: Avoid using object names ("panel"), calculate placements directly from parameters

def create_sweep(group, profile, radius, vertices, name="SweepObject", color=(0.0, 0.0, 0.0)):
    """Creates a swept solid given a profile (cross section) and list of vertices representing the bends""" 
    edges: list[tuple[Part.Edge, str]] = []
    for i in range(len(vertices) - 1):
        start = vertices[i]
        end = vertices[i+1]
        line = Part.makeLine(start, end)
        edges.append((line, f"Edge_{i+1}"))

    # Path where the wires will cross, made from vertices, straight lines joining them
    path_obj = Part.Wire([edge[0] for edge in edges])

    if profile.lower() == "circle":
        # creating a profile for every sweep is inefficient, add functionality for reusing profile?
        direction = edges[0][0].tangentAt(0)

        # Cross section of the wire
        profile_shape = Part.makeCircle(radius, edges[0][0].valueAt(0), direction)
        profile_wire = Part.Wire(profile_shape)
    
    else:
        raise ValueError(f"Profile type '{profile}' is not supported.")

    sweep_shape = path_obj.makePipeShell([profile_wire], True, True, 2)

    sweep = group.newObject("Part::Feature", name)
    sweep.Shape = sweep_shape

    if hasattr(sweep, "ViewObject"):
        sweep.ViewObject.ShapeColor = color

    return sweep

def create_object(group, placement, name="test object", colour=(50, 50, 50), size=50):
    new_obj = group.newObject("Part::Feature", f"{name}")
    new_obj.Shape = Part.makeSphere(size)
    new_obj.Placement.Base = placement
    new_obj.ViewObject.ShapeColor = colour
    return new_obj
    
def generate_panel_matrix(params):
    """
    Generates a matrix of solar panel placements based on parameters from src/design/mirror.py.
    
    Each element in the matrix represents a panel and is a tuple of tuples: 
    ((start_x, end_x), (start_y, end_y), (start_z, end_z)).
    """
    panel_matrix = []
    
    rows = params.get('panels_longitudinal', 0) // 2
    cols = params.get('panels_transversal', 0)

    for i in range(rows):
        row_placements = []
        for j in range(cols):
            x_pos = -params['pillar_width'] / 2 + j * params['panel_length']
            y_pos = params['crossdeck_width'] / 2 + i * params['panel_width']
            z_pos = params['panel_base_level']

            start_x = x_pos
            end_x = x_pos + params['panel_length']
            
            start_y = y_pos
            end_y = y_pos + params['panel_width']
            
            start_z = z_pos
            end_z = z_pos + params['panel_height']
            
            placement = ((start_x, end_x), (start_y, end_y), (start_z, end_z))
            row_placements.append(placement)
        panel_matrix.append(row_placements)
        
    return panel_matrix

def get_connection_points(panel_matrix):
    """
    Computes the connection points (positive & negative) for wiring based on the panel matrix.

    """
    if not panel_matrix or not panel_matrix[0]:
        raise ValueError("Panel matrix is empty or malformed.")

    positive_connections = []
    negative_connections = []

    z_level = panel_matrix[0][0][2][0]  # Base z-level of the first panel
    for row in panel_matrix:
        temp_pos = []
        temp_neg = []
        for panel in row:
            (start_x, end_x), (start_y, end_y), _ = panel
            y_pos, y_neg = (end_y - start_y) / 3 + start_y, (end_y - start_y) / 3 * 2 + start_y
            x = (end_x - start_x) / 3 + start_x

            temp_pos.append((x, y_pos, z_level))
            temp_neg.append((x, y_neg, z_level))

        positive_connections.append(temp_pos)
        negative_connections.append(temp_neg)
    return positive_connections, negative_connections

def wire_solar_panels(group, radius=5, params={}, string_direction='transverse'):
    """
    Generates wiring for all solar panels on both sides of the boat.
    
    Args:
        group: The FreeCAD Document or Group object to add electrical components to.
        radius: Radius of the wire sweep.
        params: Dictionary of parameters for panel layout.
    """
    
    electrical_group = group.addObject("App::DocumentObjectGroup", "ElectricalComponents")
    
    # Wire colors to be used
    BLUE = (0.0, 0.0, 1.0)
    RED = (1.0, 0.0, 0.0)
    PURPLE  = (1.0, 0.0, 1.0)


    biru_side_matrix = generate_panel_matrix(params)[::-1]

    kuning_side_matrix = []
    for row in biru_side_matrix[::-1]:  # Reverse for proper ordering after reflection
        mirrored_row = []
        for placement in row:
            (start_x, end_x), (start_y, end_y), (start_z, end_z) = placement
            # Reflect across XZ plane (y -> -y)
            mirrored_placement = ((start_x, end_x), (-end_y, -start_y), (start_z, end_z))
            mirrored_row.append(mirrored_placement)
        kuning_side_matrix.append(mirrored_row)
    
    panel_matrix = biru_side_matrix + kuning_side_matrix

    if not panel_matrix:
        print("Panel matrix is empty, no wires to create.")
        return

    print(f"Generated a {len(panel_matrix)}x{len(panel_matrix[0]) if panel_matrix and panel_matrix[0] else 0} panel matrix for wiring both sides.")

    if not panel_matrix[0]:
        return

    # Get positive and negative endpoints for each panel
    positive_connections, negative_connections = get_connection_points(panel_matrix)

    # Draw central wire
    central_x = panel_matrix[0][1][0][1] + params['deck_width'] / 3  # Place in the middle of the deck
    central_y_start = panel_matrix[0][0][1][1]
    central_y_end = panel_matrix[-1][0][1][0]
    central_z = params['deck_level'] / 2

    central_start = Base.Vector(central_x, central_y_start, central_z)
    central_end = Base.Vector(central_x, central_y_end, central_z)
    centre = (central_start + central_end) * 0.5

    create_sweep(electrical_group, "circle", radius, [central_start, central_end], name="Central_Wire")

    # Place Batteries
    num_batt_series = params["batteries_in_series"]
    num_batt_parallel = params["batteries_in_parallel"]
    batteries = []
    batt_offset_vector = Base.Vector(0, 100, 0)
    for i in range(num_batt_series*num_batt_parallel):
        offset = (1 if i%2==0 else -1) * (i//2 + 1)
        batt_location = centre + offset * batt_offset_vector
        battery = create_object(electrical_group, batt_location, f"battery_{i}", colour=RED)
        batteries.append(battery)

        
    # Place MPPT Trackers
    num_mppt = params["num_mppt"]
    mppts = []
    mppt_offset_vector = batt_offset_vector * len(batteries)
    for i in range(num_mppt):
        # Placement of MPPTs is automatic currently, but may be ugly with odd number MPPTs
        # Can change to different placement later 
        offset = (1 if i%2==0 else -1) * (i//2 + 1)
        mppt_location = centre + offset * mppt_offset_vector
        mppt_unit = create_object(electrical_group, mppt_location, f"mppt_{i}", colour=BLUE)
        mppts.append(mppt_unit)
        
    # TODO: Redo wire connections using new parameters, mppt stuff and mppt series panels

    # Draw wires for panels
    panel_series_per_mppt = params["panels_in_series_per_mppt"]
    panel_parallel_per_mppt = params["panels_in_parallel_per_mppt"]
    panels_per_mppt = params["panels_per_mppt"]
    k = panel_series_per_mppt
    prev_point = None
    prev_panel = (-1, -1)  # To keep track of the last panel for connecting wires
    counter = 0

    # Assumption: Panels per string = Panels in series
    for i, panel_row in enumerate(panel_matrix):
        for j, panel in enumerate(panel_row):
            if i % 2 == 1:
                j = (len(panel_row) - 1) - j  # Reverse order for every second row

            if counter % k == 0:
                # Start of new string, connect from correct MPPT unit to positive end of panel
                panel_positive = positive_connections[i][j]
                bend = Base.Vector(panel_positive[0], panel_positive[1], central_z)
                mppt_idx = counter // panels_per_mppt
                mppt_location = mppts[mppt_idx].Placement.Base
                wire_name = f"panel_{i}_{j}_to_mppt_{mppt_idx}"
                prev_point = negative_connections[i][j]
                prev_panel = (i, j)
                color = RED
                create_sweep(electrical_group, "circle", radius, [panel_positive, bend, mppt_location], name=wire_name, color=color) # Red wire from panel to mppt                  
            
            else:
                if (counter % k) == (k - 1):
                    # End of a string, connect to negative terminal of mppt tracker, from panel
                    panel_negative = negative_connections[i][j]
                    bend = Base.Vector(panel_negative[0], panel_negative[1], central_z)
                    mppt_idx = counter // panels_per_mppt
                    mppt_location = mppts[mppt_idx].Placement.Base
                    wire_name = f"panel_{i}_{j}_to_mppt_{mppt_idx}"
                    color = BLUE

                    create_sweep(electrical_group, "circle", radius, [panel_negative, bend, mppt_location], name=wire_name, color=color) # Blue wire

                # Connnect two panels
                start_point = prev_point
                end_point = positive_connections[i][j]
                wire_name = f"panel_{i}_{j}_to_panel_{prev_panel[0]}_{prev_panel[1]}"
                prev_point = negative_connections[i][j]
                prev_panel = (i, j)
                color = PURPLE
            
                create_sweep(electrical_group, "circle", radius, [start_point, end_point], name=wire_name, color=color)

            counter += 1

    print("Created wiring for all panels")