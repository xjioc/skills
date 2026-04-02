# 图表与组件配置参考

积木报表支持 4 种图层组件和 30+ 图表类型的完整配置参考。

---

## 1. 组件类型总览

| 组件 | jsonStr 字段 | 用途 |
|------|-------------|------|
| 图片 | `imgList` | 外部图片/Logo/背景图 |
| 图表 | `chartList` | ECharts 可视化图表 |
| 条形码 | `barcodeList` | CODE128/EAN 等一维码 |
| 二维码 | `qrcodeList` | QR Code 二维码 |

所有组件共享基础属性：`row`, `col`, `colspan`, `rowspan`, `width`, `height`, `layer_id`, `offsetX`, `offsetY`, `virtualCellRange`

## 2. Virtual Cell 占位规则

所有图层组件都需要在 `rows` 中声明 virtual 占位：

```python
for r in range(row_start, row_end + 1):
    cells = {}
    for c in range(col_start, col_end + 1):
        cells[str(c)] = {"text": " ", "virtual": layer_id}
    rows_data[str(r)] = {"cells": cells}
```

**注意：** `virtual` 值必须和 `layer_id` 一致；`text` 必须为 `" "`（一个空格）；组件区域不能和数据行重叠。

## 3. 图片组件 (imgList)

```python
{
    "row": 0, "col": 1, "colspan": 0, "rowspan": 0,
    "width": 315, "height": 151,       # 数字
    "src": "/jmreport/img/upload/xxx.png",
    "isBackend": False, "isBackendImg": False,
    "layer_id": "img_xxx",
    "offsetX": 0, "offsetY": 0,
    "virtualCellRange": [[0,1],[0,2],[1,1],[1,2]]
}
```

## 4. 条形码组件 (barcodeList)

```python
{
    "row": 3, "col": 0, "colspan": 0, "rowspan": 0,
    "width": 300, "height": 200,
    "layer_id": "barcode_xxx",
    "offsetX": 0, "offsetY": 0,
    "jsonString": json.dumps({
        "barcodeContent": "jmreport",   # 支持 ${dbCode.field} 动态绑定
        "format": "CODE128",            # CODE128/CODE39/EAN13/EAN8/UPC/ITF14
        "width": 2, "height": 100,
        "displayValue": False,
        "text": "jmreport",
        "fontSize": 20, "background": "#fff", "lineColor": "#000", "margin": 10
    }),
    "virtualCellRange": [[3,0],[3,1],[4,0],[4,1]]
}
```

## 5. 二维码组件 (qrcodeList)

```python
{
    "row": 5, "col": 0, "colspan": 0, "rowspan": 0,
    "width": 128, "height": 128,
    "layer_id": "qrcode_xxx",
    "offsetX": 0, "offsetY": 0,
    "jsonString": json.dumps({
        "text": "http://jimureport.com/",  # 支持 ${dbCode.field}
        "width": 128, "height": 128,
        "colorDark": "#000000", "colorLight": "#ffffff"
    }),
    "virtualCellRange": [[5,0],[5,1],[6,0],[6,1]]
}
```

## 6. 单元格内嵌组件 (displayConfig)

```python
cell = {"text": "#{dbCode.imgUrl}", "display": "img"}                          # 图片
cell = {"text": "#{dbCode.code}",   "display": "barcode", "config": "bc1"}   # 条形码
cell = {"text": "#{dbCode.url}",    "display": "qrcode",  "config": "qr1"}   # 二维码
# config 引用 displayConfig 中的配置ID
# 条形码 displayValue 默认 false（不显示文字），需传完整字段
# 详见 references/report-design.md 第7节 displayConfig
```

---

## 7. 图表组件 (chartList)

### 图表模板文件

`src/main/resources/static/jmreport/desreport_/chartjson/`

可通过 `GET /jmreport/addChart?chartType=bar.simple` 获取模板配置。

### 图表分类速查

#### 柱状图 (Bar)

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

#### 折线图 (Line)

| chartType | 说明 | 数据集要求 |
|-----------|------|-----------|
| `line.simple` | 单系列折线图 | `name, value` |
| `line.multi` | 多系列折线图 | `name, value, type` |
| `line.smooth` | 平滑曲线图 | `name, value` |
| `line.area` | 面积图 | `name, value, type` |
| `line.step` | 阶梯折线图 | `name, value` |

#### 饼图 (Pie)

| chartType | 说明 | 数据集要求 |
|-----------|------|-----------|
| `pie.simple` | 饼图 | `name, value` |
| `pie.doughnut` | 环形图 | `name, value` |
| `pie.rose` | 玫瑰图 | `name, value` |

#### 其他图表

| chartType | 说明 | 数据集要求 |
|-----------|------|-----------|
| `mixed.linebar` | 柱线混合图 | `name, value, type` |
| `gauge.simple` | 仪表盘 | `name, value` |
| `gauge.simple180` | 半圆仪表盘 | `name, value` |
| `radar.basic` | 雷达图 | 特殊（indicator） |
| `funnel.simple` | 漏斗图 | `name, value` |
| `funnel.pyramid` | 金字塔图 | `name, value` |
| `scatter.simple` | 散点图 | 特殊 |
| `map.simple` | 地图 | 特殊 |
| `map.scatter` | 地图散点 | 特殊 |
| `graph.simple` | 关系图 | 特殊（需两个数据集） |
| `pictorial.spirits` | 象形柱图 | `name, value` |

### chartList 结构

```python
{
    "row": 0, "col": 0,
    "colspan": 7,            # col_end - col + 1，不是 0
    "rowspan": 14,           # row_end - row + 1，不是 0
    "width": 650,            # int，不是字符串
    "height": 350,           # int，不是字符串
    "config": json.dumps(echarts_option),  # ECharts 配置 JSON 字符串
    "url": "",
    "extData": {             # dict 对象，不是 JSON 字符串（浏览器实测 2026-04-02）
        "chartId": "chart_xxx",      # 必须等于 layer_id！
        "id": "chart_xxx",           # 必须等于 layer_id！
        "chartType": "bar.simple",   # 图表类型
        # ── 数据集绑定 ──────────────────────────────
        "dataType": "api",           # "sql"/"api"/"json"/"javabean"
        "apiStatus": "1",
        "dataId": "数据集ID",
        "dataId1": "",               # 第二数据集（graph.simple 双数据集用）
        "dbCode": "数据集编码",
        "axisX": "name",             # X轴字段（标准模式，isCustomPropName=False 时生效）
        "axisY": "value",            # Y轴字段（标准模式）
        "series": "type",            # 系列字段（单系列/自定义属性模式传 ""）
        # ── 自定义属性模式（UI 上"自定义属性"开关）────────────
        # isCustomPropName=True 时，xText/yText 优先生效（对应 UI 分类属性/值属性下拉）
        # isCustomPropName=False 时，xText/yText 置空，用 axisX/axisY
        "isCustomPropName": False,   # True=启用自定义属性
        "xText": "",                 # 分类属性（UI: 分类属性）启用自定义时填字段名
        "yText": "",                 # 值属性（UI: 值属性）启用自定义时填字段名
        # ── 联动/钻取 ────────────────────────────────
        "linkIds": "",
        "source": "", "target": "",  # graph 图用
        # ── 定时刷新（浏览器实测 2026-04-02）────────────────
        # 禁用：isTiming=""  intervalTime=""
        # 启用：isTiming=True（布尔 true）  intervalTime="5"（字符串秒数）
        "isTiming": "",
        "intervalTime": "",
        # ── 其他 ────────────────────────────────────
        "isCustomPropName": False,
    },
    "layer_id": "chart_xxx",
    "offsetX": 0, "offsetY": 0,
    "backgroud": {"enabled": False, "color": "#fff", "image": ""},  # 注意拼写 backgroud
    "virtualCellRange": [[0,0],[0,1],...]   # 只标第一行
}
```

> **关键：** `width`/`height` 是 int；`backgroud` 拼写有误但必须这样（不是 background）；`colspan`/`rowspan` 是实际跨度

### 图表字段映射规则

> **重要：图表数据绑定使用固定的三个字段名 name/value/type，SQL 需要 AS 别名。**

```sql
-- 单系列
SELECT product_name AS name, sales_amount AS value, '' AS type FROM sales_table

-- 多系列
SELECT month AS name, amount AS value, category AS type FROM sales_table

-- 仪表盘
SELECT '完成率' AS name, ROUND(done*100/total) AS value, '' AS type FROM task_summary
```

## 8. 常用 ECharts 配置模板

> 完整默认值可通过 `GET /jmreport/addChart?chartType=<type>` 获取原始配置。

### bar.simple — 单系列柱状图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=bar.simple`（2026-04-02 实测）

```python
{
    "title": {
        "show": True, "text": "某站点用户访问来源",
        "top": "5", "left": "left",
        "padding": [5, 20, 5, 20],
        "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}
    },
    "xAxis": {
        "show": True, "name": "服饰",
        "data": ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"],
        "axisLabel": {"rotate": 0, "interval": "auto", "textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "yAxis": {
        "show": True, "name": "销量",
        "axisLabel": {"textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "series": [{
        "type": "bar", "name": "销量",
        "data": [5, 20, 36, 10, 10, 20],
        "barWidth": 50, "barMinHeight": 2,
        "itemStyle": {"color": "#c43632", "barBorderRadius": 0},
        "label": {"show": True, "position": "top",
                  "textStyle": {"color": "black", "fontSize": 16, "fontWeight": "bolder"}}
    }],
    "grid": {"top": 60, "left": 60, "bottom": 60, "right": 100},
    "tooltip": {"show": True, "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

**使用时替换：** `title.text`、`xAxis.name`/`data`、`yAxis.name`、`series[].name`/`data`

### bar.simple — 简化最小配置（实际使用）

```python
{
    "title": {"show": True, "text": "标题", "left": "left", "top": "5",
              "textStyle": {"fontSize": 18, "fontWeight": "bolder", "color": "#c23531"}},
    "grid": {"left": 60, "top": 60, "right": 100, "bottom": 60},
    "tooltip": {"show": True, "textStyle": {"color": "#fff", "fontSize": 18}},
    "xAxis": {"show": True, "data": []},
    "yAxis": {"show": True},
    "series": [{"name": "", "type": "bar", "data": [], "barWidth": 50,
                "itemStyle": {"barBorderRadius": 0, "color": "#c43632"}}]
}
```

### bar.background — 带背景柱状图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=bar.background`（2026-04-02 实测）
> 与 bar.simple 区别：series 增加 `showBackground: true` + `backgroundStyle`；tooltip 增加 `formatter`

```python
{
    "title": {"show": True, "text": "某站点用户访问来源", "top": "5", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "xAxis": {
        "show": True, "name": "服饰",
        "data": ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"],
        "axisLabel": {"rotate": 0, "interval": "auto", "textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "yAxis": {
        "show": True, "name": "销量",
        "axisLabel": {"textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "series": [{
        "type": "bar", "name": "销量",
        "data": [5, 20, 36, 10, 10, 20],
        "barWidth": 50, "barMinHeight": 2,
        "showBackground": True,                              # 关键：开启背景
        "backgroundStyle": {"color": "rgba(220, 220, 220, 0.8)"},
        "itemStyle": {"color": "#c43632", "barBorderRadius": 0},
        "label": {"show": True, "position": "top",
                  "textStyle": {"color": "black", "fontSize": 16, "fontWeight": "bolder"}}
    }],
    "grid": {"top": 60, "left": 60, "bottom": 60, "right": 100},
    "tooltip": {"show": True, "formatter": "{b} : {c}",    # 单值格式
                "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

---

### bar.multi — 多数据对比柱状图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=bar.multi`（2026-04-02 实测）
> 与 bar.simple 区别：多个 series、增加 `legend`、tooltip 用 axis 触发

```python
{
    "title": {"show": True, "text": "某站点用户访问来源", "top": "5", "left": "left",  # 注意：无 top 字段
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "legend": {
        "show": True, "top": "top", "left": "center", "orient": "horizontal",
        "data": ["直接访问", "邮件营销", "联盟广告"],
        "padding": [25, 20, 25, 10],
        "textStyle": {"color": "#333", "fontSize": 12}
    },
    "xAxis": {
        "show": True, "type": "category",
        "data": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        "axisLabel": {"rotate": 0, "interval": "auto", "textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "yAxis": {
        "show": True,
        # 注意：API 返回 "type " 有尾部空格，实际使用写 "type": "value"
        "axisLabel": {"textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "series": [
        {"type": "bar", "name": "直接访问", "data": [320, 332, 301, 334, 390, 330, 320],
         "barWidth": 0, "barMinHeight": 2,
         "itemStyle": {"color": "", "barBorderRadius": 0},
         "label": {"show": True, "position": "top", "textStyle": {"color": "black", "fontSize": 12, "fontWeight": "bolder"}}},
        {"type": "bar", "name": "邮件营销", "data": [120, 132, 101, 134, 90, 230, 210],
         "barWidth": 0, "barMinHeight": 2,
         "itemStyle": {"color": "", "barBorderRadius": 0},
         "label": {"show": True, "position": "top", "textStyle": {"color": "black", "fontSize": 12, "fontWeight": "bolder"}}},
        {"type": "bar", "name": "联盟广告", "data": [220, 182, 191, 234, 290, 330, 310],
         "barWidth": 0, "barMinHeight": 2,
         "itemStyle": {"color": "", "barBorderRadius": 0},
         "label": {"show": True, "position": "top", "textStyle": {"color": "black", "fontSize": 12, "fontWeight": "bolder"}}}
    ],
    "grid": {"top": 60, "left": 60, "bottom": 60, "right": 100},
    "tooltip": {"show": True, "trigger": "axis", "axisPointer": {"type": "shadow"},
                "appendToBody": True, "confine": True,
                "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

---

### bar.stack — 堆叠柱状图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=bar.stack`（2026-04-02 实测）
> 关键：series 中用 `stack` 字段分组，同 stack 值的系列堆叠在一起

```python
{
    "title": {"show": True, "text": "某站点用户访问来源", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "legend": {
        "show": True, "top": "top", "left": "center", "orient": "horizontal",
        "data": ["直接访问", "邮件营销", "联盟广告", "百度", "谷歌", "必应"],
        "padding": [25, 20, 25, 10],
        "textStyle": {"color": "#333", "fontSize": 12}
    },
    "xAxis": {
        "show": True, "type": "category",
        "data": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        "axisLabel": {"rotate": 0, "interval": "auto", "textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "yAxis": {
        "show": True,
        "axisLabel": {"textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "series": [
        # stack="" → 不参与堆叠（独立柱）；stack="总量" → 与同名 stack 堆叠
        {"type": "bar", "name": "直接访问", "stack": "",     "data": [320, 332, 301, 334, 390, 330, 320], "barWidth": 15, "barMinHeight": 2, "itemStyle": {"color": "", "barBorderRadius": 0}},
        {"type": "bar", "name": "邮件营销", "stack": "总量", "data": [120, 132, 101, 134, 90,  230, 210], "barWidth": 15, "barMinHeight": 2, "itemStyle": {"color": "", "barBorderRadius": 0}},
        {"type": "bar", "name": "联盟广告", "stack": "总量", "data": [220, 182, 191, 234, 290, 330, 310], "barWidth": 15, "barMinHeight": 2, "itemStyle": {"color": "", "barBorderRadius": 0}},
        {"type": "bar", "name": "百度",     "stack": "搜索引擎", "data": [620, 732, 701, 734, 1090, 1130, 1120], "barWidth": 15, "barMinHeight": 2, "itemStyle": {"color": "", "barBorderRadius": 0}},
        {"type": "bar", "name": "谷歌",     "stack": "搜索引擎", "data": [120, 132, 101, 134, 290, 230, 220],   "barWidth": 15, "barMinHeight": 2, "itemStyle": {"color": "", "barBorderRadius": 0}},
        {"type": "bar", "name": "必应",     "stack": "搜索引擎", "data": [60,  72,  71,  74,  190, 130, 110],   "barWidth": 15, "barMinHeight": 2, "itemStyle": {"color": "", "barBorderRadius": 0}},
    ],
    "grid": {"top": 60, "left": 60, "bottom": 60, "right": 100},
    "tooltip": {"show": True, "trigger": "axis", "axisPointer": {"type": "shadow"},
                "appendToBody": True, "confine": True,
                "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

---

### bar.negative — 正负条形图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=bar.negative`（2026-04-02 实测）
> **注意：轴方向与普通柱图相反** — yAxis 放分类数据，xAxis 放数值（横向图）；负值用负数表示

```python
{
    "title": {"show": True, "text": "利润统计", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "legend": {
        "show": True, "top": "top", "left": "center", "orient": "horizontal",
        "data": ["利润", "支出", "收入"],
        "padding": [25, 20, 25, 10],
        "textStyle": {"color": "#333", "fontSize": 12}
    },
    # 横向图：yAxis 放分类，xAxis 放数值
    "yAxis": {
        "show": True, "type": "category",
        "data": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        "axisLabel": {"rotate": 0, "interval": "auto", "textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "xAxis": {
        "show": True,   # 注意：API返回 "type ": "value"（有空格bug），实际写 "type": "value"
        "splitLine": {"show": True, "lineStyle": {"color": "red", "width": 1, "type": "solid"}},
        "axisLabel": {"textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}}
    },
    "series": [
        {"type": "bar", "name": "利润", "stack": "利润", "data": [200, 170, 240, 244, 200, 220, 210],
         "barWidth": 25, "barMinHeight": 2,
         "itemStyle": {"color": "", "barBorderRadius": 0},
         "label": {"show": True, "position": "inside"}},
        {"type": "bar", "name": "收入", "stack": "总量", "data": [320, 302, 341, 374, 390, 450, 420],
         "barWidth": 25, "barMinHeight": 2,
         "itemStyle": {"color": "", "barBorderRadius": 0},
         "label": {"show": True}},
        {"type": "bar", "name": "支出", "stack": "总量", "data": [-120, -132, -101, -134, -190, -230, -210],
         "barWidth": 5, "barMinHeight": 2,
         "itemStyle": {"color": "", "barBorderRadius": 0},
         "label": {"show": True, "position": "left"}},   # 负值 label 在左侧
    ],
    "grid": {"top": 60, "left": 60, "bottom": 60, "right": 100},
    "tooltip": {"show": True, "trigger": "axis", "axisPointer": {"type": "shadow"},
                "appendToBody": True, "confine": True,
                "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

---

### bar.horizontal — 横向柱状图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=bar.horizontal`（2026-04-02 实测）
> 单系列横向：yAxis 放分类，xAxis 放数值；label position 为 `"right"`

```python
{
    "title": {"show": True, "text": "某站点用户访问来源", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "yAxis": {
        "show": True, "name": "星期", "type": "category",
        "data": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        "axisLabel": {"rotate": 0, "interval": "auto", "textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "xAxis": {
        "show": True, "name": "访问量",  # 注意：API返回 "type ": "value"（空格bug），实际用 "type": "value"
        "axisLabel": {"textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "series": [{
        "type": "bar", "name": "直接访问",
        "data": [320, 332, 301, 334, 390, 400, 470],
        "barWidth": 0, "barMinHeight": 2,
        "itemStyle": {"color": "", "barBorderRadius": 0},
        "label": {"show": True, "position": "right",    # 横向图 label 在右侧
                  "textStyle": {"color": "black", "fontSize": 16, "fontWeight": "bolder"}}
    }],
    "grid": {"top": 60, "left": 60, "bottom": 60, "right": 100},
    "tooltip": {"show": True, "trigger": "axis", "axisPointer": {"type": "shadow"},
                "appendToBody": True, "confine": True,
                "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

---

### bar.multi.horizontal — 多数据横向柱状图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=bar.multi.horizontal`（2026-04-02 实测）
> bar.horizontal 的多系列版本，无 stack

```python
{
    "title": {"show": True, "text": "某站点用户访问来源", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "legend": {
        "show": True, "top": "top", "left": "center", "orient": "horizontal",
        "data": ["直接访问", "邮件营销", "联盟广告"],
        "padding": [25, 20, 25, 10],
        "textStyle": {"color": "#333", "fontSize": 12}
    },
    "yAxis": {
        "show": True, "type": "category",
        "data": ["周一", "周二", "周三", "周四", "周五"],
        "axisLabel": {"rotate": 0, "interval": "auto", "textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "xAxis": {
        "show": True,   # "type ": "value" API bug，实际用 "type": "value"
        "axisLabel": {"textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "series": [
        {"type": "bar", "name": "直接访问", "data": [320, 332, 301, 334, 390],
         "barWidth": 0, "barMinHeight": 2, "itemStyle": {"color": "", "barBorderRadius": 0},
         "label": {"show": True, "position": "right", "textStyle": {"color": "black", "fontSize": 16, "fontWeight": "bolder"}}},
        {"type": "bar", "name": "邮件营销", "data": [120, 132, 101, 134, 90],
         "barWidth": 0, "barMinHeight": 2, "itemStyle": {"color": "", "barBorderRadius": 0},
         "label": {"show": True, "position": "right", "textStyle": {"color": "black", "fontSize": 16, "fontWeight": "bolder"}}},
        {"type": "bar", "name": "联盟广告", "data": [220, 182, 191, 234, 290],
         "barWidth": 0, "barMinHeight": 2, "itemStyle": {"color": "", "barBorderRadius": 0},
         "label": {"show": True, "position": "right", "textStyle": {"color": "black", "fontSize": 16, "fontWeight": "bolder"}}},
    ],
    "grid": {"top": 60, "left": 60, "bottom": 60, "right": 100},
    "tooltip": {"show": True, "trigger": "axis", "axisPointer": {"type": "shadow"},
                "appendToBody": True, "confine": True,
                "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

---

### bar.stack.horizontal — 堆叠横向柱状图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=bar.stack.horizontal`（2026-04-02 实测）
> bar.stack 的横向版本：yAxis 放分类，xAxis 放数值，所有系列共用同一 stack

```python
{
    "title": {"show": True, "text": "某站点用户访问来源", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "legend": {
        "show": True, "top": "top", "left": "center", "orient": "horizontal",
        "data": ["直接访问", "邮件营销", "联盟广告"],
        "padding": [25, 20, 25, 10],
        "textStyle": {"color": "#333", "fontSize": 12}
    },
    "yAxis": {
        "show": True, "type": "category",
        "data": ["周一", "周二", "周三", "周四", "周五"],
        "axisLabel": {"rotate": 0, "interval": "auto", "textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "xAxis": {
        "show": True,   # "type ": "value" API bug，实际用 "type": "value"
        "axisLabel": {"textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "series": [
        {"type": "bar", "name": "直接访问", "stack": "总量", "data": [320, 332, 301, 334, 390],
         "barWidth": 15, "barMinHeight": 2, "itemStyle": {"color": "", "barBorderRadius": 0}},
        {"type": "bar", "name": "邮件营销", "stack": "总量", "data": [120, 132, 101, 134, 90],
         "barWidth": 15, "barMinHeight": 2, "itemStyle": {"color": "", "barBorderRadius": 0}},
        {"type": "bar", "name": "联盟广告", "stack": "总量", "data": [220, 182, 191, 234, 290],
         "barWidth": 15, "barMinHeight": 2, "itemStyle": {"color": "", "barBorderRadius": 0}},
    ],
    "grid": {"top": 60, "left": 60, "bottom": 60, "right": 100},
    "tooltip": {"show": True, "trigger": "axis", "axisPointer": {"type": "shadow"},
                "appendToBody": True, "confine": True,
                "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

> **横向图通用规律：** yAxis 设 `type: "category"` + `data`；xAxis 设 `type: "value"`（API 返回有 `"type "` 尾部空格 bug，实际写时不带空格）；label `position` 用 `"right"` 而非 `"top"`

---

### line.simple — 普通折线图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=line.simple`（2026-04-02 实测）

```python
{
    "title": {"show": True, "text": "某站点用户访问来源", "left": "left",
              "padding": [5, 20, 5, 10],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "xAxis": {
        "show": True, "name": "服饰",
        "data": ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"],
        "axisLabel": {"rotate": 0, "interval": "auto", "textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "yAxis": {
        "show": True, "name": "销量",
        "axisLabel": {"textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "series": [{
        "type": "line", "name": "销量",
        "data": [5, 20, 36, 10, 10, 20],
        "smooth": False,           # 折线图控制平滑
        "step": False,             # 阶梯折线
        "isArea": False,           # 是否面积图
        "areaStyle": {"color": "rgba(220,38,38,0)", "opacity": 1},  # 透明 = 无填充
        "showSymbol": True, "symbolSize": 5,
        "lineStyle": {"width": 2},
        "itemStyle": {"color": "#c43632"},
        "label": {"show": True, "position": "top",
                  "textStyle": {"color": "black", "fontSize": 16, "fontWeight": "bolder"}}
    }],
    "grid": {"top": 60, "left": 60, "bottom": 60, "right": 100},
    "tooltip": {"show": True, "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

> **折线图四种变体对比（单系列）：**
>
> | chartType | `smooth` | `step` | `isArea` | `areaStyle.color` |
> |-----------|----------|--------|----------|-------------------|
> | `line.simple` | `False` | `False` | `False` | `rgba(220,38,38,0)`（透明） |
> | `line.smooth` | `True`  | `False` | `False` | `rgba(220,38,38,0)`（透明） |
> | `line.area`   | `False` | `False` | `True`  | `"#c43632"`（不透明，显示面积色） |
> | `line.step`   | `False` | `True`  | `False` | `rgba(220,38,38,0)`（透明） |

---

### line.area — 面积折线图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=line.area`（2026-04-02 实测）
> 与 line.simple 区别：`isArea: true`，`areaStyle.color` 改为实色（不透明）

```python
# 结构同 line.simple，仅 series 中以下字段不同：
"isArea": True,
"areaStyle": {"color": "#c43632", "opacity": 1},   # 实色填充
"smooth": False,
"step": False,
# tooltip 增加 formatter
"tooltip": {"show": True, "formatter": "{b} : {c}", "textStyle": {"color": "#fff", "fontSize": 18}}
```

---

### line.smooth — 平滑曲线折线图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=line.smooth`（2026-04-02 实测）
> 与 line.simple 区别：`smooth: true`

```python
# 结构同 line.simple，仅 series 中以下字段不同：
"smooth": True,    # 平滑曲线
"isArea": False,
"areaStyle": {"color": "rgba(220,38,38,0)", "opacity": 1},
"step": False,
# tooltip 增加 formatter
"tooltip": {"show": True, "formatter": "{b} : {c}", "textStyle": {"color": "#fff", "fontSize": 18}}
```

---

### line.step — 阶梯折线图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=line.step`（2026-04-02 实测）
> 与 line.simple 区别：`step: true`

```python
# 结构同 line.simple，仅 series 中以下字段不同：
"step": True,      # 阶梯折线
"smooth": False,
"isArea": False,
"areaStyle": {"color": "rgba(220,38,38,0)", "opacity": 1},
# tooltip 增加 appendToBody/confine
"tooltip": {"show": True, "formatter": "{b} : {c}",
            "appendToBody": True, "confine": True,
            "textStyle": {"color": "#fff", "fontSize": 18}}
```

---

### line.multi — 多数据对比折线图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=line.multi`（2026-04-02 实测）
> 多系列：增加 `legend`；xAxis 增加 `boundaryGap: true`，`type: "category"`；yAxis 有 `type: "value"`（无空格bug）

```python
{
    "title": {"show": True, "text": "某楼盘销售情况", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "legend": {
        "show": True, "top": "top", "left": "center", "orient": "horizontal",
        "data": ["意向", "预购", "成交"],
        "padding": [25, 20, 25, 10],
        "textStyle": {"color": "#333", "fontSize": 12}
    },
    "xAxis": {
        "show": True, "type": "category",
        "boundaryGap": True,                    # 多系列折线图特有
        "data": ["周一", "周二", "周三", "周四", "周五"],
        "axisLabel": {"rotate": 0, "interval": "auto", "textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "yAxis": {
        "show": True, "type": "value",          # 注意：此处无空格bug
        "axisLabel": {"textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "series": [
        {"type": "line", "name": "预购", "data": [30, 182, 434, 791, 390],
         "smooth": False, "step": False, "showSymbol": True, "symbolSize": 5,
         "lineStyle": {"width": 2}, "itemStyle": {"color": ""},
         "label": {"show": True, "position": "top", "textStyle": {"color": "black", "fontSize": 16, "fontWeight": "bolder"}}},
        {"type": "line", "name": "成交", "data": [10, 12, 21, 54, 260],
         "smooth": False, "step": False, "showSymbol": True, "symbolSize": 5,
         "lineStyle": {"width": 2}, "itemStyle": {"color": ""},
         "label": {"show": True, "position": "top", "textStyle": {"color": "black", "fontSize": 16, "fontWeight": "bolder"}}},
        {"type": "line", "name": "意向", "data": [1320, 1132, 601, 234, 120],
         "smooth": False, "step": False, "showSymbol": True, "symbolSize": 5,
         "lineStyle": {"width": 2}, "itemStyle": {"color": ""},
         "label": {"show": True, "position": "top", "textStyle": {"color": "black", "fontSize": 16, "fontWeight": "bolder"}}},
    ],
    "grid": {"top": 60, "left": 60, "bottom": 60, "right": 100},
    "tooltip": {"show": True, "trigger": "axis",
                "appendToBody": True, "confine": True,
                "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

### pie.simple — 普通饼图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=pie.simple`（2026-04-02 实测）
> **注意：饼图 data 格式与柱线图不同** — 每项是 `{name, value, itemStyle}` 对象，不是平铺数组

```python
{
    "title": {"show": True, "text": "某站点用户访问来源", "left": "left",
              "padding": [5, 20, 5, 10],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "legend": {
        "show": True, "top": "top", "left": "center", "orient": "horizontal",
        "data": ["视频广告", "联盟广告", "邮件营销", "直接访问", "搜索引擎"],
        "padding": [25, 20, 25, 10],
        "textStyle": {"color": "#333", "fontSize": 12}
    },
    "series": [{
        "type": "pie", "name": "访问来源",
        "radius": "55%",           # 单值 = 实心饼图
        "center": [320, 180],
        "isRose": False,           # 是否玫瑰图
        "isRadius": False,         # 是否环形图
        "roseType": "",            # 玫瑰图类型："radius"/"area"/""
        "minAngle": 0,
        "autoSort": False,
        "notCount": False,
        # 饼图 data 每项是对象，不是平铺数组！
        "data": [
            {"name": "视频广告", "value": 1170, "itemStyle": {"color": None}},
            {"name": "联盟广告", "value": 417,  "itemStyle": {"color": None}},
            {"name": "邮件营销", "value": 335,  "itemStyle": {"color": None}},
            {"name": "直接访问", "value": 410,  "itemStyle": {"color": None}},
            {"name": "搜索引擎", "value": 800,  "itemStyle": {"color": None}},
        ],
        "label": {"show": True, "position": "outside",
                  "textStyle": {"fontSize": 16, "fontWeight": "bolder"}}
    }],
    "tooltip": {"show": True, "formatter": "{a} <br/>{b} : {c}",
                "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

> **三种饼图变体对比：**
>
> | chartType | `isRose` | `isRadius` | `roseType` | `radius` |
> |-----------|----------|------------|------------|----------|
> | `pie.simple`   | `False` | `False` | `""`       | `"55%"`（字符串） |
> | `pie.doughnut` | `False` | `True`  | `""`       | `["45%","55%"]`（数组，内外半径） |
> | `pie.rose`     | `True`  | `False` | `"radius"` | `"55%"`（字符串） |

---

### pie.doughnut — 环形饼图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=pie.doughnut`（2026-04-02 实测）
> 与 pie.simple 区别：`isRadius: true`，`radius` 改为数组 `["45%","55%"]`

```python
# 结构同 pie.simple，series 中以下字段不同：
"isRadius": True,
"radius": ["45%", "55%"],    # 数组 → 内径45% 外径55% = 环形
"isRose": False,
"roseType": "",
```

---

### pie.rose — 南丁格尔玫瑰饼图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=pie.rose`（2026-04-02 实测）
> 与 pie.simple 区别：`isRose: true`，`roseType: "radius"`

```python
# 结构同 pie.simple，series 中以下字段不同：
"isRose": True,
"roseType": "radius",        # "radius"=半径玫瑰图，"area"=面积玫瑰图
"isRadius": False,
"radius": "55%",
```

### mixed.linebar — 折柱混合图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=mixed.linebar`（2026-04-02 实测）
> **注意：** `yAxis` 是**数组**（双 Y 轴）；根级有 `chartType: "linebar"`；右轴系列需设 `yAxisIndex: 1`；tooltip `axisPointer.type: "cross"`

```python
{
    "chartType": "linebar",            # 根级标识，折柱混合图特有
    "title": {"show": True, "text": "某站点用户访问来源", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "legend": {
        "show": True, "top": "top", "left": "center", "orient": "horizontal",
        "data": ["蒸发量", "降水量", "平均温度"],
        "padding": [25, 20, 25, 10],
        "textStyle": {"color": "#333", "fontSize": 12}
    },
    "xAxis": {
        "show": True, "type": "category",
        "data": ["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"],
        "axisPointer": {"type": "shadow"},   # 折柱混合图 xAxis 特有
        "axisLabel": {"rotate": 0, "interval": "auto", "textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    # 双 Y 轴：yAxis 是数组，索引0=左轴，索引1=右轴
    "yAxis": [
        {"show": True, "name": "水量", "type": "value",
         "axisLabel": {"textStyle": {"color": "#333", "fontSize": 12}},
         "axisLine": {"lineStyle": {"color": "#333"}},
         "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}},
        {"show": True, "name": "温度", "type": "value",
         "axisLabel": {"textStyle": {"color": "#333", "fontSize": 12}},
         "axisLine": {"lineStyle": {"color": "#333"}},
         "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}},
    ],
    "series": [
        # 左轴折线（无 yAxisIndex 默认用索引0）
        {"type": "line", "name": "蒸发量", "barWidth": 15, "barMinHeight": 2,
         "data": [2.0,4.9,7.0,23.2,25.6,76.7,135.6,162.2,32.6,20.0,6.4,3.3],
         "itemStyle": {"color": "", "barBorderRadius": 0},
         "label": {"show": True, "position": "top", "textStyle": {"color": "black", "fontSize": 16, "fontWeight": "bolder"}}},
        # 左轴柱形
        {"type": "bar",  "name": "降水量", "barWidth": 15, "barMinHeight": 2,
         "data": [2.6,5.9,9.0,26.4,28.7,70.7,175.6,182.2,48.7,18.8,6.0,2.3],
         "itemStyle": {"color": "", "barBorderRadius": 0},
         "label": {"show": True, "position": "top", "textStyle": {"color": "black", "fontSize": 16, "fontWeight": "bolder"}}},
        # 右轴系列：yAxisIndex: 1 绑定右轴
        {"type": "bar",  "name": "平均温度", "yAxisIndex": 1,
         "data": [2.0,2.2,3.3,4.5,6.3,10.2,20.3,23.4,23.0,16.5,12.0,6.2],
         "showSymbol": True, "symbolSize": 5, "lineStyle": {"width": 2},
         "smooth": False, "step": False,
         "itemStyle": {"color": ""},
         "label": {"show": True, "position": "top", "textStyle": {"color": "", "fontSize": 16, "fontWeight": "bolder"}}},
    ],
    "grid": {"top": 60, "left": 60, "bottom": 60, "right": 100},
    "tooltip": {
        "show": True, "trigger": "axis",
        "axisPointer": {"type": "cross", "crossStyle": {"color": "#999"}},  # 十字准星
        "appendToBody": True, "confine": True,
        "textStyle": {"color": "#fff", "fontSize": 18}
    }
}
```

### gauge.simple — 360° 仪表盘（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=gauge.simple`（2026-04-02 实测）
> **注意：** 仪表盘无 xAxis/yAxis；`data` 单项 `{name, value}`；`axisLine.lineStyle.color` 为分段着色数组

```python
{
    "title": {"show": True, "text": "某站点用户访问来源", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "series": [{
        "type": "gauge",
        "name": "业务指标",
        "center": [330, 200],
        "radius": "75%",               # 360°仪表盘有 radius；180°无此字段
        "pointer": {"show": True},
        # data 单项：name=指标名（显示在表盘下方），value=当前值
        "data": [{"name": "完成率", "value": 50}],
        "itemStyle": {"color": "#63869E"},
        # axisLine.lineStyle.color：分段着色，每项 [比例阈值, 颜色]，比例 0~1
        "axisLine": {
            "lineStyle": {
                "width": 25,
                "color": [[0.2, "#91c7ae"], [0.8, "#63869E"], [1, "#C23531"]]
            }
        },
        "axisTick":  {"length": 10,  "lineStyle": {"color": "#fff"}},
        "splitLine": {"length": 30,  "lineStyle": {"color": "#ffffff", "width": 3}},
        "axisLabel": {"show": True, "color": "auto", "textStyle": {"fontSize": 10}},
        "title":  {"show": True, "textStyle": {"color": "#000000", "fontSize": 20,
                                               "shadowBlur": 10, "shadowColor": "#000"}},
        "detail": {"formatter": "{value}%",
                   "textStyle": {"color": "rgba(0,0,0,1)", "fontSize": 25}},
    }],
    "tooltip": {"show": True, "formatter": "{b} : {c}",
                "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

---

### gauge.simple180 — 180° 仪表盘（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=gauge.simple180`（2026-04-02 实测）
> 与 gauge.simple 区别：增加 `startAngle: 190` / `endAngle: -10`，无 `radius` 字段

```python
{
    "title": {"show": True, "text": "某站点用户访问来源", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "series": [{
        "type": "gauge",
        "name": "业务指标",
        "center": [330, 200],
        "startAngle": 190,             # 180°仪表盘特有：起始角度
        "endAngle": -10,               # 180°仪表盘特有：结束角度
        # 注意：无 radius 字段（gauge.simple 有）
        "pointer": {"show": True},
        "data": [{"name": "成绩", "value": 60}],
        "itemStyle": {"color": "#63869E"},
        "axisLine": {
            "lineStyle": {
                "width": 25,
                "color": [[0.2, "#91c7ae"], [0.8, "#63869E"], [1, "#C23531"]]
            }
        },
        "axisTick":  {"length": 10,  "lineStyle": {"color": "#fff"}},
        "splitLine": {"length": 30,  "lineStyle": {"color": "#fff", "width": 3}},
        "axisLabel": {"show": True, "color": "auto", "textStyle": {"fontSize": 10}},
        "title":  {"show": True, "textStyle": {"color": "#000", "fontSize": 20,
                                               "shadowBlur": 10, "shadowColor": "#000"}},
        "detail": {"formatter": "{value}%",
                   "textStyle": {"color": "rgba(0,0,0,1)", "fontSize": 25}},
    }],
    "tooltip": {"show": True, "formatter": "{b} : {c}",
                "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

> **仪表盘两种变体对比：**
>
> | chartType | `startAngle` | `endAngle` | `radius` |
> |-----------|-------------|------------|----------|
> | `gauge.simple`    | 无（默认225°） | 无（默认-45°） | `"75%"` |
> | `gauge.simple180` | `190`          | `-10`          | 无       |
>
> **仪表盘通用注意：** `axisLine.lineStyle.color` 是分段数组 `[[阈值比例, 颜色], ...]`，比例为 0~1，最后一项必须为 `1`；`extData.series` 仍需设为 `""` 空字符串（仪表盘无系列维度）。

### scatter.simple — 普通散点图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=scatter.simple`（2026-04-02 实测）
> **注意：** 散点图 data 每项是 `[x, y]` 二元数组，不是对象；无 legend

```python
{
    "title": {"show": True, "text": "散点图", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "xAxis": {
        "show": True, "name": "",
        "axisLabel": {"rotate": 0, "interval": "auto", "textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "yAxis": {
        "show": True, "name": "",
        "axisLabel": {"textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "series": [{
        "type": "scatter",
        "symbolSize": 20,
        # data 每项是 [x, y] 二元数组，不是 {name, value} 对象！
        "data": [[10.0,8.04],[8.0,6.95],[13.0,7.58],[9.0,8.81],[11.0,8.33],
                 [14.0,9.96],[6.0,7.24],[4.0,4.26],[12.0,10.84],[7.0,4.82],[5.0,5.68]],
        "itemStyle": {"color": "#C23531", "opacity": 1},
        "label": {"show": True, "formatter": "{c}", "position": "top", "opacity": 1,
                  "textStyle": {"color": "black", "fontSize": 16, "fontWeight": "bolder"}},
    }],
    "grid": {"top": 60, "left": 60, "bottom": 60, "right": 100},
    "tooltip": {"show": True, "formatter": "{c}", "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

---

### scatter.bubble — 气泡散点图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=scatter.bubble`（2026-04-02 实测）
> 与 scatter.simple 区别：多系列 + legend；`itemStyle.color` 使用**径向渐变对象**而非颜色字符串

```python
{
    "title": {"show": True, "text": "散点图", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "legend": {
        "show": True, "top": "top", "left": "center", "orient": "horizontal",
        "data": ["1990", "2015"],
        "padding": [25, 20, 25, 10],
        "textStyle": {"color": "#333", "fontSize": 12}
    },
    "xAxis": {
        "show": True, "name": "",
        "axisLabel": {"rotate": 0, "interval": "auto", "textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "yAxis": {
        "show": True, "name": "",
        "axisLabel": {"textStyle": {"color": "#333", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "series": [
        {
            "type": "scatter", "name": "1990", "symbolSize": 20,
            "data": [[28604,77],[31163,77.4],[1516,68],[13670,74.7],[28599,75]],  # [x, y]
            # 气泡散点用径向渐变色（区别于普通散点的单色）
            "itemStyle": {
                "color": {"type": "radial", "r": 0.8,
                          "colorStops": [{"offset": 0, "color": "#E7727C"},
                                         {"offset": 1, "color": "#D7291F"}]},
                "shadowBlur": 10, "shadowColor": "rgba(25,100,150,0.5)", "shadowOffsetY": 5
            },
        },
        {
            "type": "scatter", "name": "2015", "symbolSize": 20,
            "data": [[44056,81.8],[43294,81.7],[13334,76.9],[21291,78.5],[38923,80.8]],
            "itemStyle": {
                "color": {"type": "radial", "r": 0.8,
                          "colorStops": [{"offset": 0, "color": "#70D1E1"},
                                         {"offset": 1, "color": "#0188FB"}]},
                "shadowBlur": 10, "shadowColor": "rgba(25,100,150,0.5)", "shadowOffsetY": 5
            },
        },
    ],
    "grid": {"top": 60, "left": 60, "bottom": 60, "right": 100},
    "tooltip": {"show": True, "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

---

### funnel.simple — 普通漏斗图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=funnel.simple`（2026-04-02 实测）
> **注意：** data 是 `{name, value}` 对象数组；`sort: "descending"` = 漏斗形（大→小），`"ascending"` = 金字塔形

```python
{
    "title": {"show": True, "text": "某站点用户访问来源", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "legend": {
        "show": True, "top": "top", "left": "center", "orient": "horizontal",
        "data": ["展现", "点击", "访问", "咨询", "订单"],
        "padding": [25, 20, 25, 10],
        "textStyle": {"color": "#333", "fontSize": 12}
    },
    "series": [{
        "type": "funnel", "name": "漏斗图",
        "orient": "vertical",
        "sort": "descending",          # "descending"=漏斗形（大到小）
        "left": "10%", "width": "80%",
        "top": 60, "bottom": 60,
        "gap": 2,
        "data": [
            {"name": "展现", "value": 100},
            {"name": "点击", "value": 80},
            {"name": "访问", "value": 60},
            {"name": "咨询", "value": 40},
            {"name": "订单", "value": 20},
        ],
        "itemStyle": {"borderColor": "#fff", "borderWidth": 1},
        "label": {"show": True, "position": "inside",
                  "textStyle": {"fontSize": 16, "fontWeight": "normal"}},
        "labelLine": {"length": 10, "lineStyle": {"width": 1, "type": "solid"}},
        "emphasis": {"label": {"fontSize": 20}},
    }],
    "tooltip": {"show": True, "trigger": "item", "formatter": "{b} : {c}",
                "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

---

### funnel.pyramid — 金字塔漏斗图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=funnel.pyramid`（2026-04-02 实测）
> 与 funnel.simple 唯一区别：`sort: "ascending"`（小到大，底宽顶窄 = 金字塔形）

```python
# 结构与 funnel.simple 完全相同，仅 series 中以下字段不同：
"sort": "ascending",       # 小到大 → 金字塔形（funnel.simple 是 "descending"）
"name": "金字塔漏斗图",
```

> **漏斗图两种变体对比：**
>
> | chartType | `sort` | 形状 |
> |-----------|--------|------|
> | `funnel.simple`  | `"descending"` | 漏斗形（顶宽底窄） |
> | `funnel.pyramid` | `"ascending"`  | 金字塔形（底宽顶窄） |

---

### radar.basic — 普通雷达图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=radar.basic`（2026-04-02 实测）
> **注意：雷达图结构特殊** — 有独立的 `radar[]` 数组定义坐标轴，`series[].data` 每项的 `value` 是与 `indicator` 顺序对应的数值数组

```python
{
    "title": {"show": True, "text": "基础雷达图", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "legend": {
        "show": True, "top": "top", "left": "center", "orient": "horizontal",
        "data": ["预算分配（Allocated Budget）", "实际开销（Actual Spending）"],
        "padding": [25, 20, 25, 10],
        "textStyle": {"color": "#333", "fontSize": 12}
    },
    "radar": [{
        "shape": "polygon",            # 多边形雷达图（radar.basic）
        "center": [320, 200],
        # indicator 定义各维度名称和最大值，顺序与 series.data[].value 一一对应
        "indicator": [
            {"name": "销售（sales）",              "max": 6500},
            {"name": "管理（Administration）",     "max": 16000},
            {"name": "信息技术（Information Technology）", "max": 30000},
            {"name": "客服（Customer Support）",   "max": 38000},
            {"name": "研发（Development）",        "max": 52000},
            {"name": "市场（Marketing）",          "max": 25000},
        ],
        "name": {"formatter": "【{value}】", "textStyle": {"color": "#72ACD1", "fontSize": 14}},
        "axisLine": {"lineStyle": {"color": "gray", "opacity": 0.5}},
        "splitLine": {"lineStyle": {"color": "gray", "opacity": 0.5}},
    }],
    "series": [{
        "type": "radar",
        "name": "预算 vs 开销（Budget vs spending）",
        # data 每项：name=系列名，value=与 indicator 顺序对应的数值数组
        "data": [
            {"name": "预算分配（Allocated Budget）",  "value": [4300, 10000, 28000, 35000, 50000, 19000], "lineStyle": {}},
            {"name": "实际开销（Actual Spending）",   "value": [5000, 14000, 28000, 31000, 42000, 21000], "lineStyle": {}},
        ]
    }],
    "tooltip": {"show": True, "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

---

### radar.custom — 圆形雷达图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=radar.custom`（2026-04-02 实测）
> 与 radar.basic 区别：`shape: "circle"`，增加 `startAngle`/`splitArea`/`splitNumber`，`radius` 为数值（像素）

```python
{
    "title": {"show": True, "text": "圆形雷达图", "left": "left",
              "padding": [8, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "legend": {
        "show": True, "top": "top", "left": "center", "orient": "horizontal",
        "data": ["图一", "图二"],
        "padding": [25, 20, 25, 10],
        "textStyle": {"color": "#333", "fontSize": 12}
    },
    "radar": [{
        "shape": "circle",             # 圆形雷达图（radar.custom）
        "center": [320, 200],
        "radius": 90,                  # 数值像素，不是百分比
        "startAngle": 90,              # 起始角度（radar.custom 特有）
        "splitNumber": 4,              # 分割层数（radar.custom 特有）
        "indicator": [
            {"name": "指标一", "max": 6500},
            {"name": "指标二", "max": 6500},
            {"name": "指标三", "max": 6500},
            {"name": "指标四", "max": 6500},
            {"name": "指标五", "max": 6500},
        ],
        "name": {"formatter": "【{value}】", "textStyle": {"color": "#72ACD1"}},
        "axisLine": {"lineStyle": {"color": "gray", "opacity": 0.5}},
        "splitLine": {"lineStyle": {"color": "gray", "opacity": 0.5}},
        # 分层填充色（radar.custom 特有）
        "splitArea": {
            "areaStyle": {
                "color": ["rgba(114,172,209,0.2)", "rgba(114,172,209,0.4)",
                          "rgba(114,172,209,0.6)", "rgba(114,172,209,0.8)", "rgba(114,172,209,1)"],
                "shadowBlur": 10, "shadowColor": "rgba(0,0,0,0.3)"
            }
        },
    }],
    "series": [{
        "type": "radar", "name": "雷达图",
        "data": [
            {"name": "图一", "value": [1000, 2000, 3000, 4000, 2000], "lineStyle": {}},
            {"name": "图二", "value": [5000, 4000, 3000, 100,  1500], "lineStyle": {}},
        ]
    }],
    "tooltip": {"show": True, "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

> **雷达图两种变体对比：**
>
> | chartType | `shape` | `startAngle` | `splitArea` | `splitNumber` | `radius` |
> |-----------|---------|-------------|-------------|---------------|----------|
> | `radar.basic`  | `"polygon"` | 无 | 无 | 无 | 无 |
> | `radar.custom` | `"circle"`  | `90` | 有（渐变填充） | `4` | `90`（像素） |
>
> **雷达图通用注意：** `indicator` 顺序必须与 `series[].data[].value` 数组顺序严格一一对应；每个系列的 `value` 长度必须等于 `indicator` 长度。

---

### graph.simple — 普通关系图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=graph.simple`（2026-04-02 实测）
> **注意：关系图结构最特殊** — 无 xAxis/yAxis；series 同时含 `data`（节点）、`links`（边）、`categories`（分类）三个数组，需两个数据集分别提供节点和关系数据

```python
{
    "title": {"show": True, "text": "某站点用户访问来源", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "legend": {
        "show": True, "top": "top", "left": "center", "orient": "horizontal",
        "data": ["类目1", "类目2", "类目3", "类目4", "类目5", "类目6"],
        "padding": [25, 20, 25, 10],
        "textStyle": {"color": "#333", "fontSize": 12}
    },
    "series": [{
        "type": "graph",
        "name": "关系图",
        "layout": "circular",          # 布局："circular"=环形 / "force"=力引导 / "none"=自定义坐标
        "center": [320, 150],
        "lineStyle": {
            "curveness": 0.3,          # 连线弯曲度 0~1
            "color": "source"          # 连线颜色继承源节点颜色
        },
        "label": {"show": True, "position": "right",
                  "textStyle": {"color": "#333", "fontSize": 12}},
        # --- 节点数据（来自数据集1）---
        # 每个节点：name=节点名，category=分类索引（对应 categories 数组下标），value=节点大小
        "data": [
            {"name": "测试0", "category": 0, "value": 28},
            {"name": "测试1", "category": 1, "value": 9},
            {"name": "测试2", "category": 2, "value": 23},
            {"name": "测试3", "category": 3, "value": 8},
            {"name": "测试4", "category": 4, "value": 8},
            {"name": "测试5", "category": 5, "value": 20},
        ],
        # --- 边数据（来自数据集2）---
        # 每条边：source=起始节点名，target=目标节点名（需与 data[].name 严格匹配）
        "links": [
            {"source": "测试1", "target": "测试0"},
            {"source": "测试2", "target": "测试0"},
            {"source": "测试3", "target": "测试1"},
            # ... 更多边
        ],
        # --- 分类定义（对应 legend.data）---
        # category 索引从 0 开始，与 data[].category 对应
        "categories": [
            {"name": "类目1", "itemStyle": {"color": ""}},
            {"name": "类目2", "itemStyle": {"color": ""}},
            {"name": "类目3", "itemStyle": {"color": ""}},
            {"name": "类目4", "itemStyle": {"color": ""}},
            {"name": "类目5", "itemStyle": {"color": ""}},
            {"name": "类目6", "itemStyle": {"color": ""}},
        ],
    }],
    "tooltip": {"show": True, "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

> **关系图通用注意：**
> - 需要**两个数据集**：数据集1提供节点（`name/value/category`），数据集2提供边（`source/target`）
> - `links[].source` / `links[].target` 必须与 `data[].name` **严格一致**，否则连线无法渲染
> - `data[].category` 是 `categories` 数组的**下标索引**（0-based），不是名称
> - `extData` 中需配置两个 `dataId`（积木报表关系图特有的双数据集绑定方式）

---

### pictorial.spirits — 普通象形图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=pictorial.spirits`（2026-04-02 实测）
> **注意：** 类型为 `pictorialBar`（非 bar）；横向布局，yAxis 放分类，xAxis 放数值；`symbol` 需设置图标路径

```python
{
    "title": {"show": True, "text": "某站点用户访问来源", "top": "5", "left": "left",
              "padding": [5, 20, 5, 20],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    # 横向图：yAxis 放分类，xAxis 放数值
    "yAxis": {
        "show": True, "name": "",
        "data": ["2017", "2018", "2019", "2020"],
        "inverse": False,
        "axisTick": {"show": False},
        "axisLabel": {"textStyle": {"color": "#999", "fontSize": 16}},
        "axisLine": {"lineStyle": {"color": "#333"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "xAxis": {
        "show": True, "name": "",
        "max": 2000,                   # 必须设置最大值，与 symbolBoundingData 一致
        "axisLabel": {"rotate": 0, "margin": 10, "interval": "auto",
                      "textStyle": {"color": "green", "fontSize": 12}},
        "axisLine": {"lineStyle": {"color": "#999"}},
        "splitLine": {"show": False, "lineStyle": {"color": "red", "width": 1, "type": "solid"}}
    },
    "series": [{
        "type": "pictorialBar",        # 象形图专用类型
        "data": [891, 1220, 660, 1670],
        "symbol": "",                  # 图标路径，如 "path://..." 或 "image://url"，空=默认矩形
        "symbolSize": 30,              # 图标尺寸（像素）
        "symbolRepeat": "fixed",       # 重复方式："fixed"=固定数量
        "symbolMargin": "5%!",         # 图标间距，末尾!表示绝对间距
        "symbolBoundingData": 2000,    # 图标铺满的基准值，需与 xAxis.max 一致
        "symbolClip": True,            # 是否按数值裁剪图标
        "secondOpacity": 0.2,          # 背景图标透明度
        "double": False,               # 是否双向显示
        "label": {"show": True, "position": "right",
                  "textStyle": {"color": "black", "fontSize": 16, "fontWeight": "bolder"}}
    }],
    "grid": {"top": 60, "left": 60, "bottom": 60, "right": 100},
    # 注意：象形图默认无 tooltip
}
```

---

### map.simple — 区域地图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=map.simple`（2026-04-02 实测）
> **注意：** 地图图表用 `geo` 对象替代 xAxis/yAxis；根级有 `chartType: "map"` 标识；series 无 data（区域色由数据集驱动）

```python
{
    "chartType": "map",                # 根级标识，地图图表特有
    "title": {"show": True, "text": "中国地图", "left": "left",
              "padding": [5, 20, 5, 10],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "geo": {
        "map": "china",                # 地图类型："china" / 省份名
        "layoutCenter": ["50%", "50%"],
        "layoutSize": 600,
        "zoom": 0.7,                   # 缩放比例
        "roam": True,                  # 允许拖拽/缩放
        "regions": [],                 # 自定义区域样式，默认空
        "label": {"show": False, "color": "#fff", "fontSize": 12},
        "itemStyle": {
            "areaColor": "#224C66",    # 区域填充色
            "borderColor": "#0692a4",  # 边界线颜色
            "borderWidth": 1
        },
        "emphasis": {
            "itemStyle": {"areaColor": "#0b1c2d"},   # 高亮区域色
            "label": {"color": "#fff"}
        }
    },
    "series": [{
        "type": "map",
        "name": "地图",
        "coordinateSystem": "geo"      # 使用 geo 坐标系
        # 无 data 字段，数据由数据集 name/value 驱动，name 需匹配地图区域名
    }],
    # 注意：map.simple 默认无 tooltip
}
```

---

### map.scatter — 点地图（完整原始默认值）

> 来源：`GET /jmreport/addChart?chartType=map.scatter`（2026-04-02 实测）
> 与 map.simple 区别：series type 为 `"scatter"`，data 包含城市坐标点；`{name: 城市名, value: 数值}` 中城市名需匹配内置地理坐标库

```python
{
    "chartType": "map",                # 根级标识，与 map.simple 相同
    "title": {"show": True, "text": "主要城市空气质量", "left": "left",
              "padding": [5, 20, 5, 10],
              "textStyle": {"color": "#c23531", "fontSize": 18, "fontWeight": "bolder"}},
    "geo": {
        # geo 配置与 map.simple 完全相同
        "map": "china", "layoutCenter": ["50%", "50%"], "layoutSize": 600,
        "zoom": 0.7, "roam": True, "regions": [],
        "label": {"show": False, "color": "#fff", "fontSize": 12},
        "itemStyle": {"areaColor": "#224C66", "borderColor": "#0692a4", "borderWidth": 1},
        "emphasis": {"itemStyle": {"areaColor": "#0b1c2d"}, "label": {"color": "#fff"}}
    },
    "series": [{
        "type": "scatter",             # 散点，不是 map
        "name": "",
        "coordinateSystem": "geo",
        "encode": {"value": [2]},      # 数值编码索引
        "itemStyle": {"color": "#F4E925"},  # 散点颜色
        "label": {"show": False, "formatter": "{b}", "position": "right"},
        "emphasis": {"label": {"show": True}},
        # data 每项：name=城市名（需匹配内置坐标库），value=数值
        "data": [
            {"name": "北京", "value": 58},
            {"name": "上海", "value": 63},
            {"name": "广州", "value": 74},
            # ... 更多城市
        ]
    }],
    "tooltip": {"show": True, "textStyle": {"color": "#fff", "fontSize": 18}}
}
```

> **地图图表通用注意：**
> - 根级必须有 `"chartType": "map"` 字段
> - 无 xAxis/yAxis，用 `geo` 对象定义地图
> - `map.simple` series 无 data，区域着色靠数据集 `name` 字段匹配省份名
> - `map.scatter` series data 的 `name` 需匹配积木报表内置城市坐标库（省会城市/直辖市）
> - `extData.axisX/axisY/series` 仍需填 `"name"/"value"/"type"`，与其他图表一致

---

## 9. 快速生成图表的 Python 函数

```python
def create_chart(chart_type, title, db_code, db_id, row_start, col_start,
                 rows=10, cols=5, width="650", height="350"):
    layer_id = "chart_" + gen_id()
    base_configs = {
        "bar.simple": {
            "title": {"text": title, "left": "center"},
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
            "xAxis": [{"type": "category", "data": []}],
            "yAxis": [{"type": "value"}],
            "series": [{"type": "line", "smooth": True, "data": []}]
        }
    }
    config = base_configs.get(chart_type, base_configs["bar.simple"])
    row_end = row_start + rows - 1
    col_end = col_start + cols - 1
    virtual_cells = [[r,c] for r in range(row_start, row_end+1) for c in range(col_start, col_end+1)]
    chart_rows = {}
    for r in range(row_start, row_end + 1):
        cells = {str(c): {"text": " ", "virtual": layer_id} for c in range(col_start, col_end + 1)}
        chart_rows[str(r)] = {"cells": cells}
    chart_item = {
        "row": row_start, "col": col_start, "colspan": 0, "rowspan": 0,
        "width": width, "height": height,
        "config": json.dumps(config, ensure_ascii=False), "url": "",
        "extData": {"chartType": chart_type, "dataType": "sql", "dataId": str(db_id),
                    "dbCode": db_code, "axisX": "name", "axisY": "value", "series": "type",
                    "xText": "", "yText": "", "apiStatus": "1"},
        "layer_id": layer_id, "offsetX": 0, "offsetY": 0,
        "backgroud": {"enabled": False, "color": "#fff", "image": ""},
        "virtualCellRange": virtual_cells
    }
    return chart_item, chart_rows
```

## 10. 模板报表参考

通过 `GET /jmreport/getReportByUser?reportId=&template=1` 查询模板。

### 46个模板分类

| 分类 | 数量 | 示例 |
|------|------|------|
| 基础表格 | 30 | 信息采集表、简单分组报表 |
| 图表报表 | 9 | 全国各大城市化员数据、物业实时监控 |
| 循环报表 | 4 | 订单表循环打印、班级循环套打表 |
| 图片报表 | 4 | 员工信息表、证书打印 |
| 条码/二维码 | 3 | 实习证明、凭证条码报表 |

### 图表数据绑定 extData

| 字段 | 固定值 | 含义 |
|------|--------|------|
| `axisX` | `name` | X轴/分类 |
| `axisY` | `value` | Y轴/数值 |
| `series` | `type` | 系列/分组 |

`dataType` 取值：`"sql"`, `"api"`, `"json"`, `"javabean"`, `"files"`, `null`（静态图表）
