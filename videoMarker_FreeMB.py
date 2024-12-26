import math
import os
import re
import subprocess


class VideoCompressor:
    def __init__(self, input_path, output_path, target_size_mb=5):
        self.input_path = input_path
        self.output_path = output_path
        self.target_size_bytes = target_size_mb * 1024 * 1024  # Convert MB to bytes

    def calculate_bitrate(self):
        """Calculate the required bitrate for the target file size."""
        original_size = os.path.getsize(self.input_path)

        if original_size <= self.target_size_bytes:
            print("The video is already small enough.")
            return None

        duration_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
                        'default=noprint_wrappers=1:nokey=1', self.input_path]
        duration_output = subprocess.check_output(duration_cmd)
        duration = float(duration_output.decode().strip())

        # Calculate target bitrate in bits per second
        target_bitrate = (self.target_size_bytes * 8) / duration

        # Add a small buffer to ensure we don't undershoot the target size
        buffer_percentage = 0.05  # 5%
        target_bitrate_with_buffer = target_bitrate * (1 + buffer_percentage)

        return math.floor(target_bitrate_with_buffer)

    def compress_video(self, bitrate=None):
        if bitrate is None:
            bitrate = self.calculate_bitrate()
            if bitrate is None:
                return

        pass_logfile_prefix = "ffmpeg2pass"

        for pass_num in [1, 2]:
            cmd = [
                'ffmpeg', '-y', '-i', self.input_path,
                '-vf', 'scale=1920:1080',
                '-b:v', f'{bitrate}', '-pass', str(pass_num),
                '-an',  # Disable audio for both passes
                '-passlogfile', pass_logfile_prefix
            ]
            if pass_num == 1:
                cmd.extend(['-f', 'mp4', '/dev/null' if os.name == 'posix' else 'NUL'])
            else:
                cmd.append(self.output_path)

            try:
                with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                      universal_newlines=True) as proc:
                    for line in proc.stdout:
                        print(line, end='')  # Print the live output
                        if match := re.search(r'time=(\d{2}:\d{2}:\d{2}\.\d{2})', line):
                            print(f'\rProcessing {match.group(1)}', end='')
                if proc.returncode != 0:
                    raise subprocess.CalledProcessError(proc.returncode, proc.args)
            except subprocess.CalledProcessError as e:
                print(f"Error during pass {pass_num}: {e}")
                return


# Example usage with custom target size
target_size_mb = 3  # Specify your desired target size in MB here
compressor = VideoCompressor('inputVideo/1.mp4', 'outputVideo/Free_MB_compressed_2.mp4', target_size_mb)
compressor.compress_video()
