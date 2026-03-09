# LabelX Studio

LabelX Studio 是一个基于 **PySide6** 开发的轻量级图像标注工具，支持矩形标注、多边形标注、类别管理、图像列表浏览、缩放平移，以及多种常见数据集格式导出。

该项目采用单文件实现，便于课程作业、项目展示和软著材料整理。

---

## 功能特性

- 支持 **矩形标注**
- 支持 **多边形标注**
- 支持 **类别管理**
- 支持 **图像列表切换**
- 支持 **缩放 / 平移 / 选择 / 删除**
- 支持 **子文件夹图片加载**
- 支持多种标注格式导出：
  - YOLO Detection (`.txt`)
  - YOLO Segmentation (`.txt`)
  - COCO (`.json`)
  - VOC (`.xml`)
  - LabelMe (`.json`)
- 支持项目保存 / 加载：
  - `.lxs.json`

---

## 技术栈

- Python 3.10+
- PySide6
- Pillow
- NumPy

---

## 安装依赖

先安装所需依赖：

```bash
pip install pyside6 pillow numpy