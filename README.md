# comfyui_image2oss

## 更新说明

本分支基于原版本进行了以下改进：

### 🆕 新增功能
1. **oss2vid节点** - 新增从阿里云OSS获取视频文件的功能，支持直接下载视频文件到本地临时路径
2. **endpoint参数优化** - oss2image和oss2vid节点的endpoint参数现在支持自定义输入，不再限制于预设列表，可以输入任意有效的OSS端点地址

### 📋 节点对照表
| 原版节点名 | 新版节点名 | 主要变更 |
|-----------|-----------|----------|
| oss2image | oss2image | endpoint参数改为可输入任意字符串 |
| - | **oss2vid** | 🆕 新增视频下载功能 |

**🔄 改进说明**: 在oss2image和oss2vid节点中，endpoint参数现在支持手动输入任意有效的OSS端点地址，不再局限于预设的下拉列表选项。这样可以支持更多地区和自定义端点配置。

### 🎥 oss2vid节点说明
新增的oss2vid节点用于从阿里云OSS下载视频文件：
- **输入**: filename(视频文件路径)、access_key_id、access_key_secret、security_token、bucket_name、endpoint
- **输出**: video_path(本地临时文件路径的字符串)
- **支持格式**: 支持常见视频格式(mp4、avi、mov等)
- **使用场景**: 可以将OSS中存储的视频文件下载到本地，供后续的视频处理节点使用

---

## 功能
### 获取图片
1. image2oss  保存图片到阿里云oss上,使用自建服务阿里云AK&SK&Token
2. image2oss-sts-service 保存图片到阿里云oss上,使用自建服务获取阿里云AK&SK&Token
3. image2oss-tag 保存图片到阿里云oss上,并添加"Ai生成"的水印,使用阿里云AK&SK(支持ststoken)
4. image2oss-tag-sts-service 保存图片到阿里云oss上,并添加"Ai生成"的水印,使用自建服务阿里云AK&SK&Token
5. oss2image 从阿里云oss上获取图片,使用阿里云AK&SK(支持ststoken)
6. oss2image-sts-service 从阿里云oss上获取图片,使用自建服务阿里云AK&SK&Token
7. url2image 从url获取图片
8. **oss2vid 从阿里云oss上获取视频文件,使用阿里云AK&SK(支持ststoken)** 🆕


## Quickstart

1. 安装 [ComfyUI](https://docs.comfy.org/get_started).
2. 安装 [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)
3. 运行`comfy node registry-install image2oss` 或[直接下载](https://registry.comfy.org/publishers/nxt5656/nodes/image2oss)插件到comfyui的custom_nodes目录
4. 重启 ComfyUI.

## 参数说明
### filename
格式为字符串列表,这个列表中每个字符串是图片在oss时的对象名称,必须包含完整oss路径.
注意:保存图片到oss时,这里是个列表,可以通过image输入多张图片,与filename列表数量保持一致

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

## AI标记
中国法规要求,ai生成内容必须添加ai相关标记,标准如下:

[网络安全技术 人工智能生成合成内容标识方法](https://www.tc260.org.cn/upload/2025-03-15/1742009439794081593.pdf)
