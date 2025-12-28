from nsvqa.datamanager.manager import Manager

from tqdm import tqdm
import shutil
import hashlib
import json
import os


class Custom(Manager):
    def __init__(self, raw_data=None, postprocess_dir=None, current_split=None):
        self.raw_data = raw_data
        self.postprocess_dir = postprocess_dir
        self.current_split = current_split

    def load_data(self) -> list:
        assert self.raw_data is not None

        ret = []
        for raw_entry in self.raw_data:
            ret.append({
                "paths": {
                    "video_path": raw_entry["video_path"]
                },
                "question": raw_entry["question"],
                "candidates": raw_entry["answer_choices"],
            })
        return ret

        
    def postprocess_data(self, nsvs_path): # use whenever you want to use vqa.py
        assert self.postprocess_dir is not None
        assert self.current_split is not None

        cropped_dir = os.path.join(self.postprocess_dir, "cropped_videos")
        os.makedirs(cropped_dir, exist_ok=True)

        with open(os.path.join(nsvs_path, f"nsvqa_output_{self.current_split}.json"), "r") as f:
            nsvs_data = json.load(f)

        output = []
        for entry_nsvs in tqdm(nsvs_data):
            code = entry_nsvs["question"] + entry_nsvs["metadata"]["video_id"]
            id = hashlib.sha256(code.encode()).hexdigest()

            entry_nsvs["paths"]["cropped_path"] = os.path.join(cropped_dir, f"{id}.mp4")
            self.crop_video(
                entry_nsvs,
                save_path=entry_nsvs["paths"]["cropped_path"],
                ground_truth=False
            )
            if os.path.exists(entry_nsvs["paths"]["cropped_path"]): # if crop successful
                output.append(entry_nsvs)

        with open(os.path.join(self.postprocess_dir, f"postprocess_output_{self.current_split}.json"), "w") as f:
            json.dump(output, f, indent=4)

