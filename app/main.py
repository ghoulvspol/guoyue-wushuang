from pathlib import Path
import json
import shutil
import time
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .recognition_bridge import RecognitionBridge
from .instruments import HERO_STATS, INSTRUMENTS

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
RUNTIME_DIR = ROOT.parent / ".runtime"
UPLOAD_DIR = RUNTIME_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="国乐无双",
    description="可安装的中国传统乐器识别、图鉴与沉浸式学习应用",
    version="1.0.0",
)
bridge = RecognitionBridge()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/manifest.webmanifest")
def manifest():
    return FileResponse(STATIC_DIR / "manifest.webmanifest", media_type="application/manifest+json")

@app.get("/service-worker.js")
def service_worker():
    return FileResponse(STATIC_DIR / "service-worker.js", media_type="application/javascript")

@app.get("/api/health")
def health():
    return {"ok": True, "name": "国乐无双", "recognitionAvailable": bridge.available}

@app.get("/api/instruments")
def instruments():
    return {"stats": HERO_STATS, "items": INSTRUMENTS}

@app.get("/api/image-attributions")
def image_attributions():
    attribution_path = ROOT.parent / "data" / "image_attributions.json"
    if not attribution_path.exists():
        return {"items": []}
    return {"items": json.loads(attribution_path.read_text())}

@app.get("/api/models")
def models():
    try:
        return {"models": bridge.model_names(), "ctisDir": str(bridge.ctis_dir)}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"识别模型未就绪：{exc}") from exc

@app.post("/api/recognize")
async def recognize(audio: UploadFile = File(...), model: str = Form(default="")):
    if not audio.filename:
        raise HTTPException(status_code=400, detail="请上传音频文件")
    suffix = Path(audio.filename).suffix.lower()
    if suffix not in {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac"}:
        raise HTTPException(status_code=400, detail="仅支持 wav/mp3/m4a/flac/ogg/aac 音频")
    safe_name = f"{int(time.time() * 1000)}{suffix}"
    saved_path = UPLOAD_DIR / safe_name
    with saved_path.open("wb") as output:
        shutil.copyfileobj(audio.file, output)
    try:
        return bridge.recognize(saved_path, model or None)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"识别服务暂不可用：{exc}") from exc
    finally:
        saved_path.unlink(missing_ok=True)
