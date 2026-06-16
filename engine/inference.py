"""
YoloSide v2.0 - Unified Inference Engine

Uses the modern ultralytics high-level API (YOLO class) instead of
subclassing BasePredictor. Supports all task types: detect, segment,
pose, classify, obb, and track.

Runs in a QThread, communicates with the main thread via Qt signals.
"""

from ultralytics import YOLO
from ultralytics.engine.results import Results
from PySide6.QtCore import QObject, Signal

from engine.task_config import TaskType, TaskConfig, TASK_REGISTRY, get_task_config

import numpy as np
import cv2
import time
from pathlib import Path


class YoloEngine(QObject):
    """
    Unified inference engine for all ultralytics task types.

    Runs in a QThread. Use signals to communicate results to the UI.
    Control via public methods: set_task(), set_model(), set_source(),
    run(), stop(), pause().
    """

    # ── Signals ───────────────────────────────────────────────────
    frame_processed = Signal(np.ndarray, np.ndarray)
    # (raw_frame, annotated_frame)

    status_update = Signal(str)
    # Status messages: "Loading model...", "Detecting...", etc.

    fps_update = Signal(float)
    # Real-time FPS (float)

    progress_update = Signal(int)
    # Progress bar value 0-1000

    detection_summary = Signal(dict)
    # Per-class counts: {"person": 3, "car": 1, ...}

    total_classes = Signal(int)
    # Number of unique classes in current frame

    total_targets = Signal(int)
    # Total number of detected targets in current frame

    inference_error = Signal(str)
    # Error messages from the inference loop

    processing_finished = Signal()
    # Emitted when the source is fully processed

    # ── Initialization ────────────────────────────────────────────

    def __init__(self):
        super().__init__()
        self._model: YOLO | None = None
        self._model_name: str = ""
        self._task_config: TaskConfig = TASK_REGISTRY[TaskType.DETECT]
        self._source: str = "0"

        # Runtime flags
        self._stop_flag: bool = False
        self._pause_flag: bool = False
        self._generator = None  # holds the active result generator for cleanup
        self._capture_refs: list = []  # saved cv2.VideoCapture refs for guaranteed release
        self._saved_dataset = None   # dataset object (to clear its .caps and prevent re-open)

        # Inference parameters
        self.iou_thres: float = 0.45
        self.conf_thres: float = 0.25
        self.speed_thres: int = 10       # ms delay between frames
        self.imgsz: int = 640
        self.device: str = ""            # "" = auto

        # Save options
        self.save_res: bool = False
        self.save_txt: bool = False

    # ── Public Control API (called from main thread) ───────────────

    def set_task(self, task_type: TaskType):
        """Set the task type (detect, segment, pose, classify, obb, track)."""
        self._task_config = get_task_config(task_type)

    def set_model(self, model_name: str):
        """
        Set the model to use. Can be:
        - A filename like 'yolov8n.pt' (auto-downloaded by ultralytics)
        - A local path like './models/my_model.pt'
        The model is loaded lazily when run() is called.
        """
        # Diagnostic: trace who sets _model = None during active inference
        if self._generator is not None and self._model is not None:
            import traceback
            print("[YoloEngine.set_model] WARNING: _model set to None while generator is active!", flush=True)
            traceback.print_stack()
        self._model_name = model_name
        self._model = None  # force reload

    def set_source(self, source: str):
        """Set input source: file path, camera index (0, 1, ...), RTSP URL, etc."""
        self._source = source

    def stop(self):
        """Fully stop inference and release ALL resources (camera, file, RTSP).

        IMPORTANT: We do NOT release cv2.VideoCapture objects from the
        main thread — on Windows, COM CoInitialize/CoUninitialize must
        happen in the SAME thread. Cross-thread release leaks COM
        resources, and after 2-3 cycles the MSMF driver enters a bad
        state (error -1072873821), ultralytics internally re-creates
        captures we can't track, and the camera LED stays on forever.

        Instead, we close the generator from here (which triggers
        ultralytics' internal cleanup) and let the worker thread's
        `finally` block do the actual cap.release() — all in the same
        thread where COM was initialized.
        """
        import gc
        print("[YoloEngine.stop] ENTERED", flush=True)
        print(f"[YoloEngine.stop] _generator is None: {self._generator is None}", flush=True)
        print(f"[YoloEngine.stop] _capture_refs count: {len(self._capture_refs)}", flush=True)
        print(f"[YoloEngine.stop] _saved_dataset: {self._saved_dataset is not None}", flush=True)

        self._stop_flag = True

        # 1) Stop the dataset's internal reader threads (if running).
        #    Setting running=False tells LoadStreams.update() to exit
        #    its loop, which unblocks the generator __next__ call.
        if self._saved_dataset is not None:
            try:
                if hasattr(self._saved_dataset, 'running'):
                    self._saved_dataset.running = False
                    print("[YoloEngine.stop] set dataset.running = False", flush=True)
            except Exception as e:
                print(f"[YoloEngine.stop] error stopping dataset threads: {e}", flush=True)

        # 2) Close the generator from the main thread.  CPython's GIL
        #    makes this safe — generator.close() throws GeneratorExit
        #    at the yield point, which triggers ultralytics' internal
        #    LoadStreams.close(), releasing caps properly.  The worker
        #    thread's next __next__() call receives StopIteration and
        #    falls through to the finally block for COM-safe cleanup.
        if self._generator is not None:
            try:
                self._generator.close()
                print("[YoloEngine.stop] generator.close() succeeded", flush=True)
            except Exception as e:
                print(f"[YoloEngine.stop] generator.close() error: {e}", flush=True)

        # 3) Clear our references — the actual cap.release() calls
        #    happen in the worker thread's finally block, where COM
        #    was initialized (same thread = safe).
        self._capture_refs = []
        self._saved_dataset = None

        # 4) Nuke model reference so nothing can re-open the camera
        if self._model is not None:
            try:
                pred = getattr(self._model, 'predictor', None)
                if pred is not None:
                    if hasattr(pred, 'dataset'):
                        pred.dataset = None
                    self._model.predictor = None
            except Exception as e:
                print(f"[YoloEngine.stop] predictor cleanup error: {e}", flush=True)
        self._model = None

        # 5) Force garbage collection
        gc.collect()
        print("[YoloEngine.stop] gc.collect() done", flush=True)

        # 6) Clear source
        self._source = ""
        print("[YoloEngine.stop] EXITED", flush=True)

    def _find_and_save_captures(self) -> list:
        """
        Traverse ultralytics internals RIGHT NOW (while self._model is alive
        and predictor.dataset exists) to find all cv2.VideoCapture objects.

        Also saves the dataset reference to self._saved_dataset so stop()
        can clear dataset.caps, preventing ultralytics from re-opening the
        camera during its error-recovery retry loop.

        Returns a list of cv2.VideoCapture references that stop() can
        release directly — no dependency on self._model.
        """
        caps = []
        try:
            pred = getattr(self._model, 'predictor', None)
            if pred is None:
                return caps
            ds = getattr(pred, 'dataset', None)
            if ds is None:
                return caps
            self._saved_dataset = ds  # save for later caps-clearing
            for attr_name in ('caps', 'cap', 'vid_cap', 'stream', 'capture'):
                obj = getattr(ds, attr_name, None)
                if obj is None:
                    continue
                items = obj if isinstance(obj, (list, tuple)) else [obj]
                for c in items:
                    if c is not None and isinstance(c, cv2.VideoCapture):
                        caps.append(c)
                        print(f"[_find_and_save_captures] saved cap from '{attr_name}'", flush=True)
        except Exception as e:
            print(f"[_find_and_save_captures] error: {e}", flush=True)
        print(f"[_find_and_save_captures] total saved: {len(caps)}", flush=True)
        return caps

    def _release_capture(self):
        """Traverse ultralytics internals to find and release ALL cv2.VideoCapture objects."""
        import sys
        print("[_release_capture] ENTERED", flush=True)
        try:
            pred = getattr(self._model, 'predictor', None)
            print(f"[_release_capture] predictor exists: {pred is not None}", flush=True)
            if pred is None:
                print(f"[_release_capture] predictor attributes: {[a for a in dir(self._model) if not a.startswith('_')]}", flush=True)
                return
            ds = getattr(pred, 'dataset', None)
            print(f"[_release_capture] dataset exists: {ds is not None}", flush=True)
            if ds is None:
                print(f"[_release_capture] predictor attributes: {[a for a in dir(pred) if not a.startswith('_')]}", flush=True)
                return
            print(f"[_release_capture] dataset type: {type(ds).__name__}", flush=True)
            print(f"[_release_capture] dataset attributes: {[a for a in dir(ds) if not a.startswith('_')]}", flush=True)
            # Try every known attribute name for VideoCapture(s)
            found = False
            for attr_name in ('caps', 'cap', 'vid_cap', 'stream', 'capture', 'video'):
                obj = getattr(ds, attr_name, None)
                if obj is None:
                    continue
                print(f"[_release_capture] found attr '{attr_name}', type={type(obj).__name__}", flush=True)
                if isinstance(obj, (list, tuple)):
                    for i, c in enumerate(obj):
                        try:
                            if c is not None and hasattr(c, 'isOpened') and c.isOpened():
                                c.release()
                                found = True
                                print(f"[_release_capture] RELEASED caps[{i}]", flush=True)
                            else:
                                print(f"[_release_capture] caps[{i}] not opened or None", flush=True)
                        except Exception as e:
                            print(f"[_release_capture] error releasing caps[{i}]: {e}", flush=True)
                elif hasattr(obj, 'isOpened'):
                    if obj.isOpened():
                        obj.release()
                        found = True
                        print(f"[_release_capture] RELEASED '{attr_name}'", flush=True)
                    else:
                        print(f"[_release_capture] '{attr_name}' not opened", flush=True)
            if not found:
                print("[_release_capture] NO VideoCapture found in dataset!", flush=True)
        except Exception as e:
            import traceback
            print(f"[_release_capture] EXCEPTION: {e}", flush=True)
            traceback.print_exc()

    def pause(self, paused: bool):
        """Pause or resume the inference loop."""
        self._pause_flag = paused

    # ── Main Inference Loop (runs in QThread) ─────────────────────

    def run(self):
        """
        Main inference loop. Called via signal from the main thread
        after the QThread starts.
        """
        self._generator = None
        try:
            self._stop_flag = False
            self._pause_flag = False

            if not self._source:
                self.inference_error.emit("No source selected.")
                return

            # Load model (ultralytics auto-downloads if needed)
            self._load_model()

            # Create the appropriate result generator
            self._generator = self._create_generator()

            # ── CRITICAL: Save direct cv2.VideoCapture references NOW ──
            # Because self._model may become None before stop() is called
            # (e.g. via set_model() from timer/model refresh on main thread).
            # We save the raw cv2.VideoCapture objects so stop() can release
            # them directly without needing self._model at all.
            self._capture_refs = self._find_and_save_captures()

            frame_count = 0
            start_time = time.time()
            total_frames = self._get_total_frames()

            self.status_update.emit("Detecting...")

            for result in self._generator:
                # If ultralytics lazily initialised the capture on first yield,
                # re-scan now so we have the ref for stop().
                if not self._capture_refs:
                    self._capture_refs = self._find_and_save_captures()

                if self._stop_flag:
                    break

                # Handle pause
                while self._pause_flag and not self._stop_flag:
                    time.sleep(0.01)
                if self._stop_flag:
                    break

                # Extract raw and annotated frames
                raw_frame = result.orig_img
                if raw_frame is None:
                    continue

                annotated = result.plot()  # ultralytics built-in visualization

                # Extract summary statistics
                summary = self._extract_summary(result)

                # Emit signals
                self.frame_processed.emit(raw_frame, annotated)
                self.detection_summary.emit(summary)
                self.total_targets.emit(sum(summary.values()))
                self.total_classes.emit(len(summary))

                # FPS calculation (every 5 frames)
                frame_count += 1
                if frame_count % 5 == 0:
                    elapsed = time.time() - start_time
                    if elapsed > 0:
                        self.fps_update.emit(5.0 / elapsed)
                    start_time = time.time()

                # Progress
                if total_frames > 0:
                    self.progress_update.emit(
                        min(int(frame_count / total_frames * 1000), 1000))

                # Save results if requested
                if self.save_res or self.save_txt:
                    self._save_result(result, frame_count)

                # Frame delay (throttling)
                if self.speed_thres > 0:
                    time.sleep(self.speed_thres / 1000.0)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.inference_error.emit(str(e))
        finally:
            # ── COM-SAFE cleanup (all in worker thread) ──────────────
            # cv2.VideoCapture uses COM on Windows.  CoInitialize and
            # CoUninitialize MUST happen in the same thread.  Since
            # ultralytics creates the capture in THIS worker thread,
            # we must release it here — cross-thread release from
            # stop() leaks COM resources and causes MSMF driver hang
            # after 2-3 open/close cycles.

            # 1) Close the generator (triggers LoadStreams.close())
            if self._generator is not None:
                try:
                    self._generator.close()
                except Exception:
                    pass
            self._generator = None

            # 2) Release all saved VideoCapture refs IN THIS THREAD
            for i, cap in enumerate(self._capture_refs):
                try:
                    if cap is not None and cap.isOpened():
                        cap.release()
                        print(f"[YoloEngine.run/finally] RELEASED _capture_refs[{i}]", flush=True)
                except Exception as e:
                    print(f"[YoloEngine.run/finally] error releasing _capture_refs[{i}]: {e}", flush=True)
            self._capture_refs = []

            # 3) Clear dataset's internal caps list to prevent re-open
            if self._saved_dataset is not None:
                for attr_name in ('caps', 'cap', 'vid_cap', 'stream', 'capture'):
                    try:
                        obj = getattr(self._saved_dataset, attr_name, None)
                        if obj is not None:
                            if isinstance(obj, list):
                                obj.clear()
                            else:
                                setattr(self._saved_dataset, attr_name, None)
                    except Exception:
                        pass
            self._saved_dataset = None

            # 4) Nuke model reference
            self._model = None

            # 5) Force garbage collection
            import gc
            gc.collect()

            # Always signal that processing has ended, so the main
            # thread can reset _inference_active even on error paths.
            print("[YoloEngine.run/finally] emitting processing_finished", flush=True)
            self.processing_finished.emit()

    # ── Private Helpers ────────────────────────────────────────────

    def _load_model(self):
        """Load the YOLO model. Ultralytics auto-downloads if not found locally."""
        if self._model is None or self._model_name != getattr(self._model, 'model_name', ''):
            self.status_update.emit(f"Loading model: {self._model_name}...")
            self._model = YOLO(self._model_name)
            if self.device:
                self._model.to(self.device)
            self.status_update.emit(f"Model loaded: {self._model_name}")

    def _create_generator(self):
        """Create the appropriate result generator based on task type."""
        if self._task_config.task_type == TaskType.TRACK:
            return self._model.track(
                source=self._source,
                conf=self.conf_thres,
                iou=self.iou_thres,
                imgsz=self.imgsz,
                stream=True,
                persist=True,       # keep track IDs consistent across frames
                verbose=False,
            )
        else:
            return self._model.predict(
                source=self._source,
                conf=self.conf_thres,
                iou=self.iou_thres,
                imgsz=self.imgsz,
                stream=True,
                verbose=False,
            )

    def _get_total_frames(self) -> int:
        """Try to determine total frames for progress calculation."""
        try:
            import cv2
            if self._source.isdigit():
                # Camera — unknown total
                return 0
            elif Path(self._source).exists():
                cap = cv2.VideoCapture(self._source)
                total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.release()
                return total
        except Exception:
            pass
        return 0

    def _extract_summary(self, result: Results) -> dict:
        """Extract per-class summary from a Results object."""
        summary = {}
        task_type = self._task_config.task_type

        if task_type == TaskType.CLASSIFY:
            # Classification: top-5 with probabilities
            if result.probs is not None:
                for idx, prob in zip(result.probs.top5, result.probs.top5conf):
                    name = result.names.get(int(idx), f"class_{int(idx)}")
                    summary[name] = int(prob * 100)  # store as percentage
            return summary

        if task_type == TaskType.POSE:
            # Pose: count person instances by keypoints
            if result.keypoints is not None:
                kpt_count = len(result.keypoints.data) if result.keypoints.data is not None else 0
                if kpt_count > 0:
                    summary["person"] = kpt_count
                return summary

        # For detect, segment, track: count by boxes
        if result.boxes is not None:
            classes = result.boxes.cls
            if classes is not None and len(classes) > 0:
                cls_list = classes.cpu().numpy().astype(int)
                for c in set(cls_list):
                    name = result.names.get(c, f"class_{c}")
                    summary[name] = int((cls_list == c).sum())

        # For OBB: boxes are in result.obb
        if task_type == TaskType.OBB and result.obb is not None:
            classes = result.obb.cls
            if classes is not None and len(classes) > 0:
                cls_list = classes.cpu().numpy().astype(int)
                for c in set(cls_list):
                    name = result.names.get(c, f"class_{c}")
                    summary[name] = int((cls_list == c).sum())

        return summary

    def _save_result(self, result: Results, frame_count: int):
        """Save annotated frame or labels based on save settings."""
        try:
            output_dir = None
            if result.save_dir:
                output_dir = Path(result.save_dir)
            else:
                output_dir = Path("runs") / self._task_config.task_type.value

            if self.save_res:
                result.save(filename=str(output_dir / f"frame_{frame_count:06d}.jpg"))
            if self.save_txt:
                result.save_txt(txt_file=str(output_dir / f"frame_{frame_count:06d}.txt"))
        except Exception:
            pass  # Don't crash inference on save errors
