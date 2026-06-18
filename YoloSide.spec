# -*- mode: python ; coding: utf-8 -*-
"""
YoloSide v2.0 — PyInstaller Spec File

Build command:
    pyinstaller YoloSide.spec --clean --noconfirm

Output: dist/YoloSide/YoloSide.exe (+ _internal/)
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

# ── Project root ────────────────────────────────────────────────────
PROJECT_ROOT = Path(SPECPATH)  # SPECPATH = directory containing this .spec

# ── PySide6: collect only what we need ──────────────────────────────
# We exclude QML/Quick/VirtualKeyboard/PDF to reduce ~80 MB of bloat.
# For a full list of PySide6 submodules, see PySide6/__init__.py

pyside6_hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtNetwork',
    'PySide6.QtSvg',
    'PySide6.QtSvgWidgets',
]

# ── Ultralytics ─────────────────────────────────────────────────────
# Use the project hook file to collect ultralytics data + hidden imports.
# (Hook path is passed via hookspath=[] in the Analysis below.)

ultralytics_hidden = collect_submodules('ultralytics')
# Extra modules that collect_submodules might miss
ultralytics_hidden += [
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

# Collect ultralytics data: model config .yaml files, assets, etc.
ultralytics_datas = []
try:
    ultralytics_datas = collect_data_files('ultralytics', include_py_files=False)
except Exception:
    pass

# ── OpenCV ──────────────────────────────────────────────────────────
opencv_hidden = [
    'cv2',
    'cv2.dnn',
    'cv2.videoio_registry',
    'numpy',
]

# ── All hidden imports ──────────────────────────────────────────────
all_hidden = (
    pyside6_hiddenimports +
    ultralytics_hidden +
    opencv_hidden +
    [
        # App modules
        'app',
        'app.mainwindow',
        'engine',
        'engine.inference',
        'engine.task_config',
        'engine.batch_processor',
        'config',
        'config.settings',
        'widgets',
        'widgets.UIFunctions',
        'widgets.custom_grips',
        'ui',
        'ui.home',
        'ui.resources_rc',
        'ui.CustomMessageBox',
        'utils',
        'utils.capnums',
        'utils.rtsp_win',
        'utils.rtsp_dialog',
        # Dependencies that might be missed
        'lap',
        'PIL',
        'PIL.Image',
        'torch',
        'torchvision',
        'torchvision.ops',
        'torchvision.transforms',
        'numpy.core._methods',
        'numpy.lib.format',
    ]
)

# ── Exclude bloat ───────────────────────────────────────────────────
# ONLY exclude PySide6 modules we are certain we don't use.
# NEVER exclude Python stdlib modules — they cost almost no space
# and transitive dependencies (torch, ultralytics, importlib) break.
exclude_modules = [
    'PySide6.QtQml',
    'PySide6.QtQuick',
    'PySide6.QtQuickWidgets',
    'PySide6.QtVirtualKeyboard',
    'PySide6.QtPdf',
    'PySide6.QtPdfWidgets',
    'PySide6.QtOpenGLWidgets',
    'PySide6.QtDesigner',
    'PySide6.QtUiTools',
    'PySide6.QtHelp',
    'PySide6.QtXml',
    'PySide6.QtTest',
    'PySide6.QtDBus',
    'PySide6.QtPrintSupport',
    'PySide6.QtBluetooth',
    'PySide6.QtNfc',
    'PySide6.QtSerialPort',
    'PySide6.QtPositioning',
    'PySide6.QtWebChannel',
    'PySide6.QtWebEngine',
    'PySide6.QtWebEngineCore',
    'PySide6.QtWebEngineWidgets',
    'PySide6.QtWebSockets',
]

# ── Collect PySide6 binaries (Qt DLLs, plugins) ─────────────────────
pyside6_datas = []
try:
    import PySide6
    pyside6_root = Path(PySide6.__path__[0])

    # Platform plugin (qwindows.dll) — MANDATORY for Windows
    platforms_dir = pyside6_root / 'plugins' / 'platforms'
    if platforms_dir.exists():
        for dll in platforms_dir.glob('qwindows*.dll'):
            pyside6_datas.append((str(dll), 'PySide6/plugins/platforms'))

    # Styles plugin (qmodernwindowsstyle.dll)
    styles_dir = pyside6_root / 'plugins' / 'styles'
    if styles_dir.exists():
        for dll in styles_dir.glob('*.dll'):
            pyside6_datas.append((str(dll), 'PySide6/plugins/styles'))

    # Image format plugins (qjpeg.dll, qgif.dll, etc.)
    imgfmt_dir = pyside6_root / 'plugins' / 'imageformats'
    if imgfmt_dir.exists():
        for dll in imgfmt_dir.glob('*.dll'):
            pyside6_datas.append((str(dll), 'PySide6/plugins/imageformats'))

    # TLS plugins (for HTTPS/RTSP)
    tls_dir = pyside6_root / 'plugins' / 'tls'
    if tls_dir.exists():
        for dll in tls_dir.glob('*.dll'):
            pyside6_datas.append((str(dll), 'PySide6/plugins/tls'))

    # Icon engines
    iconengines_dir = pyside6_root / 'plugins' / 'iconengines'
    if iconengines_dir.exists():
        for dll in iconengines_dir.glob('*.dll'):
            pyside6_datas.append((str(dll), 'PySide6/plugins/iconengines'))

    # Network information
    netinfo_dir = pyside6_root / 'plugins' / 'networkinformation'
    if netinfo_dir.exists():
        for dll in netinfo_dir.glob('*.dll'):
            pyside6_datas.append((str(dll), 'PySide6/plugins/networkinformation'))

    # OpenGL software renderer (fallback)
    opengl_dll = pyside6_root / 'opengl32sw.dll'
    if opengl_dll.exists():
        pyside6_datas.append((str(opengl_dll), 'PySide6'))

    # Keep only Chinese + English translations (saves ~30 MB)
    translations_dir = pyside6_root / 'translations'
    if translations_dir.exists():
        for qm in translations_dir.glob('qt_zh_CN.qm'):
            pyside6_datas.append((str(qm), 'PySide6/translations'))
        for qm in translations_dir.glob('qt_en.qm'):
            pyside6_datas.append((str(qm), 'PySide6/translations'))
        # qtbase_zh_CN.qm is also needed for proper Chinese text
        for qm in translations_dir.glob('qtbase_zh_CN.qm'):
            pyside6_datas.append((str(qm), 'PySide6/translations'))

except Exception as e:
    print(f"WARNING: Could not collect PySide6 data: {e}")

# ── App data files ──────────────────────────────────────────────────
# Images (for Qt resources, though most are compiled in resources_rc.py)
app_datas = []
img_dir = PROJECT_ROOT / 'img'
if img_dir.exists():
    for f in img_dir.iterdir():
        if f.is_file() and f.suffix in ('.png', '.jpg', '.jpeg', '.gif', '.ico'):
            app_datas.append((str(f), 'img'))

# ── Analysis ────────────────────────────────────────────────────────
a = Analysis(
    [str(PROJECT_ROOT / 'main.py')],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=ultralytics_datas + pyside6_datas + app_datas,
    hiddenimports=all_hidden,
    hookspath=[str(PROJECT_ROOT / 'hooks')],
    hooksconfig={},
    runtime_hooks=[],
    excludes=exclude_modules,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# ── Filter duplicate binaries ───────────────────────────────────────
# PyInstaller may collect duplicates of Qt DLLs; keep the first one.
seen_binaries = set()
filtered_binaries = []
for tpl in a.binaries:
    name = tpl[0].lower()
    if name not in seen_binaries:
        seen_binaries.add(name)
        filtered_binaries.append(tpl)
    else:
        print(f"  [dedup] skipping duplicate binary: {tpl[0]}")
a.binaries = filtered_binaries

# ── PYZ (compiled Python modules) ───────────────────────────────────
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# ── EXE ─────────────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YoloSide',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX often breaks .pyd files; keep off
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # Windows GUI app (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(PROJECT_ROOT / 'img' / 'logo.ico'),
)

# ── COLLECT (output folder) ─────────────────────────────────────────
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='YoloSide',
)
