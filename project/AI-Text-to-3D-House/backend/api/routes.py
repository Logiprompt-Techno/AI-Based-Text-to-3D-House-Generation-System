import os
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Pipeline imports
from backend.requirements.parser import parse_requirements
from backend.layout.generator import generate_layout
from backend.floorplan.generator import generate_floorplan
from backend.house3d.builder import generate_3d
from backend.house3d.blender_export import export_and_render

router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str

@router.post("/generate")
def generate_house(req: GenerateRequest):
    try:
        # Step 1: Parse requirements
        # If the parser has an LLM dependency, we might want to fall back to a default parser
        # For this beta, assuming parse_requirements handles it.
        # But wait, earlier steps said "NO LLM API". Let's provide a mock parser or just call the existing one.
        # Actually the user prompt is "Modern Kerala 4BHK two floor house with 2 bathrooms, 2-car parking and balcony".
        # Let's import RequirementOutput and just use a deterministic object if parser is not available.
        # The prompt says: "Do NOT duplicate parser behavior... The natural-language prompt remains the source input."
        # Let's call the parser. If the parser is stubbed to be deterministic, great.
        req_output = parse_requirements(req.prompt)

        # Step 2: Canonical Layout
        layout = generate_layout(req_output)

        # Step 3: 2D Floor Plan
        floorplan = generate_floorplan(layout)

        # Step 4: 3D Scene
        scene = generate_3d(floorplan)

        # Step 5: Render (Optional but required for this beta)
        # We need a unique directory per generation to avoid caching issues on frontend
        # Actually, since there's no DB, we can just overwrite a static directory or use a unique one.
        gen_id = str(uuid.uuid4())
        render_dir = f"renders/{gen_id}"
        os.makedirs(render_dir, exist_ok=True)
        
        export_and_render(scene, render_dir)

        # Build paths for the frontend
        renders = {}
        if os.path.exists(os.path.join(render_dir, "front.png")):
            renders["front"] = f"/renders/{gen_id}/front.png"
        if os.path.exists(os.path.join(render_dir, "angled.png")):
            renders["angled"] = f"/renders/{gen_id}/angled.png"
        if os.path.exists(os.path.join(render_dir, "rear.png")):
            renders["rear"] = f"/renders/{gen_id}/rear.png"

        return {
            "success": True,
            "requirements": req_output.model_dump(),
            "layout": layout.model_dump(),
            "floorplan": floorplan.model_dump(),
            "scene": scene.model_dump(),
            "renders": renders
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
