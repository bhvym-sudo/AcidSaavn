from ffpyplayer.player import MediaPlayer
import time

url = "https://aac.saavncdn.com/778/d3a4b97df0a5df5bfb437c194313eccb_320.mp4"

player = MediaPlayer(url)
duration = 0
playback_started = False

print("Starting playback...")
while True:
    frame, val = player.get_frame()
    if val == 'eof':
        print("EOF reached")
        break

    if frame is not None and not playback_started:
        meta = player.get_metadata() or {}
        duration = float(meta.get("duration", 0))
        print("✅ Duration from metadata:", duration)
        print("Seeking to 30 seconds...")
        player.seek(30)
        playback_started = True

    if playback_started:
        pts = player.get_pts()
        if pts:
            print("Current time:", round(pts, 2))
    time.sleep(0.1)
