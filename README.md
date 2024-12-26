# MiniMarker

# 图像、视频处理工具类

## 简介

第一个工具类：工具类`imageMarker_Fixed16-9`则强制将图片调整为16:9的比例，并确保最终文件大小不超过指定限制
第二个：`imageMarker_Free16-9`图片（保持比例），并压缩到指定的文件大小以内。
第三个：`videoMarker_FixedMB`将视频 16：9，并压缩到固定文件大小以内，默认 5MB。
第四个：`videoMarker_FreeMB`将视频 16：9，并压缩到指定的文件大小以内，用户自定义。


## 安装依赖
本项目依赖于`Pillow`库来进行图像处理。请确保已经安装了`Pillow`：

```bash
pip install Pillow
