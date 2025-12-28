import json
import os
import subprocess
from datetime import datetime
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import shutil


def time_to_seconds(time_str):
    time_str = time_str.replace(" ", "")
    t = datetime.strptime(time_str, "%H:%M:%S.%f")
    return t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1e6


def seconds_to_srt_format(seconds):
    if seconds < 0:
        seconds = 0.0
    total_ms = int(round(seconds * 1000.0))
    hours, rem = divmod(total_ms, 3600 * 1000)
    minutes, rem = divmod(rem, 60 * 1000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def obtain_timestamp_from_subtitle(subtitle, starting_timestamp_for_subtitles, duration):
    if "timestamp" in subtitle:
        start, end = subtitle["timestamp"]

        if not isinstance(end, float):
            end = duration

        start -= starting_timestamp_for_subtitles
        end -= starting_timestamp_for_subtitles

    else:
        start, end = subtitle["start"], subtitle["end"]
        start = time_to_seconds(start)
        end = time_to_seconds(end)
        start -= starting_timestamp_for_subtitles
        end -= starting_timestamp_for_subtitles

    return start, end


def burn_subtitles_on_video(video_path, subtitles_json_path, starting_timestamp, save_path,
                             font_size=24, font="Arial-Bold", color="white"):
    # Get video duration first
    try:
        duration_cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "csv=p=0", video_path]
        result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
        video_duration = float(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"Error getting video duration for {video_path}: {e}")
        video_duration = float("inf")

    with open(subtitles_json_path, "r") as f:
        subtitles = json.load(f)

    modified_subtitles = []
    for subtitle in subtitles:
        start, end = obtain_timestamp_from_subtitle(subtitle, starting_timestamp, video_duration)

        subtitle_timestamp = (start + end) / 2
        if end - start < 1:
            end = subtitle_timestamp + 0.5
            start = subtitle_timestamp - 0.5
        if end < 0:
            continue
        if start > video_duration:
            break
        start = max(start, 0)
        end = min(end, video_duration)
        text = subtitle["line"] if "line" in subtitle else subtitle["text"]
        modified_subtitles.append({"start": start, "end": end, "line": text})

    temp_srt_path = f"{save_path}_temp.srt"

    with open(temp_srt_path, "w", encoding="utf-8") as out:
        for i, entry in enumerate(modified_subtitles, start=1):
            start_str = seconds_to_srt_format(entry["start"])
            end_str = seconds_to_srt_format(entry["end"])
            out.write(f"{i}\n{start_str} --> {end_str}\n{entry['line']}\n\n")

    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-i", video_path,
        "-vf", f"subtitles={temp_srt_path}:force_style='PrimaryColour=&HFFFFFF&,BackColour=&H000000&,BorderStyle=3'",
        "-c:v", "libx264",
        "-c:a", "copy", "-y", save_path
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error for {video_path}: {e}")
        with open("err.txt", "a") as error_log:
            error_log.write(f"FFmpeg error for {video_path}: {e}\n")
            if e.stderr:
                try:
                    error_log.write(e.stderr.decode("utf-8", errors="ignore") + "\n")
                except AttributeError:
                    error_log.write(str(e.stderr) + "\n")
            
            # copy the original video to the save path
            try:
                shutil.copy(video_path, save_path)
                print(f"Copied original video to {save_path}")
            except Exception as copy_error:
                 error_log.write(f"Failed to copy original video: {copy_error}\n")

    finally:
        try:
            os.remove(temp_srt_path)
        except FileNotFoundError:
            pass


def process_entry(entry):
    video_id = entry["video_id"]
    video_path = f"/nas/mars/dataset/LongVideoBench/LongVideoBench/videos/{video_id}.mp4"
    subtitles_json_path = f"/nas/mars/dataset/LongVideoBench/LongVideoBench/subtitles/{video_id}_en.json"
    save_path = f"/nas/mars/dataset/LongVideoBench/burn-subtitles/{video_id}.mp4"

    # Skip if already processed
    if os.path.exists(save_path):
        return

    if not os.path.exists(video_path) or not os.path.exists(subtitles_json_path):
        with open("err.txt", "a") as error_log:
            if not os.path.exists(video_path):
                error_log.write(f"Video file not found: {video_path}\n")
            if not os.path.exists(subtitles_json_path):
                error_log.write(f"Subtitles file not found: {subtitles_json_path}\n")
        
        # If possible, copy video even if subtitles missing? 
        # temp_subs copies if video exists but burning fails. 
        # If video doesn't exist, we can't copy.
        if os.path.exists(video_path):
             shutil.copy(video_path, save_path)
             print(f"Copied original video (missing subtitles) to {save_path}")
        return

    try:
        starting_timestamp = entry["starting_timestamp_for_subtitles"]
    except KeyError as e:
        with open("err.txt", "a") as error_log:
            error_log.write(f"KeyError: {e} for video_id: {video_id}\n")
        return

    burn_subtitles_on_video(video_path, subtitles_json_path, starting_timestamp, save_path)


def main():
    with open("/nas/mars/dataset/LongVideoBench/LongVideoBench/lvb_val.json", "r") as f:
        data = json.load(f)

    os.makedirs("/nas/mars/dataset/LongVideoBench/burn-subtitles", exist_ok=True)

    num_workers = min(10, cpu_count())
    print(f"Using {num_workers} parallel workers.")
    with Pool(processes=num_workers) as pool:
        list(tqdm(pool.imap_unordered(process_entry, data), total=len(data)))


if __name__ == "__main__":
    main()

