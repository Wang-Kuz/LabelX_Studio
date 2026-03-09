#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LabelX Studio — 轻量级图像标注工具（PySide6）
支持：矩形/多边形标注、类别管理、图像列表、缩放/平移、选择/删除、
YOLO-Det(.txt)、YOLO-Seg(.txt)、COCO(.json)、VOC(.xml)、LabelMe(.json) 导出、
项目保存/加载（.lxs.json）

作者：Kuz（王煜鹏）专用版本
运行环境：Python 3.10+，PySide6（或 PySide6==6.7+）
安装依赖：
    pip install pyside6 pillow numpy
启动：
    python labelx_studio.py

注意：本文件为单文件实现，便于软著提交。生产环境建议模块化拆分。
"""
from __future__ import annotations
import os
import json
import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

from PySide6.QtCore import (
    Qt, QRectF, QPointF, QSize, QItemSelectionModel, QPropertyAnimation, QEasingCurve
)
from PySide6.QtGui import (
    QAction, QIcon, QPixmap, QKeySequence, QPainterPath, QPen, QBrush, QFont, QPalette, QColor
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsPolygonItem,
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QSplitter, QToolBar, QStyle, QLineEdit, QGroupBox,
    QFormLayout, QSpinBox, QCheckBox, QFrame, QScrollArea, QSizePolicy, QComboBox
)
from PySide6.QtGui import QPainter
# ------------------------- 现代化主题设置 -------------------------

class ModernTheme:
    """现代化深色主题配色"""
    # 主色调
    PRIMARY = QColor(64, 156, 255)      # 蓝色主色调
    PRIMARY_LIGHT = QColor(100, 181, 255)
    PRIMARY_DARK = QColor(45, 125, 220)
    
    # 背景色
    BG_DARK = QColor(28, 28, 30)        # 主背景
    BG_MEDIUM = QColor(44, 44, 46)      # 次背景
    BG_LIGHT = QColor(58, 58, 60)       # 面板背景
    
    # 前景色
    TEXT_PRIMARY = QColor(255, 255, 255)    # 主要文字
    TEXT_SECONDARY = QColor(174, 174, 178)  # 次要文字
    TEXT_DISABLED = QColor(99, 99, 102)     # 禁用文字
    
    # 边框和分割线
    BORDER = QColor(58, 58, 60)
    SEPARATOR = QColor(44, 44, 46)
    
    # 状态色
    SUCCESS = QColor(52, 199, 89)       # 成功绿
    WARNING = QColor(255, 149, 0)       # 警告橙
    ERROR = QColor(255, 59, 48)         # 错误红
    
    # 标注颜色
    ANNOTATION_COLORS = [
        QColor(255, 69, 58),    # 红色
        QColor(48, 209, 88),    # 绿色
        QColor(255, 214, 10),   # 黄色
        QColor(94, 92, 230),    # 紫色
        QColor(255, 55, 95),    # 粉色
        QColor(88, 86, 214),    # 靛蓝
        QColor(255, 159, 10),   # 橙色
    ]

def apply_modern_style(app: QApplication):
    """应用现代化样式"""
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 创建调色板
    palette = QPalette()
    
    # 背景色
    palette.setColor(QPalette.Window, ModernTheme.BG_DARK)
    palette.setColor(QPalette.WindowText, ModernTheme.TEXT_PRIMARY)
    palette.setColor(QPalette.Base, ModernTheme.BG_MEDIUM)
    palette.setColor(QPalette.AlternateBase, ModernTheme.BG_LIGHT)
    
    # 文本色
    palette.setColor(QPalette.Text, ModernTheme.TEXT_PRIMARY)
    palette.setColor(QPalette.ButtonText, ModernTheme.TEXT_PRIMARY)
    
    # 按钮色
    palette.setColor(QPalette.Button, ModernTheme.BG_LIGHT)
    palette.setColor(QPalette.Light, ModernTheme.BORDER)
    palette.setColor(QPalette.Midlight, ModernTheme.BG_MEDIUM)
    palette.setColor(QPalette.Dark, ModernTheme.BG_DARK)
    
    # 高亮色
    palette.setColor(QPalette.Highlight, ModernTheme.PRIMARY)
    palette.setColor(QPalette.HighlightedText, ModernTheme.TEXT_PRIMARY)
    
    # 链接色
    palette.setColor(QPalette.Link, ModernTheme.PRIMARY)
    
    app.setPalette(palette)
    
    # 设置样式表
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1c1c1e;
            color: #ffffff;
        }
        
        QWidget {
            background-color: #1c1c1e;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 13px;
        }
        
        QGroupBox {
            background-color: #2c2c2e;
            border: 1px solid #3a3a3c;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 8px;
            font-weight: 600;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
            color: #ffffff;
        }
        
        QPushButton {
            background-color: #3a3a3c;
            border: 1px solid #48484a;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background-color: #48484a;
            border-color: #5a5a5c;
        }
        
        QPushButton:pressed {
            background-color: #2c2c2e;
        }
        
        QPushButton:checked {
            background-color: #0066cc;
            border-color: #0066cc;
            color: #ffffff;
        }
        
        QListWidget {
            background-color: #2c2c2e;
            border: 1px solid #3a3a3c;
            border-radius: 6px;
            padding: 4px;
            outline: none;
        }
        
        QListWidget::item {
            padding: 8px 12px;
            border-radius: 4px;
            margin: 1px;
        }
        
        QListWidget::item:selected {
            background-color: #0066cc;
            color: #ffffff;
        }
        
        QListWidget::item:hover {
            background-color: #3a3a3c;
        }
        
        QToolBar {
            background-color: #2c2c2e;
            border: none;
            spacing: 8px;
            padding: 8px;
        }
        
        QToolBar QToolButton {
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 6px;
            margin: 2px;
        }
        
        QToolBar QToolButton:hover {
            background-color: #3a3a3c;
            border-color: #48484a;
        }
        
        QCheckBox {
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 3px;
            border: 2px solid #48484a;
            background-color: #2c2c2e;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0066cc;
            border-color: #0066cc;
        }
        
        QSplitter::handle {
            background-color: #3a3a3c;
        }
        
        QSplitter::handle:horizontal {
            width: 1px;
        }
        
        QSplitter::handle:vertical {
            height: 1px;
        }
        
        QGraphicsView {
            background-color: #1c1c1e;
            border: 1px solid #3a3a3c;
            border-radius: 6px;
        }
        
        QStatusBar {
            background-color: #2c2c2e;
            color: #aeaeae;
            border-top: 1px solid #3a3a3c;
        }
        
        QStatusBar QLabel {
            background-color: transparent;
            border: none;
            padding: 4px 8px;
        }
        
        /* 特殊按钮样式 */
        QPushButton[class="primary"] {
            background-color: #0066cc;
            border-color: #0066cc;
            color: #ffffff;
        }
        
        QPushButton[class="primary"]:hover {
            background-color: #0077ee;
            border-color: #0077ee;
        }
        
        QPushButton[class="danger"] {
            background-color: #ff3b30;
            border-color: #ff3b30;
            color: #ffffff;
        }
        
        QPushButton[class="danger"]:hover {
            background-color: #ff453a;
            border-color: #ff453a;
        }
    """)

# ------------------------- 数据结构 -------------------------

class ShapeType:
    RECT = 'rect'
    POLY = 'poly'

@dataclass
class Annotation:
    shape: str                                 # 'rect' 或 'poly'
    cls_id: int                                # 类别 ID
    cls_name: str                              # 类别名（导出 COCO/LabelMe 用）
    points: List[Tuple[float, float]]          # 图像坐标（像素）
    # 备注：rect 用 [ (x1,y1), (x2,y2) ] 表示左上与右下；
    # poly 用 [(x,y), (x,y), ...] 至少3个点。

@dataclass
class ImageRecord:
    path: str
    width: int
    height: int
    annos: List[Annotation] = field(default_factory=list)

@dataclass
class ProjectData:
    images: Dict[str, ImageRecord] = field(default_factory=dict)   # key: 文件名
    classes: List[str] = field(default_factory=lambda: ['object'])
    # 新增：子文件夹管理
    root_dir: str = ""                    # 根目录
    sub_folders: List[str] = field(default_factory=list)  # 子文件夹列表
    current_sub_folder: str = ""          # 当前选中的子文件夹

# ------------------------- 图形项帮助 -------------------------

class RectItem(QGraphicsRectItem):
    def __init__(self, rect: QRectF, cls_color=None):
        super().__init__(rect)
        self.setFlags(
            QGraphicsRectItem.ItemIsSelectable |
            QGraphicsRectItem.ItemIsMovable
        )
        self.setZValue(10)
        
        # 使用现代化颜色
        if cls_color is None:
            cls_color = ModernTheme.PRIMARY
        
        pen = QPen(cls_color, 2, Qt.SolidLine)
        self.setPen(pen)
        self.setBrush(QBrush(QColor(0, 0, 0, 0)))  # 透明填充
        self.anno_ref: Optional[Annotation] = None

class PolyItem(QGraphicsPolygonItem):
    def __init__(self, points: List[QPointF], cls_color=None):
        super().__init__()
        self.setPolygon(points_to_qpolygonf(points))
        self.setFlags(
            QGraphicsPolygonItem.ItemIsSelectable |
            QGraphicsPolygonItem.ItemIsMovable
        )
        self.setZValue(10)
        
        # 使用现代化颜色
        if cls_color is None:
            cls_color = ModernTheme.PRIMARY
        
        pen = QPen(cls_color, 2, Qt.SolidLine)
        self.setPen(pen)
        self.setBrush(QBrush(QColor(0, 0, 0, 0)))  # 透明填充
        self.anno_ref: Optional[Annotation] = None

# 辅助：点列表转 QPolygonF
from PySide6.QtGui import QPolygonF

def points_to_qpolygonf(points: List[QPointF]) -> QPolygonF:
    poly = QPolygonF()
    for p in points:
        poly.append(p)
    return poly

# ------------------------- 视图/场景 -------------------------

class AnnotScene(QGraphicsScene):
    """负责绘制交互（拉框/多边形）。"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = 'select'       # 'select' | 'rect' | 'poly'
        self.tmp_rect_item: Optional[RectItem] = None
        self.tmp_poly_points: List[QPointF] = []
        self.tmp_poly_item: Optional[PolyItem] = None
        self.cls_color = ModernTheme.PRIMARY
        self.on_create_rect = None     # 回调：创建矩形后 (x1,y1,x2,y2)
        self.on_create_poly = None     # 回调：创建多边形后 ([points])
        self.on_delete_selected = None # 回调：删除选中项
        self.on_switch_mode = None     # 回调：切换模式
        self.on_switch_class = None    # 回调：切换类别
        self.main_window = None        # 主窗口引用

    def set_mode(self, m: str):
        self.mode = m
        # 取消临时绘制状态
        if self.tmp_rect_item:
            self.removeItem(self.tmp_rect_item)
            self.tmp_rect_item = None
        self.tmp_poly_points = []
        if self.tmp_poly_item:
            self.removeItem(self.tmp_poly_item)
            self.tmp_poly_item = None

    # 鼠标事件
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.mode == 'rect':
                pos = event.scenePos()
                self.tmp_rect_item = RectItem(QRectF(pos, QSize(1, 1)), self.cls_color)
                self.addItem(self.tmp_rect_item)
            elif self.mode == 'poly':
                pos = event.scenePos()
                self.tmp_poly_points.append(pos)
                if self.tmp_poly_item is None:
                    self.tmp_poly_item = PolyItem(self.tmp_poly_points, self.cls_color)
                    self.addItem(self.tmp_poly_item)
                else:
                    self.tmp_poly_item.setPolygon(points_to_qpolygonf(self.tmp_poly_points))
            else:
                super().mousePressEvent(event)
        elif event.button() == Qt.RightButton:
            # 右键：显示上下文菜单
            self._show_context_menu(event.scenePos())
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.mode == 'rect' and self.tmp_rect_item is not None:
            p1 = self.tmp_rect_item.rect().topLeft()
            p2 = event.scenePos()
            rect = QRectF(p1, p2).normalized()
            self.tmp_rect_item.setRect(rect)
        elif self.mode == 'poly' and self.tmp_poly_item is not None and self.tmp_poly_points:
            # 显示最后一个点跟随鼠标（临时）
            temp_points = list(self.tmp_poly_points)
            temp_points.append(event.scenePos())
            self.tmp_poly_item.setPolygon(points_to_qpolygonf(temp_points))
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.mode == 'rect' and self.tmp_rect_item is not None:
            rect = self.tmp_rect_item.rect().normalized()
            # 小尺寸过滤
            if rect.width() >= 3 and rect.height() >= 3:
                if self.on_create_rect:
                    self.on_create_rect(rect.left(), rect.top(), rect.right(), rect.bottom())
            self.removeItem(self.tmp_rect_item)
            self.tmp_rect_item = None
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        # 双击结束多边形
        if self.mode == 'poly' and len(self.tmp_poly_points) >= 3:
            if self.on_create_poly:
                pts = [(p.x(), p.y()) for p in self.tmp_poly_points]
                self.on_create_poly(pts)
            if self.tmp_poly_item:
                self.removeItem(self.tmp_poly_item)
                self.tmp_poly_item = None
            self.tmp_poly_points = []
        else:
            super().mouseDoubleClickEvent(event)

class AnnotView(QGraphicsView):
    def __init__(self, scene: AnnotScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHints(self.renderHints() | QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self._zoom = 0
        self.setMouseTracking(True)

    def wheelEvent(self, event):
        # 缩放
        if event.angleDelta().y() == 0:
            return
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self._zoom += 1 if factor > 1 else -1
        if self._zoom < -10:
            self._zoom = -10
        self.scale(factor, factor)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            # 空格切换为手形拖拽
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            event.accept()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            event.accept()
        else:
            super().keyReleaseEvent(event)

# ------------------------- 主窗口 -------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LabelX Studio — 现代化图像标注工具")
        # 适合14寸Mac的尺寸
        self.resize(1400, 900)
        self.setMinimumSize(1200, 700)

        self.project = ProjectData()
        self.current_image_key: Optional[str] = None

        # Scene / View
        self.scene = AnnotScene(self)
        self.scene.on_create_rect = self._on_rect_created
        self.scene.on_create_poly = self._on_poly_created
        self.scene.on_delete_selected = self.delete_selected
        self.scene.on_switch_mode = self.set_mode
        self.scene.on_switch_class = self._switch_class
        self.scene.main_window = self
        self.view = AnnotView(self.scene, self)
        self.view.setBackgroundBrush(QBrush(ModernTheme.BG_DARK))

        # 背景图项
        self.bg_pix = QGraphicsPixmapItem()
        self.bg_pix.setZValue(0)
        self.scene.addItem(self.bg_pix)

        # 左侧：类别面板
        self.class_list = QListWidget()
        self.class_list.addItems(self.project.classes)
        self.class_list.setCurrentRow(0)
        self.class_list.setMaximumHeight(200)

        self.btn_add_cls = QPushButton("➕ 添加类别")
        self.btn_del_cls = QPushButton("🗑️ 删除所选")
        self.btn_imp_cls = QPushButton("📁 导入classes.txt")
        self.btn_exp_cls = QPushButton("💾 导出classes.txt")

        self.btn_add_cls.clicked.connect(self.add_class)
        self.btn_del_cls.clicked.connect(self.del_class)
        self.btn_del_cls.setProperty("class", "danger")
        self.btn_imp_cls.clicked.connect(self.import_classes)
        self.btn_exp_cls.clicked.connect(self.export_classes)

        cls_box = QGroupBox("📋 类别管理")
        v = QVBoxLayout(cls_box)
        v.setSpacing(8)
        v.setContentsMargins(12, 16, 12, 12)
        v.addWidget(self.class_list)
        v.addWidget(self.btn_add_cls)
        v.addWidget(self.btn_del_cls)
        v.addWidget(self.btn_imp_cls)
        v.addWidget(self.btn_exp_cls)

        # 右侧：工具 + 导出
        self.tool_select = QPushButton("👆 选择/移动")
        self.tool_rect = QPushButton("⬜ 矩形")
        self.tool_poly = QPushButton("🔷 多边形")
        self.tool_select.setCheckable(True)
        self.tool_rect.setCheckable(True)
        self.tool_poly.setCheckable(True)
        self.tool_select.setChecked(True)
        self.tool_select.clicked.connect(lambda: self.set_mode('select'))
        self.tool_rect.clicked.connect(lambda: self.set_mode('rect'))
        self.tool_poly.clicked.connect(lambda: self.set_mode('poly'))

        self.chk_show_names = QCheckBox("显示类别名")
        self.chk_show_names.setChecked(True)

        self.btn_del_selected = QPushButton("🗑️ 删除所选")
        self.btn_del_selected.clicked.connect(self.delete_selected)
        self.btn_del_selected.setProperty("class", "danger")

        self.btn_export_yolo_det = QPushButton("📤 YOLO-Det(.txt)")
        self.btn_export_yolo_seg = QPushButton("📤 YOLO-Seg(.txt)")
        self.btn_export_coco = QPushButton("📤 COCO(.json)")
        self.btn_export_voc = QPushButton("📤 VOC(.xml)")
        self.btn_export_labelme = QPushButton("📤 LabelMe(.json)")

        self.btn_export_yolo_det.clicked.connect(self.export_yolo_det)
        self.btn_export_yolo_seg.clicked.connect(self.export_yolo_seg)
        self.btn_export_coco.clicked.connect(self.export_coco)
        self.btn_export_voc.clicked.connect(self.export_voc)
        self.btn_export_labelme.clicked.connect(self.export_labelme)

        tool_box = QGroupBox("🛠️ 工具与导出")
        tv = QVBoxLayout(tool_box)
        tv.setSpacing(8)
        tv.setContentsMargins(12, 16, 12, 12)
        tv.addWidget(self.tool_select)
        tv.addWidget(self.tool_rect)
        tv.addWidget(self.tool_poly)
        tv.addWidget(self.chk_show_names)
        tv.addWidget(self.btn_del_selected)
        tv.addSpacing(16)
        tv.addWidget(QLabel("📤 导出格式:"))
        tv.addWidget(self.btn_export_yolo_det)
        tv.addWidget(self.btn_export_yolo_seg)
        tv.addWidget(self.btn_export_coco)
        tv.addWidget(self.btn_export_voc)
        tv.addWidget(self.btn_export_labelme)
        tv.addStretch(1)

        # 下方：图像列表
        self.image_list = QListWidget()
        self.image_list.currentRowChanged.connect(self._on_image_changed)
        self.image_list.setMaximumHeight(150)
        
        # 子文件夹选择器
        self.sub_folder_combo = QComboBox()
        self.sub_folder_combo.currentTextChanged.connect(self._on_sub_folder_changed)
        self.sub_folder_combo.setVisible(False)  # 初始隐藏

        # 顶部工具栏（文件操作）
        tb = QToolBar("文件")
        tb.setIconSize(QSize(20, 20))
        self.addToolBar(tb)

        act_open = QAction("📁 打开图像文件夹", self)
        act_open.triggered.connect(self.open_images_dir)
        tb.addAction(act_open)

        act_save_proj = QAction("💾 保存项目", self)
        act_save_proj.triggered.connect(self.save_project)
        tb.addAction(act_save_proj)

        act_load_proj = QAction("📂 加载项目", self)
        act_load_proj.triggered.connect(self.load_project)
        tb.addAction(act_load_proj)

        tb.addSeparator()
        
        # 子文件夹切换按钮
        self.act_switch_folder = QAction("📁 切换子文件夹", self)
        self.act_switch_folder.triggered.connect(self._show_folder_switch_dialog)
        self.act_switch_folder.setVisible(False)  # 初始隐藏
        tb.addAction(self.act_switch_folder)
        
        tb.addSeparator()
        act_fit = QAction("🔍 适应窗口", self)
        act_fit.triggered.connect(self.fit_in_view)
        tb.addAction(act_fit)
        act_actual = QAction("📏 原始大小", self)
        act_actual.triggered.connect(self.reset_view_scale)
        tb.addAction(act_actual)

        # 布局
        left = QVBoxLayout()
        left.setSpacing(12)
        left.setContentsMargins(16, 16, 8, 16)
        left.addWidget(cls_box)
        left_w = QWidget(); left_w.setLayout(left)
        left_w.setMaximumWidth(280)

        right = QVBoxLayout()
        right.setSpacing(12)
        right.setContentsMargins(8, 16, 16, 16)
        right.addWidget(tool_box)
        right_w = QWidget(); right_w.setLayout(right)
        right_w.setMaximumWidth(280)

        center = QVBoxLayout()
        center.setSpacing(8)
        center.setContentsMargins(8, 8, 8, 8)
        center.addWidget(self.view)
        
        # 子文件夹选择器
        sub_folder_layout = QHBoxLayout()
        sub_folder_label = QLabel("📁 子文件夹:")
        sub_folder_label.setStyleSheet("font-weight: 600;")
        sub_folder_layout.addWidget(sub_folder_label)
        sub_folder_layout.addWidget(self.sub_folder_combo)
        sub_folder_layout.addStretch(1)
        center.addLayout(sub_folder_layout)
        
        # 图像列表标题
        image_list_label = QLabel("📷 图像列表（双击切换 / 方向键切换）")
        image_list_label.setStyleSheet("font-weight: 600; margin: 4px 0;")
        center.addWidget(image_list_label)
        center.addWidget(self.image_list)
        center_w = QWidget(); center_w.setLayout(center)

        splitter = QSplitter()
        splitter.addWidget(left_w)
        splitter.addWidget(center_w)
        splitter.addWidget(right_w)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        
        # 设置分割器初始尺寸
        splitter.setSizes([280, 800, 280])

        self.setCentralWidget(splitter)

        # 快捷键
        self._register_shortcuts()
        
        # 状态栏
        self.statusBar().showMessage("就绪 - 请打开图像文件夹开始标注")
        
        # 设置窗口图标和属性
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # 添加一些现代化的交互提示
        self._setup_tooltips()

    # --------------------- 业务逻辑 ---------------------
    def _register_shortcuts(self):
        QAction("选择", self, shortcut=QKeySequence("S"), triggered=lambda: self.set_mode('select'))
        QAction("矩形", self, shortcut=QKeySequence("R"), triggered=lambda: self.set_mode('rect'))
        QAction("多边形", self, shortcut=QKeySequence("P"), triggered=lambda: self.set_mode('poly'))
        QAction("删除", self, shortcut=QKeySequence.Delete, triggered=self.delete_selected)

    def _setup_tooltips(self):
        """设置工具提示"""
        self.tool_select.setToolTip("选择模式 - 点击选择或移动标注框 (快捷键: S)")
        self.tool_rect.setToolTip("矩形模式 - 拖拽绘制矩形标注 (快捷键: R)")
        self.tool_poly.setToolTip("多边形模式 - 点击绘制多边形，双击完成 (快捷键: P)")
        self.btn_del_selected.setToolTip("删除选中的标注 (快捷键: Delete)")
        self.chk_show_names.setToolTip("在标注框上显示类别名称")
        
        # 导出按钮提示
        self.btn_export_yolo_det.setToolTip("导出YOLO检测格式 - 每张图片一个.txt文件")
        self.btn_export_yolo_seg.setToolTip("导出YOLO分割格式 - 支持多边形标注")
        self.btn_export_coco.setToolTip("导出COCO格式 - 单个JSON文件")
        self.btn_export_voc.setToolTip("导出VOC格式 - 每张图片一个XML文件")
        self.btn_export_labelme.setToolTip("导出LabelMe格式 - 每张图片一个JSON文件")

    def current_class(self) -> Tuple[int, str]:
        row = self.class_list.currentRow()
        if row < 0:
            # 确保至少有一个类别
            if not self.project.classes:
                self.project.classes.append('object')
                self.class_list.addItem('object')
                self.class_list.setCurrentRow(0)
            row = 0
        return row, self.project.classes[row]

    def set_mode(self, m: str):
        self.scene.set_mode(m)
        self.tool_select.setChecked(m == 'select')
        self.tool_rect.setChecked(m == 'rect')
        self.tool_poly.setChecked(m == 'poly')
        
        # 更新状态栏
        mode_names = {
            'select': '选择模式',
            'rect': '矩形标注模式',
            'poly': '多边形标注模式'
        }
        self.statusBar().showMessage(f"当前模式: {mode_names.get(m, m)}")

    # 图像/项目
    def open_images_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择图像文件夹")
        if not d:
            return
        
        # 设置根目录
        self.project.root_dir = d
        
        # 扫描子文件夹
        self.project.sub_folders = self._scan_sub_folders(d)
        
        if not self.project.sub_folders:
            # 如果没有子文件夹，直接加载根目录的图片
            self.sub_folder_combo.setVisible(False)  # 隐藏子文件夹选择器
            self.act_switch_folder.setVisible(False)  # 隐藏工具栏切换按钮
            self._load_images_from_folder(d, "", show_warning=False) # 静默加载
        else:
            # 有子文件夹，显示子文件夹选择器
            self._show_sub_folder_selector()
    
    def _scan_sub_folders(self, root_dir: str) -> List[str]:
        """扫描根目录下的子文件夹"""
        sub_folders = []
        exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp'}
        
        try:
            for item in os.listdir(root_dir):
                item_path = os.path.join(root_dir, item)
                if os.path.isdir(item_path):
                    # 检查子文件夹是否包含图片
                    has_images = False
                    for file in os.listdir(item_path):
                        if os.path.splitext(file)[1].lower() in exts:
                            has_images = True
                            break
                    if has_images:
                        sub_folders.append(item)
        except Exception as e:
            print(f"扫描子文件夹时出错: {e}")
        
        return sorted(sub_folders)
    
    def _show_sub_folder_selector(self):
        """显示子文件夹选择器"""
        if not self.project.sub_folders:
            return
        
        # 更新界面上的子文件夹选择器（阻塞信号避免误触发"根文件夹"加载）
        self.sub_folder_combo.blockSignals(True)
        self.sub_folder_combo.clear()
        self.sub_folder_combo.addItem("根文件夹")
        self.sub_folder_combo.addItems(self.project.sub_folders)
        self.sub_folder_combo.setVisible(True)
        
        # 显示工具栏切换按钮
        self.act_switch_folder.setVisible(True)
        
        # 默认选择第一个子文件夹并加载
        if self.project.sub_folders:
            default_folder = self.project.sub_folders[0]
            self.sub_folder_combo.setCurrentText(default_folder)
            self.project.current_sub_folder = default_folder
            folder_path = os.path.join(self.project.root_dir, default_folder)
        self.sub_folder_combo.blockSignals(False)
        
        if self.project.sub_folders:
            self._load_images_from_folder(folder_path, default_folder)

    def _load_images_from_folder(self, folder_path: str, sub_folder_name: str = "", show_warning: bool = True):
        """从指定文件夹加载图片
        show_warning: 当没有图片时是否弹窗提示（用于根目录切换静默场景）
        """
        exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp'}
        
        try:
            files = [f for f in sorted(os.listdir(folder_path)) 
                    if os.path.splitext(f)[1].lower() in exts]
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法读取文件夹: {e}")
            return
        
        if not files:
            # 清空列表并更新状态栏，但根据需要控制是否弹窗
            self.project.images.clear()
            self.image_list.clear()
            if show_warning:
                QMessageBox.warning(self, "提示", "该文件夹下没有图片文件")
            else:
                self.statusBar().showMessage("该文件夹下没有图片文件")
            return
        
        # 清空当前图像列表
        self.project.images.clear()
        self.image_list.clear()
        loaded_count = 0
        
        for f in files:
            full = os.path.join(folder_path, f)
            pix = QPixmap(full)
            if pix.isNull():
                continue
            w = pix.width(); h = pix.height()
            key = os.path.basename(full)
            self.project.images[key] = ImageRecord(path=full, width=w, height=h)
            self.image_list.addItem(key)
            loaded_count += 1
        
        if loaded_count > 0:
            self.image_list.setCurrentRow(0)
            folder_display = f"子文件夹 '{sub_folder_name}'" if sub_folder_name and sub_folder_name != "根文件夹" else "根文件夹"
            self.statusBar().showMessage(f"已加载 {folder_display} 中的 {loaded_count} 张图像")
        else:
            # 即使files非空，但图片无法加载
            if show_warning:
                QMessageBox.warning(self, "提示", "未能加载任何有效的图像文件")
            else:
                self.statusBar().showMessage("未能加载任何有效的图像文件")

    def save_project(self):
        if not self.project.images:
            QMessageBox.information(self, "提示", "没有可保存的项目")
            return
        fn, _ = QFileDialog.getSaveFileName(self, "保存项目为", filter="LabelX Project (*.lxs.json)")
        if not fn:
            return
        data = {
            'classes': self.project.classes,
            'images': {
                k: {
                    'path': rec.path,
                    'width': rec.width,
                    'height': rec.height,
                    'annos': [
                        {
                            'shape': a.shape,
                            'cls_id': a.cls_id,
                            'cls_name': a.cls_name,
                            'points': a.points,
                        } for a in rec.annos
                    ]
                } for k, rec in self.project.images.items()
            }
        }
        with open(fn, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "完成", f"项目已保存到\n{fn}")

    def load_project(self):
        fn, _ = QFileDialog.getOpenFileName(self, "加载项目", filter="LabelX Project (*.lxs.json)")
        if not fn:
            return
        with open(fn, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.project = ProjectData()
        self.project.classes = data.get('classes', ['object'])
        self.class_list.clear(); self.class_list.addItems(self.project.classes); self.class_list.setCurrentRow(0)
        self.project.images.clear(); self.image_list.clear()
        for k, rec in data.get('images', {}).items():
            ir = ImageRecord(path=rec['path'], width=rec['width'], height=rec['height'])
            for a in rec.get('annos', []):
                ir.annos.append(Annotation(shape=a['shape'], cls_id=a['cls_id'], cls_name=a['cls_name'], points=[tuple(p) for p in a['points']]))
            self.project.images[k] = ir
            self.image_list.addItem(k)
        if self.image_list.count() > 0:
            self.image_list.setCurrentRow(0)

    def fit_in_view(self):
        if not self.bg_pix.pixmap().isNull():
            self.view.fitInView(self.bg_pix, Qt.KeepAspectRatio)

    def reset_view_scale(self):
        self.view.resetTransform()

    # 类别管理
    def add_class(self):
        name, ok = QFileDialog.getSaveFileName(self, "输入类别名（在文件名框中输入后取消保存即可）", "", "*")
        if not ok and not name:
            # 取消
            return
        # 小技巧：让用户在文件名输入框里打字，然后取消，拿到输入文本
        base = os.path.basename(name)
        base = os.path.splitext(base)[0]
        if not base:
            return
        self.project.classes.append(base)
        self.class_list.addItem(base)
        self.class_list.setCurrentRow(self.class_list.count()-1)

    def del_class(self):
        row = self.class_list.currentRow()
        if row < 0:
            return
        if self.class_list.count() <= 1:
            QMessageBox.warning(self, "提示", "至少保留一个类别")
            return
        name = self.project.classes[row]
        # 检查是否被使用
        used = any(any(a.cls_id == row for a in rec.annos) for rec in self.project.images.values())
        if used:
            QMessageBox.warning(self, "提示", f"类别 '{name}' 已被使用，无法删除。可先重标或改名。")
            return
        self.project.classes.pop(row)
        self.class_list.takeItem(row)
        self.class_list.setCurrentRow(0)

    def import_classes(self):
        fn, _ = QFileDialog.getOpenFileName(self, "选择 classes.txt", filter="Text (*.txt)")
        if not fn:
            return
        with open(fn, 'r', encoding='utf-8') as f:
            names = [line.strip() for line in f if line.strip()]
        if not names:
            QMessageBox.warning(self, "提示", "文件为空")
            return
        self.project.classes = names
        self.class_list.clear(); self.class_list.addItems(names); self.class_list.setCurrentRow(0)

    def export_classes(self):
        fn, _ = QFileDialog.getSaveFileName(self, "导出 classes.txt", filter="Text (*.txt)")
        if not fn:
            return
        with open(fn, 'w', encoding='utf-8') as f:
            for name in self.project.classes:
                f.write(name + "\n")
        QMessageBox.information(self, "完成", f"已导出到\n{fn}")

    # 图像切换
    def _on_image_changed(self, row: int):
        if row < 0 or row >= self.image_list.count():
            return
        key = self.image_list.item(row).text()
        self.show_image(key)

    def _on_sub_folder_changed(self, folder_name: str):
        """子文件夹选择器变化时触发"""
        if folder_name == "根文件夹":
            self.project.current_sub_folder = ""
            folder_path = self.project.root_dir
            # 根目录通常没有图片，此处静默，不弹窗
            self._load_images_from_folder(folder_path, folder_name, show_warning=False)
            return
        
        if not folder_name:
            return
        
        self.project.current_sub_folder = folder_name
        folder_path = os.path.join(self.project.root_dir, folder_name)
        self._load_images_from_folder(folder_path, folder_name)

    def show_image(self, key: str):
        if key not in self.project.images:
            return
        self.current_image_key = key
        rec = self.project.images[key]
        pix = QPixmap(rec.path)
        if pix.isNull():
            QMessageBox.warning(self, "错误", f"无法加载图像：{rec.path}")
            return
        self.scene.clear()
        self.bg_pix = QGraphicsPixmapItem(pix)
        self.bg_pix.setZValue(0)
        self.scene.addItem(self.bg_pix)
        # 重建标注项
        for a in rec.annos:
            color = ModernTheme.ANNOTATION_COLORS[a.cls_id % len(ModernTheme.ANNOTATION_COLORS)]
            if a.shape == ShapeType.RECT:
                (x1,y1),(x2,y2) = (a.points[0], a.points[1])
                item = RectItem(QRectF(QPointF(x1,y1), QPointF(x2,y2)).normalized(), color)
                item.anno_ref = a
                self.scene.addItem(item)
            else:
                pts = [QPointF(x,y) for x,y in a.points]
                item = PolyItem(pts, color)
                item.anno_ref = a
                self.scene.addItem(item)
        self.fit_in_view()
        
        # 更新状态栏
        current_index = self.image_list.currentRow() + 1
        total_count = self.image_list.count()
        anno_count = len(rec.annos)
        self.statusBar().showMessage(f"图像 {current_index}/{total_count}: {key} - {anno_count} 个标注")

    # 创建标注回调
    def _on_rect_created(self, x1, y1, x2, y2):
        if not self.current_image_key:
            return
        cls_id, cls_name = self.current_class()
        ann = Annotation(shape=ShapeType.RECT, cls_id=cls_id, cls_name=cls_name,
                         points=[(x1,y1),(x2,y2)])
        rec = self.project.images[self.current_image_key]
        rec.annos.append(ann)
        color = ModernTheme.ANNOTATION_COLORS[cls_id % len(ModernTheme.ANNOTATION_COLORS)]
        item = RectItem(QRectF(QPointF(x1,y1), QPointF(x2,y2)).normalized(), color)
        item.anno_ref = ann
        self.scene.addItem(item)
        
        # 更新状态栏
        self.statusBar().showMessage(f"已创建矩形标注: {cls_name}")

    def _on_poly_created(self, pts: List[Tuple[float,float]]):
        if not self.current_image_key:
            return
        cls_id, cls_name = self.current_class()
        ann = Annotation(shape=ShapeType.POLY, cls_id=cls_id, cls_name=cls_name,
                         points=pts)
        rec = self.project.images[self.current_image_key]
        rec.annos.append(ann)
        color = ModernTheme.ANNOTATION_COLORS[cls_id % len(ModernTheme.ANNOTATION_COLORS)]
        qpts = [QPointF(x,y) for x,y in pts]
        item = PolyItem(qpts, color)
        item.anno_ref = ann
        self.scene.addItem(item)
        
        # 更新状态栏
        self.statusBar().showMessage(f"已创建多边形标注: {cls_name} ({len(pts)} 个点)")

    def delete_selected(self):
        items = self.scene.selectedItems()
        if not items or not self.current_image_key:
            return
        rec = self.project.images[self.current_image_key]
        deleted_count = 0
        for it in items:
            if hasattr(it, 'anno_ref') and it.anno_ref in rec.annos:
                rec.annos.remove(it.anno_ref)
                deleted_count += 1
            self.scene.removeItem(it)
        
        # 更新状态栏
        if deleted_count > 0:
            self.statusBar().showMessage(f"已删除 {deleted_count} 个标注")

    def _switch_class(self, class_index: int):
        """切换类别（右键菜单回调）"""
        if self.on_switch_class and self.main_window:
            self.on_switch_class(class_index)

    # --------------------- 导出功能 ---------------------
    def export_yolo_det(self):
        # YOLO 检测（bbox），每张图片一个 .txt，格式：class x_center y_center w h（归一化）
        if not self._ensure_images():
            return
        out_dir = QFileDialog.getExistingDirectory(self, "选择导出文件夹（将生成 labels_yolo_det）")
        if not out_dir:
            return
        out_dir = os.path.join(out_dir, 'labels_yolo_det')
        os.makedirs(out_dir, exist_ok=True)
        cnt = 0
        for key, rec in self.project.images.items():
            lines = []
            for a in rec.annos:
                if a.shape != ShapeType.RECT:
                    # 多边形转外接矩形
                    xs = [p[0] for p in a.points]; ys = [p[1] for p in a.points]
                    x1, x2 = min(xs), max(xs); y1, y2 = min(ys), max(ys)
                else:
                    (x1,y1),(x2,y2) = a.points
                    if x1 > x2: x1, x2 = x2, x1
                    if y1 > y2: y1, y2 = y2, y1
                cx = ((x1 + x2)/2.0) / rec.width
                cy = ((y1 + y2)/2.0) / rec.height
                w = (x2 - x1) / rec.width
                h = (y2 - y1) / rec.height
                lines.append(f"{a.cls_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
            if lines:
                base = os.path.splitext(key)[0] + '.txt'
                with open(os.path.join(out_dir, base), 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                cnt += 1
        QMessageBox.information(self, "完成", f"YOLO-Det 导出完成，{cnt} 个标签文件，目录：\n{out_dir}")

    def export_yolo_seg(self):
        # YOLO 分割（polygon），每张图片一个 .txt，格式：class x1 y1 x2 y2 ...（归一化）
        if not self._ensure_images():
            return
        out_dir = QFileDialog.getExistingDirectory(self, "选择导出文件夹（将生成 labels_yolo_seg）")
        if not out_dir:
            return
        out_dir = os.path.join(out_dir, 'labels_yolo_seg')
        os.makedirs(out_dir, exist_ok=True)
        cnt = 0
        for key, rec in self.project.images.items():
            lines = []
            for a in rec.annos:
                if a.shape == ShapeType.POLY and len(a.points) >= 3:
                    vals = [str(a.cls_id)]
                    for x,y in a.points:
                        vals.append(f"{x/rec.width:.6f}")
                        vals.append(f"{y/rec.height:.6f}")
                    lines.append(' '.join(vals))
                elif a.shape == ShapeType.RECT:
                    # 将矩形转换为四点多边形（顺时针）
                    (x1,y1),(x2,y2) = a.points
                    if x1 > x2: x1, x2 = x2, x1
                    if y1 > y2: y1, y2 = y2, y1
                    rect_poly = [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]
                    vals = [str(a.cls_id)]
                    for x,y in rect_poly:
                        vals.append(f"{x/rec.width:.6f}")
                        vals.append(f"{y/rec.height:.6f}")
                    lines.append(' '.join(vals))
            if lines:
                base = os.path.splitext(key)[0] + '.txt'
                with open(os.path.join(out_dir, base), 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                cnt += 1
        QMessageBox.information(self, "完成", f"YOLO-Seg 导出完成，{cnt} 个标签文件，目录：\n{out_dir}")

    def export_coco(self):
        # 单一 dataset.json（images / annotations / categories）
        if not self._ensure_images():
            return
        fn, _ = QFileDialog.getSaveFileName(self, "保存 COCO 标注为", filter="JSON (*.json)")
        if not fn:
            return
        images = []
        annotations = []
        categories = [
            {"id": i, "name": name, "supercategory": "object"}
            for i, name in enumerate(self.project.classes)
        ]
        ann_id = 1
        img_id_map = {}
        for img_id, (key, rec) in enumerate(self.project.images.items(), start=1):
            images.append({
                "id": img_id,
                "file_name": key,
                "width": rec.width,
                "height": rec.height,
            })
            img_id_map[key] = img_id
            for a in rec.annos:
                if a.shape == ShapeType.RECT:
                    (x1,y1),(x2,y2) = a.points
                    if x1 > x2: x1, x2 = x2, x1
                    if y1 > y2: y1, y2 = y2, y1
                    bbox = [float(x1), float(y1), float(x2-x1), float(y2-y1)]
                    area = bbox[2]*bbox[3]
                    segmentation = []
                else:
                    xs = [p[0] for p in a.points]; ys = [p[1] for p in a.points]
                    x1, x2 = min(xs), max(xs); y1, y2 = min(ys), max(ys)
                    bbox = [float(x1), float(y1), float(x2-x1), float(y2-y1)]
                    segmentation = [ [float(v) for xy in a.points for v in xy] ]
                    # 多边形面积（Shoelace）
                    area = polygon_area(a.points)
                annotations.append({
                    "id": ann_id,
                    "image_id": img_id,
                    "category_id": a.cls_id,
                    "bbox": bbox,
                    "area": float(area),
                    "iscrowd": 0,
                    "segmentation": segmentation
                })
                ann_id += 1
        data = {"images": images, "annotations": annotations, "categories": categories}
        with open(fn, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        QMessageBox.information(self, "完成", f"COCO JSON 已保存到\n{fn}")

    def export_voc(self):
        # 每张图片一个 .xml，仅导出 bbox（多边形转外接框）
        if not self._ensure_images():
            return
        out_dir = QFileDialog.getExistingDirectory(self, "选择导出文件夹（将生成 Annotations_VOC）")
        if not out_dir:
            return
        out_dir = os.path.join(out_dir, 'Annotations_VOC')
        os.makedirs(out_dir, exist_ok=True)
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        cnt = 0
        for key, rec in self.project.images.items():
            root = ET.Element('annotation')
            ET.SubElement(root, 'filename').text = key
            size = ET.SubElement(root, 'size')
            ET.SubElement(size, 'width').text = str(rec.width)
            ET.SubElement(size, 'height').text = str(rec.height)
            ET.SubElement(size, 'depth').text = '3'
            for a in rec.annos:
                if a.shape == ShapeType.RECT:
                    (x1,y1),(x2,y2) = a.points
                else:
                    xs = [p[0] for p in a.points]; ys = [p[1] for p in a.points]
                    x1, x2 = min(xs), max(xs); y1, y2 = min(ys), max(ys)
                if x1 > x2: x1, x2 = x2, x1
                if y1 > y2: y1, y2 = y2, y1
                obj = ET.SubElement(root, 'object')
                ET.SubElement(obj, 'name').text = a.cls_name
                bnd = ET.SubElement(obj, 'bndbox')
                ET.SubElement(bnd, 'xmin').text = str(int(x1))
                ET.SubElement(bnd, 'ymin').text = str(int(y1))
                ET.SubElement(bnd, 'xmax').text = str(int(x2))
                ET.SubElement(bnd, 'ymax').text = str(int(int(y2)))
            # 美化并写入
            xml_str = ET.tostring(root, encoding='utf-8')
            pretty = minidom.parseString(xml_str).toprettyxml(indent="  ")
            base = os.path.splitext(key)[0] + '.xml'
            with open(os.path.join(out_dir, base), 'w', encoding='utf-8') as f:
                f.write(pretty)
            cnt += 1
        QMessageBox.information(self, "完成", f"VOC 导出完成，{cnt} 个标签文件，目录：\n{out_dir}")

    def export_labelme(self):
        # 每张图片一个 LabelMe 格式 json（shapes/points）
        if not self._ensure_images():
            return
        out_dir = QFileDialog.getExistingDirectory(self, "选择导出文件夹（将生成 labelme_json）")
        if not out_dir:
            return
        out_dir = os.path.join(out_dir, 'labelme_json')
        os.makedirs(out_dir, exist_ok=True)
        cnt = 0
        for key, rec in self.project.images.items():
            data = {
                "version": "5.3.0",
                "flags": {},
                "shapes": [],
                "imagePath": key,
                "imageData": None,
                "imageHeight": rec.height,
                "imageWidth": rec.width,
            }
            for a in rec.annos:
                if a.shape == ShapeType.RECT:
                    (x1,y1),(x2,y2) = a.points
                    pts = [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]
                    shape_type = 'polygon'
                else:
                    pts = a.points
                    shape_type = 'polygon'
                data['shapes'].append({
                    "label": a.cls_name,
                    "points": [[float(x), float(y)] for x,y in pts],
                    "group_id": None,
                    "shape_type": shape_type,
                    "flags": {}
                })
            base = os.path.splitext(key)[0] + '.json'
            with open(os.path.join(out_dir, base), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            cnt += 1
        QMessageBox.information(self, "完成", f"LabelMe JSON 导出完成，{cnt} 个文件，目录：\n{out_dir}")

    def _ensure_images(self) -> bool:
        if not self.project.images:
            QMessageBox.warning(self, "提示", "请先打开图像文件夹或加载项目")
            return False
        return True

    def _show_folder_switch_dialog(self):
        """显示子文件夹切换对话框"""
        if not self.project.sub_folders:
            QMessageBox.warning(self, "提示", "当前没有子文件夹可供切换")
            return
        
        dialog = QFileDialog(self, "切换子文件夹", self.project.root_dir)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly)
        
        if dialog.exec() == QFileDialog.Accepted:
            selected_folder = dialog.selectedFiles()[0]
            if selected_folder == self.project.root_dir:
                self.project.current_sub_folder = ""
                self.sub_folder_combo.setVisible(False)
                self.sub_folder_combo.setCurrentText("根文件夹")
                self.statusBar().showMessage("已切换回根文件夹")
            else:
                self.project.current_sub_folder = os.path.basename(selected_folder)
                self.sub_folder_combo.setVisible(True)
                self.sub_folder_combo.setCurrentText(self.project.current_sub_folder)
                self._load_images_from_folder(selected_folder, self.project.current_sub_folder)
                self.statusBar().showMessage(f"已切换到子文件夹: {self.project.current_sub_folder}")

    def _show_context_menu(self, pos: QPointF):
        """显示右键菜单"""
        from PySide6.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        # 工具模式切换
        tools_menu = menu.addMenu("🛠️ 工具模式")
        
        select_action = QAction("👆 选择模式", self)
        select_action.triggered.connect(lambda: self._switch_mode('select'))
        tools_menu.addAction(select_action)
        
        rect_action = QAction("⬜ 矩形模式", self)
        rect_action.triggered.connect(lambda: self._switch_mode('rect'))
        tools_menu.addAction(rect_action)
        
        poly_action = QAction("🔷 多边形模式", self)
        poly_action.triggered.connect(lambda: self._switch_mode('poly'))
        tools_menu.addAction(poly_action)
        
        menu.addSeparator()
        
        # 快速添加标注
        add_menu = menu.addMenu("➕ 快速添加")
        
        add_rect_action = QAction("⬜ 添加矩形", self)
        add_rect_action.triggered.connect(lambda: self._quick_add_rect(pos))
        add_menu.addAction(add_rect_action)
        
        add_poly_action = QAction("🔷 添加多边形", self)
        add_poly_action.triggered.connect(lambda: self._quick_add_poly(pos))
        add_menu.addAction(add_poly_action)
        
        menu.addSeparator()
        
        # 删除操作
        delete_action = QAction("🗑️ 删除选中", self)
        delete_action.triggered.connect(self._delete_selected)
        menu.addAction(delete_action)
        
        # 类别切换
        if self.project.classes:
            class_menu = menu.addMenu("📋 切换类别")
            for i, cls_name in enumerate(self.project.classes):
                class_action = QAction(f"• {cls_name}", self)
                class_action.triggered.connect(lambda checked, idx=i: self._switch_class(idx))
                class_menu.addAction(class_action)
        
        # 显示菜单
        global_pos = self.view.mapToGlobal(pos.toPoint())
        menu.exec(global_pos)
    
    def _switch_mode(self, mode: str):
        """切换工具模式"""
        if self.on_switch_mode:
            self.on_switch_mode(mode)
    
    def _quick_add_rect(self, pos: QPointF):
        """快速添加矩形"""
        if self.on_create_rect:
            # 创建一个小的矩形
            rect_size = 50
            x1, y1 = pos.x() - rect_size/2, pos.y() - rect_size/2
            x2, y2 = pos.x() + rect_size/2, pos.y() + rect_size/2
            self.on_create_rect(x1, y1, x2, y2)
    
    def _quick_add_poly(self, pos: QPointF):
        """快速添加多边形"""
        if self.on_create_poly:
            # 创建一个简单的三角形
            size = 30
            points = [
                (pos.x(), pos.y() - size),
                (pos.x() - size, pos.y() + size),
                (pos.x() + size, pos.y() + size)
            ]
            self.on_create_poly(points)
    
    def _delete_selected(self):
        """删除选中的标注"""
        if self.on_delete_selected:
            self.on_delete_selected()
    
    def _switch_class(self, class_index: int):
        """切换类别（右键菜单回调）"""
        if class_index < self.class_list.count():
            self.class_list.setCurrentRow(class_index)
            self.statusBar().showMessage(f"已切换到类别: {self.project.classes[class_index]}")

# ------------------------- 几何工具 -------------------------

def polygon_area(points: List[Tuple[float,float]]) -> float:
    # Shoelace 公式
    n = len(points)
    if n < 3:
        return 0.0
    s = 0.0
    for i in range(n):
        x1,y1 = points[i]
        x2,y2 = points[(i+1)%n]
        s += x1*y2 - x2*y1
    return abs(s)/2.0

# ------------------------- 入口 -------------------------

def main():
    import sys
    app = QApplication(sys.argv)
    
    # 应用现代化样式
    apply_modern_style(app)
    
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
