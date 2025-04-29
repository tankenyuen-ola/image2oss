import base64
import io
import json
import os
import time

import numpy as np
import requests
import torch
from PIL import Image
# Tensor to PIL
def tensor_to_pil(image):
    return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))


# Convert PIL to Tensor
def pil_to_tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)


def base64_to_image(base64_string):
    # 去除前缀
    base64_list = base64_string.split(",", 1)
    if len(base64_list) == 2:
        prefix, base64_data = base64_list
    else:
        base64_data = base64_list[0]

    # 从base64字符串中解码图像数据
    image_data = base64.b64decode(base64_data)

    # 创建一个内存流对象
    image_stream = io.BytesIO(image_data)

    # 使用PIL的Image模块打开图像数据
    image = Image.open(image_stream)

    return image


def image_to_base64(pli_image, pnginfo=None):
    # 创建一个BytesIO对象，用于临时存储图像数据
    image_data = io.BytesIO()

    # 将图像保存到BytesIO对象中，格式为PNG
    pli_image.save(image_data, format='PNG', pnginfo=pnginfo)
    image_data_bytes = image_data.getvalue()
    encoded_image = "data:image/png;base64," + base64.b64encode(image_data_bytes).decode('utf-8')

    return encoded_image


def read_image_from_url(image_url):
    try:
        # 1. 获取图片数据 (推荐开启 verify=True)
        response = requests.get(image_url, stream=True, timeout=15) # 增加超时时间
        response.raise_for_status() # 检查 HTTP 错误
        image_bytes = response.content

        # 2. 打开图片
        pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

        # 3. 转换为 NumPy 数组并归一化
        numpy_image = np.array(pil_image).astype(np.float32) / 255.0

        # 4. 转换为 PyTorch 张量
        tensor_image = torch.from_numpy(numpy_image) # Shape: (H, W, C)

        # 5. 添加 Batch 维度
        batch_tensor = tensor_image.unsqueeze(0) # Shape: (1, H, W, C)

        # 6. 返回符合 ComfyUI 格式的张量
        return (batch_tensor,)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching image from URL: {e}")
        # 可以返回一个空的或者默认的图像张量，或者抛出异常
        # 返回空张量示例: return (torch.zeros((1, 64, 64, 3)),)
        raise Exception(f"Failed to load image from URL: {image_url}. Error: {e}") from e
    except Exception as e:
        print(f"Error processing image: {e}")
        raise Exception(f"Failed to process image from URL: {image_url}. Error: {e}") from e


def hex_to_rgba(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    if len(hex_color) == 8:
        a = int(hex_color[6:8], 16)
    else:
        a = 255
    return r, g, b, a


def find_max_suffix_number(kwargs, substring):
    # 提取所有键
    keys = list(kwargs.keys())

    # 筛选出形如 'initial_valueX' 的键
    matching_keys = [key for key in keys if key.startswith(substring)]

    # 从匹配的键中提取数字部分
    numbers = [int(key[len(substring):]) for key in matching_keys]

    # 找到最大数字
    max_number = max(numbers) if numbers else 1

    return max_number


class AnyType(str):
    """A special class that is always equal in not equal comparisons. Credit to pythongosssss"""

    def __ne__(self, __value: object) -> bool:
        return False


any_type = AnyType("*")
global_config = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../global.json")
last_read_time = None

def read_global_config():
    config = {}
    if os.path.exists(global_config):
        with open(global_config, encoding='utf-8') as f:
            config = json.load(f)

    return config


def get_global_config(key):
    global last_read_time
    global config
    current_time = time.time()
    if last_read_time is None or current_time - last_read_time >= 300:
        config = read_global_config()
        last_read_time = current_time

    return config[key] if key in config else None


def check_directory(check_dir):
    allow_create_dir_when_save = get_global_config('allow_create_dir_when_save')
    check_dir = os.path.normpath(check_dir)
    if not allow_create_dir_when_save and (not os.path.isdir(check_dir) or not os.path.isabs(check_dir)):
        raise FileNotFoundError(f"dir not found: {check_dir}")

    if not os.path.isdir(check_dir):
        os.makedirs(check_dir, exist_ok=True)
    return check_dir
