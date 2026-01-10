import subprocess
import sys
import pathlib

if len(sys.argv) != 2:
    print("Usage: python convert_mjpeg_to_mp4.py <folder>")
    sys.exit(1)

folder = pathlib.Path(sys.argv[1])

for mjpeg in folder.glob("*.mjpeg"):
    mp4 = mjpeg.with_suffix(".mp4")

    cmd = [
        "ffmpeg",
        "-y",
        "-framerate", "30",
        "-i", str(mjpeg),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        str(mp4)
    ]

    print(f"Converting {mjpeg.name} → {mp4.name}")
    subprocess.run(cmd, check=True)
