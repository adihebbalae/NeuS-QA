from nsvqa.target_identification.target_identification import *
from nsvqa.nsvs.model_checker.frame_validator import *
from nsvqa.datamanager.longvideobench import *
from nsvqa.nsvs.video.read_video import *
from nsvqa.datamanager.custom import *
from nsvqa.nsvs.vlm.obj import *
from nsvqa.nsvs.nsvs import *
from nsvqa.puls.puls import *
from nsvqa.vqa.vqa import *

import argparse
import json
import os

def exec_puls(entry): # Step 1
    output = PULS(entry["question"])

    entry["puls"] = {}
    entry["puls"]["proposition"] = output["proposition"]
    entry["puls"]["specification"] = output["specification"]
    entry["puls"]["conversation_history"] = os.path.join(os.getcwd(), output["saved_path"])

def exec_target_identification(entry): # Step 2
    output = identify_target(
        entry["question"],
        entry["candidates"],
        entry["puls"]["specification"],
        entry["puls"]["conversation_history"]
    )

    entry["target_identification"] = {}
    entry["target_identification"]["frame_window"] = output["frame_window"]
    entry["target_identification"]["explanation"] = output["explanation"]
    entry["target_identification"]["conversation_history"] = os.path.join(os.getcwd(), output["saved_path"])

def exec_nsvs(entry, sample_rate, device, model): # Step 3
    print(entry["paths"]["video_path"])
    reader = Mp4Reader(path=entry["paths"]["video_path"], sample_rate=sample_rate)
    video_data = reader.read_video()
    if "metadata" not in entry:
        entry["metadata"] = {}
    entry["metadata"]["fps"] = video_data["video_info"]["fps"]
    entry["metadata"]["frame_count"] = video_data["video_info"]["frame_count"]

    try:
        output, indices = run_nsvs(
            video_data,
            entry["paths"]["video_path"],
            entry["puls"]["proposition"],
            entry["puls"]["specification"],
            device=device,
            model=model,
        )
    except Exception as e:
        entry["metadata"]["error"] = repr(e)
        output = [-1]
        indices = []
    
    entry["nsvs"] = {}
    entry["nsvs"]["output"] = output
    entry["nsvs"]["indices"] = indices

def exec_merge(entry): # Step 4
    inner = entry["target_identification"]["frame_window"].strip()[1:-1]
    parts = inner.split(',')
    result = []
    for part in parts:
        part = part.strip()
        match = re.search(r'([+-])\s*(\d+)', part)
        if match:
            sign, num = match.groups()
            result.append(int(sign + num))
        else:
            result.append(0)

    if entry["nsvs"]["output"] != [-1]:
        entry["frames_of_interest"] = [
            max(0,                                  int(entry["nsvs"]["output"][0] + result[0] * entry["metadata"]["fps"])),
            min(entry["metadata"]["frame_count"]-1, int(entry["nsvs"]["output"][1] + result[1] * entry["metadata"]["fps"]))
        ]
    else:
        entry["frames_of_interest"] = [-1]

def run_nsvqa(output_dir, current_split, total_splits, vlm_config):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "checkpoints"), exist_ok=True)

    loader = LongVideoBench()
    # loader = Custom(
    #     raw_data=[
    #         {
    #             "video_path": "/nas/mars/dataset/longvideobench/burn-subtitles/mH9LdC7IFH8.mp4",
    #             "question": "What happens when wine shows up on the screen before the vineyards showed up on the screen?",
    #             "answer_choices": [
    #                 "A close up of the wine was shown",
    #                 "The wine was trashed",
    #                 "The wine was replaced with soda",
    #                 "The man in the blue shirt was talking"
    #             ]
    #         }
    #     ]
    # )
    data = loader.load_data()
    
    output = []
    starting = (len(data) * (current_split-1)) // total_splits
    ending = (len(data) * current_split) // total_splits
    print(f"({starting}, {ending})")
    for i in range(starting, ending):
        print("\n" + "*"*50 + f" {i+1}/{len(data)} " + "*"*50)
        entry = data[i]
        exec_puls(entry)
        exec_target_identification(entry)
        exec_nsvs(entry, sample_rate=1, device=vlm_config[0], model=vlm_config[1])
        exec_merge(entry)
        output.append(entry)
        with open(os.path.join(output_dir, "checkpoints", f"nsvqa_output_{current_split}_{i}.json"), "w") as f:
            json.dump(output, f, indent=4)

    with open(os.path.join(output_dir, f"nsvqa_output_{current_split}.json"), "w") as f:
        json.dump(output, f, indent=4)

def postprocess(nsvqa_dir, postprocess_dir, current_split):
    os.makedirs(os.path.dirname(postprocess_dir), exist_ok=True)
    loader = Custom(postprocess_dir=postprocess_dir, current_split=current_split)
    loader.postprocess_data(nsvqa_dir)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--current_split", type=int, required=True)
    parser.add_argument("--total_splits", type=int, default=6)
    parser.add_argument("--device", type=int)
    args = parser.parse_args()

    current_split = args.current_split # between 1 and total_splits
    total_splits = args.total_splits
    device_number = args.device if args.device is not None else current_split
    vlm_config = (device_number, "OpenGVLab/InternVL2_5-8B") # device_number, model_name

    output_dir = "/nas/mars/experiment_result/nsvqa/9_post_submission/" # change to your desired output directory
    nsvqa_dir = os.path.join(output_dir, "nsvqa_output")
    postprocess_dir = os.path.join(output_dir, "postprocess_output")
    vqa_dir = os.path.join(output_dir, "vqa_output")

    run_nsvqa(nsvqa_dir, current_split, total_splits, vlm_config)
    postprocess(nsvqa_dir, postprocess_dir, current_split)
    # vqa(postprocess_dir, vqa_dir, current_split, vlm_config, eval=True)

if __name__ == "__main__":
    main()

