# YoloSide v2.0 — Ultralytics 桌面 GUI

基于 PySide6 的现代化桌面应用，为 [ultralytics](https://github.com/ultralytics/ultralytics) YOLO 框架提供图形化操作界面。支持全部任务类型：**检测、分割、姿态估计、分类、旋转目标检测（OBB）以及目标跟踪**。

![](img/home.png)

## 功能特性

- 🎯 **全任务类型支持** — 检测 / 分割 / 姿态 / 分类 / OBB / 跟踪
- 📷 **多输入源** — USB 摄像头、本地视频/图片文件、RTSP 流
- 📁 **批量处理** — 一键处理整个文件夹的图片
- ⬇️ **自动下载模型** — 从下拉列表中选择任意模型，ultralytics 自动下载
- 🎨 **紫色渐变主题** — 无边框现代窗口，圆角阴影
- 💾 **结果保存** — 支持保存标注图片和 YOLO 格式 txt 标签
- ⚙️ **可调参数** — IOU、置信度、推理速度、图像尺寸
- 📊 **实时统计** — FPS 帧率、类别计数、目标计数、进度条
- 🔄 **多轮运行稳定** — 摄像头在多次运行间正确释放（COM 线程安全修复）

## 快速开始

### 环境要求
- **Python** ≥ 3.10
- **操作系统**：Windows 10/11（主要支持），Linux/macOS（未测试但理论上可用）

### 安装
```bash
git clone https://github.com/Jai-wei/YoloSide.git
cd YoloSide
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
```

### 运行
```bash
python main.py
```

首次运行时，从下拉框中选择一个模型 — ultralytics 会自动将其下载到 `models/` 文件夹中。然后选择输入源（摄像头 / 本地文件 / RTSP），点击 **▶ Start** 即可开始推理。

## 项目结构

```
YoloSide/
├── main.py                    # 入口文件
├── app/mainwindow.py          # MainWindow — UI 调度核心
├── engine/                    # 推理引擎
│   ├── inference.py           #   YoloEngine(QObject) — COM 安全的推理工作线程
│   ├── task_config.py         #   任务类型 + 83 个模型注册表
│   └── batch_processor.py     #   批量处理逻辑
├── config/settings.py         # 类型化配置（AppSettings 数据类）
├── widgets/                   # UI 控件
│   ├── UIFunctions.py         #   窗口控制、阴影、动画
│   └── custom_grips.py        #   窗口拖拽调整大小
├── ui/                        # Qt Designer 生成的 UI 文件
│   ├── home.py                #   主窗口布局
│   ├── resources_rc.py        #   编译后的资源文件
│   └── CustomMessageBox.py    #   自定义消息对话框
├── utils/                     # 工具模块
│   ├── capnums.py             #   摄像头枚举（DSHOW）
│   ├── rtsp_win.py            #   RTSP 输入窗口
│   └── rtsp_dialog.py         #   RTSP 对话框 UI
├── models/.gitkeep            # 模型下载目录（.pt 文件被 gitignore）
├── img/                       # 图标和图片资源
└── hooks/                     # PyInstaller 打包钩子
```

## 架构设计

- **引擎**：`YoloEngine(QObject)` 运行在独立的 `QThread` 中，通过 Qt Signal/Slot 机制与 UI 通信
- **线程安全**：`cv2.VideoCapture` 的释放在工作线程中完成（与 COM `CoInitialize` 同一线程），避免 Windows MSMF 驱动资源泄漏
- **生成器模式**：`YOLO().predict(source, stream=True)` 实现逐帧推理
- **可视化**：使用 ultralytics 内置的 `result.plot()` 方法，覆盖所有任务类型

## 模型支持

覆盖 ultralytics 生态中 83 个模型：YOLOv5、YOLOv8、YOLOv9、YOLOv10、YOLOv11、YOLOv12、RT-DETR、FastSAM、SAM 2.1 等。从下拉框中选择任意模型 — 如果本地不存在，ultralytics 会自动下载。

## 版本发布

用户无需安装 Python 环境即可使用。每次 Release 提供单个安装包：

**`YoloSide_Setup_v2.0.exe`**（~500 MB）— 双击运行，中文向导引导安装，自动创建桌面快捷方式、开始菜单入口和卸载程序。默认安装到 `%LOCALAPPDATA%\Programs\YoloSide`，无需管理员权限。

> 💡 首次运行时会自动下载所选模型到安装目录下的 `models/` 文件夹（需联网）。

## 待办事项

- [x] ~~PyInstaller `.exe` 打包 + Inno Setup 安装器~~ （v2.0 已完成，一键 `build.bat` 构建）
- [ ] 模型下载进度指示（目前下载期间界面无反馈）
- [ ] GPU/CUDA 设备选择界面（当前自动使用可用的 CUDA 设备）
- [ ] 设置面板中的图像尺寸（imgsz）手动控制
- [ ] 目标跟踪自定义轨迹可视化（当前使用 ultralytics 内置 `plot()`）
- [ ] 清理 `engine/inference.py` 中的 debug `print()` 语句
- [ ] 已知小问题：跨线程 generator.close() 警告（无害）、摄像头枚举重复设备号（DSHOW 多 pin）

## 打包为 EXE

项目配置了 PyInstaller (`--onedir` 模式) + Inno Setup 一键构建流水线。运行 `build.bat` 即可同时产出安装器和便携版。

### 一键构建
```batch
build.bat
```
脚本自动完成：清理旧构建 → PyInstaller 打包（3-8 分钟） → Inno Setup 打包 → 验证产物。

### 产物
| 产物 | 路径 | 说明 |
|------|------|------|
| 安装器（推荐分发） | `dist\YoloSide_Setup_v2.0.exe` | 单个 exe，约 500MB，用户双击安装 |
| 便携版目录 | `dist\YoloSide\` | 整个文件夹 zip 后即可分发 |

> ⚠️ 便携版的 `YoloSide.exe` **不能单独运行** — 它依赖同目录下的 `_internal/` 文件夹（内含 Python 运行时和全部依赖库）。分发便携版时必须打包整个 `YoloSide/` 文件夹。

### 用户安装体验
1. 双击 `YoloSide_Setup_v2.0.exe` → 中文安装向导
2. 选择安装路径（默认 `%LOCALAPPDATA%\Programs\YoloSide`，**无需管理员权限**）
3. 自动完成：文件解压、桌面快捷方式、开始菜单入口、卸载程序注册
4. 勾选"立即运行"即可启动

### 构建依赖
- **PyInstaller**：`pip install pyinstaller`（已包含在 `requirements.txt` 中）
- **Inno Setup 6**：[下载地址](https://jrsoftware.org/isinfo.php)（仅构建者需要）
- Python 虚拟环境需已安装全部运行时依赖

### 技术说明
- `YoloSide.spec` — PyInstaller 打包配置，排除未使用的 Qt 模块以减小体积
- `installer.iss` — Inno Setup 中文安装向导脚本，含完整中文 `[CustomMessages]`
- `hooks/hook-ultralytics.py` — 确保 ultralytics 的 YAML 配置等数据文件被打包
- `.pt` 模型文件**不会**被打包（体积过大），用户首次使用时自动下载到安装目录 `models/`
- 当前打包 CPU 版 PyTorch；如需 GPU 版，替换虚拟环境中的 torch 包后重新构建
- PyInstaller 使用 `--onedir` 模式（非 `--onefile`），因为 torch + ultralytics 的 C 扩展与单文件模式不兼容

## 注意事项

- `ultralytics` 使用 **AGPL-3.0** 许可证 — 商业使用需另行获取授权
- 训练好的 `.pt` 文件放在 `models/` 文件夹下
- 推理结果默认保存到 `./runs/` 目录
- 如需修改界面，在 Qt Designer 中编辑 `home.ui`，然后运行 `pyside6-uic home.ui > ui/home.py`

## 参考资料

- [ultralytics](https://github.com/ultralytics/ultralytics)
- [YOLOv8-PySide6-GUI](https://github.com/Jai-wei/YOLOv8-PySide6-GUI)（原始 v1.0 基础版本）
- [PyQt5-YOLOv5](https://github.com/Javacr/PyQt5-YOLOv5)
