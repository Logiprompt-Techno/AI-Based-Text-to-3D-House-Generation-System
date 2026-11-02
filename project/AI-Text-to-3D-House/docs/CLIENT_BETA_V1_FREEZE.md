# AI Text-to-3D House — Client Beta v1 Freeze

## 1. Current Status
**APPROVED — CLIENT BETA V1 FREEZE**

The project is stable, functionally complete according to the initial scope, and ready to be frozen as Client Beta v1.

## 2. Implemented Features
- User registration and authentication via JWT.
- Natural language requirement parsing.
- Deterministic 2D floor plan generation from parsed requirements.
- Extrusion-based 3D house geometry generation from 2D floor plans.
- Blender export support for high-quality rendering.
- Design persistence (Save, Load, Delete).
- Full frontend UI to interact with all generator features.

## 3. Core Architecture
The current verified pipeline strictly follows this deterministic flow:
User Prompt → Requirement Parser → Canonical House Layout → Validation → 2D Floor Plan → 3D House Geometry → Blender Export/Render → Save Design.
Both the 2D floor plan generator and the 3D geometry engine derive directly from the canonical layout representation produced by the parser and layout placement rules.

## 4. Backend
Built with FastAPI (Python 3.11). Verified modules include:
- `backend/api` (Routes for auth and designs)
- `backend/auth` (JWT and password hashing)
- `backend/db` (SQLAlchemy schemas and session management)
- `backend/requirements` (Parser models)
- `backend/layout` (Deterministic generator and geometry logic)
- `backend/floorplan` (2D generation from layout)
- `backend/house3d` (3D extrusion from layout)

## 5. Frontend
Built with React, Vite, and Tailwind CSS. The verified flow includes Login/Register screens, a Home dashboard, a Generator page for requirement input, components to display 2D floor plans and 3D house previews, and management pages to Save, Open, and Delete designs from the user's account. State is correctly managed with secure JWT tokens.

## 6. Database & Authentication
The system uses a local SQLite database (`app.db`) managed via SQLAlchemy. It includes `users` and `designs` tables. Password hashes are securely stored (no plaintext passwords). JWT authentication is strictly enforced, and cross-user design access is protected via database-level ownership checks. The `password_hash` is stripped from all API responses.

## 7. 2D Floor Plan
The 2D generator deterministically draws floor plans based on the bounding box coordinates (x, y, width, depth) produced by the layout engine, supporting multiple floors and basic room labels.

## 8. 3D House
The 3D house engine extrudes the 2D canonical footprint into 3D meshes (vertices and faces). It supports floor heights and wall thicknesses. It includes export capabilities to Blender format (Blender 4.3).

## 9. ResPlan Dataset
- The ResPlan dataset is used strictly for **research, evaluation, and reference only**.
- The isolated dataset loader, adapter, and evaluation scripts exist in `backend/dataset`.
- ResPlan is **NOT** the current generation engine. `/api/generate` operates entirely independently of ResPlan.
- No AI model training is part of Client Beta v1.

## 10. Verification Results
- **Backend Tests:** 87 / 87 Passed.
- **Frontend Build:** Successfully built via `vite build` (0 errors).
- No exposed secrets, `.env` variables, or raw password hashes were detected in the source/routes.
- The project structure strictly adheres to the requested architecture.

## 11. Known Limitations
- The current deterministic layout engine uses rigid rectangular bounding boxes and simple placement rules, which can occasionally lead to sub-optimal space utilization compared to real-world organic designs.
- The 3D engine currently produces basic extruded shells without complex roof geometries, interior decor, or parametric window/door placements.

## 12. Out of Scope
- AI Model Training (e.g., Graph-to-Layout neural networks).
- Integration of the ResPlan dataset into the live `/api/generate` endpoint.
- Advanced procedural generation of roofs, materials, and complex architectural styles.

## 13. Freeze Decision
**APPROVED — CLIENT BETA V1 FREEZE**
