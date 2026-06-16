"""
YoloSide v2.0 — Ultralytics Desktop GUI

A graphical user interface for the ultralytics framework.
Supports: Detection, Segmentation, Pose, Classification, OBB, and Tracking.

Run: .venv/Scripts/python main.py
"""

import sys
from PySide6.QtWidgets import QApplication
from app.mainwindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    Home = MainWindow()
    Home.show()
    sys.exit(app.exec())
