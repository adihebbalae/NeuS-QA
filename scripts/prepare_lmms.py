import json
import os
import shutil

def main():
    longvideobench_path = "/nas/mars/dataset/longvideobench/LongVideoBench/lvb_val.json"
    logging_path = "/nas/mars/experiment_result/nsvqa/9_post_submission/"
    lmms_path = os.path.join(logging_path, "lmms")
    postprocess_path = os.path.join(logging_path, "postprocess_output")
    os.makedirs(lmms_path, exist_ok=True)
    original_output_path = os.path.join(lmms_path, "original")
    neusqa_output_path = os.path.join(lmms_path, "neusqa")
    os.makedirs(original_output_path, exist_ok=True)
    os.makedirs(neusqa_output_path, exist_ok=True)

    with open(longvideobench_path, "r") as f:
        original_data = json.load(f)

    postprocess_data = []
    output_files = []
    for filename in os.listdir(postprocess_path):
        if filename.startswith("postprocess_output_") and filename.endswith(".json"):
            file_idx = int(filename.split('_')[-1].split('.')[0])
            output_files.append((file_idx, os.path.join(postprocess_path, filename)))

    output_files.sort(key=lambda x: x[0])
    for _, file_path in output_files:
        with open(file_path, "r") as f:
            data = json.load(f)
            postprocess_data.extend(data)

    original_map = {}
    for original_entry in original_data:
        original_map[(original_entry["question"], original_entry["video_id"])] = original_entry

    original_output_data = []
    neusqa_output_data = []
    
    videos_to_move = set()

    for postprocess_entry in postprocess_data:
        key = (postprocess_entry["question"], postprocess_entry["metadata"]["video_id"])
        if key in original_map:
            original_entry = original_map[key]
            new_entry = original_entry.copy()
            cropped_path = postprocess_entry["paths"]["cropped_path"]

            filename = os.path.basename(cropped_path)
            stem = os.path.splitext(filename)[0]
            new_entry["video_id"] = stem
            new_entry["id"] = f"{stem}_0"
            new_entry["video_path"] = filename
            
            original_output_data.append(original_entry)
            neusqa_output_data.append(new_entry)

            videos_to_move.add(original_entry["video_path"])

    for entry in original_output_data:
        for i, candidate in enumerate(entry["candidates"]):
            entry[f"option{i}"] = candidate
    for entry in neusqa_output_data:
        for i, candidate in enumerate(entry["candidates"]):
            entry[f"option{i}"] = candidate

    with open(os.path.join(original_output_path, "lvb_val.json"), "w") as f:
        json.dump(original_output_data, f, indent=4)
    with open(os.path.join(neusqa_output_path, "lvb_val.json"), "w") as f:
        json.dump(neusqa_output_data, f, indent=4)

    # original videos
    burn_subtitles_path = "/nas/mars/dataset/LongVideoBench/burn-subtitles/"
    original_output_videos_path = os.path.join(original_output_path, "videos")
    os.makedirs(original_output_videos_path, exist_ok=True)
    for video_path in videos_to_move:
        burned_subtitles_video_file = os.path.join(burn_subtitles_path, video_path)
        original_output_videos_file = os.path.join(original_output_videos_path, video_path)
        shutil.copy(burned_subtitles_video_file, original_output_videos_file)

    # neusqa videos
    cropped_videos_path = os.path.join(postprocess_path, "cropped_videos")
    neusqa_videos_output_path = os.path.join(neusqa_output_path, "videos")
    if os.path.exists(neusqa_videos_output_path):
        shutil.rmtree(neusqa_videos_output_path)
    shutil.copytree(cropped_videos_path, neusqa_videos_output_path)

if __name__ == "__main__":
    main()
