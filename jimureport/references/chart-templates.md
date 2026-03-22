# 图表模板快速参考

积木报表内置 30+ 图表模板，文件位于 `static/jmreport/desreport_/chartjson/`。
可通过 `GET /jmreport/addChart?chartType=bar.simple` 获取模板配置。

生成图表时，从模板中取 ECharts 配置，修改 `title.text`，清空 `data`（由数据集驱动），然后放入 `chartList[].config`。

## 图表分类速查

### 柱状图 (Bar)

| chartType | 说明 | 数据集要求 |
|-----------|------|-----------|
| `bar.simple` | 单系列柱状图 | `name, value` |
| `bar.multi` | 多系列柱状图 | `name, value, type` |
| `bar.stack` | 堆叠柱状图 | `name, value, type` |
| `bar.horizontal` | 横向柱状图 | `name, value` |
| `bar.multi.horizontal` | 横向多系列 | `name, value, type` |
| `bar.stack.horizontal` | 横向堆叠 | `name, value, type` |
| `bar.negative` | 正负柱状图 | `name, value, type` |
| `bar.background` | 带背景柱状图 | `name, value` |

### 折线图 (Line)

| chartType | 说明 | 数据集要求 |
|-----------|------|-----------|
| `line.simple` | 单系列折线图 | `name, value` |
| `line.multi` | 多系列折线图 | `name, value, type` |
| `line.smooth` | 平滑曲线图 | `name, value` |
| `line.area` | 面积图 | `name, value, type` |
| `line.step` | 阶梯折线图 | `name, value` |

### 饼图 (Pie)

| chartType | 说明 | 数据集要求 |
|-----------|------|-----------|
| `pie.simple` | 饼图 | `name, value` |
| `pie.doughnut` | 环形图 | `name, value` |
| `pie.rose` | 玫瑰图（南丁格尔） | `name, value` |

### 混合图

| chartType | 说明 | 数据集要求 |
|-----------|------|-----------|
| `mixed.linebar` | 柱状+折线混合 | `name, value, type` |

### 其他图表

| chartType | 说明 | 数据集要求 |
|-----------|------|-----------|
| `gauge.simple` | 仪表盘 | `name, value` |
| `gauge.simple180` | 半圆仪表盘 | `name, value` |
| `radar.basic` | 雷达图 | 特殊（indicator） |
| `radar.custom` | 自定义雷达图 | 特殊 |
| `funnel.simple` | 漏斗图 | `name, value` |
| `funnel.pyramid` | 金字塔图 | `name, value` |
| `scatter.simple` | 散点图 | 特殊 |
| `scatter.bubble` | 气泡图 | 特殊 |
| `map.simple` | 地图 | 特殊 |
| `map.scatter` | 地图散点 | 特殊 |
| `graph.simple` | 关系图 | 特殊（需两个数据集） |
| `pictorial.spirits` | 象形柱图 | `name, value` |

## 常用图表 ECharts 配置模板

### bar.simple — 单系列柱状图

```python
{
    "title": {"show": True, "text": "标题", "left": "left", "top": "5",
              "padding": [5,20,5,20],
              "textStyle": {"fontSize": 18, "fontWeight": "bolder", "color": "#c23531"}},
    "grid": {"left": 60, "top": 60, "right": 100, "bottom": 60},
    "tooltip": {"show": True, "textStyle": {"color": "#fff", "fontSize": 18}},
    "xAxis": {"show": True, "name": "", "data": [],
              "axisLabel": {"textStyle": {"fontSize": 12, "color": "#333"}},
              "axisLine": {"lineStyle": {"color": "#333"}}},
    "yAxis": {"show": True, "name": "",
              "axisLabel": {"textStyle": {"fontSize": 12, "color": "#333"}},
              "axisLine": {"lineStyle": {"color": "#333"}}},
    "series": [{"name": "", "type": "bar", "data": [],
                "barWidth": 50, "barMinHeight": 2,
                "itemStyle": {"barBorderRadius": 0, "color": "#c43632"}}]
}
```

### bar.multi — 多系列柱状图

```python
{
    "title": {"show": True, "text": "标题", "left": "left",
              "padding": [5,20,5,20],
              "textStyle": {"fontSize": 18, "fontWeight": "bolder", "color": "#c23531"}},
    "legend": {"show": True, "data": [], "top": "top", "left": "center",
               "orient": "horizontal", "padding": [25,20,25,10],
               "textStyle": {"color": "#333", "fontSize": 12}},
    "grid": {"left": 60, "top": 60, "right": 100, "bottom": 60},
    "tooltip": {"show": True, "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "textStyle": {"color": "#fff", "fontSize": 18}},
    "xAxis": {"show": True, "type": "category", "data": [],
              "axisLabel": {"textStyle": {"fontSize": 12, "color": "#333"}},
              "axisLine": {"lineStyle": {"color": "#333"}}},
    "yAxis": {"show": True,
              "axisLabel": {"textStyle": {"fontSize": 12, "color": "#333"}},
              "axisLine": {"lineStyle": {"color": "#333"}}},
    "series": [
        {"name": "系列1", "type": "bar", "data": [], "barWidth": 0, "barMinHeight": 2,
         "label": {"show": True, "position": "top", "textStyle": {"color": "black", "fontSize": 12}},
         "itemStyle": {"barBorderRadius": 0, "color": ""}},
        {"name": "系列2", "type": "bar", "data": [], "barWidth": 0, "barMinHeight": 2,
         "label": {"show": True, "position": "top", "textStyle": {"color": "black", "fontSize": 12}},
         "itemStyle": {"barBorderRadius": 0, "color": ""}}
    ]
}
```

### line.simple — 单系列折线图

```python
{
    "title": {"show": True, "text": "标题",
              "textStyle": {"fontSize": 18, "fontWeight": "bolder", "color": "#c23531"}},
    "grid": {"left": 60, "top": 60, "right": 100, "bottom": 60},
    "xAxis": {"show": True, "data": []},
    "yAxis": {"show": True, "name": ""},
    "series": [{"name": "", "type": "line", "data": [],
                "smooth": False, "showSymbol": True, "symbolSize": 5,
                "lineStyle": {"width": 2, "color": "#c43632"}}]
}
```

### pie.simple — 饼图

```python
{
    "title": {"show": True, "text": "标题",
              "textStyle": {"fontSize": 18, "fontWeight": "bolder", "color": "#c23531"}},
    "tooltip": {"show": True, "formatter": "{a} <br/>{b} : {c}"},
    "legend": {"show": True, "data": [], "orient": "horizontal",
               "textStyle": {"color": "#333", "fontSize": 12}},
    "series": [{"name": "数据", "type": "pie",
                "radius": "55%", "minAngle": 0,
                "center": [320, 180],
                "label": {"show": True, "position": "outside"},
                "data": []}]
}
```

### pie.doughnut — 环形图

```python
{
    "title": {"show": True, "text": "标题",
              "textStyle": {"fontSize": 18, "fontWeight": "bolder", "color": "#c23531"}},
    "tooltip": {"show": True, "formatter": "{a} <br/>{b} : {c}"},
    "legend": {"show": True, "data": [], "orient": "horizontal",
               "textStyle": {"color": "#333", "fontSize": 12}},
    "series": [{"name": "数据", "type": "pie",
                "isRadius": True,
                "radius": ["45%", "55%"],    # 内外半径 → 环形
                "minAngle": 0, "roseType": "", "isRose": False,
                "center": [320, 180],
                "label": {"show": True, "position": "outside"},
                "data": []}]
}
```

### mixed.linebar — 柱线混合图

```python
{
    "chartType": "linebar",
    "title": {"show": True, "text": "标题",
              "textStyle": {"fontSize": 18, "fontWeight": "bolder", "color": "#c23531"}},
    "legend": {"data": []},
    "xAxis": {"type": "category", "data": []},
    "yAxis": [
        {"type": "value", "name": "左轴"},
        {"type": "value", "name": "右轴"}
    ],
    "series": [
        {"name": "柱状", "type": "bar", "data": []},
        {"name": "折线", "type": "line", "data": []},
        {"name": "右轴数据", "type": "bar", "yAxisIndex": 1, "data": []}
    ]
}
```

### gauge.simple — 仪表盘

```python
{
    "title": {"show": True, "text": "标题",
              "textStyle": {"fontSize": 18, "fontWeight": "bolder", "color": "#c23531"}},
    "tooltip": {"show": True, "formatter": "{b} : {c}"},
    "series": [{"name": "业务指标", "type": "gauge",
                "radius": "75%", "center": [330, 200],
                "itemStyle": {"color": "#63869E"},
                "pointer": {"show": True},
                "detail": {"formatter": "{value}%",
                           "textStyle": {"color": "rgba(0,0,0,1)", "fontSize": 25}},
                "axisLine": {"lineStyle": {
                    "color": [[0.2, "#91c7ae"], [0.8, "#63869E"], [1, "#C23531"]],
                    "width": 25}},
                "data": [{"value": 50, "name": "完成率"}]}]
}
```

### funnel.simple — 漏斗图

```python
{
    "title": {"show": True, "text": "标题",
              "textStyle": {"fontSize": 18, "fontWeight": "bolder", "color": "#c23531"}},
    "legend": {"show": True, "data": []},
    "tooltip": {"show": True, "trigger": "item", "formatter": "{b} : {c}"},
    "series": [{"name": "漏斗图", "type": "funnel",
                "left": "10%", "top": 60, "bottom": 60, "width": "80%",
                "sort": "descending", "gap": 2, "orient": "vertical",
                "label": {"show": True, "position": "inside",
                          "textStyle": {"fontSize": 16}},
                "itemStyle": {"borderColor": "#fff", "borderWidth": 1},
                "data": []}]
}
```

### radar.basic — 雷达图

```python
{
    "title": {"show": True, "text": "标题",
              "textStyle": {"fontSize": 18, "fontWeight": "bolder", "color": "#c23531"}},
    "legend": {"show": True, "data": []},
    "tooltip": {"show": True},
    "radar": [{"shape": "polygon", "center": [320, 200],
               "name": {"formatter": "【{value}】",
                        "textStyle": {"fontSize": 14, "color": "#72ACD1"}},
               "indicator": [
                   {"name": "维度1", "max": 100},
                   {"name": "维度2", "max": 100},
                   {"name": "维度3", "max": 100}
               ]}],
    "series": [{"name": "", "type": "radar",
                "data": [{"value": [80, 60, 70], "name": "系列1"}]}]
}
```

## 数据集 SQL 映射规则

图表数据集使用固定的 `name`/`value`/`type` 字段映射：

```sql
-- 单系列（bar.simple, line.simple, pie.simple 等）
SELECT product_name AS name, sales_amount AS value, '' AS type
FROM sales_table

-- 多系列（bar.multi, line.multi, mixed.linebar 等）
SELECT month AS name, amount AS value, category AS type
FROM sales_table

-- 仪表盘（gauge）
SELECT '完成率' AS name, ROUND(done*100/total) AS value, '' AS type
FROM task_summary

-- 漏斗图（funnel）
SELECT stage AS name, count AS value, '' AS type
FROM funnel_data ORDER BY count DESC
```

## 快速生成图表的 Python 代码

```python
def create_chart(chart_type, title, db_code, db_id, row_start, col_start,
                 rows=10, cols=5, width="650", height="350"):
    """快速生成图表配置"""
    layer_id = "chart_" + gen_id()

    # 根据类型选择基础配置
    base_configs = {
        "bar.simple": {
            "title": {"text": title, "left": "center", "top": "10"},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": [{"type": "category", "data": []}],
            "yAxis": [{"type": "value"}],
            "series": [{"type": "bar", "data": [], "barWidth": "40%"}]
        },
        "pie.simple": {
            "title": {"text": title, "left": "center"},
            "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
            "legend": {"bottom": "5%", "left": "center"},
            "series": [{"type": "pie", "radius": "55%", "center": ["50%", "50%"], "data": []}]
        },
        "line.simple": {
            "title": {"text": title, "left": "center"},
            "tooltip": {"trigger": "axis"},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": [{"type": "category", "data": []}],
            "yAxis": [{"type": "value"}],
            "series": [{"type": "line", "smooth": True, "data": []}]
        },
        "gauge.simple": {
            "title": {"text": title, "left": "center"},
            "series": [{"type": "gauge", "radius": "75%",
                        "detail": {"formatter": "{value}%"},
                        "data": [{"value": 0, "name": ""}]}]
        }
    }
    config = base_configs.get(chart_type, base_configs["bar.simple"])

    # virtual cells
    row_end = row_start + rows - 1
    col_end = col_start + cols - 1
    virtual_cells = [[r,c] for r in range(row_start, row_end+1) for c in range(col_start, col_end+1)]

    # rows 占位
    chart_rows = {}
    for r in range(row_start, row_end + 1):
        cells = {}
        for c in range(col_start, col_end + 1):
            cells[str(c)] = {"text": " ", "virtual": layer_id}
        chart_rows[str(r)] = {"cells": cells}

    chart_item = {
        "row": row_start, "col": col_start, "colspan": 0, "rowspan": 0,
        "width": width, "height": height,
        "config": json.dumps(config, ensure_ascii=False),
        "url": "",
        "extData": {
            "chartType": chart_type, "dataType": "sql",
            "dataId": str(db_id), "dbCode": db_code,
            "axisX": "name", "axisY": "value", "series": "type",
            "xText": "", "yText": "", "apiStatus": "1"
        },
        "layer_id": layer_id,
        "offsetX": 0, "offsetY": 0,
        "backgroud": {"enabled": False, "color": "#fff", "image": ""},
        "virtualCellRange": virtual_cells
    }

    return chart_item, chart_rows
```
