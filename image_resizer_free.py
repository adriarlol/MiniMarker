import os

from PIL import Image


class ImageResizer:
    def __init__(self, input_dir, output_dir, target_size_mb=2, max_dimensions=(1920, 1080)):
        """
        初始化图像调整器。

        :param input_dir: 输入图像文件夹路径。
        :param output_dir: 输出调整后图像文件夹路径。
        :param target_size_mb: 目标文件大小，单位为MB，默认为2MB。
        :param max_dimensions: 图像最大尺寸，默认为(1920, 1080)。
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.target_size_bytes = target_size_mb * 1024 * 1024  # Convert MB to bytes
        self.max_width, self.max_height = max_dimensions

    def resize_image(self, img_path):
        """调整单个图像大小至最大尺寸（保持比例），并返回新的文件路径。"""
        with Image.open(img_path) as img:
            original_width, original_height = img.size

            # 计算缩放比例，保持比例不变
            ratio = min(self.max_width / original_width, self.max_height / original_height, 1)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)

            if (new_width, new_height) != (original_width, original_height):
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            return img

    def compress_image(self, img, img_path):
        """压缩图像直至文件大小小于等于目标大小，并保存到输出目录。"""
        quality = 95  # 初始高质量设置
        step = 5  # 每次减少的质量值
        file_name = os.path.basename(img_path)
        output_path = os.path.join(self.output_dir, file_name)

        while True:
            img.save(output_path, quality=quality)

            file_size = os.path.getsize(output_path)
            if file_size <= self.target_size_bytes or quality <= 10:
                break

            quality -= step

        print(f"最终质量设置为: {quality}")
        print(f"最终文件大小: {file_size / 1024:.2f} KB")
        return output_path

    def process_images(self):
        """处理输入文件夹中的所有图片文件。"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for filename in os.listdir(self.input_dir):
            file_path = os.path.join(self.input_dir, filename)
            if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                print(f"正在处理: {filename}")
                img = self.resize_image(file_path)
                self.compress_image(img, file_path)


# 使用示例
if __name__ == "__main__":
    input_dir = 'input_img'  # 输入文件夹路径
    output_dir = 'output_img'  # 输出文件夹路径
    target_size_mb = 1.5  # 目标文件大小为1.5MB

    resizer = ImageResizer(input_dir, output_dir, target_size_mb)
    resizer.process_images()
