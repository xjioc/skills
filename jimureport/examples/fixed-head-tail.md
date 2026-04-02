# 固定表头表尾报表示例

固定表头表尾：打印时每页重复显示表头和表尾，适用于多页打印的报表。

---

## 一、核心规则

### 关键配置

1. **fixedPrintHeadRows** — 定义固定表头区域，打印时每页顶部重复
2. **fixedPrintTailRows** — 定义固定表尾区域，打印时每页底部重复
3. **表头单元格** — 加 `"fixedHead": 1`
4. **表尾单元格** — 加 `"fixedTail": 1`

### 与普通表头的区别

| 对比项 | 普通表头 | 固定表头 |
|-------|---------|---------|
| 打印多页时 | 仅第一页显示 | **每页都显示** |
| 单元格标记 | 无 | `"fixedHead": 1` |
| jsonStr 配置 | 无 | `fixedPrintHeadRows` |

### 关键约束

- **标题单元格必须有 `merge` 属性**：仅在 `merges` 列表中声明合并不够，标题单元格自身必须有 `"merge": [行跨度-1, 列跨度-1]`，否则设计器中标题不会合并
- **表尾必须覆盖全部数据列**：表尾的合并单元格之和必须等于数据列数，不能只覆盖部分列，否则表尾右侧会有空白
- **固定表尾可包含多行**：如需空行间距 + 表尾内容，`sri`/`eri` 跨多行即可，空行也需标记 `fixedTail: 1`

---

## 二、完整示例（10列商品销售统计表）

### 布局结构

```
Row 1: 标题「商品销售统计表」（合并10列，不固定，仅首页）
Row 2: 空行间距（15px）
Row 3: 固定表头行（fixedHead:1）← fixedPrintHeadRows
Row 4: 数据绑定行
Row 5: 空行间距（fixedTail:1）← fixedPrintTailRows 起始
Row 6: 表尾内容行（fixedTail:1）← fixedPrintTailRows 结束
```

### fixedPrintHeadRows / fixedPrintTailRows 结构

```python
# 固定表头：仅表头行(Row 3)
fixed_head = [{"sci": 1, "eci": 10, "sri": 3, "eri": 3}]

# 固定表尾：空行(Row 5) + 表尾内容(Row 6)，共2行
fixed_tail = [{"sci": 1, "eci": 10, "sri": 5, "eri": 6}]
```

| 字段 | 说明 |
|------|------|
| `sci`/`eci` | 列范围（rows 中的列 key，1-based） |
| `sri`/`eri` | 行范围（rows 中的行 key，1-based） |

### 完整 rows 数据

```python
rows = {
    # Row 1: 标题（合并10列，merge属性必须在单元格上）
    "1": {
        "cells": {
            "1": {"text": "商品销售统计表", "style": 5, "merge": [0, 9]}
        },
        "height": 45
    },
    # Row 2: 空行间距
    "2": {"cells": {}, "height": 15},
    # Row 3: 固定表头（每个单元格加 fixedHead: 1）
    "3": {
        "cells": {
            "1":  {"text": "商品名称", "style": 4, "fixedHead": 1},
            "2":  {"text": "类别",     "style": 4, "fixedHead": 1},
            "3":  {"text": "品牌",     "style": 4, "fixedHead": 1},
            "4":  {"text": "规格型号", "style": 4, "fixedHead": 1},
            "5":  {"text": "单价",     "style": 4, "fixedHead": 1},
            "6":  {"text": "数量",     "style": 4, "fixedHead": 1},
            "7":  {"text": "销售总额", "style": 4, "fixedHead": 1},
            "8":  {"text": "销售日期", "style": 4, "fixedHead": 1},
            "9":  {"text": "销售区域", "style": 4, "fixedHead": 1},
            "10": {"text": "销售员",   "style": 4, "fixedHead": 1},
        },
        "height": 34
    },
    # Row 4: 数据绑定行
    "4": {
        "cells": {
            "1":  {"text": "#{sales.product_name}",  "style": 2},
            "2":  {"text": "#{sales.category}",      "style": 2},
            "3":  {"text": "#{sales.brand}",         "style": 2},
            "4":  {"text": "#{sales.spec}",          "style": 2},
            "5":  {"text": "#{sales.unit_price}",    "style": 2},
            "6":  {"text": "#{sales.quantity}",      "style": 2},
            "7":  {"text": "#{sales.total_amount}",  "style": 2},
            "8":  {"text": "#{sales.sale_date}",     "style": 2},
            "9":  {"text": "#{sales.region}",        "style": 2},
            "10": {"text": "#{sales.salesman}",      "style": 2},
        }
    },
    # Row 5: 表尾空行间距（也需标记 fixedTail，合并全列避免显示异常）
    "5": {
        "cells": {
            "1": {"text": "", "fixedTail": 1, "merge": [0, 9]}
        },
        "height": 10
    },
    # Row 6: 表尾内容（合并列数之和 = 数据列数）
    "6": {
        "cells": {
            "1": {"text": "制表人：admin",    "style": 6, "fixedTail": 1, "merge": [0, 2]},
            "4": {"text": "审核人：",         "style": 6, "fixedTail": 1, "merge": [0, 1]},
            "6": {"text": "日期：2026-03-27", "style": 6, "fixedTail": 1, "merge": [0, 1]},
            "8": {"text": "第  页/共  页",    "style": 6, "fixedTail": 1, "merge": [0, 2]},
        },
        "height": 30
    },
    "len": 200
}
```

### 列宽

```python
cols = {
    "1": {"width": 160},   # 商品名称
    "2": {"width": 80},    # 类别
    "3": {"width": 80},    # 品牌
    "4": {"width": 140},   # 规格型号
    "5": {"width": 100},   # 单价
    "6": {"width": 70},    # 数量
    "7": {"width": 120},   # 销售总额
    "8": {"width": 100},   # 销售日期
    "9": {"width": 80},    # 销售区域
    "10": {"width": 80},   # 销售员
    "len": 100
}
```

### 合并单元格

```python
# UI行号 = rows key + 1
merges = [
    "B2:K2",     # 标题合并10列（Row 1 → UI行2）
    "B7:D7",     # 表尾-制表人 3列（Row 6 → UI行7）
    "E7:F7",     # 表尾-审核人 2列
    "G7:H7",     # 表尾-日期 2列
    "I7:K7",     # 表尾-页码 3列（3+2+2+3=10列，覆盖全部）
]
```

### 样式

```python
styles = [
    # 0: 边框
    {"border": {"bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"]}},
    # 1: 边框+居中
    {"border": {"bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"]}, "align": "center"},
    # 2: 数据行（边框+居中+垂直居中）
    {"border": {"bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"]}, "align": "center", "valign": "middle"},
    # 3: 蓝底（无白字）
    {"border": {"bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"]}, "align": "center", "valign": "middle", "bgcolor": "#01b0f1"},
    # 4: 表头（蓝底白字）
    {"border": {"bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"]}, "align": "center", "valign": "middle", "bgcolor": "#01b0f1", "color": "#ffffff"},
    # 5: 标题（淡蓝底深蓝字加粗）
    {"border": {"bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"]}, "align": "center", "valign": "middle", "font": {"bold": True, "size": 14}, "bgcolor": "#E6F2FF", "color": "#0066CC"},
    # 6: 表尾（浅灰底，左对齐，浅灰边框）
    {"border": {"bottom": ["thin","#d8d8d8"], "top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}, "align": "left", "valign": "middle", "bgcolor": "#f5f5f5", "color": "#333333"},
]
```

### save 请求体关键字段

```python
save_data = {
    # ... 标准字段 ...
    "fixedPrintHeadRows": [{"sci": 1, "eci": 10, "sri": 3, "eri": 3}],
    "fixedPrintTailRows": [{"sci": 1, "eci": 10, "sri": 5, "eri": 6}],
    "printConfig": {"paper": "A4", "width": 210, "height": 297, "definition": 1,
                    "isBackend": False, "marginX": 10, "marginY": 10,
                    "layout": "landscape", "printCallBackUrl": ""},
    # ...
}
```

---

## 三、表尾列分配计算方法

表尾的合并单元格总列数**必须等于**数据列数，否则右侧会出现空白。

**通用计算公式：**

```python
total_cols = 10  # 数据列数
tail_sections = ["制表人", "审核人", "日期", "页码"]  # 4个区域
# 基础分配: 10 / 4 = 2余2，前2个区域各多1列
# → 3 + 3 + 2 + 2 = 10  或  3 + 2 + 2 + 3 = 10
```

**不同列数的分配示例：**

| 数据列数 | 制表人 | 审核人 | 日期 | 页码 | 合计 |
|---------|--------|-------|------|------|------|
| 6列 | 2 | 1 | 1 | 2 | 6 |
| 8列 | 2 | 2 | 2 | 2 | 8 |
| 10列 | 3 | 2 | 2 | 3 | 10 |

---

## 四、预览效果（打印多页时）

```
┌───────────────────────────── 第1页 ─────────────────────────────┐
│              商品销售统计表（标题，仅首页显示）                      │
│                                                                  │
│ 商品名称│类别│品牌│规格型号│单价│数量│销售总额│日期│区域│销售员     │ ← 固定表头
│ iPhone  │手机│苹果│256GB  │8999│120 │1079880│1/5 │华东│张伟       │
│ MacBook │电脑│苹果│M3 Pro │... │... │...    │... │... │...        │
│                                                                  │
│ 制表人：admin    审核人：     日期：2026-03-27    第  页/共  页     │ ← 固定表尾
└──────────────────────────────────────────────────────────────────┘

┌───────────────────────────── 第2页 ─────────────────────────────┐
│ 商品名称│类别│品牌│规格型号│单价│数量│销售总额│日期│区域│销售员     │ ← 固定表头（自动重复）
│ iPad Pro│平板│苹果│M4/256 │8499│55  │467445 │3/12│华南│李娜       │
│ AirPods │配件│苹果│USB-C  │1799│300 │569700 │... │... │...        │
│                                                                  │
│ 制表人：admin    审核人：     日期：2026-03-27    第  页/共  页     │ ← 固定表尾（自动重复）
└──────────────────────────────────────────────────────────────────┘
```

---

## 五、注意事项

1. **固定表头/表尾仅在打印时生效**，预览页面不会重复显示
2. **标题行不在固定表头范围内**（标题只在第一页显示）
3. **固定表头可包含多行**（如多级表头），`sri`/`eri` 跨多行即可
4. **固定表尾可包含多行**（如空行间距 + 内容行），空行单元格也需标记 `fixedTail: 1`
5. **数据集类型不限**（SQL/API/JavaBean/JSON 均可）
6. **列数较多（>6列）时**，建议 `printConfig.layout` 设为 `"landscape"`（横向打印）
7. **标题单元格必须同时声明 `merge` 属性和 `merges` 列表**，缺一不可
8. **表尾空行建议合并全列**：`"merge": [0, 列数-1]`，避免空行中出现多余边框