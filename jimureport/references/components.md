# 报表组件参考

积木报表支持 4 种图层组件（Layer），它们以独立数组存储在 jsonStr 顶层，与 rows/cols 平级。

## 组件类型总览

| 组件 | jsonStr 字段 | 类型标识 | 用途 |
|------|-------------|---------|------|
| 图片 | `imgList` | `img` | 外部图片/Logo/背景图 |
| 图表 | `chartList` | `chart` | ECharts 可视化图表 |
| 条形码 | `barcodeList` | `barcode` | CODE128/EAN 等一维码 |
| 二维码 | `qrcodeList` | `qrcode` | QR Code 二维码 |

所有组件共享以下基础属性：

```python
{
    "row": 0,           # 起始行号（从0开始）
    "col": 0,           # 起始列号（从0开始）
    "colspan": 0,       # 列跨度
    "rowspan": 0,       # 行跨度
    "width": 300,       # 宽度（像素，图表必须是字符串如"300"）
    "height": 200,      # 高度（像素，图表必须是字符串如"200"）
    "layer_id": "唯一ID",  # 唯一标识，对应 virtual cell
    "offsetX": 0,       # X偏移
    "offsetY": 0,       # Y偏移
    "virtualCellRange": [[row,col], ...]  # 占据的所有单元格坐标
}
```

## 1. 图片组件 (imgList)

### JSON 结构

```python
img_item = {
    "row": 0,
    "col": 1,
    "colspan": 0,
    "rowspan": 0,
    "width": 315,           # 数字
    "height": 151,          # 数字
    "src": "/jmreport/img/upload/xxx.png",  # 图片路径（相对或绝对）
    "isBackend": False,     # 是否作为前置遮罩
    "isBackendImg": False,  # 是否作为背景图
    "commonBackend": None,  # 共享遮罩/背景属性
    "layer_id": "img_xxx",
    "offsetX": 0,
    "offsetY": 0,
    "virtualCellRange": [[0,1],[0,2],[1,1],[1,2]]
}
```

### 图片路径说明

| 类型 | 示例 |
|------|------|
| 上传图片 | `/jmreport/img/upload/xxx.png` |
| 外部URL | `https://example.com/logo.png` |
| 数据绑定 | `${dbCode.imgField}` — 字段值为图片URL |

## 2. 图表组件 (chartList)

详见 `chart-config.md`，这里列出关键结构。

### JSON 结构

```python
chart_item = {
    "row": 5,
    "col": 1,
    "colspan": 0,
    "rowspan": 0,
    "width": "650",          # 必须是字符串！
    "height": "350",         # 必须是字符串！
    "config": json.dumps(echarts_option),  # ECharts 配置 JSON 字符串
    "url": "",               # 外部数据 URL（通常为空）
    "extData": {
        "chartType": "bar.simple",  # 图表类型
        "dataType": "sql",          # 数据来源: "sql"/"api"/"json"/"javabean"/"files"
        "dataId": "数据集ID",       # saveDb 返回的 id
        "dbCode": "数据集编码",     # 数据集编码
        "axisX": "name",           # 固定值
        "axisY": "value",          # 固定值
        "series": "type",          # 固定值
        "xText": "",
        "yText": "",
        "apiStatus": "1"
    },
    "layer_id": "chart_xxx",
    "offsetX": 0,
    "offsetY": 0,
    "backgroud": {"enabled": False, "color": "#fff", "image": ""},
    "virtualCellRange": [[5,1],[5,2],...]
}
```

## 3. 条形码组件 (barcodeList)

### JSON 结构

```python
barcode_item = {
    "row": 3,
    "col": 0,
    "colspan": 0,
    "rowspan": 0,
    "width": 300,
    "height": 200,
    "layer_id": "barcode_xxx",
    "offsetX": 0,
    "offsetY": 0,
    "jsonString": json.dumps({
        "barcodeContent": "jmreport",   # 条码内容（支持 ${dbCode.field} 动态绑定）
        "format": "CODE128",            # 条码格式
        "width": 2,                     # 条线宽度
        "height": 100,                  # 条码高度
        "displayValue": False,          # 是否显示文字
        "text": "jmreport",             # 显示文字内容
        "fontOptions": "",              # 字体选项（bold/italic）
        "font": "monospace",            # 字体
        "textAlign": "center",          # 文字对齐
        "textPosition": "bottom",       # 文字位置
        "textMargin": 2,               # 文字间距
        "fontSize": 20,                # 字体大小
        "background": "#fff",          # 背景色
        "lineColor": "#000",           # 条线颜色
        "margin": 10                   # 边距
    }),
    "virtualCellRange": [[3,0],[3,1],[4,0],[4,1]]
}
```

### 支持的条码格式

| format | 说明 |
|--------|------|
| `CODE128` | Code 128（默认，最常用） |
| `CODE39` | Code 39 |
| `EAN13` | EAN-13 |
| `EAN8` | EAN-8 |
| `UPC` | UPC-A |
| `ITF14` | ITF-14 |

### 动态数据绑定

条码内容支持表达式：`${dbCode.fieldName}`，运行时替换为数据集字段值。

## 4. 二维码组件 (qrcodeList)

### JSON 结构

```python
qrcode_item = {
    "row": 5,
    "col": 0,
    "colspan": 0,
    "rowspan": 0,
    "width": 128,
    "height": 128,
    "layer_id": "qrcode_xxx",
    "offsetX": 0,
    "offsetY": 0,
    "jsonString": json.dumps({
        "text": "http://jimureport.com/",  # 二维码内容（支持 ${dbCode.field}）
        "width": 128,
        "height": 128,
        "colorDark": "#000000",            # 前景色
        "colorLight": "#ffffff"            # 背景色
    }),
    "virtualCellRange": [[5,0],[5,1],[6,0],[6,1]]
}
```

## 5. 单元格内嵌组件 (displayConfig)

除了图层组件，单元格本身也可以通过 `display` 属性渲染为特殊组件：

```python
# 在 rows 的 cell 中设置
cell = {
    "text": "#{dbCode.imgUrl}",
    "display": "img"           # 渲染为图片
}

# 或
cell = {
    "text": "#{dbCode.code}",
    "display": "barcode"       # 渲染为条形码
}

# 或
cell = {
    "text": "#{dbCode.url}",
    "display": "qrcode"        # 渲染为二维码
}
```

**display 可选值：**

| 值 | 说明 |
|----|------|
| `normal` | 普通文本（默认） |
| `img` | 图片（text 为图片 URL） |
| `barcode` | 条形码（text 为条码内容） |
| `qrcode` | 二维码（text 为二维码内容） |
| `base64Img` | Base64 图片 |
| `richText` | 富文本/HTML |

## Virtual Cell 占位规则

所有图层组件都需要在 `rows` 中声明 virtual 占位：

```python
# 1. 确定组件占据的行列范围
row_start, row_end = 5, 8
col_start, col_end = 1, 4
layer_id = "chart_xxx"

# 2. 构造 virtualCellRange
virtual_cells = []
for r in range(row_start, row_end + 1):
    for c in range(col_start, col_end + 1):
        virtual_cells.append([r, c])

# 3. 在 rows 中添加 virtual 占位
for r in range(row_start, row_end + 1):
    cells = {}
    for c in range(col_start, col_end + 1):
        cells[str(c)] = {"text": " ", "virtual": layer_id}
    rows_data[str(r)] = {"cells": cells}

# 4. 组件中设置 virtualCellRange
component["virtualCellRange"] = virtual_cells
```

**注意事项：**
- `virtual` 值必须和组件的 `layer_id` 一致
- `text` 必须为 `" "`（一个空格），不能为空
- 组件区域不能和数据绑定行重叠
- 一个组件的 virtual cells 不能和其他组件重叠

## Python 构造完整示例

```python
# 构造一个包含 表格 + 柱状图 + 二维码 的报表

layer_chart_id = "chart_" + gen_id()
layer_qr_id = "qrcode_" + gen_id()

rows_data = {
    # 标题行
    "1": {"cells": {"1": {"text": "销售报表", "style": 5}}, "height": 40},
    # 表头
    "2": {"cells": {
        "1": {"text": "产品", "style": 4},
        "2": {"text": "销量", "style": 4},
        "3": {"text": "金额", "style": 4}
    }, "height": 34},
    # 数据行
    "3": {"cells": {
        "1": {"text": "#{ds.name}", "style": 2},
        "2": {"text": "#{ds.qty}", "style": 2},
        "3": {"text": "#{ds.amount}", "style": 2}
    }},
    # 空行
    "4": {"cells": {}, "height": 15},
    "len": 200
}

# 柱状图占位 (row 5-12, col 1-5)
for r in range(5, 13):
    cells = {}
    for c in range(1, 6):
        cells[str(c)] = {"text": " ", "virtual": layer_chart_id}
    rows_data[str(r)] = {"cells": cells}

# 二维码占位 (row 5-8, col 6-7)
for r in range(5, 9):
    cells = rows_data.get(str(r), {"cells": {}})["cells"]
    for c in range(6, 8):
        cells[str(c)] = {"text": " ", "virtual": layer_qr_id}
    rows_data[str(r)] = {"cells": cells}

# 柱状图
chart_config = {
    "title": {"text": "销量统计", "left": "center"},
    "tooltip": {"trigger": "axis"},
    "xAxis": [{"type": "category", "data": []}],
    "yAxis": [{"type": "value"}],
    "series": [{"type": "bar", "data": [], "itemStyle": {"color": "#01b0f1"}}]
}

chart_list = [{
    "row": 5, "col": 1, "colspan": 0, "rowspan": 0,
    "width": "500", "height": "300",
    "config": json.dumps(chart_config, ensure_ascii=False),
    "url": "",
    "extData": {
        "chartType": "bar.simple", "dataType": "sql",
        "dataId": chart_db_id, "dbCode": "saleschart",
        "axisX": "name", "axisY": "value", "series": "type",
        "xText": "", "yText": "", "apiStatus": "1"
    },
    "layer_id": layer_chart_id,
    "offsetX": 0, "offsetY": 0,
    "backgroud": {"enabled": False, "color": "#fff", "image": ""},
    "virtualCellRange": [[r,c] for r in range(5,13) for c in range(1,6)]
}]

# 二维码
qrcode_list = [{
    "row": 5, "col": 6, "colspan": 0, "rowspan": 0,
    "width": 128, "height": 128,
    "layer_id": layer_qr_id,
    "offsetX": 0, "offsetY": 0,
    "jsonString": json.dumps({"text": "https://example.com", "width": 128, "height": 128, "colorDark": "#000000", "colorLight": "#ffffff"}),
    "virtualCellRange": [[r,c] for r in range(5,9) for c in range(6,8)]
}]

# 最终保存数据中包含
save_data = {
    # ... 其他字段
    "chartList": chart_list,
    "qrcodeList": qrcode_list,
    # imgList 和 barcodeList 为空时可省略或传 []
}
```
