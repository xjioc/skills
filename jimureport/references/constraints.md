# 积木报表重要约束

1. **数据集编码 `db_code` 不能重复且只支持英文字符** — 同一个报表内的多个数据集，每个的 `db_code` 必须唯一。编码只能使用英文字母、数字和下划线，不能包含中文或特殊字符。重复会导致数据覆盖或查询异常。
2. **`is_page` 分页只能有一个** — 一个报表中只能有一个数据集设置 `is_page=1`（启用分页），其余数据集必须为 `is_page=0`。多个数据集同时分页会导致分页冲突。

## 数据绑定语法

| 语法 | 说明 | 场景 |
|------|------|------|
| `${db.field}` | 单值绑定 | 主表字段、固定值 |
| `#{db.field}` | 列表绑定 | 明细行、循环数据 |
| `#{db.group(field)}` | 纵向分组 | 按字段分组汇总 |
| `#{db.groupRight(field)}` | 横向分组 | 按字段横向展开 |
| `#{db.dynamic(field)}` | 动态聚合 | 交叉表数据 |
| `#{db.customGroup(field)}` | 自定义分组 | 横向自定义展开 |
| `=SUM(D7)` | Excel 公式 | 列汇总 |

## 单元格属性

| 属性 | 说明 | 值 |
|------|------|-----|
| `merge` | 合并 | `[行数,列数]`，如 `[0,2]` 向右合并2列 |
| `style` | 样式索引 | 引用 `styles` 数组下标 |
| `loopBlock` | 循环块标记 | 1=属于循环块 |
| `zonedEdition` | 分版标记 | 1/2/... 分版编号 |
| `fixedHead` | 固定表头 | 1=固定 |
| `fixedTail` | 固定表尾 | 1=固定 |
| `aggregate` | 聚合类型 | 见下方分组配置 |
| `subtotal` | 小计配置 | 见下方分组配置 |
| `funcname` | 聚合函数 | 见下方分组配置 |
| `subtotalText` | 小计行文本 | `"合计"` / `"小计"` |
| `direction` | 展开方向 | 见下方分组配置 |
| `sort` | 排序 | 见下方分组配置 |
| `rendered` | 渲染标记 | `""` |
| `config` | 配置标记 | `""` |
| `decimalPlaces` | 小数位 | `"0"`/`"1"`/`"4"` |
| `display` | 显示格式 | 见下方 display 值表 |
| `fillForm` | 填报组件 | 组件配置对象 |

## 分组相关配置

### aggregate 聚合方式（polyWayList）

| 值 | 说明 |
|-----|------|
| `select` | 列表（普通列，不分组） |
| `group` | 分组（相同值合并单元格） |

### subtotal 是否启用小计

| 值 | 说明 |
|-----|------|
| `"-1"` | 否（不显示小计行） |
| `"groupField"` | 是（分组切换时显示小计/合计行） |

### funcname 聚合函数（aggregateList）

| 值 | 说明 | 用于 |
|-----|------|------|
| `"-1"` | 无（不计算，仅显示 subtotalText 文本） | 分组字段（地区、销售员等） |
| `"SUM"` | 求和 | 数值字段（金额、数量等） |
| `"MAX"` | 最大值 | 数值字段 |
| `"MIN"` | 最小值 | 数值字段 |
| `"AVERAGE"` | 平均值 | 数值字段 |
| `"COUNT"` | 计数 | 任意字段 |

### direction 展开方向（directionList）

| 值 | 说明 |
|-----|------|
| `"down"` | 纵向（默认） |
| `"right"` | 横向 |

### sort 排序（sortType）

| 值 | 说明 |
|-----|------|
| `"default"` | 默认（不排序） |
| `"asc"` | 正序 |
| `"desc"` | 倒序 |

### aggregate 高级模式（advancedList）

| 值 | 说明 |
|-----|------|
| `"default"` | 普通属性 |
| `"dynamic"` | 动态属性（交叉表） |

### 分组单元格配置示例

**分组字段（地区，一级分组 — 合计）：**
```json
{
    "text": "#{sales.group(region)}",
    "style": 4,
    "aggregate": "group",
    "subtotal": "groupField",
    "funcname": "-1",
    "subtotalText": "合计",
    "rendered": "",
    "config": ""
}
```

**分组字段（销售员，二级分组 — 小计）：**
```json
{
    "text": "#{sales.group(salesman)}",
    "style": 4,
    "aggregate": "group",
    "subtotal": "groupField",
    "funcname": "-1",
    "subtotalText": "小计"
}
```

**数值字段（销售额，小计/合计行自动求和）：**
```json
{
    "text": "#{sales.amount}",
    "style": 4,
    "funcname": "SUM",
    "subtotal": "-1",
    "display": "number",
    "rendered": "",
    "config": ""
}
```

**注意：** 数值字段的 `subtotal` 为 `"-1"`（不是 `"groupField"`），`funcname` 为 `"SUM"`。含义是：该字段不触发分组切换，但在分组切换产生的小计/合计行中自动按 SUM 聚合。

## display 显示格式（JmConst.CELL_FORMAT_*）

| display 值 | 说明 | 示例 |
|------------|------|------|
| `normal` | 默认文本 | — |
| `number` | 数值（数值类型字段默认） | 58000 |
| `percent` | 百分比 | 85% |
| `rmb` | 人民币 | ¥58,000.00 |
| `usd` | 美元 | $58,000.00 |
| `eur` | 欧元 | €58,000.00 |
| `date` | 日期 | 2026-03-20 |
| `date2` | 日期(斜杠) | 2026/03/20 |
| `time` | 时间 | 12:30:00 |
| `datetime` | 日期时间 | 2026-03-20 12:30:00 |
| `year` | 年 | 2026 |
| `month` | 月 | 03 |
| `base64Img` | Base64图片 | — |
| `img` | 图片 | — |
| `qrcode` | 二维码 | — |
| `barcode` | 条形码 | — |
| `richText` | 富文本 | — |

## 顶层配置

| 字段 | 说明 |
|------|------|
| `loopBlockList` | 循环块定义（含 `loopTime` 分栏次数） |
| `zonedEditionList` | 分版区域定义 |
| `fixedPrintHeadRows` | 固定打印表头 |
| `fixedPrintTailRows` | 固定打印表尾 |
| `groupField` | 分组字段 |
| `isGroup` | 是否启用分组 |
| `submitHandlers` | 填报提交处理器 |
| `background` | 背景图配置 |
| `imgList` | 图片列表 |
| `displayConfig` | 二维码/条码显示配置 |
| `dicts` | 引用的字典编码列表 |
| `printConfig` | 打印配置（纸张/方向/边距） |
| `merges` | 合并单元格列表（如 `"B1:H1"`) |
