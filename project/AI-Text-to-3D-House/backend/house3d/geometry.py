def boxes_intersect(x1, y1, w1, d1, x2, y2, w2, d2, tol=0.01) -> bool:
    """Check if two 2D bounding boxes intersect."""
    return not (x1 + w1 - tol <= x2 or 
                x2 + w2 - tol <= x1 or 
                y1 + d1 - tol <= y2 or 
                y2 + d2 - tol <= y1)

def box_contains(outer_x, outer_y, outer_w, outer_d, inner_x, inner_y, inner_w, inner_d, tol=0.01) -> bool:
    """Check if outer box fully contains inner box."""
    return (inner_x >= outer_x - tol and 
            inner_y >= outer_y - tol and 
            inner_x + inner_w <= outer_x + outer_w + tol and 
            inner_y + inner_d <= outer_y + outer_d + tol)

def validate_opening_in_wall(wall_x1, wall_y1, wall_x2, wall_y2, thickness, op_x, op_y, op_w, tol=0.05) -> bool:
    """
    Validate that an opening is physically located within the host wall bounds.
    Wall is defined by its center line (x1,y1) to (x2,y2).
    Opening is defined by its center point (op_x, op_y).
    """
    if abs(wall_x1 - wall_x2) < tol:
        # Vertical wall
        if abs(op_x - wall_x1) > thickness / 2 + tol:
            return False
        min_y, max_y = min(wall_y1, wall_y2), max(wall_y1, wall_y2)
        if op_y - op_w/2 < min_y - tol or op_y + op_w/2 > max_y + tol:
            return False
        return True
    elif abs(wall_y1 - wall_y2) < tol:
        # Horizontal wall
        if abs(op_y - wall_y1) > thickness / 2 + tol:
            return False
        min_x, max_x = min(wall_x1, wall_x2), max(wall_x1, wall_x2)
        if op_x - op_w/2 < min_x - tol or op_x + op_w/2 > max_x - tol:
            return False
        return True
    return False

def segment_wall_with_openings(w_x1: float, w_y1: float, w_x2: float, w_y2: float, w_thickness: float, w_height: float, openings: list) -> list:
    """
    Given a wall and a list of openings (dict with 'x', 'y', 'width', 'type'), 
    return a list of Constructive Solid Geometry blocks to represent the wall with holes.
    Each block is a dict: {'x': float, 'y': float, 'w': float, 'd': float, 'z': float, 'h': float}
    Coordinates are the lower-left corner for the block.
    """
    blocks = []
    is_vert = abs(w_x1 - w_x2) < 0.01
    
    # Base dimensions
    length = abs(w_y2 - w_y1) if is_vert else abs(w_x2 - w_x1)
    base_x = w_x1 - w_thickness/2 if is_vert else min(w_x1, w_x2)
    base_y = min(w_y1, w_y2) if is_vert else w_y1 - w_thickness/2
    
    # Sort openings along the wall axis
    ops = []
    for o in openings:
        pos = o['y'] if is_vert else o['x']
        # Convert absolute position to relative position along the wall
        rel_pos = pos - min(w_y1, w_y2) if is_vert else pos - min(w_x1, w_x2)
        ops.append({
            'start': max(0.0, rel_pos - o['width']/2),
            'end': min(length, rel_pos + o['width']/2),
            'type': o['type']
        })
    
    ops.sort(key=lambda x: x['start'])
    
    # 1. Fill vertical gaps between openings
    cursor = 0.0
    for o in ops:
        if o['start'] > cursor:
            # Solid block from cursor to start
            if is_vert:
                blocks.append({'x': base_x, 'y': base_y + cursor, 'w': w_thickness, 'd': o['start'] - cursor, 'z': 0.0, 'h': w_height})
            else:
                blocks.append({'x': base_x + cursor, 'y': base_y, 'w': o['start'] - cursor, 'd': w_thickness, 'z': 0.0, 'h': w_height})
                
        # Fill above/below the opening
        if o['type'] in ('door', 'entrance'):
            door_h = 2.1
            if w_height > door_h:
                if is_vert:
                    blocks.append({'x': base_x, 'y': base_y + o['start'], 'w': w_thickness, 'd': o['end'] - o['start'], 'z': door_h, 'h': w_height - door_h})
                else:
                    blocks.append({'x': base_x + o['start'], 'y': base_y, 'w': o['end'] - o['start'], 'd': w_thickness, 'z': door_h, 'h': w_height - door_h})
        elif o['type'] == 'window':
            sill = 1.0
            win_h = 1.4
            # Sill block
            if is_vert:
                blocks.append({'x': base_x, 'y': base_y + o['start'], 'w': w_thickness, 'd': o['end'] - o['start'], 'z': 0.0, 'h': sill})
            else:
                blocks.append({'x': base_x + o['start'], 'y': base_y, 'w': o['end'] - o['start'], 'd': w_thickness, 'z': 0.0, 'h': sill})
            
            # Header block
            header_z = sill + win_h
            if w_height > header_z:
                if is_vert:
                    blocks.append({'x': base_x, 'y': base_y + o['start'], 'w': w_thickness, 'd': o['end'] - o['start'], 'z': header_z, 'h': w_height - header_z})
                else:
                    blocks.append({'x': base_x + o['start'], 'y': base_y, 'w': o['end'] - o['start'], 'd': w_thickness, 'z': header_z, 'h': w_height - header_z})
                    
        cursor = max(cursor, o['end'])
        
    # Fill remaining wall after last opening
    if cursor < length:
        if is_vert:
            blocks.append({'x': base_x, 'y': base_y + cursor, 'w': w_thickness, 'd': length - cursor, 'z': 0.0, 'h': w_height})
        else:
            blocks.append({'x': base_x + cursor, 'y': base_y, 'w': length - cursor, 'd': w_thickness, 'z': 0.0, 'h': w_height})
            
    return blocks
