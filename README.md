# YoloSide v2.0 — Ultralytics Desktop GUI

A PySide6 desktop application providing a modern GUI for the [ultralytics](https://github.com/ultralytics/ultralytics) YOLO framework. Supports all task types: **Detection, Segmentation, Pose Estimation, Classification, Oriented Bounding Boxes (OBB), and Tracking**.

![](img/home.png)

## Features

- 🎯 **All ultralytics task types** — Detect, Segment, Pose, Classify, OBB, Track
- 📷 **Multiple input sources** — USB camera, local video/image files, RTSP streams
- 📁 **Batch processing** — process entire folders of images at once
- ⬇️ **Auto-download models** — select any model from the registry, ultralytics downloads it automatically
- 🎨 **Purple gradient theme** — frameless modern window with rounded corners and shadows
- 💾 **Save results** — annotated images and YOLO-format txt labels
- ⚙️ **Adjustable parameters** — IOU, Confidence, inference speed, image size
- 📊 **Real-time stats** — FPS counter, class counts, target counts, progress bar
- 🔄 **Multi-cycle stable** — camera properly releases between runs (COM thread-safety fix)

## Quick Start

### Requirements
- **Python** ≥ 3.10
- **OS**: Windows 10/11 (primary), Linux/macOS (untested but likely work)

### Install
```bash
git clone https://github.com/Jai-wei/YoloSide.git
cd YoloSide
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
```

### Run
```bash
python main.py
```

On first run, select a model from the dropdown — ultralytics will automatically download it to the `models/` folder. Then choose an input source (Camera / Local File / RTSP) and click **▶ Start**.

## Project Structure

```
YoloSide/
├── main.py                    # Entry point
├── app/mainwindow.py          # MainWindow — UI orchestration
├── engine/                    # Inference engine
│   ├── inference.py           #   YoloEngine(QObject) — COM-safe worker
│   ├── task_config.py         #   Task types + 83-model registry
│   └── batch_processor.py     #   Batch processing logic
├── config/settings.py         # Typed config (AppSettings dataclass)
├── widgets/                   # UI widgets
│   ├── UIFunctions.py         #   Window controls, shadows, animations
│   └── custom_grips.py        #   Resize grips
├── ui/                        # Qt Designer output
│   ├── home.py                #   Main window layout
│   ├── resources_rc.py        #   Compiled resources
│   └── CustomMessageBox.py    #   Styled message dialog
├── utils/                     # Utilities
│   ├── capnums.py             #   Camera enumeration (DSHOW)
│   ├── rtsp_win.py            #   RTSP input window
│   └── rtsp_dialog.py         #   RTSP dialog UI
├── models/.gitkeep            # Downloaded .pt files (gitignored)
├── img/                       # Icons and images
└── hooks/                     # PyInstaller packaging hooks
```

## Architecture

- **Engine**: `YoloEngine(QObject)` runs in a `QThread`, communicates via Qt Signal/Slot
- **Thread safety**: `cv2.VideoCapture` release happens in the worker thread (same thread as COM `CoInitialize`) — prevents Windows MSMF driver leaks
- **Generator pattern**: `YOLO().predict(source, stream=True)` for frame-by-frame inference
- **Visualization**: `result.plot()` — ultralytics built-in, covers all task types

## Model Support

83 models across the ultralytics ecosystem: YOLOv5, YOLOv8, YOLOv9, YOLOv10, YOLOv11, YOLOv12, RT-DETR, FastSAM, SAM 2.1, and more. Select any model from the dropdown — if not present locally, ultralytics downloads it automatically.

## To Do

- [ ] PyInstaller `.exe` packaging
- [ ] Model download progress indicator
- [ ] GPU/CUDA device selection UI
- [ ] Image size (imgsz) control in settings
- [ ] Custom tracking trail visualization

## Notice

- `ultralytics` is licensed under **AGPL-3.0** — commercial use requires a separate license
- Trained `.pt` files go in the `models/` folder
- Saved results go to `./runs/` by default
- To modify the UI, edit `home.ui` in Qt Designer, then run `pyside6-uic home.ui > ui/home.py`

## References

- [ultralytics](https://github.com/ultralytics/ultralytics)
- [YOLOv8-PySide6-GUI](https://github.com/Jai-wei/YOLOv8-PySide6-GUI) (original v1.0 base)
- [PyQt5-YOLOv5](https://github.com/Javacr/PyQt5-YOLOv5)
