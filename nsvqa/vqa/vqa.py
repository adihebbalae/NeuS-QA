from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from tqdm import tqdm
import numpy as np
import base64
import json
import cv2
import os


NUM_SAMPLES = 16

class VLLMClient:
    def __init__(
        self,
        api_key="EMPTY",
        api_base="http://localhost:8000/v1",
        model="Qwen/Qwen2.5-VL-7B-Instruct"
    ):
        if "gpt" in model:
            api_base="https://api.openai.com/v1"
            api_key=os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key, base_url=api_base)
        self.model = model

    def _encode_frame(self, frame):
        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            raise ValueError("Could not encode frame")
        return base64.b64encode(buffer).decode("utf-8")

    def multiple_choice(self, frames_by_cam: dict, question: str, candidates: list[str]) -> str:
        user_content = []
        user_content.append(
            {
                "type": "text",
                "text": "The following is the sequence of images",
            }
        )
        frames = list(frames_by_cam.values())[0]
        encoded_images = [self._encode_frame(frame) for frame in frames]
        for encoded in encoded_images:
            user_content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                }
            )

        parsing_rule = "You must only return the letter of the answer choice, and nothing else. Do not include any other symbols, information, text, or justification in your answer. For example, if the correct answer is 'a) ...', you must only return 'a'."
        prompt = f"{question}\n"
        for candidate in candidates:
            prompt += f"{candidate}\n"
        prompt += f"\n[PARSING RULE]: {parsing_rule}"
        user_content.append({"type": "text", "text": prompt})

        chat_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": user_content},
            ],
            max_tokens=1,
            temperature=0.0,
        )
        return chat_response.choices[0].message.content.lower().strip()

def get_video_frame_count(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    cap.release()
    return frame_count

def load_video_frames(video_path, num_frames):
    frame_count = get_video_frame_count(video_path)
    if frame_count < num_frames:
        frame_indices = np.arange(frame_count)
    else:
        frame_indices = np.linspace(0, frame_count - 1, num_frames, dtype=int)

    images = []
    cap = cv2.VideoCapture(video_path)
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame_bgr = cap.read()
        if ok and frame_bgr is not None:
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            images.append(frame_rgb)
    cap.release()
    return images

def run_experiment(data, video_type, vllm_client, output_path, eval):
    results = []

    all_predicted_answer = []
    for entry in tqdm(data):
        frames = load_video_frames(entry["paths"][video_type], num_frames=NUM_SAMPLES)
        if not frames:
            continue
        for i in range(len(entry["candidates"])):
            entry["candidates"][i] = f"{chr(97+i)}) {entry['candidates'][i]}"
        all_predicted_answer.append(
            vllm_client.multiple_choice(
                {"main": frames}, entry["question"], entry["candidates"]
            )
        )

    total_correct = {"overall": 0}
    total_per_category = {"overall": 0}
    for i, entry in enumerate(data):
        predicted_answer = all_predicted_answer[i]
        output_dict = {
            "video_path": entry["paths"][video_type],
            "question": entry["question"],
            "candidates": entry["candidates"],
            "predicted_answer": predicted_answer
        }
        if "question_category" in entry:
            output_dict["question_category"] = entry["question_category"]
        if eval:
            correct_answer = chr(97+entry["correct_choice"])
            is_correct = 1 if predicted_answer == correct_answer else 0
            total_correct["overall"] += is_correct
            total_per_category["overall"] += 1 # should equal len(data)
            output_dict["correct_answer"] = correct_answer
            output_dict["is_correct"] = is_correct

            if "metadata" in entry and "question_category" in entry["metadata"]:
                category = entry["metadata"]["question_category"]
                total_correct[category] = total_correct.get(category, 0) + is_correct
                total_per_category[category] = total_per_category.get(category, 0) + 1
                output_dict["question_category"] = category
        results.append(output_dict)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)

    if eval:
        for category in total_correct:
            accuracy = total_correct[category] / total_per_category[category]
            print(f"Accuracy for {category}: {accuracy:.2%}")
    else:
        for entry in results:
            print(entry["predicted_answer"])

def vqa(postprocess_path, output_path, current_split, vlm_config, eval=False):
    os.makedirs(output_path, exist_ok=True)

    vllm_client = VLLMClient(
        model=vlm_config[1],
        api_base=f"http://localhost:800{vlm_config[0]}/v1"
    )

    for video_type in ["video_path", "cropped_path"]:
        print(f"\nRunning VQA on {video_type}")
        with open(os.path.join(postprocess_path, f"postprocess_output_{current_split}.json"), "r") as f:
            data = json.load(f)

        run_experiment(
            data=data,
            video_type=video_type,
            vllm_client=vllm_client,
            output_path=os.path.join(output_path, f"vqa_output_{video_type}_{current_split}.json"),
            eval=eval
        )

