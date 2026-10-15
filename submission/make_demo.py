"""Make an MP4 walkthrough from real browser captures; no generated UI frames."""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / ".tools"))
import imageio_ffmpeg

DEMO = ROOT / "submission" / "demo"
FRAMES = DEMO / "frames"
FRAMES.mkdir(exist_ok=True)
scenes = [
    ("01-home.jpg", "Brief Ledger / a local workspace for freelance estimates", 5),
    ("02-brief.jpg", "Paste a fictional client brief. Inference runs locally with Qwen3 4B.", 6),
    ("03-scope.jpg", "Read each scope item beside its source quote. Review the interpretation.", 8),
    ("04-review.jpg", "Edit questions and scope. You enter the hours and hourly rate.", 8),
    ("05-estimate.jpg", "Calculate a draft estimate with decimal arithmetic, then download it.", 8),
    ("06-mobile.jpg", "The same review workflow fits a 375-pixel phone layout.", 5),
]
font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 24)
items = []
for index, (filename, caption, duration) in enumerate(scenes):
    frame = Image.new("RGB", (1280, 800), "#eef2f9")
    source = Image.open(DEMO / filename).convert("RGB")
    source.thumbnail((1240, 700), Image.Resampling.LANCZOS)
    frame.paste(source, ((1280 - source.width) // 2, (710 - source.height) // 2))
    draw = ImageDraw.Draw(frame)
    draw.rectangle((0, 720, 1280, 800), fill="#17243d")
    draw.text((30, 742), caption, font=font, fill="white")
    output = FRAMES / f"{index:02}.jpg"
    frame.save(output, quality=95)
    items.extend([f"file '{output.as_posix()}'", f"duration {duration}"])
items.append(f"file '{output.as_posix()}'")
manifest = FRAMES / "scenes.txt"
manifest.write_text("\n".join(items) + "\n", encoding="utf-8")
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
target = DEMO / "brief-ledger-demo.mp4"
subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(manifest),
                "-vf", "fps=24", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                "-movflags", "+faststart", str(target)], check=True)
subprocess.run([ffmpeg, "-v", "error", "-i", str(target), "-f", "null", "-"], check=True)
print(f"Decoded demo successfully: {target}")
