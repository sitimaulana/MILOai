"""
Unit tests for Live2D model assets, vendor libraries, and FastAPI mounting.
"""

import json
import os

def test_live2d_assets_exist():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    live2d_dir = os.path.join(base_dir, "frontend", "assets", "live2d")

    assert os.path.exists(os.path.join(live2d_dir, "MILO Model.moc3")), "MILO Model.moc3 missing"
    assert os.path.exists(os.path.join(live2d_dir, "MILO Model.model3.json")), "MILO Model.model3.json missing"
    assert os.path.exists(os.path.join(live2d_dir, "MILO Model.cdi3.json")), "MILO Model.cdi3.json missing"
    assert os.path.exists(os.path.join(live2d_dir, "MILO Model.1024", "texture_00.png")), "texture_00.png missing"

def test_live2d_vendor_libraries_exist():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vendor_dir = os.path.join(base_dir, "frontend", "js", "vendor", "live2d")

    assert os.path.exists(os.path.join(vendor_dir, "live2dcubismcore.min.js")), "live2dcubismcore.min.js missing"
    assert os.path.exists(os.path.join(vendor_dir, "pixi.min.js")), "pixi.min.js missing"
    assert os.path.exists(os.path.join(vendor_dir, "cubism4.min.js")), "cubism4.min.js missing"
    assert os.path.exists(os.path.join(base_dir, "frontend", "js", "milo-live2d.js")), "milo-live2d.js missing"

def test_live2d_model3_json_configuration():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_json_path = os.path.join(base_dir, "frontend", "assets", "live2d", "MILO Model.model3.json")

    with open(model_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["Version"] == 3
    assert data["FileReferences"]["Moc"] == "MILO Model.moc3"
    assert len(data["FileReferences"]["Textures"]) > 0

    groups = {g["Name"]: g["Ids"] for g in data.get("Groups", [])}
    assert "EyeBlink" in groups, "EyeBlink group not found"
    assert "ParamEyeLOpen" in groups["EyeBlink"]
    assert "ParamEyeROpen" in groups["EyeBlink"]

    assert "LipSync" in groups, "LipSync group not found"
    assert "ParamMouthOpenY" in groups["LipSync"]

def test_live2d_endpoints_served_by_fastapi():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    # Test static files from /ui
    res = client.get("/ui/assets/live2d/MILO%20Model.model3.json")
    assert res.status_code == 200
    assert "Version" in res.json()

    res = client.get("/ui/js/milo-live2d.js")
    assert res.status_code == 200
    assert "MiloLive2DCompanion" in res.text

    # Test fallback mount at /live2dmodel
    res = client.get("/live2dmodel/MILO%20Model.model3.json")
    assert res.status_code == 200
