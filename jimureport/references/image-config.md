# 普通图片配置完整参考（imgList 非套打模式）

积木报表普通图片：将图片放置在报表单元格上方，用于展示 logo、签章、插图等。与套打不同，普通图片不开启后端打印（`isBackend: false`），`background` 保持 `false`。

---

## 1. 普通图片 vs 套打 vs 背景图

| 特性 | 普通图片 | 套打（imgList） | 背景图 |
|------|---------|----------------|--------|
| 配置字段 | `imgList` 数组 | `imgList` 数组 | `background` 对象 |
| `printConfig.isBackend` | `false` | `true` | `false` |
| `imgList[].isBackend` | 无此字段 | `true` | - |
| `imgList[].commonBackend` | 无此字段 | `true` | - |
| `background` 字段值 | `false`（布尔值） | `"false"`（字符串） | 对象 `{path,repeat,width,height}` |
| 图片路径前缀 | 无前缀，直接使用 `message` | 无前缀，直接使用 `message` | `/jmreport/img/` + `message` |
| `width`/`height` 格式 | 纯数字字符串 `"719"` | 带 px 后缀 `"800px"` | 纯数字字符串 `"1920"` |

---

## 2. imgList — 普通图片配置

```python
imgList = [
    {
        "row": 7,               # 图片起始行（0-based）
        "col": 0,               # 图片起始列（0-based）
        "colspan": 8,           # 跨列数（图片覆盖的列数）
        "rowspan": 14,          # 跨行数（图片覆盖的行数）
        "width": "719",         # 图片显示宽度（纯数字字符串，无px后缀）
        "height": "326",        # 图片显示高度（纯数字字符串，无px后缀）
        "src": "jimureport/90aead22-4b55-408e-8653-17d7dbe7053b_1775124166358.png",  # 图片路径（无前缀）
        "layer_id": "hZBCTj4R6N7cKXkN",   # 图层唯一ID（随机字符串，与 rows virtual 对应）
        "offsetX": 0,           # X 轴偏移量（像素）
        "offsetY": 0,           # Y 轴偏移量（像素）
        "virtualCellRange": [   # 图片覆盖的单元格坐标 [row, col]，只需标记起始行
            [7,0],[7,1],[7,2],[7,3],[7,4],[7,5],[7,6],[7,7]
        ]
    }
]
```

### imgList 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `row` / `col` | int | 图片左上角单元格位置（0-based） |
| `colspan` / `rowspan` | int | 图片覆盖的列数/行数 |
| `width` / `height` | string | 图片显示尺寸，**纯数字字符串**（如 `"719"`），不带 px 后缀 |
| `src` | string | 图片路径，通过 `/jmreport/upload` 上传后返回的 `message` 值，**不含 `/jmreport/img/` 前缀** |
| `layer_id` | string | 图层唯一标识，与 `rows` 中 `virtual` 值一致 |
| `offsetX` / `offsetY` | int | 图片偏移量（像素），通常为 0 |
| `virtualCellRange` | array | 图片覆盖的起始行所有 `[row, col]` 坐标 |

### 与套打 imgList 的关键区别

- **无** `isBackend` 和 `commonBackend` 字段
- `width`/`height` 为纯数字字符串（`"719"`），不带 `px` 后缀

---

## 3. rows — 虚拟单元格标记

图片起始行覆盖范围内的每个单元格需在 `rows` 中标记 `virtual` 字段：

```python
rows = {
    "7": {
        "cells": {
            "0": {"text": " ", "virtual": "hZBCTj4R6N7cKXkN"},
            "1": {"text": " ", "virtual": "hZBCTj4R6N7cKXkN"},
            "2": {"text": " ", "virtual": "hZBCTj4R6N7cKXkN"},
            "3": {"text": " ", "virtual": "hZBCTj4R6N7cKXkN"},
            "4": {"text": " ", "virtual": "hZBCTj4R6N7cKXkN"},
            "5": {"text": " ", "virtual": "hZBCTj4R6N7cKXkN"},
            "6": {"text": " ", "virtual": "hZBCTj4R6N7cKXkN"},
            "7": {"text": " ", "virtual": "hZBCTj4R6N7cKXkN"}
        }
    },
    # 其他数据行正常填写
    "len": 200
}
```

> **注意：** `virtual` 单元格只需标记图片起始行（`row`），不需要标记所有 rowspan 行。

---

## 4. 图片上传

普通图片与套打、背景图使用相同的上传接口，**必须由用户提供图片文件**，AI 无法自动上传。

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
    "message": "jimureport/90aead22-4b55-408e-8653-17d7dbe7053b_1775124166358.png",
    "code": 0,
    "result": null,
    "timestamp": 1775124166358
}
```

### 路径使用规则

- `imgList.src` 直接使用 `message` 值（**无需加任何前缀**）

---

## 5. 完整普通图片配置示例（Python 构建）

```python
import random
import string

def gen_layer_id(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

layer_id = gen_layer_id()   # 例如 "hZBCTj4R6N7cKXkN"

# 图片放置在 row=7, col=0，覆盖 8 列、14 行
start_row = 7
start_col = 0
colspan = 8
rowspan = 14
img_width = "719"
img_height = "326"

virtual_cell_range = [[start_row, c] for c in range(start_col, start_col + colspan)]

img_list = [
    {
        "row": start_row,
        "col": start_col,
        "colspan": colspan,
        "rowspan": rowspan,
        "width": img_width,
        "height": img_height,
        "src": "jimureport/90aead22-xxx.png",  # 上传返回的 message
        "layer_id": layer_id,
        "offsetX": 0,
        "offsetY": 0,
        "virtualCellRange": virtual_cell_range
    }
]

# rows 中标记 virtual（只需起始行）
virtual_row_cells = {
    str(c): {"text": " ", "virtual": layer_id}
    for c in range(start_col, start_col + colspan)
}
rows = {
    str(start_row): {"cells": virtual_row_cells},
    # 其他数据行...
    "len": 200
}
```

---

## 6. 注意事项

1. `imgList.src` 路径**不含** `/jmreport/img/` 前缀（直接使用上传返回的 `message`）
2. `layer_id` 为随机字符串，`imgList` 和 `rows.virtual` 必须保持一致
3. `virtualCellRange` 只需标记起始行的单元格坐标
4. `width`/`height` 为纯数字字符串，不带 `px` 后缀（与套打不同）
5. 普通图片不需要设置 `isBackend`、`commonBackend` 字段
6. `printConfig.isBackend` 保持 `false`，`background` 保持 `false`
7. 一个报表可以同时添加多张图片，每张图片使用不同的 `layer_id`
