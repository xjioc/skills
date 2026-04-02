# 打印配置完整参考（printConfig）

积木报表的打印设置，包含纸张、布局、边距、页码、页眉页脚、水印等配置。所有配置存储在 jsonStr 的 `printConfig` 字段中。

---

## 1. 完整 printConfig 结构

```python
printConfig = {
    # ===== 纸张与布局 =====
    "paper": "A4",              # 纸张大小
    "width": 210,               # 纸张宽度(mm)
    "height": 297,              # 纸张高度(mm)
    "layout": "portrait",       # 打印布局: portrait(纵向) / landscape(横向)
    # "definition": 1,          # 清晰度（已从打印设置UI中移除，无需设置）
    "isBackend": False,         # 是否套打

    # ===== 边距 =====
    "marginX": 10,              # 左右边距(mm)
    "marginY": 10,              # 上下边距(mm)

    # ===== 回调 =====
    "printCallBackUrl": "",     # 打印回调接口URL（文档：https://help.jimureport.com/printNew/callback/）

    # ===== 页码 =====
    "paginationShow": True,     # 是否显示页码
    "paginationLocation": "middle",  # 页码位置: left / middle / right
    "paginationStart": 1,       # 页码起始范围（第N页及以后显示页码）

    # ===== 页眉页脚 =====
    "headerFooterShow": False,  # 是否启用页眉页脚
    "headerLocation": "left",   # 页眉位置: left / middle / right（配合文本使用）
    "headerText": "",           # 页眉文本
    "footerLocation": "left",   # 页脚位置: left / middle / right
    "footerText": "",           # 页脚文本

    # ===== 水印 =====
    "watermarkShow": False,     # 是否显示水印
    "watermarkText": "积木报表", # 水印文本
    "fontsize": 28,             # 水印字号(10-72)
    "watermarkColor": "#d5d5d5",# 水印颜色
    "rotationAngle": -45,       # 水印旋转角度（负值=逆时针）

    # ===== 表尾固定 =====
    "printFootorFixBottom": False  # 打印时表尾是否固定到页面底部
}
```

---

## 2. 纸张大小

### 2.1 系统内置纸张

| paper 值 | 中文名 | width × height (mm) |
|----------|--------|---------------------|
| `"A4"` | A4 | 210 × 297 |
| `"A3"` | A3 | 297 × 420 |
| `"Letter"` | Letter | 216 × 279 |
| `"Legal"` | Legal | 216 × 355 |
| `"Executive"` | Executive | 184 × 266 |

> **注意**：修改 paper 时需同步修改 width 和 height。paper 值区分大小写，需与上表完全一致（如 `"Letter"` 首字母大写）。

### 2.2 自定义纸张

通过修改 `application.yml`（启动类所在项目）新增自定义纸张（v1.1.09+）：

```yaml
jeecg:
  jmreport:
    printPaper:
      - title: A5纸
        size:
          - 148   # 宽度(mm)
          - 210   # 高度(mm)
      - title: B4纸
        size:
          - 250
          - 353
```

配置后，设计器纸张下拉列表中出现自定义选项，`paper` 字段传入 `title` 值，`width`/`height` 对应 `size[0]`/`size[1]`。

### 2.3 纸张自动识别规则（AI 生成报表时使用）

**当用户提到纸张时，按以下优先级匹配：**

1. **先读 yml 自定义配置**：从服务 `application-*.yml` 中读取 `jeecg.jmreport.printPaper` 列表，按 `title` 模糊匹配用户的描述
2. **再匹配系统内置纸张**：按下表关键词识别
3. **匹配失败时**：告知用户该纸张不在系统配置中，并列出可用选项，不要擅自选择其他纸张

**内置纸张关键词匹配表：**

| 用户描述关键词 | paper 值 | width | height |
|--------------|----------|-------|--------|
| A4、a4 | `"A4"` | 210 | 297 |
| A3、a3 | `"A3"` | 297 | 420 |
| Letter、letter、信纸 | `"Letter"` | 216 | 279 |
| Legal、legal、法律 | `"Legal"` | 216 | 355 |
| Executive、executive | `"Executive"` | 184 | 266 |

**当前服务自定义纸张：** 无（yml 中未配置 `printPaper`）

> **重要：** 若用户指定的纸张在内置列表和 yml 自定义配置中均找不到，必须明确告知用户：
> "系统中未找到「XX纸张」配置，当前可用纸张为：A4、A3、A5、B5、Letter、Legal。如需使用自定义纸张，请在 `application.yml` 中配置 `jeecg.jmreport.printPaper`。"
> 不允许静默降级到 A4 或其他纸张。

---

## 3. 打印布局

| layout | 说明 | 适用场景 |
|--------|------|---------|
| `"portrait"` | 纵向（默认） | 列数 ≤ 6 |
| `"landscape"` | 横向 | 列数 > 6，宽表格 |

---

## 4. 页码配置

```python
# 显示页码，居中，从第1页开始
"paginationShow": True,
"paginationLocation": "middle",
"paginationStart": 1

# 不显示页码
"paginationShow": False
```

| 字段 | 值 | 说明 |
|------|-----|------|
| `paginationShow` | `True/False` | 是否显示页码 |
| `paginationLocation` | `"left"/"middle"/"right"` | 页码位置 |
| `paginationStart` | 数字 | 从第N页开始显示页码（之前的页不显示） |

---

## 5. 页眉页脚配置

```python
# 启用页眉页脚
"headerFooterShow": True,
"headerLocation": "left",    # 页眉靠左
"headerText": "机密文件",     # 页眉内容
"footerLocation": "right",   # 页脚靠右
"footerText": "公司内部使用"   # 页脚内容
```

| 字段 | 值 | 说明 |
|------|-----|------|
| `headerFooterShow` | `True/False` | 是否启用页眉页脚 |
| `headerLocation` | `"left"/"middle"/"right"` | 页眉位置 |
| `headerText` | 字符串 | 页眉文本 |
| `footerLocation` | `"left"/"middle"/"right"` | 页脚位置 |
| `footerText` | 字符串 | 页脚文本 |

> **与固定表头表尾的区别**：页眉页脚是打印设置中的轻量文本，固定表头表尾是 jsonStr 中的单元格区域（支持合并、样式等）。

---

## 6. 水印配置

```python
# 启用水印
"watermarkShow": True,
"watermarkText": "机密文件",
"fontsize": 28,
"watermarkColor": "#d5d5d5",
"rotationAngle": -45
```

| 字段 | 值 | 说明 |
|------|-----|------|
| `watermarkShow` | `True/False` | 是否显示水印 |
| `watermarkText` | 字符串 | 水印文本（默认"积木报表"） |
| `fontsize` | 数字 | 水印字号，可选：10/12/14/16/18/20/22/24/26/28/36/48/72 |
| `watermarkColor` | 颜色值 | 水印颜色（默认 `#d5d5d5` 浅灰） |
| `rotationAngle` | 数字 | 旋转角度（-45=逆时针45度，0=水平） |

---

## 7. 常用配置模板

### 标准A4纵向（默认）
```python
"printConfig": {
    "paper": "A4", "width": 210, "height": 297,
    "definition": 1, "isBackend": False,
    "marginX": 10, "marginY": 10,
    "layout": "portrait", "printCallBackUrl": ""
}
```

### 横向宽表格 + 页码 + 页眉页脚
```python
"printConfig": {
    "paper": "A4", "width": 210, "height": 297,
    "definition": 1, "isBackend": False,
    "marginX": 10, "marginY": 10,
    "layout": "landscape", "printCallBackUrl": "",
    "paginationShow": True,
    "paginationLocation": "middle",
    "paginationStart": 1,
    "headerFooterShow": True,
    "headerLocation": "left",
    "headerText": "销售部门报表",
    "footerLocation": "right",
    "footerText": "仅供内部使用"
}
```

### 带水印的机密报表
```python
"printConfig": {
    "paper": "A4", "width": 210, "height": 297,
    "definition": 1, "isBackend": False,
    "marginX": 10, "marginY": 10,
    "layout": "portrait", "printCallBackUrl": "",
    "watermarkShow": True,
    "watermarkText": "机密文件",
    "fontsize": 36,
    "watermarkColor": "#e0e0e0",
    "rotationAngle": -30
}
```

### 完整配置（所有功能开启）
```python
"printConfig": {
    "paper": "A4", "width": 210, "height": 297,
    "definition": 1, "isBackend": False,
    "marginX": 15, "marginY": 15,
    "layout": "landscape", "printCallBackUrl": "",
    "paginationShow": True,
    "paginationLocation": "middle",
    "paginationStart": 1,
    "headerFooterShow": True,
    "headerLocation": "left",
    "headerText": "XX公司-销售报表",
    "footerLocation": "right",
    "footerText": "打印日期：2026-03-27",
    "watermarkShow": True,
    "watermarkText": "内部文件",
    "fontsize": 28,
    "watermarkColor": "#d5d5d5",
    "rotationAngle": -45,
    "printFootorFixBottom": True
}
```

---

## 8. 注意事项

1. **边距最小值**：`marginX`/`marginY` 建议 ≥ 10mm，小于 10mm 页眉页脚可能显示不全
2. **套打模式**（`isBackend: True`）：套打时页眉页脚不可用
3. **页码起始**：`paginationStart: 2` 表示第1页不显示页码，从第2页开始
4. **水印字号**：只支持固定值 10/12/14/16/18/20/22/24/26/28/36/48/72
5. **横向打印**：列数 > 6 时建议 `layout: "landscape"`，实际纸张宽高不变（由打印机处理方向）
6. **printFootorFixBottom**：开启后打印时表尾固定到每页底部（类似 fixedPrintTailRows 但更简单）

---

## 9. 打印规则（官方文档）

> 来源：https://help.jimureport.com/print/rule

### 9.1 纸张宽度与内容宽度规则

设计器中绿色虚线标识当前纸张宽度边界，打印时遵循以下规则：

| 情况 | 打印行为 |
|------|---------|
| 内容宽度 ≤ 纸张宽度 | 按纸张尺寸打印，内容居中或按边距对齐 |
| 内容宽度 > 纸张宽度 | **超出部分不打印**（旧的超宽规则已废弃） |

> **横向打印（landscape）不是让超宽内容适配纸张，而是需要在 `printConfig.layout` 中显式配置。**

### 9.2 打印内容居中

当内容宽度小于纸张宽度时，内容可能偏左，有两种居中方案：

1. **自动居中**：在报表设计器布局设置中开启水平居中（`isViewContentHorizontalCenter: true`）
2. **手动居中**：设计时在内容左右两侧各留等宽的空列作为边距，使内容视觉上居中

### 9.3 图表背景色

打印时图表会带灰色边框（来自图表背景颜色），若不需要，在图表属性中将背景颜色设置为透明/无色即可。

### 9.4 自定义纸张（v1.1.09+）

在 `application.yml` 中通过 `jeecg.jmreport.printPaper` 配置自定义纸张，单位为毫米：

```yaml
jeecg:
  jmreport:
    printPaper:
      - title: A5纸
        size:
          - 148
          - 210
      - title: B4纸
        size:
          - 250
          - 353
```

配置后，设计器纸张下拉列表中会出现自定义纸张选项。

### 9.5 套打（isBackend）

套打时，打印内容的范围取决于**套打图片的尺寸**，超出图片边界的单元格数据不会被打印。设计时需确保所有内容都在套打图片范围内。

### 9.6 打印全部数据的请求规则（开发参考）

当用户点击"打印全部"或"导出PDF"时，系统向后端发送的数据集查询请求会附加：

- `printAll=true`
- `pageSize` = 该数据集的 `count`（总记录数）

**含义：** 打印全部时会将全量数据一次性加载，对于大数据集需注意性能。开发自定义打印接口时，可通过 `printAll` 参数判断是否需要返回全量数据。

### 9.7 慎用自动换行

开启单元格自动换行（`wrap: true`）可能引发以下问题：

- 当某个单元格内容高度超过一页高度时，该行会被拆分到下一页
- 拆分后当前页底部出现大片空白区域，导致页面利用率低
- 多行数据时，空白问题会累积，产生多个近乎空白的页面

**建议：** 对于可能内容较多的单元格（如备注、描述字段），优先通过限制列宽、截断文本或调整字号来控制高度，而非依赖自动换行。