import base64
import io
import json
import os
import time
import oss2
import numpy as np
import requests
import torch
from PIL import Image
from io import BytesIO
OSS_ENDPOINT_LIST = [
    # 中国内地
    "oss-cn-hangzhou.aliyuncs.com",
    "oss-cn-shanghai.aliyuncs.com",
    "oss-cn-qingdao.aliyuncs.com",
    "oss-cn-beijing.aliyuncs.com",
    "oss-cn-shenzhen.aliyuncs.com",
    "oss-cn-heyuan.aliyuncs.com",
    "oss-cn-zhangjiakou.aliyuncs.com",
    "oss-cn-huhehaote.aliyuncs.com",
    "oss-cn-wulanchabu.aliyuncs.com",
    "oss-cn-chengdu.aliyuncs.com",
    "oss-cn-hangzhou-internal.aliyuncs.com",
    "oss-cn-shanghai-internal.aliyuncs.com",
    "oss-cn-qingdao-internal.aliyuncs.com",
    "oss-cn-beijing-internal.aliyuncs.com",
    "oss-cn-shenzhen-internal.aliyuncs.com",
    "oss-cn-heyuan-internal.aliyuncs.com",
    "oss-cn-zhangjiakou-internal.aliyuncs.com",
    "oss-cn-huhehaote-internal.aliyuncs.com",
    "oss-cn-wulanchabu-internal.aliyuncs.com",
    "oss-cn-chengdu-internal.aliyuncs.com",
    # 中国香港
    "oss-cn-hongkong.aliyuncs.com",
    "oss-cn-hongkong-internal.aliyuncs.com",
    # 美国
    "oss-us-west-1.aliyuncs.com",
    "oss-us-east-1.aliyuncs.com",
    "oss-us-west-1-internal.aliyuncs.com",
    "oss-us-east-1-internal.aliyuncs.com",
    # 亚太
    "oss-ap-southeast-1.aliyuncs.com",
    "oss-ap-southeast-2.aliyuncs.com",
    "oss-ap-southeast-3.aliyuncs.com",
    "oss-ap-southeast-5.aliyuncs.com",
    "oss-ap-northeast-1.aliyuncs.com",
    "oss-ap-south-1.aliyuncs.com",
    "oss-ap-southeast-1-internal.aliyuncs.com",
    "oss-ap-southeast-2-internal.aliyuncs.com",
    "oss-ap-southeast-3-internal.aliyuncs.com",
    "oss-ap-southeast-5-internal.aliyuncs.com",
    "oss-ap-northeast-1-internal.aliyuncs.com",
    "oss-ap-south-1-internal.aliyuncs.com",
    # 欧洲
    "oss-eu-central-1.aliyuncs.com",
    "oss-eu-west-1.aliyuncs.com",
    "oss-eu-central-1-internal.aliyuncs.com",
    "oss-eu-west-1-internal.aliyuncs.com",
    # 中东
    "oss-me-east-1.aliyuncs.com",
    "oss-me-east-1-internal.aliyuncs.com"
]


# 将一个图像张量（Tensor）转换成 PIL (Pillow) 图像对象
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

# 从url中获取图片
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

# 上传图片到oss中
def put_object(file,filename,access_key_id, access_key_secret, security_token,bucket_name, endpoint):
    auth = oss2.StsAuth(access_key_id,access_key_secret,security_token,auth_version = "v2")
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    image_bytes = BytesIO()
    file.save(image_bytes, format='JPEG')  # 保存为 JPEG 格式
    image_bytes.seek(0)  # 将流指针回到开头
    try:
        bucket.put_object(filename, image_bytes)
        print(f'图片成功上传到 OSS，文件名为: {filename}')
    except oss2.exceptions.OssError as e:
        raise ValueError(f'上传失败，错误信息: {e}')
# 从oss获取图片
def get_object(object_key, access_key_id, access_key_secret, security_token, bucket_name, endpoint):
    try:
        auth = oss2.StsAuth(access_key_id,access_key_secret,security_token,auth_version = "v2")
        bucket = oss2.Bucket(auth, endpoint, bucket_name)
        object_stream = bucket.get_object(object_key)
        img_data = object_stream.read()
        if not img_data:
            raise ValueError(f"Failed to read data for object: {object_key}")
        image = Image.open(io.BytesIO(img_data))
        image = image.convert("RGB")
        image_np = np.array(image).astype(np.float32)
        image_np /= 255.0
        image_tensor = torch.from_numpy(image_np)
        image_tensor = image_tensor.unsqueeze(0)
        print(f"Successfully loaded image from OSS. Tensor shape: {image_tensor.shape}")
        return (image_tensor,)
    except oss2.exceptions.NoSuchKey:
        print(f"Error: Object '{object_key}' not found in bucket '{bucket_name}'.")
        # 可以选择返回一个空图像或默认图像，或者直接抛出异常
        # 这里我们重新抛出异常，让 ComfyUI 显示错误
        raise oss2.exceptions.NoSuchKey(f"Object '{object_key}' not found in bucket '{bucket_name}'.")
    except Exception as e:
        print(f"An error occurred while loading image from OSS: {e}")
        # 重新抛出异常，以便在 ComfyUI 中看到错误信息
        raise e
    finally:
        # 确保 response 被关闭 (oss2 的 get_object 返回的 stream 在 read() 后通常会自动处理，但显式关闭更安全)
        if 'object_stream' in locals() and hasattr(object_stream, 'resp') and object_stream.resp:
            # oss2 < 2.17.0: object_stream.resp.release_conn()
            # oss2 >= 2.17.0: object_stream.close()
            # 简单起见，如果 read() 成功，连接通常已关闭。如果读取失败或部分读取，则需要手动关闭。
            # Pillow 的 Image.open(io.BytesIO(img_data)) 处理的是内存数据，不涉及原始连接。
            # 如果直接用 Image.open(object_stream.resp)，则Pillow会负责读取和关闭。
            # 鉴于我们先 read() 了全部数据，这里通常不需要额外关闭。
            pass

# 获取阿里云ak信息
def get_aliyun_ak(sts_service_url):
    try:
        response = requests.get(sts_service_url)
        response.raise_for_status()
        data = response.json()
        if not data["success"]:
            raise ValueError(f"获取ak失败: {data}")
        return data
    except requests.exceptions.HTTPError as http_err:
        raise ValueError(f"HTTP 错误发生: {http_err}")
    except requests.exceptions.RequestException as req_err:
        raise ValueError(f"请求错误发生: {req_err}")
    except ValueError as value_err:
        raise ValueError(f"JSON 解析错误: {value_err}")
