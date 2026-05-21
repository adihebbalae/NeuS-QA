from transformers import AutoModel, AutoTokenizer
from torch.nn.functional import softmax
import numpy as np
import logging
import copy
import torch
import gc
from torchvision.transforms.functional import InterpolationMode
from decord import VideoReader, cpu
import torchvision.transforms as T
from PIL import Image
import math

from nsvqa.utils.sigmoid import calibrate_sigmoid 
from nsvqa.nsvs.vlm.obj import DetectedObject


class InternVL:
    """InternVL's Vision Language Model."""

    def __init__(
        self,
        model_name: str = "InternVL2-8B",
        multi_gpus: bool = False,
        device: int = 0,
    ) -> None:
        """Initialization the InternVL."""
        logging.info(
            (
                "You are using the model based on HuggingFace API.",
                "The model will be downloaded to the HuggingFace cache dir.",
            )
        )
        self.model_name = model_name
        self._path = f"OpenGVLab/{model_name}"
        self._num_gpus = torch.cuda.device_count()
        self.device = device
        if multi_gpus:
            device_map = split_model(model_name)
        else:
            device_map = assign_device_map(model_name=model_name, manual_gpu_id=device)
        self._device_map = device_map
        self.model = AutoModel.from_pretrained(
            self._path,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
            use_flash_attn=True,
            trust_remote_code=True,
            device_map=device_map,
        ).eval()
        # accelerate has already placed weights from device_map. Moving all
        # buffers/params again can collapse sharded weights back onto one GPU.
        if not isinstance(device_map, dict):
            self.model.apply(self.move_tensors_to_gpu)
        self.tokenizer = AutoTokenizer.from_pretrained(self._path, trust_remote_code=True, use_fast=False)

    def reset_model(self) -> None:
        """Reset the model to its initial state using pretrained weights."""
        self.model = AutoModel.from_pretrained(
            self._path,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
            use_flash_attn=True,
            trust_remote_code=True,
        ).eval()
        self.model.apply(self.move_tensors_to_gpu)

    def clear_gpu_memory(self) -> None:
        """Clear CUDA cache and run garbage collection to free GPU memory."""
        torch.cuda.empty_cache()
        if torch.cuda.is_available():
            torch.cuda.ipc_collect()
        gc.collect()  # Run garbage collector

    def move_tensors_to_gpu(
        self,
        module: torch.nn.Module,
    ) -> None:
        """Move all tensors in the module to GPU if they are on the CPU."""
        for name, tensor in module.named_buffers():
            if isinstance(tensor, torch.Tensor) and tensor.device.type == "cpu":
                module.register_buffer(
                    name,
                    tensor.cuda(self.device),
                    persistent=False,
                )
        for _, param in module.named_parameters():
            if param.device.type == "cpu":
                param.data = param.data.cuda(self.device)

    def detect(
        self,
        seq_of_frames: list[np.ndarray],
        scene_description: str,
        threshold: float
    ) -> DetectedObject:
        """Detect objects in the given frame image.

        Args:
            seq_of_frames (list[np.ndarray]): List of video frames to process.
            scene_description (str): Description of the scene.
            threshold (float): Detection threshold.

        Returns:
            DetectedObject: Detected objects with their details.
        """
        if "subtitle" in scene_description:
            subtitle_scene_description = scene_description.replace("subtitle_", "").replace("_", " ")
            parsing_rule = "You must only return a Yes or No, and not both, to any question asked. You must not include any other symbols, information, text, justification in your answer or repeat Yes or No multiple times. For example, if the question is \"Does the video have the subtitle 'this is very interesting' present in the sequence of images?\", the answer must only be 'Yes' or 'No'."
            prompt = rf"Does the video have the subtitle '{subtitle_scene_description}' present in the sequence of images? " f"\n[PARSING RULE]: {parsing_rule}"
        else:
            object_scene_description = scene_description.replace("_", " ")
            parsing_rule = "You must only return a Yes or No, and not both, to any question asked. You must not include any other symbols, information, text, justification in your answer or repeat Yes or No multiple times. For example, if the question is \"Is there a cat present in the sequence of images?\", the answer must only be 'Yes' or 'No'."
            prompt = rf"Is there a '{object_scene_description}' present in the sequence of images? " f"\n[PARSING RULE]: {parsing_rule}"

        response, confidence = self.infer_with_video_confidence(
            language=prompt,
            seq_of_frames=seq_of_frames,
        )

        detected = "yes" in response.lower()
        probability = calibrate_sigmoid(confidence, false_threshold=threshold)

        return DetectedObject(
            name=scene_description,
            is_detected=detected,
            confidence=round(confidence, 3),
            probability=round(probability, 3),
        )

    def infer_with_video_confidence(
        self,
        language: str,
        seq_of_frames: list[np.ndarray],
        max_new_tokens: int = 8,
        do_sample: bool = False,
    ) -> tuple[str, float]:
        """Perform video inference and return response with confidence score.

        Args:
            language (str): The input prompt or question.
            seq_of_frames (list[np.ndarray] | None):
                List of video frames as numpy arrays.
            video_path (str | None): Path to the input video file.
            max_new_tokens (int): Maximum number of new tokens to generate.
            do_sample (bool): Whether to use sampling for generation.

        Returns:
            tuple[str, float]: Generated response and confidence score.
        """

        generation_config = {
            "max_new_tokens": max_new_tokens,
            "do_sample": do_sample,
        }

        pixel_values, num_patches_list = load_video_from_seq_of_frames(
            seq_of_frames=seq_of_frames, device=self.device
        )

        video_prefix = "".join([f"Frame{i+1}: <image>\n" for i in range(len(num_patches_list))])
        language = video_prefix + language

        return self.chat_with_confidence(
            self.tokenizer,
            pixel_values,
            language,
            generation_config,
            num_patches_list=num_patches_list,
        )

    def chat_with_confidence(
        self,
        tokenizer: AutoTokenizer,
        pixel_values: torch.Tensor,
        question: str,
        generation_config: dict,
        num_patches_list: list[int] | None = None,
        IMG_START_TOKEN: str = "<img>",
        IMG_END_TOKEN: str = "</img>",
        IMG_CONTEXT_TOKEN: str = "<IMG_CONTEXT>",
        verbose: bool = False,
    ) -> tuple[str, float]:
        """Generate a response with confidence score for the given input.

        Args:
            tokenizer: The tokenizer to use.
            pixel_values: Image tensor input.
            question: The input question or prompt.
            generation_config: Configuration for text generation.
            num_patches_list: List of number of patches for video frames.
            IMG_START_TOKEN: Token to mark the start of an image.
            IMG_END_TOKEN: Token to mark the end of an image.
            IMG_CONTEXT_TOKEN: Token for image context.
            verbose: Whether to print verbose output.

        Returns:
            A tuple containing the generated response and its confidence score.
        """
        if num_patches_list is None:
            num_patches_list = [pixel_values.shape[0]] if pixel_values is not None else []

        assert pixel_values is None or len(pixel_values) == sum(num_patches_list)

        img_context_token_id = tokenizer.convert_tokens_to_ids(IMG_CONTEXT_TOKEN)
        self.model.img_context_token_id = img_context_token_id

        template = copy.deepcopy(self.model.conv_template)
        template.system_message = self.model.system_message
        eos_token_id = tokenizer.convert_tokens_to_ids(template.sep)

        template.append_message(template.roles[0], question)
        template.append_message(template.roles[1], None)
        query = template.get_prompt()

        if verbose and pixel_values is not None:
            image_bs = pixel_values.shape[0]
            print(f"dynamic ViT batch size: {image_bs}")

        for num_patches in num_patches_list:
            context_tokens = IMG_CONTEXT_TOKEN * self.model.num_image_token * num_patches
            image_tokens = IMG_START_TOKEN + context_tokens + IMG_END_TOKEN
            query = query.replace("<image>", image_tokens, 1)

        model_inputs = tokenizer(query, return_tensors="pt")
        input_ids = model_inputs["input_ids"].cuda(self.device)
        attention_mask = model_inputs["attention_mask"].cuda(self.device)
        generation_config["eos_token_id"] = eos_token_id
        generation_config["return_dict_in_generate"] = True
        generation_config["output_scores"] = True
        generation_config["output_logits"] = True
        generation_output = self.model.generate(
            pixel_values=pixel_values,
            input_ids=input_ids,
            attention_mask=attention_mask,
            **generation_config,
        )
        response = tokenizer.batch_decode(generation_output.sequences, skip_special_tokens=True)[0]
        response = response.split(template.sep)[0].strip()

        logits_to_compute = np.where(generation_output.sequences[0].detach().cpu().numpy() != eos_token_id)[0]
        confidence = 1.0
        for logit in logits_to_compute:
            token = generation_output.sequences[0, logit].item()
            prob = softmax(generation_output.logits[logit])[0, token]
            confidence = prob.item() * confidence
        self.clear_gpu_memory()

        return response, confidence

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

def build_transform(input_size: int) -> T.Compose:
    """Builds a transformation pipeline for the given input size."""
    mean, std = IMAGENET_MEAN, IMAGENET_STD
    return T.Compose(
        [
            T.Lambda(lambda img: img.convert("RGB") if img.mode != "RGB" else img),
            T.Resize(
                (input_size, input_size),
                interpolation=InterpolationMode.BICUBIC,
            ),
            T.ToTensor(),
            T.Normalize(mean=mean, std=std),
        ]
    )


def _num_language_layers(model_name: str) -> int:
    return {
        "InternVL2-1B": 24,
        "InternVL2-2B": 24,
        "InternVL2-4B": 32,
        "InternVL2-8B": 32,
        "InternVL2-26B": 48,
        "InternVL2-40B": 60,
        "InternVL2-Llama3-76B": 80,
    }[model_name]


def _base_device_map(model_name: str) -> dict:
    """Submodule keys that match OpenGVLab/InternVL2* (InternLM2 backbone)."""
    num_layers = _num_language_layers(model_name)
    device_map: dict = {
        "vision_model": 0,
        "mlp1": 0,
        "language_model.model.tok_embeddings": 0,
        "language_model.model.norm": 0,
        "language_model.output": 0,
    }
    for layer_idx in range(num_layers):
        device_map[f"language_model.model.layers.{layer_idx}"] = 0
    return device_map


def assign_device_map(model_name, manual_gpu_id=0):
    device_map = _base_device_map(model_name)
    for key in device_map:
        device_map[key] = manual_gpu_id

    return device_map


def find_closest_aspect_ratio(aspect_ratio, target_ratios, width, height, image_size):
    best_ratio_diff = float("inf")
    best_ratio = (1, 1)
    area = width * height
    for ratio in target_ratios:
        target_aspect_ratio = ratio[0] / ratio[1]
        ratio_diff = abs(aspect_ratio - target_aspect_ratio)
        if ratio_diff < best_ratio_diff:
            best_ratio_diff = ratio_diff
            best_ratio = ratio
        elif ratio_diff == best_ratio_diff:
            if area > 0.5 * image_size * image_size * ratio[0] * ratio[1]:
                best_ratio = ratio
    return best_ratio


def dynamic_preprocess(image, min_num=1, max_num=12, image_size=448, use_thumbnail=False):
    # Convert numpy array to PIL Image if needed
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)

    orig_width, orig_height = image.size
    aspect_ratio = orig_width / orig_height

    # calculate the existing image aspect ratio
    target_ratios = set(
        (i, j)
        for n in range(min_num, max_num + 1)
        for i in range(1, n + 1)
        for j in range(1, n + 1)
        if i * j <= max_num and i * j >= min_num
    )
    target_ratios = sorted(target_ratios, key=lambda x: x[0] * x[1])

    # find the closest aspect ratio to the target
    target_aspect_ratio = find_closest_aspect_ratio(aspect_ratio, target_ratios, orig_width, orig_height, image_size)

    # calculate the target width and height
    target_width = image_size * target_aspect_ratio[0]
    target_height = image_size * target_aspect_ratio[1]
    blocks = target_aspect_ratio[0] * target_aspect_ratio[1]

    # resize the image
    resized_img = image.resize((target_width, target_height))
    processed_images = []
    for i in range(blocks):
        box = (
            (i % (target_width // image_size)) * image_size,
            (i // (target_width // image_size)) * image_size,
            ((i % (target_width // image_size)) + 1) * image_size,
            ((i // (target_width // image_size)) + 1) * image_size,
        )
        # split the image
        split_img = resized_img.crop(box)
        processed_images.append(split_img)
    assert len(processed_images) == blocks
    if use_thumbnail and len(processed_images) != 1:
        thumbnail_img = image.resize((image_size, image_size))
        processed_images.append(thumbnail_img)
    return processed_images


def split_model(model_name):
    world_size = torch.cuda.device_count()
    if world_size < 2:
        return assign_device_map(model_name, manual_gpu_id=0)

    num_layers = _num_language_layers(model_name)
    device_map = _base_device_map(model_name)
    # ViT + connector on GPU 0; spread language layers across all GPUs.
    num_layers_per_gpu = math.ceil(num_layers / max(1, world_size - 0.5))
    counts = [num_layers_per_gpu] * world_size
    counts[0] = math.ceil(num_layers_per_gpu * 0.5)
    layer_cnt = 0
    for i, num_layer in enumerate(counts):
        for _ in range(num_layer):
            if layer_cnt >= num_layers:
                break
            device_map[f"language_model.model.layers.{layer_cnt}"] = i
            layer_cnt += 1
    device_map["vision_model"] = 0
    device_map["mlp1"] = 0
    device_map["language_model.model.tok_embeddings"] = 0
    device_map["language_model.output"] = 0
    device_map["language_model.model.norm"] = 0

    return device_map


def move_tensors_to_gpu(module):
    for name, tensor in module.named_buffers():
        if isinstance(tensor, torch.Tensor) and tensor.device.type == "cpu":
            module.register_buffer(name, tensor.cuda(), persistent=False)
    for _, param in module.named_parameters():
        if param.device.type == "cpu":
            param.data = param.data.cuda()


# video multi-round conversation (视频多轮对话)
def get_index(bound, fps, max_frame, first_idx=0, num_segments=32):
    if bound:
        start, end = bound[0], bound[1]
    else:
        start, end = -100000, 100000
    start_idx = max(first_idx, round(start * fps))
    end_idx = min(round(end * fps), max_frame)
    seg_size = float(end_idx - start_idx) / num_segments
    frame_indices = np.array(
        [int(start_idx + (seg_size / 2) + np.round(seg_size * idx)) for idx in range(num_segments)]
    )
    return frame_indices


def load_video_from_seq_of_frames(
    seq_of_frames: list[np.ndarray],
    input_size=448,
    max_num=1,
    device="cuda",
    dtype=torch.bfloat16,
):
    pixel_values_list, num_patches_list = [], []
    transform = build_transform(input_size=input_size)
    for img in seq_of_frames:
        img = dynamic_preprocess(img, image_size=input_size, use_thumbnail=True, max_num=max_num)
        pixel_values = [transform(tile) for tile in img]
        pixel_values = torch.stack(pixel_values).to(dtype=dtype, device=device)  # Convert to bfloat16
        num_patches_list.append(pixel_values.shape[0])
        pixel_values_list.append(pixel_values)
    return torch.cat(pixel_values_list), num_patches_list


def load_video(video_path, bound=None, input_size=448, max_num=1, num_segments=32):
    vr = VideoReader(video_path, ctx=cpu(0), num_threads=1)
    max_frame = len(vr) - 1
    fps = float(vr.get_avg_fps())

    pixel_values_list, num_patches_list = [], []
    transform = build_transform(input_size=input_size)
    frame_indices = get_index(bound, fps, max_frame, first_idx=0, num_segments=num_segments)
    for frame_index in frame_indices:
        img = Image.fromarray(vr[frame_index].asnumpy()).convert("RGB")
        img = dynamic_preprocess(img, image_size=input_size, use_thumbnail=True, max_num=max_num)
        pixel_values = [transform(tile) for tile in img]
        pixel_values = torch.stack(pixel_values)
        num_patches_list.append(pixel_values.shape[0])
        pixel_values_list.append(pixel_values.to(torch.bfloat16))
    pixel_values = torch.cat(pixel_values_list)
    return pixel_values, num_patches_list
