"""
YoloSide v2.0 - UI Functions (Standalone Mixin)

Provides window control, menu animations, shadow effects, and resize grips.
No longer imports from main.py — pure mixin that accesses widgets via self.
"""

from widgets.custom_grips import CustomGrip
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QEvent, QTimer
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizeGrip, QGraphicsDropShadowEffect

GLOBAL_STATE = False    # max min flag
GLOBAL_TITLE_BAR = True


class UIFunctions:
    """Standalone UI mixin. Attach to any QMainWindow with the expected widget names."""

    # ── Left menu expand/collapse animation ────────────────────────

    def toggleMenu(self, enable: bool):
        if enable:
            standard = 68
            maxExtend = 180
            width = self.LeftMenuBg.width()

            if width == 68:
                widthExtended = maxExtend
            else:
                widthExtended = standard

            # animation
            self.animation = QPropertyAnimation(self.LeftMenuBg, b"minimumWidth")
            self.animation.setDuration(500)  # ms
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QEasingCurve.InOutQuint)
            self.animation.start()

    # ── Right settings panel slide animation ───────────────────────

    def settingBox(self, enable: bool):
        if enable:
            # GET WIDTH
            widthRightBox = self.prm_page.width()       # right set column width
            widthLeftBox = self.LeftMenuBg.width()      # left column length
            maxExtend = 220
            standard = 0

            # SET MAX WIDTH
            if widthRightBox == 0:
                widthExtended = maxExtend
            else:
                widthExtended = standard

            # ANIMATION LEFT BOX
            self.left_box = QPropertyAnimation(self.LeftMenuBg, b"minimumWidth")
            self.left_box.setDuration(500)
            self.left_box.setStartValue(widthLeftBox)
            self.left_box.setEndValue(68)
            self.left_box.setEasingCurve(QEasingCurve.InOutQuart)

            # ANIMATION RIGHT BOX
            self.right_box = QPropertyAnimation(self.prm_page, b"minimumWidth")
            self.right_box.setDuration(500)
            self.right_box.setStartValue(widthRightBox)
            self.right_box.setEndValue(widthExtended)
            self.right_box.setEasingCurve(QEasingCurve.InOutQuart)

            # GROUP ANIMATION
            from PySide6.QtCore import QParallelAnimationGroup
            self.group = QParallelAnimationGroup()
            self.group.addAnimation(self.left_box)
            self.group.addAnimation(self.right_box)
            self.group.start()

    # ── Maximize / Restore ─────────────────────────────────────────

    def maximize_restore(self):
        global GLOBAL_STATE
        status = GLOBAL_STATE
        if status is False:
            GLOBAL_STATE = True
            self.showMaximized()
            self.max_sf.setToolTip("Restore")
            self.frame_size_grip.hide()
            self.left_grip.hide()
            self.right_grip.hide()
            self.top_grip.hide()
            self.bottom_grip.hide()
        else:
            GLOBAL_STATE = False
            self.showNormal()
            self.resize(self.width() + 1, self.height() + 1)
            self.max_sf.setToolTip("Maximize")
            self.frame_size_grip.show()
            self.left_grip.show()
            self.right_grip.show()
            self.top_grip.show()
            self.bottom_grip.show()

    # ── Window control setup (call once from __init__) ─────────────

    def uiDefinitions(self):
        # Double-click the title bar to maximize
        def dobleClickMaximizeRestore(event):
            if event.type() == QEvent.MouseButtonDblClick:
                QTimer.singleShot(250, lambda: UIFunctions.maximize_restore(self))
        self.top.mouseDoubleClickEvent = dobleClickMaximizeRestore

        # MOVE WINDOW / MAXIMIZE / RESTORE
        def moveWindow(event):
            if GLOBAL_STATE:  # IF MAXIMIZED CHANGE TO NORMAL
                UIFunctions.maximize_restore(self)
            if event.buttons() == Qt.LeftButton:  # MOVE
                self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                self.dragPos = event.globalPosition().toPoint()
        self.top.mouseMoveEvent = moveWindow

        # CUSTOM GRIPS
        self.left_grip = CustomGrip(self, Qt.LeftEdge, True)
        self.right_grip = CustomGrip(self, Qt.RightEdge, True)
        self.top_grip = CustomGrip(self, Qt.TopEdge, True)
        self.bottom_grip = CustomGrip(self, Qt.BottomEdge, True)

        # MINIMIZE
        self.min_sf.clicked.connect(lambda: self.showMinimized())
        # MAXIMIZE/RESTORE
        self.max_sf.clicked.connect(lambda: UIFunctions.maximize_restore(self))
        # CLOSE APPLICATION
        self.close_button.clicked.connect(self.close)

    # ── Resize grips positioning ───────────────────────────────────

    def resize_grips(self):
        self.left_grip.setGeometry(0, 10, 10, self.height())
        self.right_grip.setGeometry(self.width() - 10, 10, 10, self.height())
        self.top_grip.setGeometry(0, 0, self.width(), 10)
        self.bottom_grip.setGeometry(0, self.height() - 10, self.width(), 10)

    # ── Drop shadow helper ─────────────────────────────────────────

    def shadow_style(self, widget, Color):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(8, 8)       # offset
        shadow.setBlurRadius(38)     # shadow radius
        shadow.setColor(Color)       # shadow color
        widget.setGraphicsEffect(shadow)
