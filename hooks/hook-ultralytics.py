"""
PyInstaller hook for ultralytics.

Ensures all .yaml config files, submodules, and data files
are included in the bundled application.
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all ultralytics data files (model configs, dataset configs, etc.)
datas = collect_data_files('ultralytics', include_py_files=False)

# Ensure all submodules are included (dynamic imports by ultralytics)
hiddenimports = collect_submodules('ultralytics')

# Explicit hidden imports that collect_submodules might miss
hiddenimports += [
    'ultralytics.nn.modules.block',
    'ultralytics.nn.modules.conv',
    'ultralytics.nn.modules.head',
    'ultralytics.nn.modules.transformer',
    'ultralytics.nn.tasks',
    'ultralytics.utils.callbacks',
    'ultralytics.utils.checks',
    'ultralytics.utils.downloads',
    'ultralytics.data.utils',
    'ultralytics.data.augment',
    'ultralytics.data.loaders',
    'ultralytics.engine.results',
    'ultralytics.engine.model',
    'ultralytics.models.yolo.detect',
    'ultralytics.models.yolo.segment',
    'ultralytics.models.yolo.pose',
    'ultralytics.models.yolo.classify',
    'ultralytics.models.yolo.obb',
    'ultralytics.models.sam',
    'ultralytics.models.fastsam',
    'ultralytics.models.rtdetr',
    'ultralytics.trackers',
    'ultralytics.trackers.bot_sort',
    'ultralytics.trackers.byte_tracker',
    'ultralytics.trackers.track',
]
