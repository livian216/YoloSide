"""
YoloSide v2.0 - Typed Application Settings

Replaces the fragile manual dict read/write in main.py with
a dataclass-based settings manager that handles:
- JSON persistence
- Old format auto-migration
- Type safety
"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
import json
import os


@dataclass
class InferenceSettings:
    """Detection/inference parameters."""
    iou: float = 0.45
    conf: float = 0.25
    rate: int = 10          # ms delay between frames
    imgsz: int = 640        # inference image size
    device: str = ""        # "" = auto, "cpu", "cuda:0", etc.


@dataclass
class SaveSettings:
    """Output saving options."""
    save_res: bool = False   # save annotated images/video
    save_txt: bool = False   # save YOLO-format txt labels
    save_crop: bool = False  # save cropped detections
    output_dir: str = ""     # custom output dir (empty = ./runs)


@dataclass
class UISettings:
    """UI state persistence."""
    task_type: str = "detect"
    last_model: str = "yolov8n.pt"
    last_source_type: str = "camera"  # "file", "camera", "rtsp", "batch"
    last_source: str = "0"
    open_fold: str = ""               # last folder for file dialog
    rtsp_ip: str = ""


@dataclass
class AppSettings:
    """Root settings container."""
    inference: InferenceSettings = field(default_factory=InferenceSettings)
    save_opts: SaveSettings = field(default_factory=SaveSettings)
    ui: UISettings = field(default_factory=UISettings)
    _version: int = 2  # schema version for migration

    # ── Persistence ────────────────────────────────────────────────

    @classmethod
    def load(cls, path: Path = Path("config/setting.json")) -> "AppSettings":
        """Load settings from JSON, auto-migrate old format."""
        if not path.exists():
            return cls._create_default(path)

        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        # Detect old v1 format (flat dict with 5 keys: iou, conf, rate, save_res, save_txt)
        if cls._is_v1_format(raw):
            return cls._migrate_v1(raw, path)

        # v2 format (nested)
        return cls(
            inference=InferenceSettings(
                iou=raw.get("inference", {}).get("iou", 0.45),
                conf=raw.get("inference", {}).get("conf", 0.25),
                rate=raw.get("inference", {}).get("rate", 10),
                imgsz=raw.get("inference", {}).get("imgsz", 640),
                device=raw.get("inference", {}).get("device", ""),
            ),
            save_opts=SaveSettings(
                save_res=bool(raw.get("save", {}).get("save_res", False)),
                save_txt=bool(raw.get("save", {}).get("save_txt", False)),
                save_crop=bool(raw.get("save", {}).get("save_crop", False)),
                output_dir=raw.get("save", {}).get("output_dir", ""),
            ),
            ui=UISettings(
                task_type=raw.get("ui", {}).get("task_type", "detect"),
                last_model=raw.get("ui", {}).get("last_model", "yolov8n.pt"),
                last_source_type=raw.get("ui", {}).get("last_source_type", "camera"),
                last_source=raw.get("ui", {}).get("last_source", "0"),
                open_fold=raw.get("ui", {}).get("open_fold", ""),
                rtsp_ip=raw.get("ui", {}).get("rtsp_ip", ""),
            ),
        )

    def save(self, path: Path = Path("config/setting.json")):
        """Save settings to JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "inference": asdict(self.inference),
            "save": asdict(self.save_opts),
            "ui": asdict(self.ui),
            "_version": self._version,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ── Migration ──────────────────────────────────────────────────

    @staticmethod
    def _is_v1_format(raw: dict) -> bool:
        """Check if the JSON is v1 format (flat: iou, conf, rate, save_res, save_txt)."""
        v1_keys = {"iou", "conf", "rate", "save_res", "save_txt"}
        return v1_keys.issubset(raw.keys()) and "_version" not in raw

    @classmethod
    def _migrate_v1(cls, raw: dict, path: Path) -> "AppSettings":
        """Migrate v1 flat settings to v2 nested format, then save."""
        settings = cls(
            inference=InferenceSettings(
                iou=raw.get("iou", 0.45),
                conf=raw.get("conf", 0.25),
                rate=raw.get("rate", 10),
            ),
            save_opts=SaveSettings(
                save_res=bool(raw.get("save_res", 0)),
                save_txt=bool(raw.get("save_txt", 0)),
            ),
        )
        # Also load legacy fold.json / ip.json into ui settings
        fold_path = path.parent / "fold.json"
        ip_path = path.parent / "ip.json"
        if fold_path.exists():
            with open(fold_path, "r", encoding="utf-8") as f:
                fold_data = json.load(f)
            settings.ui.open_fold = fold_data.get("open_fold", "")
        if ip_path.exists():
            with open(ip_path, "r", encoding="utf-8") as f:
                ip_data = json.load(f)
            settings.ui.rtsp_ip = ip_data.get("ip", "")

        # Save in new format
        settings.save(path)
        return settings

    @classmethod
    def _create_default(cls, path: Path) -> "AppSettings":
        """Create default settings and save."""
        settings = cls()
        settings.save(path)
        return settings


# ── Convenience ────────────────────────────────────────────────────

def load_config(config_dir: str = "config") -> AppSettings:
    """Convenience function: load AppSettings from a config directory."""
    return AppSettings.load(Path(config_dir) / "setting.json")


def save_config(settings: AppSettings, config_dir: str = "config"):
    """Convenience function: save AppSettings to a config directory."""
    settings.save(Path(config_dir) / "setting.json")


# ── Legacy file helpers (still used by file dialog & RTSP) ─────────

def load_fold_config(config_dir: str = "config") -> str:
    """Load last opened folder from fold.json (legacy compat)."""
    path = Path(config_dir) / "fold.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("open_fold", os.getcwd())
    return os.getcwd()


def save_fold_config(folder: str, config_dir: str = "config"):
    """Save last opened folder to fold.json (legacy compat)."""
    path = Path(config_dir) / "fold.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"open_fold": folder}, f, ensure_ascii=False, indent=2)


def load_ip_config(config_dir: str = "config") -> str:
    """Load last RTSP IP from ip.json."""
    path = Path(config_dir) / "ip.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("ip", "")
    return "rtsp://admin:admin888@192.168.1.2:555"


def save_ip_config(ip: str, config_dir: str = "config"):
    """Save RTSP IP to ip.json."""
    path = Path(config_dir) / "ip.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"ip": ip}, f, ensure_ascii=False, indent=2)
