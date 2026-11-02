import { useState, useMemo } from 'react';
import type { FloorPlan, Opening } from '../types/house';

interface Props {
    floorplan: FloorPlan;
}

export function FloorPlanViewer({ floorplan }: Props) {
    const [selectedFloorNum, setSelectedFloorNum] = useState<number>(0);

    const floor = useMemo(() => {
        return floorplan.floors.find(f => f.floor_number === selectedFloorNum) || floorplan.floors[0];
    }, [floorplan, selectedFloorNum]);

    if (!floor) return <div>No floor plan available.</div>;

    // Calculate bounding box for SVG viewbox
    let minX = 0, minY = 0, maxX = 10, maxY = 10;
    if (floor.room_boundaries.length > 0) {
        minX = Math.min(...floor.room_boundaries.map(r => r.x));
        minY = Math.min(...floor.room_boundaries.map(r => r.y));
        maxX = Math.max(...floor.room_boundaries.map(r => r.x + r.width));
        maxY = Math.max(...floor.room_boundaries.map(r => r.y + r.depth));
        
        // Add padding
        minX -= 3;
        minY -= 3;
        maxX += 3;
        maxY += 3;
    }

    const viewBox = `${minX} ${minY} ${maxX - minX} ${maxY - minY}`;

    const renderOpening = (opening: Opening) => {
        const wall = floor.walls.find(w => w.id === opening.wall_id);
        if (!wall) return null;
        
        // Check if wall is horizontal or vertical based on geometry
        const isHorizontal = Math.abs(wall.y1 - wall.y2) < 0.1;
        const thickness = wall.thickness;
        const w = opening.width;
        const cx = opening.x;
        const cy = opening.y;

        if (opening.opening_type === 'window') {
            const ww = isHorizontal ? w : thickness;
            const hh = isHorizontal ? thickness : w;
            const x = cx - ww/2;
            const y = cy - hh/2;
            
            return (
                <g key={opening.id}>
                    {/* Cut out the wall */}
                    <rect x={x} y={y} width={ww} height={hh} fill="#fff" />
                    {/* Window frame / glass */}
                    {isHorizontal ? (
                        <>
                            <line x1={x} y1={y} x2={x+ww} y2={y} stroke="#64748b" strokeWidth="0.05" />
                            <line x1={x} y1={y+hh} x2={x+ww} y2={y+hh} stroke="#64748b" strokeWidth="0.05" />
                            <line x1={x} y1={cy} x2={x+ww} y2={cy} stroke="#94a3b8" strokeWidth="0.03" />
                        </>
                    ) : (
                        <>
                            <line x1={x} y1={y} x2={x} y2={y+hh} stroke="#64748b" strokeWidth="0.05" />
                            <line x1={x+ww} y1={y} x2={x+ww} y2={y+hh} stroke="#64748b" strokeWidth="0.05" />
                            <line x1={cx} y1={y} x2={cx} y2={y+hh} stroke="#94a3b8" strokeWidth="0.03" />
                        </>
                    )}
                </g>
            );
        } else if (opening.opening_type === 'door' || opening.opening_type === 'entrance') {
            const isMain = opening.opening_type === 'entrance';
            const doorColor = isMain ? "#334155" : "#64748b";
            
            const ww = isHorizontal ? w : thickness;
            const hh = isHorizontal ? thickness : w;
            const x = cx - ww/2;
            const y = cy - hh/2;

            return (
                <g key={opening.id}>
                    {/* Cut out wall */}
                    <rect x={x} y={y} width={ww} height={hh} fill="#fff" />
                    
                    {/* Architectural door symbol (Leaf + Swing arc) */}
                    {isHorizontal ? (
                        <path d={`M ${cx - w/2} ${cy} L ${cx - w/2} ${cy - w} A ${w} ${w} 0 0 1 ${cx + w/2} ${cy}`} fill="none" stroke={doorColor} strokeWidth="0.05" />
                    ) : (
                        <path d={`M ${cx} ${cy - w/2} L ${cx + w} ${cy - w/2} A ${w} ${w} 0 0 1 ${cx} ${cy + w/2}`} fill="none" stroke={doorColor} strokeWidth="0.05" />
                    )}

                    {isMain && (
                        <text x={cx} y={cy + (isHorizontal ? 1.5 : -1.5)} fontSize="0.25" fill="#334155" fontWeight="bold" textAnchor="middle">
                            MAIN ENTRANCE
                        </text>
                    )}
                </g>
            );
        }
    };

    return (
        <div className="floorplan-viewer flex flex-col h-full bg-slate-50 rounded-xl overflow-hidden border border-slate-200 shadow-inner relative font-sans">
            <div className="floor-selector flex gap-2 p-4 justify-center bg-white/90 backdrop-blur-md border-b border-slate-200 absolute top-0 w-full z-10 shadow-sm">
                {floorplan.floors.map(f => (
                    <button
                        key={f.floor_number}
                        onClick={() => setSelectedFloorNum(f.floor_number)}
                        className={`px-6 py-2 text-sm font-semibold rounded-full transition-all duration-200 ${selectedFloorNum === f.floor_number ? 'bg-slate-800 text-white shadow-md transform scale-105' : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50 hover:border-slate-300'}`}
                    >
                        {f.floor_number === 0 ? 'Ground Floor' : `Floor ${f.floor_number}`}
                    </button>
                ))}
            </div>

            <div className="svg-container flex-1 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+CjxyZWN0IHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgZmlsbD0iI2ZmZiIvPgo8Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIxLjUiIGZpbGw9IiNmMThmNmYiLz4KPC9zdmc+')] flex items-center justify-center overflow-hidden pt-20 p-6">
                <svg viewBox={viewBox} className="w-full h-full max-h-[700px] origin-center drop-shadow-sm" preserveAspectRatio="xMidYMid meet">
                    {/* External spaces */}
                    {floor.external_spaces?.map(space => (
                        <g key={space.room_id}>
                            <rect
                                x={space.x}
                                y={space.y}
                                width={space.width}
                                height={space.depth}
                                fill={space.space_type === 'balcony' ? '#f8fafc' : '#f1f5f9'}
                                stroke="#94a3b8"
                                strokeWidth="0.08"
                                strokeDasharray={space.space_type === 'balcony' ? "0.2,0.2" : "none"}
                            />
                            {/* Visual divide for parking into 2 bays */}
                            {space.space_type === 'parking' && (
                                <line 
                                    x1={space.x + space.width / 2} 
                                    y1={space.y} 
                                    x2={space.x + space.width / 2} 
                                    y2={space.y + space.depth} 
                                    stroke="#cbd5e1" 
                                    strokeWidth="0.05" 
                                    strokeDasharray="0.3,0.3"
                                />
                            )}
                            <text
                                x={space.x + space.width / 2}
                                y={space.y + space.depth / 2}
                                fontSize="0.35"
                                fontWeight="bold"
                                textAnchor="middle"
                                dominantBaseline="middle"
                                fill="#64748b"
                                letterSpacing="0.05em"
                            >
                                {space.space_type.toUpperCase()}
                            </text>
                            {space.space_type === 'parking' && (
                                <text
                                    x={space.x + space.width / 2}
                                    y={space.y + space.depth / 2 + 0.4}
                                    fontSize="0.2"
                                    textAnchor="middle"
                                    dominantBaseline="middle"
                                    fill="#94a3b8"
                                >
                                    (2 Bays)
                                </text>
                            )}
                        </g>
                    ))}

                    {/* Rooms */}
                    {floor.room_boundaries.map(room => (
                        <g key={room.room_id}>
                            <rect
                                x={room.x}
                                y={room.y}
                                width={room.width}
                                height={room.depth}
                                fill="#ffffff"
                                stroke="#e2e8f0"
                                strokeWidth="0.05"
                            />
                            
                            {/* Staircase Treads */}
                            {room.room_type === 'staircase' && (
                                <g>
                                    {Array.from({length: Math.floor(room.depth / 0.3)}).map((_, i) => (
                                        <line 
                                            key={`stair-${i}`}
                                            x1={room.x} 
                                            y1={room.y + (i * 0.3)} 
                                            x2={room.x + room.width} 
                                            y2={room.y + (i * 0.3)} 
                                            stroke="#cbd5e1" 
                                            strokeWidth="0.02" 
                                        />
                                    ))}
                                </g>
                            )}

                            <text
                                x={room.x + room.width / 2}
                                y={room.y + room.depth / 2 - 0.15}
                                fontSize="0.35"
                                fontWeight="bold"
                                textAnchor="middle"
                                dominantBaseline="middle"
                                fill="#334155"
                                letterSpacing="0.02em"
                            >
                                {room.room_type.replace('_', ' ').toUpperCase()}
                            </text>
                            <text
                                x={room.x + room.width / 2}
                                y={room.y + room.depth / 2 + 0.3}
                                fontSize="0.22"
                                textAnchor="middle"
                                dominantBaseline="middle"
                                fill="#64748b"
                            >
                                {room.width.toFixed(1)}m × {room.depth.toFixed(1)}m
                            </text>
                        </g>
                    ))}

                    {/* Walls */}
                    {floor.walls.map(wall => (
                        <line
                            key={wall.id}
                            x1={wall.x1}
                            y1={wall.y1}
                            x2={wall.x2}
                            y2={wall.y2}
                            stroke={wall.is_exterior ? "#0f172a" : "#475569"}
                            strokeWidth={wall.thickness}
                            strokeLinecap="square"
                        />
                    ))}

                    {/* Openings (Doors / Windows / Entrances) */}
                    {floor.openings.map(o => renderOpening(o))}

                    {/* North Arrow */}
                    <g transform={`translate(${minX + 1.5}, ${minY + 1.5}) scale(0.6)`}>
                        <circle cx="0" cy="0" r="1.2" fill="#fff" stroke="#94a3b8" strokeWidth="0.05" />
                        <path d="M 0 -0.8 L 0.3 0.6 L 0 0.3 L -0.3 0.6 Z" fill="#334155" />
                        <text x="0" y="-1.1" fontSize="0.4" fontWeight="bold" textAnchor="middle" fill="#334155">N</text>
                    </g>

                    {/* Legend */}
                    <g transform={`translate(${minX + 1.5}, ${maxY - 2})`}>
                        <rect x="0" y="0" width="3.5" height="1.8" fill="#fff" stroke="#cbd5e1" strokeWidth="0.05" rx="0.1" />
                        <text x="0.3" y="0.4" fontSize="0.2" fontWeight="bold" fill="#334155">LEGEND</text>
                        
                        {/* Door legend */}
                        <path d="M 0.3 0.8 L 0.3 0.5 A 0.3 0.3 0 0 1 0.6 0.8" fill="none" stroke="#f59e0b" strokeWidth="0.03" />
                        <text x="0.8" y="0.8" fontSize="0.15" fill="#64748b">Door</text>

                        {/* Window legend */}
                        <rect x="0.3" y="1.1" width="0.4" height="0.1" fill="#fff" stroke="#0ea5e9" strokeWidth="0.03" />
                        <line x1="0.3" y1="1.15" x2="0.7" y2="1.15" stroke="#0ea5e9" strokeWidth="0.02" />
                        <text x="0.8" y="1.2" fontSize="0.15" fill="#64748b">Window</text>

                        {/* Entrance legend */}
                        <path d="M 0.3 1.6 L 0.3 1.3 A 0.3 0.3 0 0 1 0.6 1.6" fill="none" stroke="#ef4444" strokeWidth="0.03" />
                        <text x="0.8" y="1.6" fontSize="0.15" fill="#64748b">Main Entrance</text>
                    </g>

                    {/* Scale Indicator */}
                    <g transform={`translate(${maxX - 3.5}, ${maxY - 1})`}>
                        <line x1="0" y1="0" x2="2" y2="0" stroke="#334155" strokeWidth="0.05" />
                        <line x1="0" y1="-0.1" x2="0" y2="0.1" stroke="#334155" strokeWidth="0.05" />
                        <line x1="1" y1="-0.1" x2="1" y2="0.1" stroke="#334155" strokeWidth="0.05" />
                        <line x1="2" y1="-0.1" x2="2" y2="0.1" stroke="#334155" strokeWidth="0.05" />
                        <text x="0" y="-0.3" fontSize="0.2" textAnchor="middle" fill="#64748b">0</text>
                        <text x="1" y="-0.3" fontSize="0.2" textAnchor="middle" fill="#64748b">1m</text>
                        <text x="2" y="-0.3" fontSize="0.2" textAnchor="middle" fill="#64748b">2m</text>
                    </g>
                </svg>
            </div>
        </div>
    );
}
