import os
import re
import subprocess


class VideoCompressor:
    def __init__(self, input_path, output_path, target_size_mb=5):
        self.input_path = input_path
        self.output_path = output_path
        self.target_size_bytes = target_size_mb * 1024 * 1024  # Convert MB to bytes

    def compress_video(self):
        original_size = os.path.getsize(self.input_path)
        if original_size <= self.target_size_bytes:
            print("The video is already small enough.")
            return

        duration_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
                        'default=noprint_wrappers=1:nokey=1', self.input_path]
        duration_output = subprocess.check_output(duration_cmd)
        duration = float(duration_output.decode().strip())
        bitrate = (self.target_size_bytes * 8) / duration  # Calculate bitrate in bits per second

        pass_logfile_prefix = "ffmpeg2pass"

        for pass_num in [1, 2]:
            cmd = [
                'ffmpeg', '-y', '-i', self.input_path,
                '-vf', 'scale=1920:1080',
                '-b:v', f'{bitrate:.0f}', '-pass', str(pass_num),
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


compressor = VideoCompressor('inputVideo/1.mp4', 'outputVideo/Fixed_5MB_compressed_1.mp4')
compressor.compress_video()
