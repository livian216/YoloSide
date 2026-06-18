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

## 待办事项

- [ ] PyInstaller `.exe` 打包（已有初步构建，见下方说明）
- [ ] 模型下载进度指示
- [ ] GPU/CUDA 设备选择界面
- [ ] 设置中的图像尺寸（imgsz）控制
- [ ] 自定义跟踪轨迹可视化

## 注意事项

- `ultralytics` 使用 **AGPL-3.0** 许可证 — 商业使用需另行获取授权
- 训练好的 `.pt` 文件放在 `models/` 文件夹下
- 推理结果默认保存到 `./runs/` 目录
- 如需修改界面，在 Qt Designer 中编辑 `home.ui`，然后运行 `pyside6-uic home.ui > ui/home.py`

## 参考资料

- [ultralytics](https://github.com/ultralytics/ultralytics)
- [YOLOv8-PySide6-GUI](https://github.com/Jai-wei/YOLOv8-PySide6-GUI)（原始 v1.0 基础版本）
- [PyQt5-YOLOv5](https://github.com/Javacr/PyQt5-YOLOv5)
