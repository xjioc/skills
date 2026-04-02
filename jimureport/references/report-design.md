# 报表设计核心参考

积木报表的 jsonStr 设计配置完整参考，包含单元格属性、数据绑定、分组合计、查询配置、循环块等。

---

## 1. 重要约束

1. **数据集编码 `db_code` 不能重复且只支持英文字符** — 同一个报表内的多个数据集，每个的 `db_code` 必须唯一。编码只能使用英文字母、数字和下划线。
2. **第一个数据集默认勾选分页（`isPage: "1"`）** — 创建报表时，第一个数据集应设置 `isPage: "1"`。一个报表**只能有一个数据集**启用分页，其余必须为 `isPage: "0"`。多个数据集同时分页会导致冲突。

## 2. 数据绑定语法

| 语法 | 说明 | 场景 |
|------|------|------|
| `${db.field}` | 单值绑定 | 对象数据集（单条记录）、主表字段。数据集需设 `isList:"0"`, `isPage:"0"` |
| `#{db.field}` | 列表绑定 | 明细行、循环数据 |
| `#{db.group(field)}` | 纵向分组 | 按字段分组汇总 |
| `#{db.groupRight(field)}` | 横向分组 | 按字段横向展开 |
| `#{db.dynamic(field)}` | 动态聚合 | 交叉表数据 |
| `#{db.customGroup(field)}` | 自定义分组 | 横向自定义展开 |
| `=SUM(D7)` | Excel 公式 | 列汇总 |

## 3. 单元格属性

| 属性 | 说明 | 值 |
|------|------|-----|
| `text` | 单元格内容 | 支持 `#{db.field}` 数据绑定 |
| `merge` | 合并 | `[行数,列数]`，如 `[0,2]` 向右合并2列。**必须同时在 `merges` 数组添加对应范围** |
| `style` | 样式索引 | 引用 `styles` 数组下标 |
| `loopBlock` | 循环块标记 | 1=属于循环块 |
| `zonedEdition` | 分版标记 | 1/2/... 分版编号 |
| `fixedHead` | 固定表头 | 1=固定 |
| `fixedTail` | 固定表尾 | 1=固定 |
| `aggregate` | 聚合类型 | `"select"` 普通列 / `"group"` 分组 |
| `subtotal` | 小计配置 | `"groupField"` 分组依据 / `"-1"` 聚合字段 |
| `funcname` | 聚合函数 | `"SUM"` / `"AVERAGE"` / `"COUNT"` / `"MAX"` / `"MIN"` / `"-1"` 无 |
| `subtotalText` | 小计行文本 | `"合计"` / `"小计"` |
| `decimalPlaces` | 小数位 | `"0"`/`"1"`/`"2"`/`"4"` |
| `direction` | 展开方向 | `"down"` 纵向 / `"right"` 横向 |
| `sort` | 排序 | `"default"` / `"asc"` / `"desc"` |
| `display` | 显示格式 | 见下方 display 值表 |
| `rendered` | 渲染标记 | `""` |
| `config` | 配置标记 | `""` |
| `fillForm` | 填报组件 | 组件配置对象 |
| `virtual` | 图层占位 | 对应组件的 `layer_id` |

### display 显示格式

| display 值 | 说明 | 示例 |
|------------|------|------|
| `normal` | 默认文本 | — |
| `number` | 数值 | 58000 |
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

## 4. 分组合计配置

当报表需要按某字段分组并在每组末尾显示合计行时，需要配置分组字段和聚合字段。

### 分组字段配置

```json
{
    "text": "#{sales.group(customer_name)}",
    "style": 2,
    "aggregate": "group",
    "subtotal": "groupField",
    "funcname": "-1",
    "subtotalText": "合计"
}
```

### 聚合字段配置（数值字段）

```json
{
    "text": "#{sales.total_amount}",
    "style": 2,
    "subtotal": "-1",
    "funcname": "SUM",
    "decimalPlaces": "2"
}
```

### jsonStr 顶层需添加

```json
{
    "isGroup": true,
    "groupField": "数据集编码.分组字段名"
}
```

### 聚合函数对照表

| funcname 值 | 渲染时转换 | 说明 |
|-------------|-----------|------|
| `"SUM"` | `=SUM` | 求和 |
| `"AVERAGE"` | `=AVERAGE` | 平均值 |
| `"COUNT"` | `=COUNT` | 计数 |
| `"MAX"` | `=MAX` | 最大值 |
| `"MIN"` | `=MIN` | 最小值 |
| `"COUNTNZ"` | `=COUNTNZ` | 非零计数 |

> **注意：** cell 中的 `funcname` 存储不带 `=` 前缀（如 `"SUM"`），渲染引擎在 `initSubtotal()` 中自动加 `=` 前缀。

### 多级分组示例

**一级分组（地区，显示"合计"）：**
```json
{
    "text": "#{sales.group(region)}",
    "aggregate": "group",
    "subtotal": "groupField",
    "funcname": "-1",
    "subtotalText": "合计"
}
```

**二级分组（销售员，显示"小计"）：**
```json
{
    "text": "#{sales.group(salesman)}",
    "aggregate": "group",
    "subtotal": "groupField",
    "funcname": "-1",
    "subtotalText": "小计"
}
```

**数值字段（销售额，自动求和）：**
```json
{
    "text": "#{sales.amount}",
    "funcname": "SUM",
    "subtotal": "-1",
    "display": "number",
    "decimalPlaces": "2"
}
```

### 常见错误

1. **聚合字段的 subtotal 设为 "groupField"** — 聚合字段必须 `subtotal="-1"`，只有分组依据字段（text 含 `group()` 语法）才能用 `"groupField"`。否则渲染引擎的 `getTemplate()` 不会生成别名模板，合计行数值无法回填。
2. **数值字段未设置 funcname** — 导致 `subtotalFieldList` 为空，合计行只有文字标签没有数值。
3. **缺少 isGroup 和 groupField** — jsonStr 顶层需设置 `"isGroup": true` 和 `"groupField": "数据集编码.分组字段名"`。

### 渲染引擎流程

1. `beforeRenderRow()` 解析 `subtotal="groupField"` → 分组依据列表；解析 `funcname` → 聚合字段列表
2. `getData()` → `initResultList()` 按分组排序，在组边界插入合计行
3. `addResult()` 调用 `initSubtotal()` 计算聚合，结果存入 `keyMap[fieldName_funcName]`
4. `getTemplate()` 对 `subtotal="-1"` 的单元格生成 `${field!field_funcName}` 别名模板

## 5. 循环报表 (loopBlockList)

```json
{
    "loopBlockList": [
        {
            "sci": 1,        // 起始列
            "sri": 2,        // 起始行
            "eci": 5,        // 结束列
            "eri": 5,        // 结束行
            "index": 1,      // 块索引
            "db": "jm",      // 数据集别名
            "loopTime": 3    // 循环次数(可选，分栏打印用)
        }
    ]
}
```

循环块内的单元格需要设置 `"loopBlock": 1` 属性。

### 5.1 循环块两种布局

**列表式（简单明细表）：** 循环块只占1行，每条记录渲染1行。

**卡片式（信息明细表）：** 循环块占多行，每条记录渲染一张多行卡片。适用于员工信息表、证书打印等场景。

### 5.2 卡片式循环块示例

每条记录渲染3行标签-值对 + 1行间隔，右侧可放二维码：

```
┌──────────── 员工信息明细表 ────────────┐
│ 姓名：│ 张三   │所在部门：│ 研发部  │ QR │ ← 循环块
│ 年龄：│ 21     │ 学历：  │ 本科    │    │   每条记录
│ 性别：│ 男     │ 薪水：  │ 8000    │    │   渲染4行
│       │        │         │         │    │ ← 间隔行
├───────┼────────┼─────────┼─────────┼────┤
│ 姓名：│ 李四   │所在部门：│ 市场部  │ QR │ ← 下一条
│ ...
```

**jsonStr 配置：**

```json
{
    "rows": {
        "1": {
            "cells": {"1": {"text": "员工信息明细表", "style": 5, "merge": [0, 5]}},
            "height": 45
        },
        "2": {
            "cells": {
                "1": {"text": "姓名：", "style": 6, "loopBlock": 1},
                "2": {"text": "#{emp.name}", "style": 7, "loopBlock": 1},
                "3": {"text": "所在部门：", "style": 6, "loopBlock": 1},
                "4": {"text": "#{emp.department}", "style": 7, "loopBlock": 1},
                "5": {"text": "#{emp.tm}", "style": 2, "merge": [2, 1], "loopBlock": 1,
                      "display": "qrcode", "config": "qr1"}
            },
            "height": 30
        },
        "3": {
            "cells": {
                "1": {"text": "年龄：", "style": 6, "loopBlock": 1},
                "2": {"text": "#{emp.age}", "style": 7, "loopBlock": 1},
                "3": {"text": "学历：", "style": 6, "loopBlock": 1},
                "4": {"text": "#{emp.education}", "style": 7, "loopBlock": 1}
            },
            "height": 30
        },
        "4": {
            "cells": {
                "1": {"text": "性别：", "style": 6, "loopBlock": 1},
                "2": {"text": "#{emp.sex}", "style": 7, "loopBlock": 1},
                "3": {"text": "薪水：", "style": 6, "loopBlock": 1},
                "4": {"text": "#{emp.salary}", "style": 7, "loopBlock": 1}
            },
            "height": 30
        },
        "5": {
            "cells": {
                "1": {"text": "", "loopBlock": 1},
                "2": {"text": "", "loopBlock": 1},
                "3": {"text": "", "loopBlock": 1},
                "4": {"text": "", "loopBlock": 1}
            },
            "height": 10
        },
        "len": 200
    },
    "loopBlockList": [{"sci": 1, "eci": 6, "sri": 2, "eri": 5, "index": 1, "db": "emp"}],
    "displayConfig": {
        "qr1": {"text": "#{emp.tm}", "width": 90, "height": 90, "colorDark": "#000000", "colorLight": "#ffffff"}
    },
    "merges": ["B1:G1", "F2:G4"]
}
```

**关键点：**
- 标签列用 bold 样式（style 6），值列用普通样式（style 7）
- **必须在循环块末尾加一行空行（height: 10px）作为卡片间隔**，否则记录之间会粘在一起
- 空行的单元格也需要 `"loopBlock": 1`
- loopBlockList 的 `eri` 要包含间隔行
- 二维码通过 `display: "qrcode"` + `config` 引用 displayConfig，不是必须的，可省略
- 二维码单元格用 `merge: [2, 1]` 跨3行2列

## 5.3 横向分组

积木报表有两种横向分组方式，根据场景选择：

### 选择决策

| 场景 | 推荐方式 | 说明 |
|------|---------|------|
| 表头1-3行 + 下方有数值需要动态填充 | **横向动态分组 (groupRight)** | 交叉表场景：行分组 × 列分组 = 动态值 |
| 每条记录横向展开，每行一个字段 | **自定义横向分组 (customGroup)** | 卡片横向展开，无需 dynamic 属性 |

**关键区别：** groupRight 必须配合 `dynamic()` 字段使用（交叉表的值单元格），customGroup 不需要。

---

### 5.3.1 横向动态分组 (groupRight + dynamic)

将某个字段的值横向展开为列头，配合 `dynamic()` 在交叉单元格中填充数据。适用于交叉表、月度统计等场景。

**参考文档：** https://help.jimureport.com/group/transverseDynamic

#### 核心语法

| 语法 | 用途 |
|------|------|
| `#{db.groupRight(field)}` | 横向展开列头（如月份、楼号） |
| `#{db.dynamic(field)}` | 交叉单元格动态值（如销售额、人数） |
| `#{db.group(field)}` | 纵向分组行头（如省份、社区） |

#### 布局模式

多级横向分组（月份 + 省份都横向展开，销售额为 dynamic 值）：

```
              省份月度销售统计
┌────────┬────────┬────────┬────────┬────────┬────────┬───
│ 月份   │  1月   │  1月   │  1月   │  2月   │  2月   │ ← groupRight(month)
│ 省份   │ 广东省 │ 江苏省 │ 浙江省 │ 广东省 │ 江苏省 │ ← groupRight(province)
│ 销售额 │ 85000  │ 72000  │ 65000  │ 92000  │ 68000  │ ← dynamic(sales)
└────────┴────────┴────────┴────────┴────────┴────────┴───
```

也支持纵向 + 横向混合（行头用 group，列头用 groupRight）：

```
┌────────┬────────┬────────┬────────┐
│ 省份   │  1月   │  2月   │  3月   │ ← groupRight(month)
│ 广东省 │ 85000  │ 92000  │ 78000  │ ← group(province) + dynamic(sales)
│ 江苏省 │ 72000  │ 68000  │ 81000  │
└────────┴────────┴────────┴────────┘
```

#### 单元格属性

**横向列头（groupRight）：** 蓝底白字表头样式
```json
{
    "text": "#{db.groupRight(field)}",
    "style": 4,
    "aggregate": "group",
    "direction": "right"
}
```

**动态值（dynamic）：** 普通数据行样式，与值字段保持一致
```json
{
    "text": "#{db.dynamic(field)}",
    "style": 2
}
```

**纵向行头（group，可选）：**
```json
{
    "text": "#{db.group(field)}",
    "style": 2,
    "aggregate": "group"
}
```

**完整 JSON 示例见** `examples/horizontal-group.md` 示例1 和 `examples/multi-level-header.md` 示例3。

#### 关键点

1. **最多支持3级动态表头** — groupRight 可嵌套最多3层
2. **必须有 dynamic 字段** — groupRight 列头下方必须有 `#{db.dynamic(field)}` 值字段，否则无法渲染
3. **groupRight 需要 merge 合并下方列数** — 横向分组单元格需要用 `merge: [0, N-1]` 合并 N 列（N = 下方 dynamic/compute 字段数）。例如下方有 sales、donation、compute 三个字段，则 groupRight 设置 `merge: [0, 2]` 合并3列
4. **第一条数据必须完整** — 如需显示1-12月列，数据集第一条记录必须包含所有月份
5. **groupRight 都是横向展开** — 多个 groupRight 字段各占一行，都向右展开
6. **dynamic 值行样式与数据一致** — 用普通数据样式，不要用表头样式
7. **merges 预留足够列** — 标题合并范围要预留横向展开的空间
8. **groupRight 和 dynamic/group 在相邻行** — groupRight 表头占一行，dynamic+group 数据在下一行，不要多加空行

#### 横向纵向组合分组（多级循环表头）

当报表同时需要**行头纵向分组** + **列头横向分组** + **动态数据填充**时，使用 group + groupRight + dynamic 组合。

**参考文档：** https://help.jimureport.com/group/directionDynamic
**完整 JSON 示例见** `examples/multi-level-header.md`（示例1：二级表头 + 示例2：纵横组合）。

| 部分 | 语法 | 说明 |
|------|------|------|
| 行头（纵向分组） | `#{db.group(field)}` | 纵向合并相同值 |
| 列头（横向分组） | `#{db.groupRight(field)}` | 横向展开为动态列 |
| 数据区域（动态值） | `#{db.dynamic(field)}` | 填充交叉单元格 |

**特殊规则：**
1. 动态列之前的列字段**必须**设置成纵向分组（group）
2. 横向分组下**必须**有动态列（dynamic）
3. 多个 dynamic 字段会在每个横向分组值下重复展开
4. 第一条数据必须完整
5. 最多3级动态表头

#### 横向分组小计/总计

**参考文档：** https://help.jimureport.com/group/horizontalSubtotal

两种方式：

**方式一：SUM 公式（表头固定，不循环）**

```
=SUM(D7,E7)     单元格逗号分隔
=SUM(M7:N7)     单元格范围（包含中间列）
```

适用于固定表头结构，放在数据行同行或总计行中。大小写均可。

**方式二：compute 表达式（表头动态循环）**

```
#{db.compute(field1+field2)}
```

示例：`#{area.compute(sales+gift)}` — 对每个横向分组内的 sales 和 gift 求和

- `compute` 为固定关键字，支持 `+` `-` `*` `/` 四则运算
- 适用于 groupRight 动态展开的场景，小计列会跟随横向分组自动循环
- 总计行也可使用同样方式

**选择依据：**

| 场景 | 推荐方式 |
|------|---------|
| 表头固定不变 | `=SUM(D7,E7)` 或 `=SUM(D7:F7)` |
| 表头由 groupRight 动态展开 | `#{db.compute(field1+field2)}` |

---

### 5.3.2 自定义横向分组 (customGroup)

将数据集的每条记录横向展开为列，每行显示一个字段。适用于横向统计表、数据透视等场景。

#### 核心语法

```
#{数据集编码.customGroup(字段名)}
```

### 与其他分组方式的区别

| 语法 | 方向 | 效果 |
|------|------|------|
| `#{db.group(field)}` | **纵向** | 按字段值分组，相同值合并行 |
| `#{db.groupRight(field)}` | **横向** | 按字段值动态展开列（交叉表） |
| `#{db.customGroup(field)}` | **横向** | 每条记录展开为一列，每行一个字段 |

### 布局模式

```
              标题
┌──────────┬────────┬────────┬────────┬───
│ 字段A标签 │ 记录1值 │ 记录2值 │ 记录3值 │ ← customGroup(fieldA) →
│ 字段B标签 │ 记录1值 │ 记录2值 │ 记录3值 │ ← customGroup(fieldB) →
│ 字段C标签 │ 记录1值 │ 记录2值 │ 记录3值 │ ← customGroup(fieldC) →
└──────────┴────────┴────────┴────────┴───
```

- **每行** = 一个字段，col 1 是标签，col 2 用 `customGroup` + `direction:"right"` 向右展开
- **每列** = 一条记录的所有字段值纵向排列
- 记录数量决定列数（动态扩展）

### 单元格关键属性

| 属性 | 值 | 说明 |
|------|-----|------|
| `text` | `#{db.customGroup(field)}` | 横向展开语法 |
| `direction` | `"right"` | **必须设置**，标记横向展开方向 |
| `rendered` | `""` | 渲染标记（第一个展开行需要） |
| `isDrag` | `true` | 行级属性，标记可拖拽 |
| `style` | 数值索引 | 标签列用 style 7（蓝底），值列用 style 11（白底居中带边框） |

### 完整参考 JSON（员工信息横向统计表）

来源：`examples/horizontal-group.md`，数据集编码 `hex`，字段为员工信息。

```json
{
    "loopBlockList": [],
    "printConfig": {"paper": "A4", "width": 210, "height": 297, "definition": 1, "isBackend": false, "marginX": 10, "marginY": 10},
    "area": {"sri": 7, "sci": 5, "eri": 7, "eci": 5, "width": 100, "height": 36},
    "rows": {
        "1": {
            "cells": {"0": {"text": "员工信息横向统计表", "style": 9, "merge": [0, 11]}},
            "height": 97
        },
        "2": {
            "cells": {
                "1": {"text": "部门", "style": 7},
                "2": {"text": "#{hex.customGroup(department)}", "style": 11, "direction": "right", "rendered": ""}
            },
            "isDrag": true, "height": 40
        },
        "3": {
            "cells": {
                "1": {"text": "学历", "style": 7},
                "2": {"text": "#{hex.customGroup(education)}", "style": 11, "direction": "right"}
            },
            "isDrag": true, "height": 39
        },
        "4": {
            "cells": {
                "1": {"text": "性别", "style": 7},
                "2": {"text": "#{hex.customGroup(sex)}", "style": 11, "direction": "right"}
            },
            "isDrag": true, "height": 41
        },
        "5": {
            "cells": {
                "1": {"text": "年龄", "style": 7},
                "2": {"text": "#{hex.customGroup(age)}", "style": 11}
            },
            "isDrag": true, "height": 39
        },
        "6": {
            "cells": {
                "1": {"text": "姓名", "style": 7},
                "2": {"text": "#{hex.customGroup(name)}", "style": 11, "direction": "right"}
            },
            "isDrag": true, "height": 40
        },
        "7": {
            "cells": {
                "1": {"text": "薪水", "style": 7},
                "2": {"text": "#{hex.customGroup(salary)}", "style": 11, "direction": "right"}
            },
            "isDrag": true, "height": 36
        },
        "len": 100
    },
    "cols": {"0": {"width": 44}, "1": {"width": 79}, "2": {"width": 81}, "len": 50},
    "merges": ["A2:L2"],
    "styles": [
        {"bgcolor": "#9cc2e6"},
        {"bgcolor": "#9cc2e6", "align": "center"},
        {"bgcolor": "#9cc2e6", "align": "center", "border": {"bottom": ["thin","#5b9cd6"], "top": ["thin","#5b9cd6"], "left": ["thin","#5b9cd6"], "right": ["thin","#5b9cd6"]}},
        {"border": {"bottom": ["thin","#5b9cd6"], "top": ["thin","#5b9cd6"], "left": ["thin","#5b9cd6"], "right": ["thin","#5b9cd6"]}},
        {"align": "center"},
        {"align": "center", "font": {"bold": true}},
        {"align": "center", "font": {"bold": true, "size": 14}},
        {"bgcolor": "#9cc2e6", "align": "center", "border": {"bottom": ["thin","#5b9cd6"], "top": ["thin","#5b9cd6"], "left": ["thin","#5b9cd6"], "right": ["thin","#5b9cd6"]}, "font": {"name": "宋体"}},
        {"border": {"bottom": ["thin","#5b9cd6"], "top": ["thin","#5b9cd6"], "left": ["thin","#5b9cd6"], "right": ["thin","#5b9cd6"]}, "font": {"name": "宋体"}},
        {"align": "center", "font": {"bold": true, "size": 14, "name": "宋体"}},
        {"align": "center", "font": {"bold": false, "size": 14, "name": "宋体"}},
        {"border": {"bottom": ["thin","#5b9cd6"], "top": ["thin","#5b9cd6"], "left": ["thin","#5b9cd6"], "right": ["thin","#5b9cd6"]}, "font": {"name": "宋体"}, "align": "center"}
    ]
}
```

### 关键样式索引

| 索引 | 效果 | 用途 |
|------|------|------|
| 7 | 蓝底(`#9cc2e6`)+居中+蓝边框+宋体 | 标签列（部门、学历、性别...） |
| 9 | 居中+加粗14号宋体 | 标题行 |
| 11 | 白底+居中+蓝边框+宋体 | 值列（customGroup展开的数据） |

### 关键点

1. **`direction: "right"` 必须设置** — 每个 customGroup 单元格都需要，否则不会横向展开
2. **第一行加 `rendered: ""`** — 第一个展开字段（如"部门"行）需要加 `rendered` 属性
3. **某行不加 `direction`** — 如"年龄"行无 `direction: "right"`，则该行数据纵向排列（不横向展开），可灵活混用
4. **`isDrag: true`** — 每个数据行需要设置
5. **area** — `area.sri`/`area.eri` 设为最后一个数据行的下一行位置
6. **cols 索引从 0 开始** — col 0 是标签列前的空列（width: 44），col 1 标签列，col 2 值列
7. **merges 留足空间** — 标题合并如 `"A2:L2"` 需要预留足够列数容纳横向展开
8. **loopBlockList 为空** — 自定义横向分组不使用循环块
9. **不要添加多余的辅助行** — 参考示例 JSON 中数据行之后无需额外空行。如果添加了含 `direction: "right"` 或 `aggregate: "group"` 的空行，会在设计器中显示多余的横向分组标识

标签列用蓝底（`#9cc2e6`）+ 蓝边框（`#5b9cd6`），值列用白底 + 蓝边框居中。

## 6. 查询配置

查询条件通过数据集的 `fieldList` 和 `paramList` 中的字段属性配置。

**参考文档：**
- https://help.jimureport.com/queryCriteria/api — API查询条件
- https://help.jimureport.com/queryCriteria/dictionary — 字典下拉
- https://help.jimureport.com/queryCriteria/sql — SQL动态条件
- https://help.jimureport.com/queryCriteria/apiByTime — 时间查询
- https://help.jimureport.com/queryCriteria/apiRange — 范围查询
- https://help.jimureport.com/queryCriteria/apiInterface — API接口参数接收

### 6.1 参数语法

| 语法 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `${paramName}` | 用户参数 | 需在报表参数/SQL中声明 | `${id}`, `${name}` |
| `#{sysVar}` | 系统变量 | 无需声明，自动解析 | `#{sysUserCode}` |

**SQL 示例：** `select * from demo where id='${id}' and create_by='#{sysUserCode}'`
**API 示例：** `http://host/api/getData?name=${name}&date=${date}`

### 系统变量

| 变量 | 说明 |
|------|------|
| `#{sysUserCode}` | 当前登录用户名 |
| `#{sysOrgCode}` | 当前登录用户部门编码 |
| `#{sysDate}` | 当前系统日期 |
| `#{sysDateTime}` | 当前系统日期时间 |
| `#{domainURL}` | 系统域名地址 |

### 6.2 查询控件配置（字段属性）

查询条件通过 `saveDb` 接口的 `fieldList` 或 `paramList` 中的字段属性控制：

| 字段属性 | 类型 | 说明 | 取值 |
|---------|------|------|------|
| `searchFlag` | Integer | 是否启用查询 | `1`=启用, `0`/null=不启用 |
| `searchMode` | Integer | 查询模式 | `1`=单条件, `2`=范围查询, `3`=多选 |
| `searchValue` | String | 查询默认值 | 静态值/表达式/系统变量 |
| `dictCode` | String | 字典编码（下拉数据源） | 字典编码/SQL/API地址 |
| `searchFormat` | String | 日期格式 | `yyyy-MM-dd`, `yyyy-MM-dd HH:mm:ss` |
| `widgetType` | String | 控件类型 | `String`, `Number`, `date`, `datetime` |
| `extJson` | String | 扩展配置JSON | `{"selectSearchPageSize":20}`, `{"loadTree":"..."}`, `{"required":true}` |

### searchMode 查询模式值

| searchMode | 类型 | 说明 |
|-----------|------|------|
| `1` | 文本输入 | 默认输入框 |
| `2` | 范围查询 | 日期/数值范围，自动生成 `_begin`/`_end` 参数 |
| `3` | 下拉多选 | 多选下拉框，需配合 dictCode |
| `4` | 下拉单选 | 单选下拉框，需配合 dictCode |
| `5` | 模糊查询 | 模糊匹配输入框 |
| `6` | 下拉树 | 树形下拉，需配合 extJson.loadTree |
| `7` | 自定义下拉框 | JS增强自定义下拉，需配合 JS 代码 |

### 查询控件类型对照

| 控件效果 | searchFlag | searchMode | dictCode | widgetType |
|---------|-----------|-----------|----------|-----------|
| 文本输入框 | 1 | 1 | 空 | String |
| 模糊查询输入框 | 1 | 5 | 空 | String |
| 下拉单选 | 1 | 4 | 字典编码/SQL/API | String |
| 下拉多选 | 1 | 3 | 字典编码/SQL/API | String |
| 范围查询（日期） | 1 | 2 | 空 | date |
| 范围查询（数值） | 1 | 2 | 空 | Number |
| 时间选择 | 1 | 1 | 空 | date/datetime |
| 下拉树 | 1 | 6 | 空 | String |
| 自定义下拉框 | 1 | 7 | 空 | String |

### 6.3 下拉数据源配置（dictCode）

三种方式，通过 `dictCode` 字段配置：

**系统字典：** 直接填字典编码（如 `sex`）

**SQL字典：**
```sql
SELECT username AS value, realname AS text FROM sys_user
```
> 注意：必须别名为 `value` 和 `text`，仅支持SQL数据源

**API字典：**
```
/jmreport/test/getDictSex?createBy=#{sysUserCode}
```
返回格式：`[{"text":"男","value":"1"},{"text":"女","value":"2"}]`

API字典支持（v1.7.9+）：
- `dictCode` — 字典编码
- `pageNo`/`pageSize` — 分页（默认10条）
- `searchText` — 搜索关键字
- `queryAll=true` — 返回全部数据

### 6.4 时间查询

将 `widgetType` 设为 `date` 或 `datetime`，日期以字符串格式传递。

**支持的日期格式：**

| 格式 | 示例 |
|------|------|
| `yyyy-MM-dd HH:mm:ss` | 2021-07-29 12:11:10 |
| `yyyy-MM-dd` | 2021-07-29 |
| `yyyy-MM` | 2021-07 |
| `yyyy` | 2021 |

**dateStr 默认值函数：**

| 表达式 | 结果 |
|--------|------|
| `=dateStr()` | 当前日期时间 |
| `=dateStr('yyyy-MM-dd')` | 当前日期 |
| `=dateStr('MM', 2)` | 当前月+2 |
| `=dateStr('dd', -1)` | 昨天 |
| `=dateStr('yyyy-MM', -1)` | 上个月 |

### 6.5 范围查询

`searchMode=2` 时启用范围查询。系统自动生成 `字段名_begin` 和 `字段名_end` 两个参数。

**默认值用管道符 `|` 分隔起止值：**

| 场景 | searchValue |
|------|------------|
| 数字范围 | `16\|22` |
| 本月1日到今天 | `=concat(string.substring(dateStr('yyyy-MM-dd'),0,8),'01')\|=dateStr('yyyy-MM-dd')` |
| 最近10天 | `=concat(dateStr('yyyy-MM-dd',-10),' 00:00:00')\|=dateStr('yyyy-MM-dd HH:mm:ss')` |

**API 后端接收：**
```java
@GetMapping("/getData")
public JSONObject getData(
    @RequestParam(name = "riqi_begin", required = false) String riqiBegin,
    @RequestParam(name = "riqi_end", required = false) String riqiEnd) { ... }
```

### 6.6 SQL条件表达式（FreeMarker语法）

```sql
select id, name, age from demo where create_by = '#{sysUserCode}'
<#if isNotEmpty(age)> and age = '${age}'</#if>
<#if isNotEmpty(name)> and name = '${name}'</#if>
```

**LIKE模糊查询：**
```sql
select * from demo where 1=1
<#if name?? && name?length gt 0>
  and name like concat('%', '${name}', '%')
</#if>
```

**DaoFormat 函数：**

| 函数 | 用途 | 示例 |
|------|------|------|
| `DaoFormat.in('${sex}')` | 字符串IN | `male,female` → `'male','female'` |
| `DaoFormat.inNumber('${age}')` | 数字IN | `21,22` → `21,22` |
| `DaoFormat.concat('${a}', ' 00:00:00')` | 拼接 | — |

### 6.7 下拉树控件

配置 `extJson`：`{"loadTree": "{{ domainURL }}/sys/user/treeTest"}`

接口返回格式：
```json
[
  {"id": "001", "pid": "", "value": "A01", "title": "节点1", "izLeaf": 0},
  {"id": "002", "pid": "001", "value": "A02", "title": "子节点1", "izLeaf": 1}
]
```

### 6.8 JS增强 API

| 方法 | 用途 |
|------|------|
| `updateSelectOptions(dbCode, fieldName, options)` | 动态更新下拉选项 |
| `onSearchFormChange(dbCode, fieldName, callback)` | 监听控件值变化 |
| `updateSearchFormValue(dbCode, fieldName, value)` | 设置控件初始值 |
| `getSelectOptions(dbCode, fieldName)` | 获取当前下拉选项 |
| `notLoadDataWhenShow()` | 预览时不自动加载数据 |

**三级联动下拉示例：**
```javascript
function init(){
  $http.metaGet('http://localhost:8080/jeecg-boot/ces/ai/customSelect')
    .then(res => { this.updateSelectOptions('pca', 'pro', res.data) })
  this.onSearchFormChange('pca', 'pro', (value) => {
    $http.metaGet('http://localhost:8080/jeecg-boot/ces/ai/customSelect', {pid: value})
      .then(res => { this.updateSelectOptions('pca', 'city', res.data) })
  })
  this.onSearchFormChange('pca', 'city', (value) => {
    $http.metaGet('http://localhost:8080/jeecg-boot/ces/ai/customSelect', {pid: value})
      .then(res => { this.updateSelectOptions('pca', 'area', res.data) })
  })
}
```

### 6.9 API 参数传递

**URL参数传递：** 预览时通过URL传参覆盖默认值
```
http://localhost:8085/jmreport/view/{reportId}?name=scott&age=25
```

**后端接收：**
- GET: `@RequestParam(name="name", required=false) String name`
- POST Body: `@RequestBody JSONObject json` → `json.getString("name")`

### 6.10 querySetting

```json
"querySetting": {
    "izOpenQueryBar": true,
    "izDefaultQuery": true
}
```

| 设置 | 默认值 | 说明 |
|------|--------|------|
| `izDefaultQuery` | true | 是否自动执行查询 |
| `izOpenQueryBar` | false | 是否默认展开查询栏（有查询条件时建议设为 true） |

### 6.11 fieldList 查询条件配置示例

在 `saveDb` 时通过 fieldList 配置查询条件：

```python
field_list = [
    # 普通字段（不查询）
    {"fieldName": "id", "fieldText": "ID", "widgetType": "String", "orderNum": 0},

    # 文本输入查询
    {"fieldName": "name", "fieldText": "姓名", "widgetType": "String", "orderNum": 1,
     "searchFlag": 1, "searchMode": 1},

    # 下拉单选（字典）
    {"fieldName": "sex", "fieldText": "性别", "widgetType": "String", "orderNum": 2,
     "searchFlag": 1, "searchMode": 4, "dictCode": "sex"},

    # 下拉多选（API）
    {"fieldName": "department", "fieldText": "部门", "widgetType": "String", "orderNum": 3,
     "searchFlag": 1, "searchMode": 3, "dictCode": "/jmreport/test/getDept"},

    # 日期范围查询
    {"fieldName": "create_time", "fieldText": "创建时间", "widgetType": "date", "orderNum": 4,
     "searchFlag": 1, "searchMode": 2, "searchFormat": "yyyy-MM-dd",
     "searchValue": "=dateStr('yyyy-MM-dd',-30)|=dateStr('yyyy-MM-dd')"},

    # 普通数据字段
    {"fieldName": "salary", "fieldText": "薪水", "widgetType": "Number", "orderNum": 5}
]
```

## 7. displayConfig 单元格组件

用于在普通单元格中渲染条码、二维码、图片。

### 使用方式

1. 在 `displayConfig` 中定义配置（key 为配置ID）
2. 在单元格中通过 `"display": "barcode"/"qrcode"` + `"config": "配置ID"` 引用

### 条形码配置（完整字段）

```json
{
    "displayConfig": {
        "bc1": {
            "barcodeContent": "#{order.order_no}",
            "format": "CODE128",
            "width": "2",
            "height": "50",
            "displayValue": false,
            "text": "",
            "textPosition": "bottom",
            "textAlign": "center",
            "fontSize": "20",
            "fontOptions": "",
            "lineColor": "#000",
            "background": "#fff"
        }
    }
}
```

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `barcodeContent` | 条码内容，支持 `#{db.field}` | 必填 |
| `format` | 条码格式 | `CODE128` |
| `width` | 条间距 | `"2"` |
| `height` | 高度 | `"50"` |
| `displayValue` | **是否显示文字，默认 false** | `false` |
| `text` | 覆盖显示的文字（为空则显示条码内容） | `""` |
| `textPosition` | 文字位置：`bottom`/`top` | `"bottom"` |
| `textAlign` | 文字对齐：`center`/`left`/`right` | `"center"` |
| `fontSize` | 文字大小 | `"20"` |
| `fontOptions` | 文字样式：`bold`/`italic`/`bold italic` | `""` |
| `lineColor` | 条颜色 | `"#000"` |
| `background` | 背景色 | `"#fff"` |

> **重要：** `displayValue` 默认为 `false`。只有用户明确要求显示文字时才设为 `true`。必须传完整字段，否则前端组件可能用默认值覆盖。

**单元格引用：**
```json
{"text": "#{order.order_no}", "style": 2, "display": "barcode", "config": "bc1"}
```

### 二维码配置

```json
{
    "displayConfig": {
        "qr1": {
            "text": "#{order.product_name}",
            "width": 80,
            "height": 80,
            "colorDark": "#000000",
            "colorLight": "#ffffff"
        }
    }
}
```

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `text` | 二维码内容，支持 `#{db.field}` | 必填 |
| `width` | 宽度(px) | `80` |
| `height` | 高度(px) | `80` |
| `colorDark` | 前景色 | `"#000000"` |
| `colorLight` | 背景色 | `"#ffffff"` |

**单元格引用：**
```json
{"text": "#{order.product_name}", "style": 2, "display": "qrcode", "config": "qr1"}
```

### JSON 数据集示例（订单报表含条形码+二维码）

```python
# JSON数据集 (dbType=3)
json_data = json.dumps({"data": [
    {"order_no": "ORD20240101001", "product_name": "iPhone 15 Pro", "price": 8999, "qty": 2, "total": 17998, "order_date": "2024-01-10", "status": "已发货"},
    {"order_no": "ORD20240101002", "product_name": "MacBook Air M3", "price": 9999, "qty": 1, "total": 9999, "order_date": "2024-01-15", "status": "已完成"}
]}, ensure_ascii=False)

# saveDb
db_data = {
    "dbType": "3",          # JSON数据集
    "jsonData": json_data,  # JSON字符串
    "isPage": "0",          # JSON数据集不分页
    ...
}

# displayConfig
display_config = {
    "qr_product": {"text": "#{order.product_name}", "width": 80, "height": 80, "colorDark": "#000000", "colorLight": "#ffffff"},
    "bc_order": {"barcodeContent": "#{order.order_no}", "format": "CODE128", "width": "2", "height": "50",
                 "displayValue": False, "text": "", "textPosition": "bottom", "textAlign": "center",
                 "fontSize": "20", "fontOptions": "", "lineColor": "#000", "background": "#fff"}
}

# 数据行单元格
"8": {"text": "#{order.product_name}", "style": 2, "display": "qrcode", "config": "qr_product"},
"9": {"text": "#{order.order_no}", "style": 2, "display": "barcode", "config": "bc_order"}
```

## 8. 顶层配置字段

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
| `chartList` | 图表列表 |
| `barcodeList` | 条码列表 |
| `qrcodeList` | 二维码列表 |
| `displayConfig` | 二维码/条码显示配置 |
| `dicts` | 引用的字典编码列表 |
| `printConfig` | 打印配置（纸张/方向/边距） |
| `merges` | 合并单元格列表（如 `"A2:H2"`），**必须同时在 cell 上设置 `merge` 属性** |
| `querySetting` | 查询设置 |
| `pyGroupEngine` | 是否使用Python分组引擎 |
