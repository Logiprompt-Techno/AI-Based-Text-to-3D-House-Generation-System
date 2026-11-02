import os
import json
import subprocess
from pathlib import Path
from .models import Scene3D

BLENDER_EXECUTABLE = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

def export_and_render(scene: Scene3D, output_dir: str):
    """
    Export the Scene3D model to a JSON file and invoke Blender in headless mode to render it.
    """
    if not os.path.exists(BLENDER_EXECUTABLE):
        raise FileNotFoundError(f"Blender executable not found at {BLENDER_EXECUTABLE}")

    os.makedirs(output_dir, exist_ok=True)
    
    scene_json_path = os.path.join(output_dir, "scene_data.json")
    with open(scene_json_path, "w", encoding="utf-8") as f:
        f.write(scene.model_dump_json(indent=2))

    script_path = os.path.join(os.path.dirname(__file__), "blender_script.py")
    
    cmd = [
        BLENDER_EXECUTABLE,
        "-b",  # Background/headless mode
        "-P", script_path,
        "--",  # Arguments after this are passed to the python script
        os.path.abspath(scene_json_path),
        os.path.abspath(output_dir)
    ]

    print("Invoking Blender...")
    print(" ".join(cmd))
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Blender Error Output:")
        print(result.stderr)
        print("Blender Standard Output:")
        print(result.stdout)
        raise RuntimeError("Blender execution failed.")
        
    print("Blender execution complete.")
