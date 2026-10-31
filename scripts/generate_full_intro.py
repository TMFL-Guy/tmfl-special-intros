#!/usr/bin/env python3
"""Render five distinct Wan clips and combine them into a single silent MP4.

Place images at assets/halloween/{stadium,raven,titan,collision,finale}.png,
or supply direct HTTPS image URLs in the workflow form. The existing repo poster
is used only for the finale. Distinct source images are required for other scenes.
"""
import os
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
ASSETS = ROOT / "assets" / "halloween"
POSTER = ROOT / "ChatGPT Image Oct 30, 2026, 05_17_08 PM.png"
DURATION = os.environ.get("SCENE_DURATION", "3.5")
SCENES = [
    ("stadium", "Photorealistic empty football stadium at midnight. Thick ground fog drifts across the field, stadium floodlights flicker, camera slowly pushes forward. Continuous realistic motion, no text, no morphing."),
    ("raven", "Cinematic closeup of a realistic black raven perched on a stadium floodlight at night. Purple reflections in its eyes. The bird naturally spreads both wings and launches into flight, camera follows smoothly. Anatomically consistent raven, no morphing, no text."),
    ("titan", "Cinematic massive ancient armored titan warrior in a dark stormy stadium. Blue lightning illuminates armor, blue fog swirls as the warrior slowly steps forward. Natural continuous movement, no morphing, no text."),
    ("collision", "Epic nighttime football stadium under storm clouds. Purple lightning and blue lightning surge toward each other and collide above the field, swirling fog and dramatic camera movement. Realistic continuous motion, no text."),
    ("finale", "Slow dramatic camera push toward a glowing Halloween Classic football poster, purple and electric blue smoke billows across the edges, cinematic atmospheric lighting, maintain original logo shapes and typography, no morphing."),
]

def source_for(name):
    url = os.environ.get("IMAGE_URL_" + name.upper(), "").strip()
    if url:
        return url, None
    uploaded_names = {
        "stadium": "01_Original_Haunted_Stadium.jpg",
        "raven": "a_dramatic_cinematic_night_scene_the_same_black.png",
        "titan": "dramatic_cinematic_scene_a_giant_armored_titan_w.png",
        "collision": "a_dramatic_cinematic_sci_fi_sports_collision_scene.png",
    }
    uploaded = ASSETS / uploaded_names.get(name, "__none__")
    if uploaded.is_file():
        return "", uploaded
    for ext in (".png", ".jpg", ".jpeg"):
        file = ASSETS / (name + ext)
        if file.is_file():
            return "", file
    if name == "finale" and POSTER.is_file():
        return "", POSTER
    return "", None

def main():
    missing = [name for name, _ in SCENES if not any(source_for(name))]
    if missing:
        raise RuntimeError(
            "Missing scene images: " + ", ".join(missing) +
            ". Upload distinct images into assets/halloween/ (stadium.png, raven.png, titan.png, collision.png), "
            "or enter direct image URLs in Run workflow. The existing poster is used for finale."
        )
    clips = []
    for idx, (name, prompt) in enumerate(SCENES, 1):
        print(f"=== Scene {idx}/5: {name} ===", flush=True)
        url, local = source_for(name)
        env = os.environ.copy()
        env.update(INPUT_IMAGE_URL=url, INPUT_PROMPT=prompt, INPUT_DURATION=DURATION)
        if local:
            # The existing generator checks assets/scene.png before its own poster fallback.
            # Feed the scene image through a local file copy to that expected path.
            shared = ROOT / "assets" / "scene.png"
            shared.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(local, shared)
        else:
            shared = ROOT / "assets" / "scene.png"
            shared.unlink(missing_ok=True)
        try:
            subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_wan_clip.py")],
                           env=env, check=True)
        finally:
            shared.unlink(missing_ok=True)
        generated = OUT / "halloween-classic-clip.mp4"
        clip = OUT / f"{idx:02d}-{name}.mp4"
        generated.replace(clip)
        clips.append(clip)
    # Re-encode to consistent parameters; the upstream may vary dimensions/frame rates.
    normalized = []
    for idx, clip in enumerate(clips, 1):
        norm = OUT / f"normalized-{idx:02d}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip),
                        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=24,format=yuv420p",
                        "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "19",
                        str(norm)], check=True)
        normalized.append(norm)
    manifest = OUT / "concat.txt"
    manifest.write_text("".join(f"file '{p.name}'\n" for p in normalized))
    final = OUT / "TMFL-Halloween-Classic-Intro.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(manifest), "-c", "copy", "-movflags", "+faststart", str(final)], check=True)
    (OUT / "full-intro-status.txt").write_text(f"SUCCESS: {final.name}; 5 scenes; silent video\n")
    print(f"SUCCESS: {final}", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        (OUT / "full-intro-status.txt").write_text(f"FAILED: {type(exc).__name__}: {exc}\n")
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
