import os

from PIL import Image


class ImageResizer:
    def __init__(self, input_path, output_path, target_size_mb=2, max_dimensions=(1920, 1080)):
        """
        初始化图像调整器。

        :param input_path: 输入图像文件路径。
        :param output_path: 输出调整后图像文件路径。
        :param target_size_mb: 目标文件大小，单位为MB，默认为2MB。
        :param max_dimensions: 图像最大尺寸，默认为(1920, 1080)。
        """
        self.input_path = input_path
        self.output_path = output_path
        self.target_size_bytes = target_size_mb * 1024 * 1024  # Convert MB to bytes
        self.max_width, self.max_height = max_dimensions

    def resize_image(self):
        """调整图像大小至最大尺寸（保持比例），并保存。"""
        with Image.open(self.input_path) as img:
            original_width, original_height = img.size

            # 计算缩放比例，保持比例不变
            ratio = min(self.max_width / original_width, self.max_height / original_height, 1)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)

            if (new_width, new_height) != (original_width, original_height):
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 保存调整后的图像，暂时不考虑文件大小
            img.save(self.output_path, quality=95)

    def compress_image(self):
        """压缩图像直至文件大小小于等于目标大小。"""
        quality = 95  # 初始高质量设置
        step = 5  # 每次减少的质量值

        while True:
            self.resize_image()  # 确保每次循环前都调整到正确尺寸

            file_size = os.path.getsize(self.output_path)
            if file_size <= self.target_size_bytes or quality <= 10:
                break

            quality -= step
            img = Image.open(self.output_path)
            img.save(self.output_path, quality=quality)

        print(f"最终质量设置为: {quality}")
        print(f"最终文件大小: {file_size / 1024:.2f} KB")


# 使用示例
input_image_path = 'inputImage/1.jpg'  # 替换为您的输入图片路径
output_image_path = 'outputImage/New_1.jpg'  # 替换为您的输出图片路径
target_size_mb = 1.5  # 目标文件大小为2MB

resizer = ImageResizer(input_image_path, output_image_path, target_size_mb)
resizer.compress_image()
