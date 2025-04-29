# comfyui_image2oss

Upload the image to Alibaba Cloud OSS

将图片上传到阿里云OSS上


## Quickstart

1. 安装 [ComfyUI](https://docs.comfy.org/get_started).
1. 安装 [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)
1. 运行`comfy node registry-install image2oss` 或[直接下载](https://registry.comfy.org/publishers/nxt5656/nodes/image2oss)插件到comfyui的custom_nodes目录
1. 重启 ComfyUI.

## 参数说明
### filename
格式为字符串列表,这个列表中每个字符串是图片在oss时的对象名称,必须包含完整oss路径.

### access_key_id
阿里云ak

### access_key_secret
阿里云ak对应的密钥

### security_token
阿里云STS安全令牌

### sts_service_url
获取阿里云ak信息的地址
返回数据格式为:
```json
{
  "requestId": "非必要",
  "success": true,
  "errorMessage": "",
  "data": {
    "accessKeyId": "阿里云AK",
    "accessKeySecret": "阿里云SK",
    "securityToken": "阿里云STS安全令牌",
    "expiration": "2025-04-29T14:37:56Z",
    "arn": "非必要",
    "assumedRoleId": "非必要"
  }
}
```


### bucket_name
阿里云 bucket 名称



### endpoint
[oss的endpoing](https://help.aliyun.com/zh/oss/user-guide/regions-and-endpoints)
