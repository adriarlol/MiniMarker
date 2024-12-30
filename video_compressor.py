import argparse
import math
import os
import re
import subprocess


class VideoCompressor:
    def __init__(self, input_path, output_path, log_path, target_size_mb=5):
        """
        Initialize the video compressor.

        :param input_path: Input path (either directory or file).
        :param output_path: Output path for compressed videos.
        :param log_path: Directory to store logs and intermediate files.
        :param target_size_mb: Target file size in MB (default is 5MB).
        """
        self.input_path = input_path
        self.output_path = output_path
        self.log_path = log_path
        self.target_size_bytes = target_size_mb * 1024 * 1024  # Convert MB to bytes

    def calculate_bitrate(self, video_path):
        """Calculate the required bitrate for the target file size."""
        original_size = os.path.getsize(video_path)

        if original_size <= self.target_size_bytes:
            print(f"The video {os.path.basename(video_path)} is already small enough.")
            return None

        duration_cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', video_path
        ]
        duration_output = subprocess.check_output(duration_cmd)
        duration = float(duration_output.decode().strip())

        # Calculate target bitrate in bits per second
        target_bitrate = (self.target_size_bytes * 8) / duration

        # Add a small buffer to ensure we don't undershoot the target size
        buffer_percentage = 0.05  # 5%
        target_bitrate_with_buffer = target_bitrate * (1 + buffer_percentage)

        return math.floor(target_bitrate_with_buffer)

    def compress_video(self, video_path, log_prefix):
        """Compress a single video file."""
        file_name = os.path.basename(video_path)
        output_path = os.path.join(self.output_path, file_name)

        bitrate = self.calculate_bitrate(video_path)
        if bitrate is None:
            # If the video is already small enough, copy it directly to the output directory
            os.makedirs(self.output_path, exist_ok=True)
            os.link(video_path, output_path)
            return

        for pass_num in [1, 2]:
            cmd = [
                'ffmpeg', '-y', '-i', video_path,
                '-vf', 'scale=1920:1080',
                '-b:v', f'{bitrate}', '-pass', str(pass_num),
                '-an',  # Disable audio for both passes
                '-passlogfile', log_prefix
            ]
            if pass_num == 1:
                cmd.extend(['-f', 'mp4', '/dev/null' if os.name == 'posix' else 'NUL'])
            else:
                cmd.append(output_path)

            try:
                with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                      universal_newlines=True) as proc:
                    for line in proc.stdout:
                        print(line, end='')  # Print live output
                        if match := re.search(r'time=(\d{2}:\d{2}:\d{2}\.\d{2})', line):
                            print(f'\rProcessing {file_name}: {match.group(1)}', end='')
                if proc.returncode != 0:
                    raise subprocess.CalledProcessError(proc.returncode, proc.args)
            except subprocess.CalledProcessError as e:
                print(f"Error during pass {pass_num} for {file_name}: {e}")
                return

    def process_videos(self):
        """Process all video files in the input directory."""
        os.makedirs(self.output_path, exist_ok=True)
        os.makedirs(self.log_path, exist_ok=True)

        if os.path.isdir(self.input_path):
            print("Processing all videos in the specified directory.")
            for filename in os.listdir(self.input_path):
                file_path = os.path.join(self.input_path, filename)
                if os.path.isfile(file_path) and filename.lower().endswith(('.mp4', '.avi', '.mkv')):
                    print(f"Processing: {filename}")
                    log_prefix = os.path.join(self.log_path, f"log_{os.path.splitext(filename)[0]}")
                    self.compress_video(file_path, log_prefix)
        elif os.path.isfile(self.input_path):
            print("Processing the specified video file.")
            file_name = os.path.basename(self.input_path)
            log_prefix = os.path.join(self.log_path, f"log_{os.path.splitext(file_name)[0]}")
            self.compress_video(self.input_path, log_prefix)
        else:
            print("Invalid input path.")


# Command-line argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description="Compress video files to a target size.")
    parser.add_argument('input_path', help="Input file or directory containing video files.")
    parser.add_argument('output_path', help="Output directory for compressed videos.")
    parser.add_argument('log_path', help="Directory to store logs and intermediate files.")
    parser.add_argument('--target-size-mb', type=int, default=5, help="Target file size in MB (default is 5MB).")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    compressor = VideoCompressor(args.input_path, args.output_path, args.log_path, args.target_size_mb)
    compressor.process_videos()

# 使用方法
# 指定目录（批量处理）
# 要处理指定目录下的所有视频文件，请在命令行中输入如下命令：
# python video_compressor.py input_video output_video log --target-size-mb 8
# 这将处理input_dir中的所有视频文件，并将压缩后的文件保存到output_dir中，日志文件和其他中间文件将被保存到log_dir中。
#
# 指定文件（单独处理）
# 要仅处理指定的单个视频文件，请在命令行中输入如下命令：
# python video_compressor.py input_video/New_Post.mp4 output_video log --target-size-mb 6
# 这将仅处理inputVideo/New_Post.mp4文件，并将压缩后的文件保存到output_dir中，日志文件和其他中间文件将被保存到log_dir中。
