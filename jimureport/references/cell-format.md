# 单元格格式化与类型完整参考

积木报表单元格有**两套独立的配置**，来源：`format.js` + 右侧属性面板。

---

## 一、单元格类型（display 字段）

右侧面板"类型"下拉，控制单元格**渲染方式**，存储在 cell 的 `display` 字段。

| display 值 | 显示名 | 说明 |
|-----------|--------|------|
| `normal` | 文本 | 默认，原样显示文本（可省略不写） |
| `number` | 数值 | 数字展示，启用数值相关处理 |
| `img` | 图片 | 将单元格值渲染为图片（URL） |
| `base64Img` | Base64图片 | 渲染 base64 编码图片 |
| `barcode` | 条形码 | 将值渲染为条形码 |
| `qrcode` | 二维码 | 将值渲染为二维码 |
| `richText` | 富文本 | 渲染 HTML 富文本内容 |

**JSON 示例：**

```json
{"text": "#{product.img}",  "display": "img"}
{"text": "#{order.code}",   "display": "barcode"}
{"text": "#{goods.qrUrl}",  "display": "qrcode"}
{"text": "#{desc.html}",    "display": "richText"}
{"text": "#{order.amount}", "display": "number"}
{"text": "张三",             "display": "normal"}
```

> `display` 不写时默认为 `normal`（文本）。

---

## 二、数值/日期格式化（styles 数组 + style 索引）

右侧面板"格式"下拉，控制数值/日期的**显示格式**（货币符号、千位分隔符、日期格式等）。

### 机制

格式**不直接写在 cell 里**，而是：
1. 顶层 `styles` 数组中定义格式对象
2. 单元格通过 `style` 字段引用数组下标

```json
{
  "styles": [
    {"format": "number"},
    {"format": "rmb"},
    {"format": "percent"},
    {"format": "date"}
  ],
  "rows": {
    "1": {
      "cells": {
        "1": {"text": "10000.32", "style": 0},
        "2": {"text": "#{order.amount}", "style": 1},
        "3": {"text": "#{rate}", "style": 2},
        "4": {"text": "#{order.date}", "style": 3}
      }
    }
  }
}
```

### 所有可用 format key

**数值类：**

| format | 示例显示 | 说明 |
|--------|---------|------|
| `number` | `1,000.12` | 千位分隔符，保留原始小数位 |
| `percent` | `32%` | 原始值 ×100，加 % |
| `rmb` | `￥1,000.00` | 加 ￥ 前缀 |
| `usd` | `$1,000.00` | 加 $ 前缀 |
| `eur` | `€1,000.00` | 加 € 前缀 |

**日期时间类：**

| format | 示例显示 | 格式模板 |
|--------|---------|---------|
| `date` | `2020/10/10` | yyyy/MM/dd |
| `date2` | `2020年10月10日` | yyyy年MM月dd日 |
| `time` | `10:10:10` | hh:mm:ss |
| `datetime` | `2020/10/10 10:10:10` | yyyy/MM/dd hh:mm:ss |
| `year` | `2020年` | yyyy年 |
| `month` | `10月` | MM月 |
| `yearMonth` | `2020年10月` | yyyy年MM月 |

---

## 三、两套系统对比

| 属性 | display | styles + style |
|------|---------|----------------|
| 作用 | 渲染类型（图片/条码/富文本等） | 数值/日期显示格式 |
| 存储位置 | cell 内直接字段 | 顶层 styles 数组，cell 用 style 索引引用 |
| 是否可组合 | 可以，两者互不冲突 | — |
| 典型场景 | `display:"img"` 显示图片 | `style:0` → `{"format":"rmb"}` |

**两者可以同时使用：**

```json
{
  "styles": [{"format": "number"}],
  "rows": {
    "1": {
      "cells": {
        "1": {"text": "#{order.amount}", "display": "number", "style": 0}
      }
    }
  }
}
```

---

## 四、AI 生成报表时的选择规则

| 数据内容 | display | style (format) |
|---------|---------|---------------|
| 金额（人民币） | `number` | `rmb` |
| 金额（美元） | `number` | `usd` |
| 金额（欧元） | `number` | `eur` |
| 普通数字 | `number` | `number` |
| 百分比/比率 | `number` | `percent` |
| 日期 | 不填（normal） | `date` 或 `date2` |
| 日期时间 | 不填（normal） | `datetime` |
| 图片 URL | `img` | 不填 |
| Base64 图片 | `base64Img` | 不填 |
| 条形码 | `barcode` | 不填 |
| 二维码 | `qrcode` | 不填 |
| 富文本 HTML | `richText` | 不填 |
| 普通文本 | 不填（normal） | 不填 |

> **注意**：`percent` 格式会将原始值 ×100 再加 %，数据源字段值应为小数（0.15 显示为 15%）。

---

## 五、AI 构建 styles 数组的模式

```python
styles = []
format_index = {}

def get_style_index(fmt):
    if fmt not in format_index:
        format_index[fmt] = len(styles)
        styles.append({"format": fmt})
    return format_index[fmt]

# 使用
rmb_idx  = get_style_index("rmb")   # → 0
date_idx = get_style_index("date")  # → 1
pct_idx  = get_style_index("percent")  # → 2

# 单元格：金额列
cell_amount = {"text": "#{order.amount}", "display": "number", "style": rmb_idx}
# 单元格：日期列
cell_date = {"text": "#{order.date}", "style": date_idx}
# 单元格：图片列（不需要 style）
cell_img = {"text": "#{product.img}", "display": "img"}
```
