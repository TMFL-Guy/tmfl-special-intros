#!/usr/bin/env python3
"""Render the TMFL Halloween Classic as an MP4 using FFmpeg and espeak-ng.
Requires: ffmpeg, espeak-ng, Python 3. Uses uploaded halloween-classic.png.
"""
import os, subprocess, tempfile, pathlib
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/"halloween-classic.mp4"
ART=ROOT/"halloween-classic.png"
if not ART.exists(): raise SystemExit("Upload halloween-classic.png to the repository root first.")
SCENES=[
("Every October... the nights grow longer.", "EVERY OCTOBER", "THE NIGHTS GROW LONGER", "wind"),
("The shadows grow darker.", "THE SHADOWS", "GROW DARKER", "clock"),
("And when the clock strikes midnight...", "WHEN THE CLOCK", "STRIKES MIDNIGHT", "clock"),
("...the monsters come out to play.", "THE MONSTERS", "COME OUT TO PLAY", "thunder"),
("From the darkness of Baltimore...", "FROM THE DARKNESS", "OF BALTIMORE", "wind"),
("An omen of fear. A shadow of death. A nightmare with wings.", "AN OMEN OF FEAR", "A NIGHTMARE WITH WINGS", "raven"),
("THE BALTIMORE RAVENS.", "BALTIMORE", "RAVENS", "raven"),
("But from the depths of Tennessee...", "FROM THE DEPTHS", "OF TENNESSEE", "thunder"),
("An ancient force awakens. Unshaken. Unforgiving. Unstoppable.", "AN ANCIENT FORCE", "AWAKENS", "thunder"),
("THE TENNESSEE TITANS.", "TENNESSEE", "TITANS", "thunder"),
("Two teams.", "TWO TEAMS", "", "drum"),
("One battlefield.", "ONE BATTLEFIELD", "", "drum"),
("And on this night...", "AND ON THIS NIGHT", "", "silence"),
("...there's nowhere to hide.", "NOWHERE", "TO HIDE", "silence"),
("Because tonight...", "BECAUSE TONIGHT", "", "heartbeat"),
("...FEAR TAKES THE FIELD.", "FEAR TAKES", "THE FIELD", "thunder"),
("BALTIMORE. TENNESSEE.", "BALTIMORE", "TENNESSEE", "drum"),
("THE HALLOWEEN CLASSIC.", "HALLOWEEN", "CLASSIC", "drum"),
("ONLY ONE... WILL SURVIVE THE NIGHT.", "ONLY ONE", "WILL SURVIVE THE NIGHT", "thunder"),
("RAVENS vs. TITANS. TMFL — WHERE NIGHTMARES BECOME LEGENDS.", "RAVENS VS. TITANS", "WHERE NIGHTMARES BECOME LEGENDS", "wind"),
("Now, if you find the urge. Get your candy corn and watch the game, if you dare", "GET YOUR CANDY CORN", "AND WATCH... IF YOU DARE", "wind"),
]
def run(args): subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
def esc(s):return s.replace("\\","\\\\").replace(":","\\:").replace("'","\\'").replace("%","\\%").replace(",","\\,")
with tempfile.TemporaryDirectory() as td:
    td=pathlib.Path(td)
    clips=[]
    font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    for i,(spoken,top,bottom,cue) in enumerate(SCENES):
        raw=td/f"{i:02}.wav";voice=td/f"{i:02}-voice.wav";clip=td/f"{i:02}.mp4"
        # Slow, low-pitched, theatrical synthetic narrator (not an impersonation).
        run(["espeak-ng","-v","en-us+m3","-s","118","-p","20","-a","160","-w",str(raw),spoken])
        run(["ffmpeg","-y","-i",str(raw),"-af","asetrate=22050*0.88,aresample=44100,aecho=0.8:0.4:110:0.13",str(voice)])
        import wave
        with wave.open(str(voice)) as w: duration=w.getnframes()/w.getframerate()
        pause=2.5 if i==14 else (1.3 if i in (3,6,9,15,18,20) else .65)
        dur=duration+pause
        color="0x9b56ed" if i in (4,5,6) else ("0x4cc6ff" if i in (7,8,9) else "0xffa24b")
        filters=(
            "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
            "eq=brightness=-0.17:saturation=1.2,"
            "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.32:t=fill,"
            f"drawtext=fontfile={font}:text='{esc(top)}':fontsize=83:fontcolor=white:x=(w-text_w)/2:y=420:shadowcolor=black:shadowx=5:shadowy=5,"
            f"drawtext=fontfile={font}:text='{esc(bottom)}':fontsize=68:fontcolor={color}:x=(w-text_w)/2:y=550:shadowcolor=black:shadowx=5:shadowy=5,"
            "fade=t=in:st=0:d=0.5,fade=t=out:st="+str(max(.1,dur-.5))+":d=0.5,format=yuv420p"
        )
        # Synthetic atmospheric low rumble underneath the narration.
        run(["ffmpeg","-y","-loop","1","-framerate","24","-i",str(ART),"-i",str(voice),
             "-f","lavfi","-i",f"sine=frequency={52 if cue!='silence' else 30}:sample_rate=44100:duration={dur}",
             "-filter_complex",f"[0:v]{filters}[v];[2:a]volume=0.025[a];[1:a][a]amix=inputs=2:duration=longest,apad=pad_dur={pause}[out]",
             "-map","[v]","-map","[out]","-t",str(dur),"-c:v","libx264","-preset","veryfast","-crf","23","-r","24","-c:a","aac","-b:a","160k",str(clip)])
        clips.append(clip)
    manifest=td/"clips.txt"
    manifest.write_text("".join("file '"+str(c)+"'\n" for c in clips))
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(manifest),"-c","copy",str(OUT)])
print("Created",OUT)
