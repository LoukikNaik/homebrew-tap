"""Check exported reels and retain preview frames from a real CLI run."""

import json
import math
from pathlib import Path
import re
import subprocess
import sys


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def main():
    root = Path(sys.argv[1]).resolve()
    previews = root / "previews"
    previews.mkdir(exist_ok=True)
    results = []
    for clip in sorted((root / "outputs").glob("*/reel_*.mp4")):
        metadata = json.loads(run("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(clip)))
        video = next(stream for stream in metadata["streams"] if stream["codec_type"] == "video")
        audio = next((stream for stream in metadata["streams"] if stream["codec_type"] == "audio"), {})
        duration = float(metadata["format"]["duration"])
        decode = subprocess.run([
            "ffmpeg", "-nostdin", "-v", "error", "-i", str(clip),
            "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-",
        ], capture_output=True, text=True)
        volume = subprocess.run([
            "ffmpeg", "-nostdin", "-hide_banner", "-i", str(clip), "-t", "10",
            "-vn", "-af", "volumedetect", "-f", "null", "-",
        ], check=True, capture_output=True, text=True)
        match = re.search(r"max_volume: ([-\w.]+) dB", volume.stderr)
        peak = float(match.group(1)) if match else float("-inf")
        for seconds in (2, min(10, duration / 2)):
            run("ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(seconds),
                "-i", str(clip), "-frames:v", "1", "-update", "1", str(previews / f"{clip.stem}_{seconds:g}s.png"))
        checks = {
            "vertical_1080x1920": (video["width"], video["height"]) == (1080, 1920),
            "h264_video": video["codec_name"] == "h264",
            "aac_audio": audio.get("codec_name") == "aac",
            "valid_duration": math.isfinite(duration) and 0 < duration <= 91,
            "full_decode": decode.returncode == 0 and not decode.stderr.strip(),
            "non_silent_audio": math.isfinite(peak),
            "scorecard_present": clip.with_suffix(".txt").is_file(),
        }
        results.append({"file": str(clip.relative_to(root)), "duration": duration, "checks": checks})
    log = (root / "run.log").read_text()
    stages = {
        "first_pass_transcription": "First-pass engine:" in log,
        "second_pass_transcription": "Second pass on" in log,
        "caption_cleanup": "Cleanup:" in log,
        "caption_render": "Subtitle burn complete" in log,
        "pipeline_complete": "Pipeline complete" in log,
    }
    passed = len(results) == 1 and all(all(result["checks"].values()) for result in results) and all(stages.values())
    summary = {"source": "First five minutes of Dan Pink: The puzzle of motivation (TEDGlobal 2009)",
               "source_page": "https://www.ted.com/talks/dan_pink_the_puzzle_of_motivation",
               "exported_clips": len(results), "clips": results, "stages": stages, "passed": passed}
    (root / "media_checks.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
