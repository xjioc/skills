# 纵向分组 + 多级合并表头 + SUM公式小计 示例

**类型：** 纵向分组报表
**特征：** `group()` 纵向分组合并 + 四级合并表头 + `=SUM()` 公式小计 + SUM 聚合合计
**适用数据集：** SQL（dbType=0）、API（dbType=1）、JSON（dbType=3）等所有类型均可参考本示例的表头合并、分组小计、SUM 公式配置，仅数据集创建方式不同
**场景：** 学校经费统计，按学校类别分组，多层级财政经费表头（本例使用 JSON 数据集演示）

---

## 创作步骤

### Step 1：分析需求，确定列布局

根据数据字段推导出所有底层列（含计算列），从底部向上构建表头合并层级：

| 列号 | 归属 | 表头 | 数据绑定 |
|------|------|------|----------|
| B(1) | — | 学校类别 | `#{jfdb.group(class_type)}` |
| C(2) | — | 学校名称 | `#{jfdb.school}` |
| D(3) | 教育事业费 | 人员经费 | `#{jfdb.renyuan_jy}` |
| E(4) | 教育事业费>其中 | 日常公用费用 | `#{jfdb.richang_jy}` |
| F(5) | 教育事业费>其中 | 小计 | `=SUM(D6,E6)` |
| G(6) | 村投入 | 人员经费 | `#{jfdb.renyuan_ct}` |
| H(7) | 村投入 | 小计 | `=SUM(G6,I6,J6,K6)` |
| I(8) | 村投入>其中 | 日常公用 | `#{jfdb.richang_ct}` |
| J(9) | 村投入>其中 | 项目经费 | `#{jfdb.xiangmu_ct}` |
| K(10) | 村投入>其中 | 基建投入 | `#{jfdb.jichubokuan_ct}` |
| L(11) | 社会捐款 | 小计 | `=SUM(M6,N6)` |
| M(12) | 社会捐款>其中 | 项目经费 | `#{jfdb.xiangmu_sh}` |
| N(13) | 社会捐款>其中 | 基础投入 | `#{jfdb.jichubokuan_sh}` |

> **关键决策：SUM 公式 vs compute()**
>
> 当用户明确要求「所有数值列需要 SUM 合计」时，小计列**必须使用 `=SUM(cell,cell)` 公式**，不能用 `#{dbCode.compute(field+field)}`。
>
> | 方式 | 语法 | 适用场景 |
> |------|------|----------|
> | **SUM 公式** | `=SUM(D6,E6)` | 用户要求 SUM 合计、需要与 Excel 一致的公式风格 |
> | **compute** | `#{db.compute(f1+f2)}` | 用户未特别指定、纯后端计算即可 |
>
> 用户的原话是判断依据——说了 SUM 就用 SUM 公式，没说就默认 compute。

### Step 2：构建表头合并层级

从上到下规划每行的合并范围，确保每级 colspan 之和等于父级 colspan：

```
Row 0: 标题 ─────────────────────────── B1:N1
Row 1: 学校类别(rs4) | 学校名称(rs4) | 财政教育经费投入(cs3) | 其他投入(cs8)
Row 2:               |               | 教育事业费(cs3)      | 村投入(cs5) | 社会捐款(cs3)
Row 3:               |               | 人员经费(rs2)|其中(cs2)| 人员经费(rs2)|小计(rs2)|其中(cs3) | 小计(rs2)|其中(cs2)
Row 4:               |               |             |日常公用费用|小计|      |         |日常公用|项目经费|基建投入|       |项目经费|基础投入
Row 5: DATA ─────────────────────────── 数据绑定行
```

验证每级列数：
- 财政教育经费投入(cs3) = 教育事业费(cs3) ✓
- 其他投入(cs8) = 村投入(cs5) + 社会捐款(cs3) = 8 ✓
- 教育事业费(3) = 人员经费(rs2,1col) + 其中(cs2,2cols) = 3 ✓
- 村投入(5) = 人员经费(rs2,1col) + 小计(rs2,1col) + 其中(cs3,3cols) = 5 ✓
- 社会捐款(3) = 小计(rs2,1col) + 其中(cs2,2cols) = 3 ✓

### Step 3：配置分组与聚合

> **关键判断：用户是否要求分组小计行？**
>
> | 用户表述 | 是否生成分组小计 | 配置方式 |
> |----------|-----------------|----------|
> | "按XX分组，每组显示小计/合计" | **是** | group() + subtotal + funcname + isGroup + groupField |
> | "按XX分组合并"（仅合并，未提小计） | **否** | 只用 group() + aggregate，不设 subtotal/funcname/isGroup/groupField |
> | 未提及分组小计 | **否** | 同上 |
>
> **核心原则：用户没说要分组小计，就不要生成。** 只有明确要求"小计"、"合计"、"分组汇总"时才配置。

#### 方式A：仅分组合并（无小计行，默认）

分组字段只需 `group()` + `aggregate`，不设 subtotal/funcname：

```json
{
    "text": "#{jfdb.group(class_type)}",
    "style": 2,
    "aggregate": "group"
}
```

数值列无需 subtotal/funcname 属性。jsonStr 顶层**不需要** `isGroup` 和 `groupField`。

#### 方式B：分组合并 + 小计行（用户明确要求时）

**分组字段：**

```json
{
    "text": "#{jfdb.group(class_type)}",
    "aggregate": "group",
    "subtotal": "groupField",
    "funcname": "-1",
    "subtotalText": "小计"
}
```

**数值列（所有数值列均需 SUM 聚合）：**

```json
{
    "text": "#{jfdb.renyuan_jy}",
    "subtotal": "-1",
    "funcname": "SUM"
}
```

**SUM 公式小计列（同样需要聚合配置）：**

```json
{
    "text": "=SUM(D6,E6)",
    "subtotal": "-1",
    "funcname": "SUM"
}
```

> **注意：** SUM 公式列也要设置 `subtotal: "-1"` 和 `funcname: "SUM"`，否则分组小计行该列无数值。

**jsonStr 顶层（仅方式B需要）：**
```json
{
    "isGroup": true,
    "groupField": "jfdb.class_type"
}
```

save 请求体同样需要这两个字段（与 rows/cols 同级）。

### Step 4：创建数据集

根据数据集类型选择不同的创建方式，**表头合并、分组小计、SUM 公式等 jsonStr 配置完全相同**：

| 数据集类型 | dbType | 数据来源 | 关键差异 |
|-----------|--------|----------|----------|
| **SQL** | `"0"` | 数据库表 | `dbDynSql` 填 SQL 语句，可用 `queryFieldBySql` 解析字段 |
| **API** | `"1"` | 外部接口 | `dbDynSql` + `apiUrl` 填接口地址，`apiMethod` 指定 GET/POST |
| **JSON** | `"3"` | 静态数据 | `jsonData` 填 `{"data": [...]}` 格式，手动构建 fieldList |
| **JavaBean** | `"2"` | Java 类 | `dbDynSql` 填 Bean 类名 |

**本例使用 JSON 数据集（dbType="3"）：**

```json
{
    "dbType": "3",
    "dbCode": "jfdb",
    "isPage": "0",
    "jsonData": "{\"data\": [{\"class_type\": \"小学\", \"school\": \"实验小学\", ...}]}"
}
```

**若改用 SQL 数据集（dbType="0"）：**

```json
{
    "dbType": "0",
    "dbCode": "jfdb",
    "isPage": "0",
    "dbDynSql": "SELECT class_type, school, renyuan_jy, richang_jy, renyuan_ct, richang_ct, xiangmu_ct, jichubokuan_ct, xiangmu_sh, jichubokuan_sh FROM school_funds ORDER BY class_type",
    "fieldList": "通过 queryFieldBySql 解析获取"
}
```

> 分组报表 `isPage` 必须为 `"0"`（不分页），否则分组合并不完整。此规则对所有数据集类型通用。

### Step 5：保存报表

按标准流程 save(空) → saveDb → save(完整)。

---

## 效果预览

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      学校经费统计                                              │
├──────┬──────┬─────────────────────────┬──────────────────────────────────────────────────────┤
│      │      │ 财政教育经费投入（万元）    │                       其他投入                         │
│      │      ├─────────────────────────┼────────────────────────────────┬─────────────────────┤
│ 学校 │ 学校 │       教育事业费           │            村投入              │      社会捐款         │
│ 类别 │ 名称 ├────────┬────────────────┼────────┬──────┬──────────────┼──────┬──────────────┤
│      │      │ 人员经费│    其中         │ 人员经费│ 小计 │    其中       │ 小计 │    其中       │
│      │      │        ├──────────┬─────┤        │      ├────┬────┬───┤      ├────┬─────────┤
│      │      │        │日常公用费│小计  │        │      │日常│项目│基建│      │项目│基础投入  │
│      │      │        │用        │     │        │      │公用│经费│投入│      │经费│         │
├──────┼──────┼────────┼─────────┼─────┼────────┼──────┼────┼────┼───┼──────┼────┼─────────┤
│      │实验小 │ 120.5  │  45.3   │165.8│  30.2  │115.3 │15.1│20.0│50 │ 35   │10  │ 25      │
│ 小学 ├──────┼────────┼─────────┼─────┼────────┼──────┼────┼────┼───┼──────┼────┼─────────┤
│      │第一小 │  98.2  │  38.7   │136.9│  25.5  │ 87.8 │12.3│15  │35 │ 26   │ 8  │ 18      │
│      ├──────┼────────┼─────────┼─────┼────────┼──────┼────┼────┼───┼──────┼────┼─────────┤
│      │第三小 │  85.0  │  32.0   │117.0│  20.0  │ 70.0 │10  │12  │28 │ 21   │ 6  │ 15      │
├──────┼──────┼────────┼─────────┼─────┼────────┼──────┼────┼────┼───┼──────┼────┼─────────┤
│      │ 小计 │ 303.7  │ 116.0   │419.7│  75.7  │273.1 │37.4│47  │113│ 82   │24  │ 58      │
├──────┼──────┼────────┼─────────┼─────┼────────┼──────┼────┼────┼───┼──────┼────┼─────────┤
│ 初中 │...   │ ...    │ ...     │ ... │  ...   │ ...  │... │... │...│ ...  │... │ ...     │
├──────┼──────┼────────┼─────────┼─────┼────────┼──────┼────┼────┼───┼──────┼────┼─────────┤
│      │ 小计 │ ...    │ ...     │ ... │  ...   │ ...  │... │... │...│ ...  │... │ ...     │
└──────┴──────┴────────┴─────────┴─────┴────────┴──────┴────┴────┴───┴──────┴────┴─────────┘
```

---

## 核心配置

### 1. 分组字段声明

jsonStr 顶层需要两个属性：

```json
{
    "isGroup": true,
    "groupField": "jfdb.class_type"
}
```

### 2. 数据行分组绑定（code row 5）

```json
"5": {
    "cells": {
        "1": {
            "text": "#{jfdb.group(class_type)}",
            "style": 2,
            "aggregate": "group",
            "subtotal": "groupField",
            "funcname": "-1",
            "subtotalText": "小计"
        },
        "2": { "style": 2, "text": "#{jfdb.school}" },
        "3": { "style": 2, "text": "#{jfdb.renyuan_jy}", "subtotal": "-1", "funcname": "SUM" },
        "4": { "style": 2, "text": "#{jfdb.richang_jy}", "subtotal": "-1", "funcname": "SUM" },
        "5": { "style": 2, "text": "=SUM(D6,E6)", "subtotal": "-1", "funcname": "SUM" },
        "6": { "style": 2, "text": "#{jfdb.renyuan_ct}", "subtotal": "-1", "funcname": "SUM" },
        "7": { "style": 2, "text": "=SUM(G6,I6,J6,K6)", "subtotal": "-1", "funcname": "SUM" },
        "8": { "style": 2, "text": "#{jfdb.richang_ct}", "subtotal": "-1", "funcname": "SUM" },
        "9": { "style": 2, "text": "#{jfdb.xiangmu_ct}", "subtotal": "-1", "funcname": "SUM" },
        "10": { "style": 2, "text": "#{jfdb.jichubokuan_ct}", "subtotal": "-1", "funcname": "SUM" },
        "11": { "style": 2, "text": "=SUM(M6,N6)", "subtotal": "-1", "funcname": "SUM" },
        "12": { "style": 2, "text": "#{jfdb.xiangmu_sh}", "subtotal": "-1", "funcname": "SUM" },
        "13": { "style": 2, "text": "#{jfdb.jichubokuan_sh}", "subtotal": "-1", "funcname": "SUM" }
    },
    "height": 28
}
```

### 3. SUM 公式 vs compute 选择规则

| 用户表述 | 应使用 | 示例 |
|----------|--------|------|
| "所有数值列需要 SUM 合计" | **=SUM() 公式** | `=SUM(D6,E6)` |
| "需要 SUM" / "用 SUM" | **=SUM() 公式** | `=SUM(G6,I6,J6,K6)` |
| 未特别指定小计方式 | **compute()** | `#{db.compute(f1+f2)}` |
| "计算列" / "自动计算" | **compute()** | `#{db.compute(renyuan_jy+richang_jy)}` |

> **核心原则：** 用户明确说了 SUM，就必须用 `=SUM()` Excel 公式，不能用 `compute()`。用户的原话是判断标准。

### 4. 分组小计聚合配置

分组小计行需要两类单元格配置协同工作：

**分组字段（显示"小计"文本）：**

| 属性 | 值 | 说明 |
|------|-----|------|
| `text` | `#{dbCode.group(fieldName)}` | 分组绑定，相同值自动合并 |
| `aggregate` | `"group"` | 标记为分组聚合列 |
| `subtotal` | `"groupField"` | 启用小计行 |
| `funcname` | `"-1"` | 分组字段本身不计算 |
| `subtotalText` | `"小计"` | 小计行显示的文字 |

**数值字段（小计行自动 SUM）：**

| 属性 | 值 | 说明 |
|------|-----|------|
| `subtotal` | `"-1"` | 启用小计行数值回填 |
| `funcname` | `"SUM"` | 小计行使用 SUM 聚合 |

> **易错点：**
> - 聚合字段 `subtotal` 必须是 `"-1"`，不能设为 `"groupField"`
> - `"groupField"` 只用于分组依据字段（text 含 `group()` 的字段）
> - SUM 公式小计列（如 `=SUM(D6,E6)`）也需要 `subtotal: "-1"` + `funcname: "SUM"`，否则小计行该列为空

---

## 四级合并表头配置

### rows 布局

| 行号 | 用途 | 行高 |
|------|------|------|
| 0 | 标题（合并 B1:N1） | 42 |
| 1 | Level 1：学校类别(rs4) + 学校名称(rs4) + 财政(cs3) + 其他投入(cs8) | 36 |
| 2 | Level 2：教育事业费(cs3) + 村投入(cs5) + 社会捐款(cs3) | 34 |
| 3 | Level 3：人员经费(rs2) + 其中(csN) + 小计(rs2) | 32 |
| 4 | Level 4：底层列名（日常公用费用、小计、项目经费等） | 32 |
| 5 | 数据绑定行 | 28 |

### merges 合并

```json
[
    "B1:N1",
    "B2:B5", "C2:C5",
    "D2:F2", "G2:N2",
    "D3:F3", "G3:K3", "L3:N3",
    "D4:D5", "E4:F4",
    "G4:G5", "H4:H5", "I4:K4",
    "L4:L5", "M4:N4"
]
```

| 合并范围 | 说明 |
|----------|------|
| `B1:N1` | 标题行合并 |
| `B2:B5` | 学校类别 rowspan4 |
| `C2:C5` | 学校名称 rowspan4 |
| `D2:F2` | 财政教育经费投入（万元）colspan3 |
| `G2:N2` | 其他投入 colspan8 |
| `D3:F3` | 教育事业费 colspan3 |
| `G3:K3` | 村投入 colspan5 |
| `L3:N3` | 社会捐款 colspan3 |
| `D4:D5` | 人员经费(教育) rowspan2 |
| `E4:F4` | 其中(教育) colspan2 |
| `G4:G5` | 人员经费(村) rowspan2 |
| `H4:H5` | 小计(村) rowspan2 |
| `I4:K4` | 其中(村) colspan3 |
| `L4:L5` | 小计(社) rowspan2 |
| `M4:N4` | 其中(社) colspan2 |

---

## 完整 jsonStr

```json
{
    "loopBlockList": [],
    "querySetting": {
        "izOpenQueryBar": false,
        "izDefaultQuery": true
    },
    "recordSubTableOrCollection": { "group": [], "record": [], "range": [] },
    "printConfig": {
        "paper": "A4",
        "width": 297,
        "height": 210,
        "definition": 1,
        "isBackend": false,
        "marginX": 10,
        "marginY": 10,
        "layout": "landscape",
        "printCallBackUrl": ""
    },
    "hidden": { "rows": [], "cols": [], "conditions": { "rows": {}, "cols": {} } },
    "queryFormSetting": { "useQueryForm": false, "dbKey": "", "idField": "" },
    "dbexps": [],
    "dicts": [],
    "fillFormToolbar": {
        "show": true,
        "btnList": ["save", "subTable_add", "verify", "subTable_del", "print", "close", "first", "prev", "next", "paging", "total", "last", "exportPDF", "exportExcel", "exportWord"]
    },
    "freeze": "A1",
    "dataRectWidth": 1200,
    "isViewContentHorizontalCenter": false,
    "autofilter": {},
    "validations": [],
    "cols": {
        "0": { "width": 25 },
        "1": { "width": 80 },
        "2": { "width": 110 },
        "3": { "width": 90 },
        "4": { "width": 100 },
        "5": { "width": 85 },
        "6": { "width": 90 },
        "7": { "width": 110 },
        "8": { "width": 85 },
        "9": { "width": 85 },
        "10": { "width": 85 },
        "11": { "width": 90 },
        "12": { "width": 85 },
        "13": { "width": 85 },
        "len": 100
    },
    "area": { "sri": 0, "sci": 0, "eri": 5, "eci": 13, "width": 1200, "height": 230 },
    "pyGroupEngine": false,
    "submitHandlers": [],
    "hiddenCells": [],
    "zonedEditionList": [],
    "rows": {
        "0": {
            "cells": {
                "1": { "text": "学校经费统计", "style": 0, "merge": [0, 12] }
            },
            "height": 42
        },
        "1": {
            "cells": {
                "1": { "text": "学校类别", "style": 1, "merge": [3, 0] },
                "2": { "text": "学校名称", "style": 1, "merge": [3, 0] },
                "3": { "text": "财政教育经费投入（万元）", "style": 1, "merge": [0, 2] },
                "6": { "text": "其他投入", "style": 1, "merge": [0, 7] }
            },
            "height": 36
        },
        "2": {
            "cells": {
                "3": { "text": "教育事业费", "style": 1, "merge": [0, 2] },
                "6": { "text": "村投入", "style": 1, "merge": [0, 4] },
                "11": { "text": "社会捐款", "style": 1, "merge": [0, 2] }
            },
            "height": 34
        },
        "3": {
            "cells": {
                "3": { "text": "人员经费", "style": 1, "merge": [1, 0] },
                "4": { "text": "其中", "style": 1, "merge": [0, 1] },
                "6": { "text": "人员经费", "style": 1, "merge": [1, 0] },
                "7": { "text": "小计", "style": 1, "merge": [1, 0] },
                "8": { "text": "其中", "style": 1, "merge": [0, 2] },
                "11": { "text": "小计", "style": 1, "merge": [1, 0] },
                "12": { "text": "其中", "style": 1, "merge": [0, 1] }
            },
            "height": 32
        },
        "4": {
            "cells": {
                "4": { "text": "日常公用费用", "style": 1 },
                "5": { "text": "小计", "style": 1 },
                "8": { "text": "日常公用", "style": 1 },
                "9": { "text": "项目经费", "style": 1 },
                "10": { "text": "基建投入", "style": 1 },
                "12": { "text": "项目经费", "style": 1 },
                "13": { "text": "基础投入", "style": 1 }
            },
            "height": 32
        },
        "5": {
            "cells": {
                "1": {
                    "text": "#{jfdb.group(class_type)}",
                    "style": 2,
                    "aggregate": "group",
                    "subtotal": "groupField",
                    "funcname": "-1",
                    "subtotalText": "小计"
                },
                "2": { "style": 2, "text": "#{jfdb.school}" },
                "3": { "style": 2, "text": "#{jfdb.renyuan_jy}", "subtotal": "-1", "funcname": "SUM" },
                "4": { "style": 2, "text": "#{jfdb.richang_jy}", "subtotal": "-1", "funcname": "SUM" },
                "5": { "style": 2, "text": "=SUM(D6,E6)", "subtotal": "-1", "funcname": "SUM" },
                "6": { "style": 2, "text": "#{jfdb.renyuan_ct}", "subtotal": "-1", "funcname": "SUM" },
                "7": { "style": 2, "text": "=SUM(G6,I6,J6,K6)", "subtotal": "-1", "funcname": "SUM" },
                "8": { "style": 2, "text": "#{jfdb.richang_ct}", "subtotal": "-1", "funcname": "SUM" },
                "9": { "style": 2, "text": "#{jfdb.xiangmu_ct}", "subtotal": "-1", "funcname": "SUM" },
                "10": { "style": 2, "text": "#{jfdb.jichubokuan_ct}", "subtotal": "-1", "funcname": "SUM" },
                "11": { "style": 2, "text": "=SUM(M6,N6)", "subtotal": "-1", "funcname": "SUM" },
                "12": { "style": 2, "text": "#{jfdb.xiangmu_sh}", "subtotal": "-1", "funcname": "SUM" },
                "13": { "style": 2, "text": "#{jfdb.jichubokuan_sh}", "subtotal": "-1", "funcname": "SUM" }
            },
            "height": 28
        },
        "len": 200
    },
    "rpbar": { "show": true, "pageSize": "", "btnList": [] },
    "groupField": "jfdb.class_type",
    "fixedPrintHeadRows": [],
    "fixedPrintTailRows": [],
    "displayConfig": {},
    "fillFormInfo": { "layout": { "direction": "horizontal", "width": 200, "height": 45 } },
    "background": false,
    "name": "sheet1",
    "styles": [
        {
            "border": { "bottom": ["thin", "#d8d8d8"], "top": ["thin", "#d8d8d8"], "left": ["thin", "#d8d8d8"], "right": ["thin", "#d8d8d8"] },
            "align": "center",
            "valign": "middle",
            "font": { "bold": true, "size": 14 }
        },
        {
            "border": { "bottom": ["thin", "#d8d8d8"], "top": ["thin", "#d8d8d8"], "left": ["thin", "#d8d8d8"], "right": ["thin", "#d8d8d8"] },
            "align": "center",
            "valign": "middle",
            "bgcolor": "#00B050",
            "color": "#ffffff"
        },
        {
            "border": { "bottom": ["thin", "#d8d8d8"], "top": ["thin", "#d8d8d8"], "left": ["thin", "#d8d8d8"], "right": ["thin", "#d8d8d8"] },
            "align": "center",
            "valign": "middle"
        }
    ],
    "isGroup": true,
    "freezeLineColor": "rgb(185, 185, 185)",
    "merges": [
        "B1:N1",
        "B2:B5", "C2:C5",
        "D2:F2", "G2:N2",
        "D3:F3", "G3:K3", "L3:N3",
        "D4:D5", "E4:F4",
        "G4:G5", "H4:H5", "I4:K4",
        "L4:L5", "M4:N4"
    ]
}
```

## 样式方案（绿色主题）

| 索引 | 背景色 | 字体色 | 用途 |
|------|--------|--------|------|
| 0 | — | — | 标题（14号加粗居中） |
| 1 | #00B050 | #ffffff | **表头行**（绿底白字） |
| 2 | — | — | **数据行**（白底居中） |

## 数据集配置（按类型）

### JSON 数据集（dbType="3"，本例使用）

```json
{
    "dbType": "3",
    "dbCode": "jfdb",
    "dbChName": "学校经费数据",
    "isPage": "0",
    "isList": "1",
    "jsonData": "{\"data\": [{\"class_type\": \"小学\", \"school\": \"实验小学\", \"renyuan_jy\": 120.5, \"richang_jy\": 45.3, \"renyuan_ct\": 30.2, \"richang_ct\": 15.1, \"xiangmu_ct\": 20.0, \"jichubokuan_ct\": 50.0, \"xiangmu_sh\": 10.0, \"jichubokuan_sh\": 25.0}]}",
    "fieldList": [
        {"fieldName": "class_type", "fieldText": "学校类别", "widgetType": "String", "orderNum": 0},
        {"fieldName": "school", "fieldText": "学校名称", "widgetType": "String", "orderNum": 1},
        {"fieldName": "renyuan_jy", "fieldText": "人员经费-教育事业费", "widgetType": "Number", "orderNum": 2},
        {"fieldName": "richang_jy", "fieldText": "日常公用费用-教育事业费", "widgetType": "Number", "orderNum": 3},
        {"fieldName": "renyuan_ct", "fieldText": "人员经费-村投入", "widgetType": "Number", "orderNum": 4},
        {"fieldName": "richang_ct", "fieldText": "日常公用-村投入", "widgetType": "Number", "orderNum": 5},
        {"fieldName": "xiangmu_ct", "fieldText": "项目经费-村投入", "widgetType": "Number", "orderNum": 6},
        {"fieldName": "jichubokuan_ct", "fieldText": "基建投入-村投入", "widgetType": "Number", "orderNum": 7},
        {"fieldName": "xiangmu_sh", "fieldText": "项目经费-社会捐款", "widgetType": "Number", "orderNum": 8},
        {"fieldName": "jichubokuan_sh", "fieldText": "基础投入-社会捐款", "widgetType": "Number", "orderNum": 9}
    ]
}
```

> **注意：** JSON 数据集 jsonData 必须用 `{"data": [...]}` 格式包裹，禁止直接传数组 `[...]`。

### SQL 数据集（dbType="0"）

```json
{
    "dbType": "0",
    "dbCode": "jfdb",
    "dbChName": "学校经费数据",
    "dbSource": "",
    "isPage": "0",
    "isList": "1",
    "dbDynSql": "SELECT class_type, school, renyuan_jy, richang_jy, renyuan_ct, richang_ct, xiangmu_ct, jichubokuan_ct, xiangmu_sh, jichubokuan_sh FROM school_funds ORDER BY class_type",
    "fieldList": "通过 queryFieldBySql 接口解析获取",
    "paramList": []
}
```

> SQL 数据集使用 `queryFieldBySql` 解析字段，分组报表 SQL 必须包含 `ORDER BY 分组字段`。

### API 数据集（dbType="1"）

```json
{
    "dbType": "1",
    "dbCode": "jfdb",
    "dbChName": "学校经费数据",
    "isPage": "0",
    "isList": "1",
    "dbDynSql": "http://api.example.com/school/funds",
    "apiUrl": "http://api.example.com/school/funds",
    "apiMethod": "0",
    "fieldList": "手动构建或从接口返回推断"
}
```

> API 数据集 `dbDynSql` 和 `apiUrl` 必须同时设置为接口地址。

### 通用规则（所有数据集类型）

- 分组报表 `isPage` 必须为 `"0"`（不分页），否则分组合并不完整
- `dbCode` 是数据绑定的前缀，jsonStr 中通过 `#{dbCode.fieldName}` 引用
- 表头合并（merges）、分组小计（group/subtotal）、SUM 公式等 **jsonStr 配置与数据集类型无关**
