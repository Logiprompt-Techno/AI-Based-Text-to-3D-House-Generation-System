# PROJECT STATUS & ROOT-CAUSE AUDIT

**Project:** AI-Text-to-3D-House
**Date:** 2026-09-06

## 1. CURRENT PROJECT INVENTORY

- `backend/`: **PARTIAL**. Contains the core pipeline (`requirements`, `layout`, `floorplan`, `house3d`), but relies on simplistic grid-based logic. No API server (`app.py` is missing).
- `frontend/`: **PARTIAL**. Basic HTML/CSS/JS present in `homevision-ar` folder, but not connected to the backend.
- `tests/`: **PARTIAL**. Programmatic geometry checks only.
- `docs/`: **PARTIAL**. Contains architecture and step documentation.
- `renders/`: **COMPLETE (Technically)**. Generates output, but visually poor.
- **Database:** **UNUSED** (as requested).
- **Unused/Dead Code:** None detected. Clean rewrite.

## 2. PHASE-BY-PHASE AUDIT

### STEP 1 - Requirement Parsing
- **Implementation:** Pydantic models validate constraints (floors, beds, plot size).
- **Automated verification:** Tested via `test_requirements.py`.
- **Visual verification:** N/A.
- **Missing:** Natural language parsing into the Pydantic models (currently manually mocked in tests).
- **Risks:** Missing input sanitization for edge cases.
- **Status:** **PARTIAL**

### STEP 2 - Canonical Layout
- **Implementation:** Hardcoded bin-packing into a fixed 12m width (5m Left Bay, 2m Spine, 5m Right Bay).
- **Automated verification:** Room existence tests.
- **Visual verification:** None.
- **Missing:** Dynamic topological generation. Rooms are forced into unnatural shapes and positions.
- **Risks:** Cannot handle complex shapes, L-shapes, or varying plot widths accurately.
- **Status:** **BROKEN (Architecturally)**

### STEP 3 - 2D Floor Plan
- **Implementation:** Extracts exterior/interior boundaries from layout blocks.
- **Automated verification:** Wall and opening counts.
- **Visual verification:** Exportable as data, but lacks visual rendering tests.
- **Missing:** Proper wall intersections (miter joints). Doors are naïvely placed exactly in the center of shared walls.
- **Risks:** Doors might clash with adjacent walls.
- **Status:** **PARTIAL**

### STEP 4 - 3D House Geometry
- **Implementation:** Extrudes walls into boxes. Slabs and roofs are bounding-box wide flat cubes.
- **Automated verification:** Basic coordinate assertions.
- **Visual verification:** Assessed via renders (Step 5).
- **Missing:** Real staircases (currently solid blocks). Pitched roofs (currently flat slabs). True window geometry.
- **Risks:** Overlapping geometry (Z-fighting) at corners.
- **Status:** **PARTIAL**

### STEP 4A - 3D Physical/Visual Verification
- **Implementation:** Programmatic script exists (`step4a_verify.py`).
- **Automated verification:** Validates geometric boundaries.
- **Missing:** Visual sanity checks (e.g. "can a human walk up this stair?").
- **Status:** **PARTIAL**

### STEP 5 - Blender Architectural Render
- **Implementation:** `blender_script.py` uses Blender's Python API to generate cubes and boolean cuts.
- **Automated verification:** Checks if PNGs are generated.
- **Visual verification:** Fails architectural standards. Flat shading, basic colors, no details.
- **Missing:** Realistic materials, environment/lighting, window frames, pitched roofs.
- **Risks:** Boolean modifiers often fail on exactly coplanar faces, leading to missing doors/windows.
- **Status:** **PARTIAL**

## 3. TRACE THE COMPLETE PIPELINE

| Stage | Module | Input | Output | Potential Failure / Information Loss |
|-------|--------|-------|--------|---------------------------------------|
| **Reqs** | `requirements.models` | Prompt (Mocked) | `RequirementOutput` | NLP extraction isn't hooked up yet. |
| **Layout** | `layout.generator` | `RequirementOutput` | `HouseLayout` | Rigid grid forces all houses to 12m wide. |
| **Floorplan** | `floorplan.generator` | `HouseLayout` | `FloorPlan` | Doors placed in exact center of walls; might cause impossible geometry. |
| **3D Geo** | `house3d.builder` | `FloorPlan` | `Scene3D` | Slabs/Roofs ignore room indentations, use full bounding box. |
| **Render** | `house3d.blender_export` | `Scene3D` | `.png` renders | Boolean cuts might fail; no architectural detailing. |

## 4. SINGLE SOURCE OF TRUTH AUDIT

There is **mostly** one canonical geometry (the Layout rooms).
However, **duplications/simplifications exist**:
- **Slabs/Roofs:** `house3d.builder` calculates slabs and roofs using `floorplan.building_width` and `building_depth` bounding box instead of tracing the actual exterior walls. A U-shaped house would have a roof covering the empty courtyard.
- **Wall Thickness:** Added retroactively in `builder.py`, creating overlapping blocks at wall intersections rather than clean continuous meshes.

## 5. 2D FLOOR PLAN QUALITY AUDIT

- **Room Proportions:** Unrealistic. Fixed to 5m wide bays.
- **Circulation:** Forced 2m central spine.
- **Doors:** Placed exactly in the middle of shared boundaries. A tiny shared boundary will result in an impossible door.
- **Staircase:** Placed identically on both floors without checking if the ground floor landing aligns correctly with the entrance.

## 6. 3D GEOMETRY AUDIT

- **WALLS:** Overlapping corners (no miter).
- **FLOORS:** Flat slabs covering the entire bounding box.
- **STAIRCASE:** Represented as a solid cube (`Material.STAIRS`). Unusable.
- **ROOF:** Simple flat bounding-box slab hovering over the walls.
- **DOORS/WINDOWS:** Just boolean cuts. No frames, no glass thickness.

## 7. BLENDER PIPELINE AUDIT

- **Execution:** Calls Blender via subprocess. Fails completely if Blender isn't in PATH.
- **Geometry Construction:** Primitive cubes and boolean `DIFFERENCE`.
- **Risks:** Blender booleans are notoriously unstable with exactly coincident faces. Since wall corners overlap and cutters are perfectly aligned on the Z-axis, it can silently fail to cut holes.

## 8. 3D VISUAL QUALITY GAP ANALYSIS

- **ARCHITECTURAL COMPLETENESS:** **WEAK**. Solid block staircases, flat roofs.
- **PROPORTIONS:** **WEAK**. Forced 12m wide grid.
- **GEOMETRY QUALITY:** **WEAK**. Z-fighting at corners.
- **MATERIAL / SHADING QUALITY:** **WEAK**. Basic diffuse colors. No textures.
- **LIGHTING:** **ACCEPTABLE**. Simple Sun + Ambient is okay for a start.
- **CAMERA:** **ACCEPTABLE**. Basic framing works.
- **ENVIRONMENT:** **MISSING**. Empty void.

## 9. ERROR / FAILURE ROOT CAUSE ANALYSIS

### CRITICAL
- **Problem:** Missing/Uncut Doors and Windows in Renders.
- **Root Cause:** Blender Boolean modifier failure due to coplanar faces or overlapping geometry in `blender_script.py`.
- **Current Protection:** Cutters are made slightly thicker (+0.5).
- **Missing Protection:** Proper vertex merging and non-overlapping wall generation in python.

### HIGH
- **Problem:** Roofs covering open courtyards / balconies.
- **Root Cause:** `house3d/builder.py` uses the full building bounding box for the roof.

## 10. TEST COVERAGE AUDIT

- **Total Tests:** Present across all 4 stages.
- **What they verify:** Array lengths, basic coordinates, file generation.
- **What they DO NOT verify:** Architectural validity (e.g. "Do walls overlap?", "Is the staircase passable?").
- **False Confidence:** Tests PASS completely, giving a false sense of beta-readiness.

## 11. FRONTEND / USER FLOW AUDIT

- **UI Exists:** `homevision-ar` has HTML/CSS/JS.
- **Integration:** **MISSING**. There is no backend web server (`app.py` is absent). The frontend is entirely disconnected from the python logic.

## 12. DATABASE / STORAGE AUDIT

- **Status:** NO DATABASE FOUND. Clean.

## 13. SECURITY / RELIABILITY AUDIT

- **Subprocess Failures:** `blender_export.py` assumes successful execution. No robust error parsing of Blender's stdout.
- **Temp Files:** Renders overwrite existing files. Could cause permission errors if files are locked.

## 14. EXACT PENDING WORK

### MUST DO BEFORE BETA
1. Create a Flask/FastAPI `app.py` to connect the frontend to the backend pipeline.
2. Fix wall intersections (generate continuous loops instead of overlapping blocks).
3. Fix Boolean cuts in Blender (ensure cutters extend cleanly past the wall boundaries).

### SHOULD DO FOR GOOD QUALITY
1. Implement a pitched roof generator instead of a flat bounding box.
2. Generate step-geometry for staircases instead of solid blocks.
3. Add window and door frames in Blender.

### DO NOT DO
- Do NOT implement user auth or databases.

## 15. 3D PERFECTION GAP

**Score: 15%**
*We are very far from professional visualization. The output is currently a grey-box massing model.*
- Geometry: 20%
- Architecture: 10%
- Openings: 15%
- Roof: 5%
- Staircase: 0% (Solid block)
- Materials: 10%

## 16. FINAL PROJECT STATUS

- STEP 1 [PARTIAL]
- STEP 2 [BROKEN]
- STEP 3 [PARTIAL]
- STEP 4 [PARTIAL]
- STEP 4A [PARTIAL]
- STEP 5 [PARTIAL]
- FRONTEND [DISCONNECTED]
- BETA READY: **NO**

**Biggest remaining problem:** The rigidly hardcoded 12m layout grid prevents realistic floorplans, and the frontend is entirely disconnected from the backend.
**What to fix FIRST:** Create `app.py` to establish the end-to-end user flow before refining geometry.
**What to NOT touch:** The Pydantic model definitions; they are solid.
