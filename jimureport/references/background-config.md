# 背景图配置完整参考（background）

积木报表背景图：将图片铺设为报表 Sheet 的背景，支持重复平铺。与套打（imgList）不同，背景图不参与打印内容叠加，属于纯视觉装饰。

---

## 1. background JSON 结构

```python
background = {
    "path": "/jmreport/img/jimureport/1_1775121842772.png",  # 图片完整路径（含前缀）
    "repeat": "no-repeat",   # 重复方式
    "width": "1920",         # 宽度（px，字符串格式）
    "height": "1080"         # 高度（px，字符串格式）
}
```

### 字段说明

| 字段 | 类型 | 说明 | 可选值 |
|------|------|------|--------|
| `path` | string | 图片完整路径（`/jmreport/img/` + 上传返回的 `message`） | - |
| `repeat` | string | 图片重复方式 | `no-repeat` / `repeat-x` / `repeat-y` / `repeat` |
| `width` | string | 背景图宽度（px，字符串格式） | 如 `"1920"` |
| `height` | string | 背景图高度（px，字符串格式） | 如 `"1080"` |

### repeat 可选值说明

| 值 | 含义 |
|----|------|
| `no-repeat` | 无重复（默认，推荐） |
| `repeat-x` | 水平方向重复 |
| `repeat-y` | 垂直方向重复 |
| `repeat` | 双向重复平铺 |

---

## 2. 无背景图时

```python
# 保存 API 参数中传 Python bool False（不是字符串 "false"）
"background": False
```

---

## 3. 图片上传

背景图需先通过上传接口获取路径，**必须由用户提供图片文件**，AI 无法自动上传。

### 上传接口

```
POST /jmreport/upload
Content-Type: multipart/form-data

参数：file（MultipartFile）
```

### 返回结果

```json
{
    "success": true,
    "message": "jimureport/1_1775122603620.png",
    "code": 0,
    "result": null,
    "timestamp": 1775122603620
}
```

### 路径使用规则

- 返回值中 **`message` 字段** 即为图片路径
- `background.path` = `/jmreport/img/` + `message` 值
  - 例：`message` = `jimureport/1_1775121842772.png`
  - → `path` = `/jmreport/img/jimureport/1_1775121842772.png`

### Python 上传示例

```python
import requests, os

def upload_image(base_url, token, file_path):
    """上传图片，返回 message 字段路径"""
    with open(file_path, 'rb') as f:
        resp = requests.post(
            f"{base_url}/jmreport/upload",
            headers={"X-Access-Token": token},
            files={"file": (os.path.basename(file_path), f)}
        )
    data = resp.json()
    if data.get("success"):
        return data["message"]   # e.g. "jimureport/1_1775121842772.png"
    raise Exception(f"上传失败: {data}")

# 构建 background 对象
msg = upload_image(base_url, token, "/path/to/bg.png")
background = {
    "path": f"/jmreport/img/{msg}",   # 加前缀
    "repeat": "no-repeat",
    "width": "1920",
    "height": "1080"
}
```

---

## 4. 背景图 vs 套打（imgList）路径前缀对比

| 用途 | 字段 | 路径格式 |
|------|------|---------|
| 背景图 | `background.path` | `/jmreport/img/` + `message` |
| 套打图片 | `imgList[].src` | `message`（直接使用，无前缀） |

> **关键区别：** 背景图路径需加 `/jmreport/img/` 前缀，套打路径直接使用上传返回的 `message` 值。

---

## 5. 注意事项

1. `printConfig.isBackend` 为 `false` 时背景图正常显示；套打（`isBackend: true`）时背景图不生效，应使用 `imgList`
2. `width`/`height` 为字符串类型（`"1920"`），不是数字
3. 保存 API 中 `background` 字段**直接传对象（dict）**，不要 json.dumps 成字符串；否则前端报 `Cannot use 'in' operator to search for 'repeat'` 错误
