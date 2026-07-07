import importlib.util
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Optional

class RecognitionBridge:
    def __init__(self, ctis_dir: Optional[str] = None):
        default_dir = Path(__file__).resolve().parents[2] / ("CT" + "IS")
        legacy_env = "CT" + "IS_DIR"
        self.ctis_dir = Path(ctis_dir or os.getenv("GUOYUE_RECOGNITION_DIR", os.getenv(legacy_env, default_dir))).resolve()
        self._module = None
        self._models = None

    @property
    def available(self) -> bool:
        return (self.ctis_dir / "app.py").exists()

    def _load(self):
        if self._module is not None:
            return self._module
        if not self.available:
            raise RuntimeError(f"recognition model project not found at {self.ctis_dir}")
        sys.path.insert(0, str(self.ctis_dir))
        previous_cwd = Path.cwd()
        os.chdir(self.ctis_dir)
        try:
            spec = importlib.util.spec_from_file_location("guoyue_ctis_app", self.ctis_dir / "app.py")
            module = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(module)
            self._module = module
            return module
        finally:
            os.chdir(previous_cwd)
            try:
                sys.path.remove(str(self.ctis_dir))
            except ValueError:
                pass

    def model_names(self):
        if self._models is not None:
            return self._models
        module = self._load()
        previous_cwd = Path.cwd()
        os.chdir(self.ctis_dir)
        try:
            self._models = module.get_modelist(assign_model="regnet_y_32gf_cqt")
        finally:
            os.chdir(previous_cwd)
        return self._models

    def recognize(self, upload_path: Path, model_name: Optional[str] = None):
        module = self._load()
        models = self.model_names()
        selected_model = model_name if model_name in models else models[0]
        with tempfile.TemporaryDirectory(prefix="guoyue-audio-") as temp_dir:
            suffix = upload_path.suffix or ".wav"
            audio_path = Path(temp_dir) / f"input{suffix}"
            shutil.copyfile(upload_path, audio_path)
            previous_cwd = Path.cwd()
            os.chdir(self.ctis_dir)
            try:
                status, filename, result = module.infer(str(audio_path), selected_model)
            finally:
                os.chdir(previous_cwd)
        normalized_status = str(status or "").strip()
        is_success = normalized_status.lower() in {"", "success", "ok", "识别完成"}
        return {
            "ok": is_success,
            "status": normalized_status or "识别完成",
            "filename": filename or upload_path.name,
            "instrument": result,
            "model": selected_model,
        }
