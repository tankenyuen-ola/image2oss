import oss2
from .util import tensor_to_pil,image_to_base64
from PIL.PngImagePlugin import PngInfo
from comfy.cli_args import args
import ast
from io import BytesIO


OSS_ENDPOINT_LIST = [
    "oss-cn-hangzhou.aliyuncs.com",
    "oss-cn-hangzhou-internal.aliyuncs.com"
]

class OSSUploadNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "filename": ("STRING",{"default":'["tmp-comfyui/filename.jpeg"]'}),
                "access_key_id": ("STRING", {"default": "access_key_id"}),
                "access_key_secret": ("STRING", {"default": "access_key_secret"}),
                "security_token": ("STRING", {"default": ""}),
                "bucket_name": ("STRING", {"default": "bucket_name"}),
                "endpoint": (OSS_ENDPOINT_LIST,{"default": "oss-cn-hangzhou.aliyuncs.com"}),
            }
        }

    # 校验参数是否正确
    @classmethod
    def VALIDATE_INPUTS(cls,image, filename, access_key_id, access_key_secret, bucket_name, endpoint):
        #print("参数校验:\t%s,%s,%s,%s,%s" % (filename, access_key_id, access_key_secret, bucket_name, endpoint))
        if filename == "" or access_key_id == "" or access_key_secret == "" or bucket_name == "" or endpoint == "":
            return "参数不能为空"
        # 检查endpoing
        if endpoint not in OSS_ENDPOINT_LIST:
            return "endpoint 不正确\t %s" % endpoint
        return True
    RETURN_TYPES = ()
    FUNCTION = "upload_to_oss"
    CATEGORY = "API/oss"
    OUTPUT_NODE = True
    def upload_to_oss(self, image, filename, access_key_id, access_key_secret,security_token, bucket_name, endpoint):
        #print("参数信息: \t%s,%s,%s,%s,%s\n" %( filename,access_key_id, access_key_secret, bucket_name, endpoint))

        # 先判断这里是不是字符串
        if not isinstance(filename, str):
            raise ValueError("文件名必须为列表")
        try:
            filenameList = ast.literal_eval(filename)
            if isinstance(filenameList, list):  # 检查解析后的结果是否是列表
                pass
            else:
                raise ValueError("文件名必须为列表")
        except:
            raise ValueError("文件名必须为列表")
        print("共有图片[%s]张,filename[%s]个\n" % (len(image), len(filenameList) ))
        if len(image)!= len(filenameList) :
            raise ValueError("生成图片数量与给定的文件名数量不对应")
        n = 0
        for i in image:
            img = tensor_to_pil(i)
            #print("文件名称: [%s] \t文件类型: %s" % (filenameList[n],type(img)))
            self.put_object(img,filenameList[n],access_key_id, access_key_secret, security_token,bucket_name, endpoint)
            n = n + 1

        return ()
    def put_object(self,file,filename,access_key_id, access_key_secret, security_token,bucket_name, endpoint):
        #auth = oss2.Auth(access_key_id, access_key_secret)
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






            # A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "OSSUploadNode": OSSUploadNode
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "OSSUploadNode": "保存图片到oss上"
}
