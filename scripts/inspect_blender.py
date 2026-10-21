import bpy
import json
from pathlib import Path
summary = {"blender_version": bpy.app.version_string, "file": bpy.data.filepath, "scenes": [{"name": s.name, "frames": [s.frame_start, s.frame_end], "fps": s.render.fps, "objects": [{"name": o.name, "type": o.type} for o in s.objects]} for s in bpy.data.scenes]}
output = Path(r"D:/ai-generation-video/output/qa/blender-inspection.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False))
