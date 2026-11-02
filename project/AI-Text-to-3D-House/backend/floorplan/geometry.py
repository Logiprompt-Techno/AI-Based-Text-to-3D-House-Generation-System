from typing import List, Tuple, Dict
from ..layout.models import Room

eps = 1e-5

def merge_intervals(intervals: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    if not intervals:
        return []
    # Sort by start
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for current in intervals[1:]:
        prev = merged[-1]
        # If overlap or touching, merge
        if current[0] <= prev[1] + eps:
            merged[-1] = (prev[0], max(prev[1], current[1]))
        else:
            merged.append(current)
    return merged

def extract_walls(rooms: List[Room], b_width: float, b_depth: float) -> List[dict]:
    # Returns a list of dicts: {"x1": float, "y1": float, "x2": float, "y2": float, "is_exterior": bool}
    horizontals: Dict[float, List[Tuple[float, float]]] = {}
    verticals: Dict[float, List[Tuple[float, float]]] = {}
    
    for r in rooms:
        # Ignore external spaces for main wall generation
        if r.room_type.value in ("parking", "balcony", "terrace"):
            continue
            
        # Top (y)
        horizontals.setdefault(r.y, []).append((r.x, r.x + r.width))
        # Bottom (y+d)
        horizontals.setdefault(r.y + r.depth, []).append((r.x, r.x + r.width))
        # Left (x)
        verticals.setdefault(r.x, []).append((r.y, r.y + r.depth))
        # Right (x+w)
        verticals.setdefault(r.x + r.width, []).append((r.y, r.y + r.depth))
        
    walls = []
    
    # Pre-calculate all exterior segments for all rooms
    all_ext_segments = []
    for r in rooms:
        if r.room_type.value not in ("parking", "balcony", "terrace"):
            all_ext_segments.extend(find_all_exterior_wall_segments(r, rooms))

    # Process horizontals
    for y, intervals in horizontals.items():
        merged = merge_intervals(intervals)
        for (x1, x2) in merged:
            # Check if this segment overlaps any exterior horizontal segment at the same y
            is_exterior = False
            for ext in all_ext_segments:
                if ext["type"] == "horizontal" and abs(ext["fixed"] - y) < eps:
                    if max(x1, ext["start"]) < min(x2, ext["end"]) - eps:
                        is_exterior = True
                        break
            walls.append({"x1": x1, "y1": y, "x2": x2, "y2": y, "is_exterior": is_exterior})
            
    # Process verticals
    for x, intervals in verticals.items():
        merged = merge_intervals(intervals)
        for (y1, y2) in merged:
            # Check if this segment overlaps any exterior vertical segment at the same x
            is_exterior = False
            for ext in all_ext_segments:
                if ext["type"] == "vertical" and abs(ext["fixed"] - x) < eps:
                    if max(y1, ext["start"]) < min(y2, ext["end"]) - eps:
                        is_exterior = True
                        break
            walls.append({"x1": x, "y1": y1, "x2": x, "y2": y2, "is_exterior": is_exterior})
            
    return walls

def get_shared_boundary(r1: Room, r2: Room) -> dict:
    """
    If r1 and r2 share a boundary, returns {"type": "horizontal"|"vertical", "fixed": float, "start": float, "end": float}
    Else returns None.
    """
    x_overlap_start = max(r1.x, r2.x)
    x_overlap_end = min(r1.x + r1.width, r2.x + r2.width)
    y_overlap_start = max(r1.y, r2.y)
    y_overlap_end = min(r1.y + r1.depth, r2.y + r2.depth)
    
    # Touch left/right?
    if abs(r1.x + r1.width - r2.x) < eps or abs(r2.x + r2.width - r1.x) < eps:
        if y_overlap_end > y_overlap_start + eps:
            fixed_x = r1.x + r1.width if abs(r1.x + r1.width - r2.x) < eps else r2.x + r2.width
            return {"type": "vertical", "fixed": fixed_x, "start": y_overlap_start, "end": y_overlap_end}
            
    # Touch top/bottom?
    if abs(r1.y + r1.depth - r2.y) < eps or abs(r2.y + r2.depth - r1.y) < eps:
        if x_overlap_end > x_overlap_start + eps:
            fixed_y = r1.y + r1.depth if abs(r1.y + r1.depth - r2.y) < eps else r2.y + r2.depth
            return {"type": "horizontal", "fixed": fixed_y, "start": x_overlap_start, "end": x_overlap_end}
            
    return None

def find_exterior_wall_segment(room: Room, b_width: float, b_depth: float) -> dict:
    """
    Returns the first exterior wall segment of a room, if any.
    {"type": "horizontal"|"vertical", "fixed": float, "start": float, "end": float}
    """
    if abs(room.y) < eps:
        return {"type": "horizontal", "fixed": 0.0, "start": room.x, "end": room.x + room.width}
    if abs(room.y + room.depth - b_depth) < eps:
        return {"type": "horizontal", "fixed": b_depth, "start": room.x, "end": room.x + room.width}
    if abs(room.x) < eps:
        return {"type": "vertical", "fixed": 0.0, "start": room.y, "end": room.y + room.depth}
    if abs(room.x + room.width - b_width) < eps:
        return {"type": "vertical", "fixed": b_width, "start": room.y, "end": room.y + room.depth}
    return None

def find_all_exterior_wall_segments(room: Room, all_rooms: List[Room]) -> List[dict]:
    """
    Returns all exterior wall segments of a room.
    A segment is exterior if it does not touch any other internal room.
    """
    segments = []
    
    # Check Top (y = room.y)
    # Are there any internal rooms that share this boundary?
    def is_free(fixed_y, start_x, end_x, is_horizontal=True):
        # Very simplified: just check if any room overlaps this exact segment
        for r in all_rooms:
            if r.id == room.id or r.room_type.value in ("parking", "balcony", "terrace", "main_entrance"):
                continue
            if is_horizontal:
                if abs(r.y + r.depth - fixed_y) < eps or abs(r.y - fixed_y) < eps:
                    # check x overlap
                    if max(start_x, r.x) < min(end_x, r.x + r.width) - eps:
                        return False
            else:
                if abs(r.x + r.width - fixed_y) < eps or abs(r.x - fixed_y) < eps:
                    # check y overlap
                    if max(start_x, r.y) < min(end_x, r.y + r.depth) - eps:
                        return False
        return True

    if is_free(room.y, room.x, room.x + room.width, True):
        segments.append({"type": "horizontal", "fixed": room.y, "start": room.x, "end": room.x + room.width})
        
    if is_free(room.y + room.depth, room.x, room.x + room.width, True):
        segments.append({"type": "horizontal", "fixed": room.y + room.depth, "start": room.x, "end": room.x + room.width})
        
    if is_free(room.x, room.y, room.y + room.depth, False):
        segments.append({"type": "vertical", "fixed": room.x, "start": room.y, "end": room.y + room.depth})
        
    if is_free(room.x + room.width, room.y, room.y + room.depth, False):
        segments.append({"type": "vertical", "fixed": room.x + room.width, "start": room.y, "end": room.y + room.depth})
        
    return segments
