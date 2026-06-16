"""
YoloSide v2.0 - Task Type Definitions & Model Registry

Defines all task types supported by the ultralytics framework
and the curated model catalog for each task.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict


class TaskType(Enum):
    DETECT = "detect"
    SEGMENT = "segment"
    POSE = "pose"
    CLASSIFY = "classify"
    OBB = "obb"
    TRACK = "track"


@dataclass
class TaskConfig:
    """Configuration for a single task type."""
    task_type: TaskType
    display_name: str                      # e.g. "Object Detection"
    icon: str                              # resource alias, e.g. ":/all/img/file.png"
    available_models: List[str] = field(default_factory=list)
    # ultralytics model task filter for list_models() if needed
    ultralytics_task_filter: str = ""

    # UI label for the result section
    result_label: str = "Detection"


# ── Curated model catalog ──────────────────────────────────────────
# Models that ultralytics will auto-download if not present locally.
# User can also place custom .pt files in ./models/

DETECT_MODELS = [
    # YOLOv8
    "yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt", "yolov8x.pt",
    # YOLOv9
    "yolov9t.pt", "yolov9s.pt", "yolov9m.pt", "yolov9c.pt", "yolov9e.pt",
    # YOLOv10
    "yolov10n.pt", "yolov10s.pt", "yolov10m.pt", "yolov10b.pt",
    "yolov10l.pt", "yolov10x.pt",
    # YOLOv11
    "yolo11n.pt", "yolo11s.pt", "yolo11m.pt", "yolo11l.pt", "yolo11x.pt",
    # YOLOv12
    "yolo12n.pt", "yolo12s.pt", "yolo12m.pt", "yolo12l.pt", "yolo12x.pt",
    # RT-DETR
    "rtdetr-l.pt", "rtdetr-x.pt",
]

SEGMENT_MODELS = [
    # YOLOv8-seg
    "yolov8n-seg.pt", "yolov8s-seg.pt", "yolov8m-seg.pt",
    "yolov8l-seg.pt", "yolov8x-seg.pt",
    # YOLOv11-seg
    "yolo11n-seg.pt", "yolo11s-seg.pt", "yolo11m-seg.pt",
    "yolo11l-seg.pt", "yolo11x-seg.pt",
    # FastSAM
    "FastSAM-s.pt", "FastSAM-x.pt",
    # SAM variants (ultralytics)
    "sam_b.pt", "sam_l.pt",
    "mobile_sam.pt",
]

POSE_MODELS = [
    # YOLOv8-pose
    "yolov8n-pose.pt", "yolov8s-pose.pt", "yolov8m-pose.pt",
    "yolov8l-pose.pt", "yolov8x-pose.pt",
    # YOLOv11-pose
    "yolo11n-pose.pt", "yolo11s-pose.pt", "yolo11m-pose.pt",
    "yolo11l-pose.pt", "yolo11x-pose.pt",
]

CLASSIFY_MODELS = [
    # YOLOv8-cls
    "yolov8n-cls.pt", "yolov8s-cls.pt", "yolov8m-cls.pt",
    "yolov8l-cls.pt", "yolov8x-cls.pt",
    # YOLOv11-cls
    "yolo11n-cls.pt", "yolo11s-cls.pt", "yolo11m-cls.pt",
    "yolo11l-cls.pt", "yolo11x-cls.pt",
]

OBB_MODELS = [
    # YOLOv8-obb
    "yolov8n-obb.pt", "yolov8s-obb.pt", "yolov8m-obb.pt",
    "yolov8l-obb.pt", "yolov8x-obb.pt",
    # YOLOv11-obb (if available)
    "yolo11n-obb.pt", "yolo11s-obb.pt", "yolo11m-obb.pt",
    "yolo11l-obb.pt", "yolo11x-obb.pt",
]

# Tracking uses detection models with Bot-SORT / ByteTrack
TRACK_MODELS = DETECT_MODELS.copy()


# ── Registry ───────────────────────────────────────────────────────

TASK_REGISTRY: Dict[TaskType, TaskConfig] = {
    TaskType.DETECT: TaskConfig(
        task_type=TaskType.DETECT,
        display_name="Object Detection",
        icon=":/all/img/file.png",
        available_models=DETECT_MODELS,
        ultralytics_task_filter="detect",
        result_label="Detection",
    ),
    TaskType.SEGMENT: TaskConfig(
        task_type=TaskType.SEGMENT,
        display_name="Instance Segmentation",
        icon=":/all/img/file.png",
        available_models=SEGMENT_MODELS,
        ultralytics_task_filter="segment",
        result_label="Segmentation",
    ),
    TaskType.POSE: TaskConfig(
        task_type=TaskType.POSE,
        display_name="Pose Estimation",
        icon=":/all/img/file.png",
        available_models=POSE_MODELS,
        ultralytics_task_filter="pose",
        result_label="Pose",
    ),
    TaskType.CLASSIFY: TaskConfig(
        task_type=TaskType.CLASSIFY,
        display_name="Image Classification",
        icon=":/all/img/file.png",
        available_models=CLASSIFY_MODELS,
        ultralytics_task_filter="classify",
        result_label="Classification",
    ),
    TaskType.OBB: TaskConfig(
        task_type=TaskType.OBB,
        display_name="Oriented BBox (OBB)",
        icon=":/all/img/file.png",
        available_models=OBB_MODELS,
        ultralytics_task_filter="obb",
        result_label="OBB Detection",
    ),
    TaskType.TRACK: TaskConfig(
        task_type=TaskType.TRACK,
        display_name="Object Tracking",
        icon=":/all/img/file.png",
        available_models=TRACK_MODELS,
        ultralytics_task_filter="detect",  # tracking uses detect models
        result_label="Tracking",
    ),
}


def get_task_config(task_type: TaskType) -> TaskConfig:
    """Get the TaskConfig for a given TaskType."""
    return TASK_REGISTRY[task_type]


def get_task_display_names() -> List[str]:
    """Return ordered list of display names for the task combo box."""
    return [
        TASK_REGISTRY[TaskType.DETECT].display_name,
        TASK_REGISTRY[TaskType.SEGMENT].display_name,
        TASK_REGISTRY[TaskType.POSE].display_name,
        TASK_REGISTRY[TaskType.CLASSIFY].display_name,
        TASK_REGISTRY[TaskType.OBB].display_name,
        TASK_REGISTRY[TaskType.TRACK].display_name,
    ]


def task_type_from_display_name(name: str) -> TaskType:
    """Reverse lookup: display name → TaskType."""
    for tt, cfg in TASK_REGISTRY.items():
        if cfg.display_name == name:
            return tt
    return TaskType.DETECT  # fallback
