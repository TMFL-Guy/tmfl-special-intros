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
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
ASSETS = ROOT / "assets" / "halloween"
POSTER = ROOT / "ChatGPT Image Oct 30, 2026, 05_17_08 PM.png"
DURATION = os.environ.get("SCENE_DURATION", "3.5")
SCENES = [
    ("stadium", "Photorealistic empty football stadium at midnight. Thick ground fog drifts across the field, stadium floodlights flicker, camera slowly pushes forward. Continuous realistic motion, no text, no morphing."),
    ("raven", "Cinematic closeup of a realistic black raven perched on a stadium floodlight at night. Purple reflections in its eyes. The bird naturally spreads both wings and launches into flight, camera follows smoothly. Anatomically consistent raven, no morphing, no text."),
    ("raven_descends", "A giant realistic black raven flies downward through a completely dark football stadium at midnight, beating its wings and descending toward the field. Its eyes glow violet. Purple lightning flashes across storm clouds and briefly illuminates its feathers. All stadium floodlights remain switched OFF, only lightning illuminates the stadium. Thick purple fog rolls across the turf. Cinematic smooth continuous motion, no logos, no text."),
    ("pumpkin_slam", "A colossal dark jack-o-lantern crashes down from above into the center of a deserted rain-soaked football field. Its impact kicks up a huge circular shockwave of dirt, leaves and rolling gray fog. After landing, its carved eyes and jagged grin slowly ignite from darkness into blazing fiery orange. The stadium remains dark, purple lightning flashes across the sky, cinematic smooth action and camera shake, no logos, no text."),
    ("titans_graveyard", "A towering armored Titan with glowing blue eyes stands in a stormy midnight stadium graveyard behind exactly TWO tombstones: Cincinnati Bengals logo and BENGALS on the left, Washington Commanders W logo and COMMANDERS on the right. A sword is planted in the muddy ground between them. Blue lightning flashes, dense blue fog drifts across the ground, camera slowly pushes toward the warrior. No Tennessee Titans logo, no additional gravestones, no extra text."),
    ("ravens_graveyard", "A black raven with glowing purple eyes flies low into a dark foggy stadium graveyard, slows and lands on a rock between EXACTLY TWO weathered tombstones. Left tombstone: Jacksonville Jaguars logo and JAGUARS. Right tombstone: Tampa Bay Buccaneers logo and BUCCANEERS. No other gravestones, no Baltimore Ravens logo. Purple lightning flashes in the distance, fog drifts slowly. Cinematic smooth motion, preserve stone engravings."),
    ("logo_disintegration", "FIRST SHOT ONLY. The armored Titan drives his glowing blue sword through the Baltimore Ravens emblem. The Ravens emblem cracks, fractures into hundreds of tiny purple shards, and completely disintegrates into purple dust and smoke. The Ravens emblem must be gone by the end. Do NOT reveal or animate the Titans emblem yet. Cinematic continuous motion, no text."),
    ("logo_emergence", "SECOND SHOT AFTER the Ravens emblem has completely disappeared. A giant Tennessee Titans emblem materializes from swirling electric blue fog, growing larger and becoming brilliantly illuminated. Blue smoke curls around the emblem, camera slowly pushes in. No Ravens emblem visible, no destruction, preserve Titans emblem shape, no extra text."),
    ("fight_charge", "Cinematic football stadium at night. The giant raven flies forward from the right with talons extended, wings beating. The armored Titan charges forward from the left, holding his blue glowing sword high over his head, ready to strike. Camera tracks the approach, wind and fog move, realistic smooth action, no impact yet, no logos or text."),
    ("fight_impact", "Cinematic impact at midfield. The Titan brings his glowing blue sword downward and the raven blocks it with extended talons. At the exact point where sword and talons touch, bright blue and purple lightning erupts outward across the night stadium. Sparks and shockwave spread through the fog. Dramatic continuous motion, no logos, no text."),
    ("raven_titans_breakthrough", "A giant black raven flies forward through a large glowing Tennessee Titans emblem, shattering it into blue crystalline fragments and swirling blue mist. The raven continues through the fragments with strong wingbeats as a Baltimore Ravens emblem emerges behind it in purple fog and violet lightning. Cinematic continuous motion, preserve logos, no text."),
    ("raven_reveal", "A black raven flies into thick rolling purple fog and vanishes. Purple lightning flickers, and the Baltimore Ravens emblem becomes visible through the clearing mist. Smooth cinematic camera push, preserve emblem design, no extra text."),
    ("titan", "A huge armored fantasy guardian stands in a misty football stadium at night. Blue light flickers gently on the armor as fog moves and the camera slowly pushes in. Smooth cinematic motion, no text."),
    ("collision", "Purple and electric-blue energy streams swirl and meet at the center of a nighttime football stadium. Sparks shimmer and clouds drift. Slow cinematic camera movement, smooth animation, no text."),
    ("finale", "Slow dramatic camera push toward a glowing Halloween Classic football poster, purple and electric blue smoke billows across the edges, cinematic atmospheric lighting, maintain original logo shapes and typography, no morphing."),
]

def source_for(name):
    override_filename = os.environ.get("IMAGE_FILE_" + name.upper(), "").strip()
    if override_filename:
        override = ASSETS / pathlib.Path(override_filename).name
        if not override.is_file():
            raise FileNotFoundError(f"Selected image for {name} does not exist: {override_filename}")
        return "", override
    url = os.environ.get("IMAGE_URL_" + name.upper(), "").strip()
    if url:
        return url, None
    uploaded_names = {
        "stadium": "01_Original_Haunted_Stadium.jpg",
        "raven_descends": "35ce7a01-21b5-45b0-a059-c59fc9badde7.png",
        "ravens_graveyard": "ed12321a-8776-43ea-bf57-f51be360e592.png",
        "titans_graveyard": "95f7cb64-f03a-433e-9a35-1334c34dddc0.png",
        "pumpkin_slam": "8d6549f3-e86c-4182-aa32-64e39bc00544.png",
        "raven": "a_dramatic_cinematic_night_scene_the_same_black.png",
        "raven_reveal": "a_dramatic_cinematic_cgi_scene_a_dark_stormy_sky.png",
        "raven_titans_breakthrough": "850b3818-23db-4c57-854a-dd58d10b180c.png",
        "fight_charge": "a_dramatic_cinematic_high_detail_cgi_photoreal_f.png",
        "logo_disintegration": "a_cinematic_hyper_detailed_digital_cgi_scene_a_d.png",
        "logo_emergence": "a_cinematic_hyper_detailed_digital_cgi_scene_a_d.png",
        "fight_impact": "image(6).png",
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
    selected = {x.strip().lower() for x in os.environ.get("SELECT_SCENES", "").split(",") if x.strip()}
    scenes = [(name, prompt) for name, prompt in SCENES if not selected or name in selected]
    if not scenes:
        raise ValueError("No matching scenes selected.")
    missing = [name for name, _ in scenes if not any(source_for(name))]
    if missing:
        raise RuntimeError(
            "Missing scene images: " + ", ".join(missing) +
            ". Upload distinct images into assets/halloween/ (stadium.png, raven.png, titan.png, collision.png), "
            "or enter direct image URLs in Run workflow. The existing poster is used for finale."
        )
    clips = []
    skipped = []
    attempts = int(os.environ.get("SCENE_MAX_ATTEMPTS", "2"))
    for idx, (name, prompt) in enumerate(scenes, 1):
        print(f"=== Scene {idx}/{len(scenes)}: {name} ===", flush=True)
        url, local = source_for(name)
        env = os.environ.copy()
        env.update(INPUT_IMAGE_URL=url, INPUT_PROMPT=prompt, INPUT_DURATION=DURATION, MAX_INPUT_WIDTH="832", MAX_INPUT_HEIGHT="480")
        shared = ROOT / "assets" / "scene.png"
        shared.parent.mkdir(parents=True, exist_ok=True)
        if local:
            shutil.copyfile(local, shared)
        else:
            shared.unlink(missing_ok=True)
        generated = OUT / "halloween-classic-clip.mp4"
        generated.unlink(missing_ok=True)
        success = False
        try:
            for attempt in range(1, attempts + 1):
                print(f"Scene {name}: rendering attempt {attempt}/{attempts}", flush=True)
                result = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / "generate_wan_clip.py")],
                    env=env, check=False
                )
                if result.returncode == 0 and generated.is_file():
                    success = True
                    break
                if attempt < attempts:
                    print(f"Scene {name} failed; next attempt in 10 seconds", flush=True)
                    time.sleep(10)
        finally:
            shared.unlink(missing_ok=True)
        if not success:
            skipped.append(name)
            print(f"WARNING: Skipping {name}: public AI service rejected this scene", flush=True)
            continue
        clip = OUT / f"{idx:02d}-{name}.mp4"
        generated.replace(clip)
        clips.append(clip)
    if selected in ({"logo_disintegration", "logo_emergence"}, {"raven_descends", "ravens_graveyard"}) and skipped:
        raise RuntimeError("Transformation incomplete: both the Ravens disintegration and the later Titans reveal must render successfully.")
    if not clips:
        raise RuntimeError("All scenes were rejected by the public AI video service.")
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
    final = OUT / ("TMFL-Ravens-Fog-Logo-Reveal.mp4" if selected == {"raven_reveal"} else "TMFL-Raven-Descent-Graveyard.mp4" if selected == {"raven_descends", "ravens_graveyard"} else "TMFL-Titans-Graveyard.mp4" if selected == {"titans_graveyard"} else "TMFL-Pumpkin-Slam.mp4" if selected == {"pumpkin_slam"} else "TMFL-Raven-Titans-Breakthrough.mp4" if selected == {"raven_titans_breakthrough"} else "TMFL-Titans-Logo-Disintegration.mp4" if selected == {"logo_disintegration", "logo_emergence"} or selected == {"logo_disintegration"} else "TMFL-Raven-Titan-Fight.mp4" if selected == {"fight_charge", "fight_impact"} else "TMFL-Titan-Collision-CGI.mp4" if selected == {"titan", "collision"} else "TMFL-Halloween-Classic-Intro.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(manifest), "-c", "copy", "-movflags", "+faststart", str(final)], check=True)
    (OUT / "full-intro-status.txt").write_text(f"SUCCESS: {final.name}; {len(clips)}/{len(scenes)} scenes; skipped: {', '.join(skipped) or 'none'}; silent video\n")
    print(f"SUCCESS: {final}; scenes rendered: {len(clips)}/5; skipped: {skipped}", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        (OUT / "full-intro-status.txt").write_text(f"FAILED: {type(exc).__name__}: {exc}\n")
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
