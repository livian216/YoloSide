"""
YoloSide v2.0 - Batch Processor

Processes all images in a folder using a given YOLO model.
Runs in its own QThread, reports progress via signals.
"""

from ultralytics import YOLO
from PySide6.QtCore import QObject, Signal

from engine.task_config import TaskType, TASK_REGISTRY

import numpy as np
import cv2
from pathlib import Path
import time


class BatchProcessor(QObject):
    """
    Standalone batch image processor.

    Creates its own YOLO instance internally (does not share with YoloEngine)
    so batch processing can run independently without blocking live inference.
    """

    # ── Signals ───────────────────────────────────────────────────
    file_progress = Signal(int, int)
    # (current_index, total_files)

    file_done = Signal(str, str)
    # (filename, status: "ok" / "error: msg")

    original_image = Signal(np.ndarray)
    # Original (source) image of the current file being processed

    current_image = Signal(np.ndarray)
    # Annotated image of the current file being processed

    batch_summary = Signal(dict)
    # e.g. {"total": 100, "success": 95, "errors": 5, "elapsed": 12.3}

    batch_finished = Signal()
    # Emitted when all files are processed

    status_update = Signal(str)
    # Status messages

    # ── Public API ─────────────────────────────────────────────────

    def __init__(self):
        super().__init__()
        self._model: YOLO | None = None
        self._model_name: str = ""
        self._task_type: TaskType = TaskType.DETECT
        self._stop_flag: bool = False

        # Parameters
        self.conf_thres: float = 0.25
        self.iou_thres: float = 0.45
        self.imgsz: int = 640
        self.save_res: bool = True
        self.save_txt: bool = False
        self.output_dir: str = ""

    def set_task(self, task_type: TaskType):
        self._task_type = task_type

    def set_model(self, model_path: str):
        self._model_name = model_path
        self._model = None

    def stop(self):
        self._stop_flag = True

    # ── Main processing loop ──────────────────────────────────────

    def run(self, folder_path: str):
        """
        Process all images in folder_path.
        Called via signal from the main thread after QThread starts.
        """
        self._stop_flag = False
        start_time = time.time()

        try:
            # Validate folder
            folder = Path(folder_path)
            if not folder.exists() or not folder.is_dir():
                self.status_update.emit(f"Error: folder not found: {folder_path}")
                self.batch_finished.emit()
                return

            # Find image files
            extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
            image_files = sorted([
                f for f in folder.iterdir()
                if f.suffix.lower() in extensions and f.is_file()
            ])

            if not image_files:
                self.status_update.emit("No image files found in folder.")
                self.batch_finished.emit()
                return

            total = len(image_files)
            self.status_update.emit(f"Found {total} images. Starting batch...")

            # Load model
            self._load_model()

            # Setup output directory
            if self.output_dir:
                out_dir = Path(self.output_dir)
            else:
                out_dir = folder / "results"
            out_dir.mkdir(parents=True, exist_ok=True)

            # Process each image
            success = 0
            errors = 0

            for idx, img_path in enumerate(image_files):
                if self._stop_flag:
                    self.status_update.emit("Batch processing stopped.")
                    break

                self.file_progress.emit(idx + 1, total)

                try:
                    if self._task_type == TaskType.TRACK:
                        results = self._model.track(
                            source=str(img_path),
                            conf=self.conf_thres,
                            iou=self.iou_thres,
                            imgsz=self.imgsz,
                            verbose=False,
                        )
                    else:
                        results = self._model.predict(
                            source=str(img_path),
                            conf=self.conf_thres,
                            iou=self.iou_thres,
                            imgsz=self.imgsz,
                            verbose=False,
                        )

                    result = results[0]

                    # Emit original and annotated images for GUI display
                    original = cv2.imread(str(img_path))
                    if original is not None:
                        self.original_image.emit(original)
                    annotated = result.plot()
                    self.current_image.emit(annotated)

                    # Save annotated image
                    if self.save_res:
                        save_path = out_dir / f"{img_path.stem}_annotated.jpg"
                        result.save(filename=str(save_path))

                    # Save txt labels
                    if self.save_txt:
                        txt_path = out_dir / f"{img_path.stem}.txt"
                        result.save_txt(txt_file=str(txt_path))

                    self.file_done.emit(img_path.name, "ok")
                    success += 1

                except Exception as e:
                    self.file_done.emit(img_path.name, f"error: {e}")
                    errors += 1

            # Emit summary
            elapsed = time.time() - start_time
            summary = {
                "total": total,
                "success": success,
                "errors": errors,
                "elapsed": round(elapsed, 1),
                "output_dir": str(out_dir),
            }
            self.batch_summary.emit(summary)
            self.status_update.emit(
                f"Batch done: {success}/{total} images in {elapsed:.1f}s. "
                f"Saved to {out_dir}"
            )
            self.batch_finished.emit()

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status_update.emit(f"Batch error: {e}")
            self.batch_finished.emit()

    # ── Private ────────────────────────────────────────────────────

    def _load_model(self):
        """Load YOLO model. Ultralytics auto-downloads if needed."""
        self.status_update.emit(f"Loading model: {self._model_name}...")
        self._model = YOLO(self._model_name)
        self.status_update.emit("Model loaded.")
