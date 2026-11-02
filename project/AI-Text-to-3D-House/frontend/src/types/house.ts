export type RoomType = 'master_bedroom' | 'bedroom' | 'bathroom' | 'kitchen' | 'living_room' | 'dining_room' | 'balcony' | 'parking' | 'staircase' | 'corridor' | 'unknown';

export interface RoomBoundary {
    room_id: string;
    room_type: RoomType;
    x: number;
    y: number;
    width: number;
    depth: number;
}

export interface Wall {
    id: string;
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    thickness: number;
    is_exterior: boolean;
}

export interface Opening {
    id: string;
    wall_id: string;
    opening_type: 'door' | 'window' | 'entrance';
    x: number;
    y: number;
    width: number;
}

export interface ExternalSpace {
    room_id: string;
    space_type: 'parking' | 'balcony';
    x: number;
    y: number;
    width: number;
    depth: number;
}

export interface FloorFloorPlan {
    floor_number: number;
    room_boundaries: RoomBoundary[];
    walls: Wall[];
    openings: Opening[];
    external_spaces: ExternalSpace[];
}

export interface FloorPlan {
    floors: FloorFloorPlan[];
}

export interface RequirementOutput {
    house_style?: string;
    house_type?: string;
    floors?: number;
    bedrooms?: number;
    bathrooms?: number;
    parking_spaces?: number;
    balconies?: number;
    terraces?: number;
    plot_width?: number;
    plot_depth?: number;
    roof_type?: string;
    special_requirements?: string[];
    source_text?: string;
}

export interface Renders {
    front?: string;
    angled?: string;
    rear?: string;
}

export interface DesignState {
    id: string;
    name?: string;
    createdAt: number;
    updatedAt: number;
    prompt: string;
    requirements: RequirementOutput;
    layout: any;
    floorplan: FloorPlan;
    scene: any;
    renders: Renders;
}
