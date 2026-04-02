# 跟随分组扩展 + 多行汇总示例

## 场景说明

横向分组交叉报表，按「年份→月份」二级横向分组，按「地区」纵向分组，分组下方有3行汇总：总计(SUM)、最大值(MAX)、最小值(MIN)。第2、3行汇总需要 `rightFollowExten: "follow"` 跟随横向分组扩展。

**核心特性：** `rightFollowExten: "follow"` — 横向分组下方第二行起的单元格必须设置，否则横向展开时这些行不会跟随扩展。

## 布局模板

```
Row 1: 每月销售额统计（标题）
Row 2: 地区(↓合并1行) | #{ds.groupRight(year)}          ← 一级横向分组
Row 3:                | #{ds.groupRight(month)}         ← 二级横向分组
Row 4: #{ds.group(region)} | #{ds.dynamic(amount)}      ← 数据行
Row 5: 总计 | =SUM(C5)                                  ← 第1个汇总行（不需要 rightFollowExten）
Row 6: 最大值 | =MAX(C5)                                ← 第2个汇总行（需要 rightFollowExten）
Row 7: 最小值 | =MIN(C5)                                ← 第3个汇总行（需要 rightFollowExten）
```

预览效果（横向展开后）：
```
┌──────┬────────────────────────────┬────────────────────────────┐
│      │         2024年              │         2025年              │
│ 地区  ├───────┬───────┬───────┬────┼───────┬───────┬───────┬────┤
│      │ 1月   │ 2月   │ 3月   │ 4月 │ 1月   │ 2月   │ 3月   │ 4月 │
├──────┼───────┼───────┼───────┼────┼───────┼───────┼───────┼────┤
│ 华北  │ 32000 │ 28000 │ 35000 │... │ 36000 │ 31000 │ 39000 │... │
│ 华南  │ 45000 │ 38000 │ 42000 │... │ 49000 │ 41000 │ 46000 │... │
│ 华东  │ 55000 │ 48000 │ 52000 │... │ 58000 │ 51000 │ 56000 │... │
├──────┼───────┼───────┼───────┼────┼───────┼───────┼───────┼────┤
│ 总计  │132000 │114000 │129000 │... │143000 │123000 │141000 │... │
│ 最大值│ 55000 │ 48000 │ 52000 │... │ 58000 │ 51000 │ 56000 │... │
│ 最小值│ 32000 │ 28000 │ 35000 │... │ 36000 │ 31000 │ 39000 │... │
└──────┴───────┴───────┴───────┴────┴───────┴───────┴───────┴────┘
```

## rightFollowExten 配置规则

| 行 | 内容 | rightFollowExten | 说明 |
|----|------|-----------------|------|
| 数据行 | `#{ds.dynamic(amount)}` | 不需要 | 数据绑定行自动跟随 |
| 第1个汇总行 | `=SUM(C5)` | 不需要 | 分组下方第1行自动跟随 |
| 第2个汇总行 | `=MAX(C5)` | `"follow"` | 分组下方第2行起必须设置 |
| 第3个汇总行 | `=MIN(C5)` | `"follow"` | 同上 |

> **最后一列除外：** 如果有小计列（compute），最后一列不需要设置 rightFollowExten。

## 数据集配置

JSON 数据集（dbType="3"），24条数据（2年 × 4月 × 3地区），`isPage: "0"`（分组不分页）：

```json
{
    "data": [
        {"region": "华北", "year": "2024年", "month": "1月", "amount": 32000},
        {"region": "华北", "year": "2024年", "month": "2月", "amount": 28000},
        {"region": "华北", "year": "2024年", "month": "3月", "amount": 35000},
        {"region": "华北", "year": "2024年", "month": "4月", "amount": 41000},
        {"region": "华南", "year": "2024年", "month": "1月", "amount": 45000},
        {"region": "华南", "year": "2024年", "month": "2月", "amount": 38000},
        ...
        {"region": "华东", "year": "2025年", "month": "4月", "amount": 65000}
    ]
}
```

## rows 完整配置

```json
{
    "1": {
        "cells": {"1": {"text": "每月销售额统计", "style": 5, "merge": [0, 1], "height": 50}},
        "height": 50
    },
    "2": {
        "cells": {
            "1": {"text": "地区", "style": 4, "merge": [1, 0]},
            "2": {
                "text": "#{ds.groupRight(year)}",
                "style": 4,
                "aggregate": "group",
                "direction": "right",
                "textOrders": "2024年|2025年"
            }
        },
        "height": 34
    },
    "3": {
        "cells": {
            "2": {
                "text": "#{ds.groupRight(month)}",
                "style": 4,
                "aggregate": "group",
                "direction": "right",
                "textOrders": "1月|2月|3月|4月"
            }
        },
        "height": 34
    },
    "4": {
        "cells": {
            "1": {
                "text": "#{ds.group(region)}",
                "style": 2,
                "aggregate": "group",
                "subtotal": "groupField",
                "funcname": "-1",
                "subtotalText": "合计"
            },
            "2": {
                "text": "#{ds.dynamic(amount)}",
                "style": 2,
                "aggregate": "dynamic"
            }
        }
    },
    "5": {
        "cells": {
            "1": {"text": "总计", "style": 6},
            "2": {"text": "=SUM(C5)", "style": 6}
        },
        "height": 30
    },
    "6": {
        "cells": {
            "1": {"text": "最大值", "style": 6},
            "2": {"text": "=MAX(C5)", "style": 6, "rightFollowExten": "follow"}
        },
        "height": 30
    },
    "7": {
        "cells": {
            "1": {"text": "最小值", "style": 6},
            "2": {"text": "=MIN(C5)", "style": 6, "rightFollowExten": "follow"}
        },
        "height": 30
    },
    "len": 200
}
```

## save 请求体顶层配置

```python
save_data = {
    ...
    "isGroup": True,
    "groupField": "ds.region",
    ...
}
```

## merges 配置

```json
["B2:C2", "B3:B4"]
```

- `B2:C2` — 标题行合并
- `B3:B4` — "地区"表头向下合并（对应 cell 的 `merge: [1, 0]`）

## 结构要点

### 二级横向分组表头

| 行 | 内容 | 关键属性 |
|----|------|---------|
| Row 2 | 一级：`#{ds.groupRight(year)}` | `aggregate:"group"`, `direction:"right"` |
| Row 3 | 二级：`#{ds.groupRight(month)}` | `aggregate:"group"`, `direction:"right"` |

> 一级分组会自动合并其下的二级分组列。例如 "2024年" 会横跨 1月~4月 四列。

### 汇总公式引用规则

汇总行的公式引用的是**数据行所在列**。例如数据行在 Row 4（C列起），则：
- `=SUM(C5)` — C5 是数据行展开后的第一列数据
- 横向分组展开时，公式会自动复制到每个展开列

### 样式建议

- 边框统一用 `#d8d8d8` 浅灰（交叉表推荐）
- 汇总行用 `#FFF2CC` 淡黄底色区分
- 表头用 `#01b0f1` 蓝底白字
