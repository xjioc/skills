# 图表配置参考

## 图表模板文件位置

`src/main/resources/static/jmreport/desreport_/chartjson/`

生成图表报表时，应先读取对应的模板 JSON 文件作为 ECharts 配置基础。

## 可用图表类型

| 文件名 | chartType | 说明 |
|--------|-----------|------|
| `bar.simple.json` | `bar.simple` | 柱状图（单系列） |
| `bar.multi.json` | `bar.multi` | 柱状图（多系列） |
| `bar.stack.json` | `bar.stack` | 堆叠柱状图 |
| `bar.horizontal.json` | `bar.horizontal` | 横向柱状图 |
| `bar.multi.horizontal.json` | `bar.multi.horizontal` | 横向多系列柱状图 |
| `bar.stack.horizontal.json` | `bar.stack.horizontal` | 横向堆叠柱状图 |
| `bar.negative.json` | `bar.negative` | 正负柱状图 |
| `bar.background.json` | `bar.background` | 带背景柱状图 |
| `line.simple.json` | `line.simple` | 折线图（单系列） |
| `line.multi.json` | `line.multi` | 折线图（多系列） |
| `line.smooth.json` | `line.smooth` | 平滑曲线图 |
| `line.area.json` | `line.area` | 面积图 |
| `line.step.json` | `line.step` | 阶梯折线图 |
| `pie.simple.json` | `pie.simple` | 饼图 |
| `pie.doughnut.json` | `pie.doughnut` | 环形图 |
| `pie.rose.json` | `pie.rose` | 玫瑰图 |
| `mixed.linebar.json` | `mixed.linebar` | 柱状+折线混合图 |
| `radar.basic.json` | `radar.basic` | 雷达图 |
| `radar.custom.json` | `radar.custom` | 自定义雷达图 |
| `scatter.simple.json` | `scatter.simple` | 散点图 |
| `scatter.bubble.json` | `scatter.bubble` | 气泡图 |
| `funnel.simple.json` | `funnel.simple` | 漏斗图 |
| `funnel.pyramid.json` | `funnel.pyramid` | 金字塔图 |
| `gauge.simple.json` | `gauge.simple` | 仪表盘 |
| `gauge.simple180.json` | `gauge.simple180` | 半圆仪表盘 |
| `graph.simple.json` | `graph.simple` | 关系图 |
| `map.simple.json` | `map.simple` | 地图 |
| `map.scatter.json` | `map.scatter` | 地图散点 |
| `pictorial.spirits.json` | `pictorial.spirits` | 象形柱图 |

## echartslist.json 主要 key 对照

| key | 对应图表 |
|-----|---------|
| `bar` | 单系列柱状图 |
| `bar2` | dataset 模式柱状图 |
| `bar3` | 多系列柱状图 |
| `line` | 单系列折线图 |
| `line3` | 平滑曲线 |
| `line4` | 多系列折线图 |
| `line5` | 阶梯折线图 |
| `pie` | 饼图 |
| `pie1` | 环形图 |
| `pie2` | 玫瑰图 |
| `linebar` | 柱状+折线混合 |
| `map` | 地图 |
| `scatter` | 散点图 |

## 图表在 jsonStr 中的配置

图表通过**单元格占位 + chartList 配置**实现，不是绝对定位。需要两部分配合：

### 1. chartList 结构

```json
{
    "chartList": [
        {
            "row": 5,
            "col": 1,
            "colspan": 0,
            "rowspan": 0,
            "width": "500",
            "height": "350",
            "config": "ECharts配置JSON字符串",
            "url": "",
            "extData": {
                "chartType": "bar.simple",
                "dataType": "sql",
                "dataId": "数据集ID",
                "dbCode": "数据集编码",
                "axisX": "name",
                "axisY": "value",
                "series": "type",
                "xText": "",
                "yText": "",
                "apiStatus": "1"
            },
            "layer_id": "唯一层ID",
            "offsetX": 0,
            "offsetY": 0,
            "backgroud": {"enabled": false, "color": "#fff", "image": ""},
            "virtualCellRange": [[5,1],[5,2],[5,3],[6,1],[6,2],[6,3]]
        }
    ]
}
```

> **关键字段说明：**
>
> | 字段 | 类型 | 说明 |
> |------|------|------|
> | `row` / `col` | number | 图表起始位置（行号/列号），**不是 left/top 像素值** |
> | `width` / `height` | **string** | 图表宽高像素，**必须是字符串**（如 `"500"`，不是 `500`） |
> | `virtualCellRange` | array | 图表占据的所有单元格坐标 `[[row,col], ...]` |
> | `layer_id` | string | 唯一标识，对应 rows 中 cells 的 `virtual` 属性 |
> | `backgroud` | object | 图表背景（注意拼写是 `backgroud` 不是 `background`） |
> | `offsetX` / `offsetY` | number | 偏移量，通常为 0 |

### 2. rows 中的 virtual 占位

图表占据的每个单元格必须在 `rows` 中声明 `"virtual": "layer_id"`：

```json
"rows": {
    "5": {
        "cells": {
            "1": {"text": " ", "virtual": "chart_xxx"},
            "2": {"text": " ", "virtual": "chart_xxx"},
            "3": {"text": " ", "virtual": "chart_xxx"}
        }
    },
    "6": {
        "cells": {
            "1": {"text": " ", "virtual": "chart_xxx"},
            "2": {"text": " ", "virtual": "chart_xxx"},
            "3": {"text": " ", "virtual": "chart_xxx"}
        }
    }
}
```

> **注意：**
> - `virtual` 的值必须和 `chartList[].layer_id` 一致
> - `text` 设为 `" "`（一个空格），不能为空字符串
> - 图表区域的行数 × 列数 = `virtualCellRange` 的元素数量
> - 图表区域不能和列表数据行重叠

### extData 关键字段

| 字段 | 说明 |
|------|------|
| `chartType` | 图表类型（如 `bar.simple`, `line.multi`, `pie.simple`） |
| `dataType` | 数据来源：`"sql"` / `"api"` / `"json"` / `"javabean"` / `"files"`（前端文本值，与 dbType 数字不同） |
| `dataId` | 数据集ID（saveDb 返回的 id） |
| `dbCode` | 数据集编码 |
| `axisX` | X轴/分类字段名，**固定为 `name`** |
| `axisY` | Y轴/数值字段名，**固定为 `value`** |
| `series` | 系列/分组字段名，**固定为 `type`**（单系列也要传 `"type"`） |
| `apiStatus` | API 数据集是否启用（`"1"` = 启用） |
| `dataId1` | 第二数据集ID（关系图 `graph.simple` 使用） |
| `isCustomPropName` | 是否自定义字段映射（默认不填，使用 name/value/type） |

### 图表字段映射规则

> **重要：图表数据绑定使用固定的三个字段名，不是数据集的原始字段名。**

| extData 字段 | 固定值 | 含义 | 示例 |
|-------------|--------|------|------|
| `axisX` | `name` | X轴/分类 | 产品名称 |
| `axisY` | `value` | Y轴/数值 | 销售额 |
| `series` | `type` | 系列/分组（多系列） | 月份、类别 |

前端渲染时会将数据集查询结果按 `name`/`value`/`type` 进行映射：
- 单系列图表：`series` 也传 `"type"`（数据中 type 字段可为空字符串）
- 多系列图表：`series` = `"type"`，按 `type` 值分组生成多条系列

**SQL 数据集示例（需要 AS 别名映射到 name/value）：**
```sql
SELECT product_name AS name, sales_amount AS value FROM sales_table
```

**多系列 SQL 示例（加 type 字段）：**
```sql
SELECT month AS name, amount AS value, category AS type FROM sales_table
```

**JSON 数据集示例：**
```json
{"data": [
    {"name": "螺丝钉", "value": 5000, "type": ""},
    {"name": "电阻器", "value": 3200, "type": ""}
]}
```

## 使用流程

1. 根据需求确定 `chartType`
2. 读取对应的 `chartjson/{chartType}.json` 文件作为 ECharts 配置模板
3. 修改模板中的 `title.text`、`series` 等，`data` 留空（由数据集驱动）
4. 将配置 JSON 字符串化后放入 `chartList[].config`
5. 配置 `extData`：`axisX`=`name`，`axisY`=`value`，`series`=`type`
6. 数据集字段必须包含 `name` 和 `value`（SQL 用 AS 别名，JSON 直接命名）
7. 确定图表占位区域（起始 row/col，占几行几列）
8. 在 `rows` 中为每个占位 cell 添加 `"virtual": "layer_id"`
9. 构造 `virtualCellRange`（所有占位坐标数组）
10. 将 `chartList` 放入 jsonStr 顶层

## 完整示例（列表 + 柱状图）

### 数据集配置

列表和图表使用**两个独立数据集**（db_code 唯一）：

| 数据集 | dbCode | dbType | 用途 | 字段 |
|--------|--------|--------|------|------|
| 进库列表 | `stocklist` | 3(JSON) | 列表展示 | name, quantity, stock_time |
| 进库图表 | `stockchart` | 3(JSON) | 柱状图 | **name, value** |

### Python 生成图表占位的关键代码

```python
layer_id = "chart_" + gen_id()

# 图表占据 row5~row14, col1~col5
chart_row_start, chart_row_end = 5, 14
chart_col_start, chart_col_end = 1, 5

# 1. 构造 virtualCellRange
virtual_cell_range = []
for r in range(chart_row_start, chart_row_end + 1):
    for c in range(chart_col_start, chart_col_end + 1):
        virtual_cell_range.append([r, c])

# 2. 构造 rows 中的 virtual 占位 cells
chart_rows = {}
for r in range(chart_row_start, chart_row_end + 1):
    cells = {}
    for c in range(chart_col_start, chart_col_end + 1):
        cells[str(c)] = {"text": " ", "virtual": layer_id}
    chart_rows[str(r)] = {"cells": cells}

# 3. 合并到 all_rows
all_rows.update(chart_rows)

# 4. chartList 配置
chart_item = {
    "row": chart_row_start,
    "col": chart_col_start,
    "colspan": 0,
    "rowspan": 0,
    "width": "500",      # 字符串！
    "height": "350",     # 字符串！
    "config": json.dumps(chart_config, ensure_ascii=False),
    "url": "",
    "extData": {
        "chartType": "bar.simple",
        "dataType": "json",
        "dataId": chart_db_id,
        "dbCode": "stockchart",
        "axisX": "name",
        "axisY": "value",
        "series": "type",
        "xText": "",
        "yText": "",
        "apiStatus": "1"
    },
    "layer_id": layer_id,
    "offsetX": 0,
    "offsetY": 0,
    "backgroud": {"enabled": False, "color": "#fff", "image": ""},
    "virtualCellRange": virtual_cell_range
}
```
