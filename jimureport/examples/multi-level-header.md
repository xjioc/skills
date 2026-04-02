# 多级循环表头示例（横向纵向组合分组）

**类型：** 多级循环表头（交叉表）
**特征：** `groupRight()` 横向展开表头 + `dynamic()` 填充数据 + `group()` 纵向分组
**参考文档：** https://help.jimureport.com/group/directionDynamic

---

## 示例1：各地区商品销售额一栏表（二级横向表头）

year（年份）和 mouth（月份）作为二级横向表头动态展开，diqu（地区）和 class（类别）纵向分组，sales（销售额）为交叉数据。

### 效果预览

```
┌──────────────────────────────────────────────────────┐
│              各地区商品销售额一栏表                       │
├──────┬──────┬───────────────────┬───────────────────┤
│ 地区 ＼时间 │       2019年       │      2020年        │ ← groupRight(year)
│  ＼销量    ├────┬────┬────┬────┼────┬────┬────┬────┤
│            │1月 │2月 │... │12月│6月 │7月 │... │12月│ ← groupRight(mouth)
├──────┬─────┼────┼────┼────┼────┼────┼────┼────┼────┤
│      │调味品│840 │570 │... │271 │128 │213 │... │271 │ ← dynamic(sales)
│ 华北 ├─────┼────┼────┼────┼────┼────┼────┼────┼────┤
│      │肉类  │... │... │... │... │... │... │... │... │
├──────┼─────┼────┼────┼────┼────┼────┼────┼────┼────┤
│ 华东 │...  │... │... │... │... │... │... │... │... │
├──────┴─────┼────┼────┼────┼────┼────┼────┼────┼────┤
│    总计     │=SUM│    │    │    │    │    │    │    │
└────────────┴────┴────┴────┴────┴────┴────┴────┴────┘
```

### 核心语法

| 行 | 字段 | 语法 | 属性 | 说明 |
|----|------|------|------|------|
| Row 1 | year | `#{db.groupRight(year)}年` | `aggregate:"group"`, `direction:"right"` | 一级表头，横向展开 |
| Row 2 | mouth | `#{db.groupRight(mouth)}` | `aggregate:"group"`, `direction:"right"` | 二级表头，嵌套在 year 下 |
| Row 3 | diqu | `#{db.group(diqu)}` | `aggregate:"group"` | 纵向分组，相同值合并 |
| Row 3 | class | `#{db.group(class)}` | `aggregate:"group"` | 纵向分组 |
| Row 3 | sales | `#{db.dynamic(sales)}` | `aggregate:"dynamic"` | 交叉数据填充 |

### 斜线表头

```json
{
    "text": "地区|销量|时间",
    "lineStart": "lefttop",
    "merge": [1, 1],
    "style": 2
}
```
- `lineStart: "lefttop"` — 从左上角画斜线
- `text` 用 `|` 分隔多个标签（左下、中间、右上）

### rows 布局（行号从 0 开始）

| 行号 | 用途 | 关键属性 |
|------|------|---------|
| 0 | 标题（合并3列） | `merge:[0,2]`, style 6 |
| 1 | 一级表头：斜线表头 + year 横向 | `lineStart:"lefttop"`, `groupRight(year)`, `direction:"right"` |
| 2 | 二级表头：mouth 横向 | `groupRight(mouth)`, `direction:"right"` |
| 3 | 数据行：地区分组 + 类别分组 + 销售额动态 | `group(diqu)`, `group(class)`, `dynamic(sales)` |
| 4 | 总计行 | `=SUM(D4)` |

### 顶层分组配置

```json
{
    "isGroup": true,
    "groupField": "db.diqu"
}
```

### merges 合并

```json
["B1:D1", "B2:C3", "B5:C5"]
```
- `B1:D1` — 标题合并
- `B2:C3` — 斜线表头占 2行2列
- `B5:C5` — 总计行合并

### 完整 jsonStr

```json
{"loopBlockList":[],"querySetting":{"izOpenQueryBar":false,"izDefaultQuery":true},"recordSubTableOrCollection":{"group":[],"record":[],"range":[]},"printConfig":{"layout":"landscape","paper":"A3","isBackend":false,"width":297,"definition":1,"marginX":10,"height":420,"marginY":10},"hidden":{"rows":[],"cols":[]},"queryFormSetting":{"useQueryForm":false,"dbKey":"","idField":""},"dbexps":[],"toolPrintSizeObj":{"printType":"A4","widthPx":718,"heightPx":1047},"dicts":[],"fillFormToolbar":{"show":true,"btnList":["save","subTable_add","verify","subTable_del","print","close","first","prev","next","paging","total","last","exportPDF","exportExcel","exportWord"]},"freeze":"A1","dataRectWidth":303,"isViewContentHorizontalCenter":false,"autofilter":{},"validations":[],"cols":{"0":{"width":36},"1":{"width":87},"2":{"width":80},"len":100},"area":{"sri":11,"sci":4,"eri":11,"eci":4,"width":100,"height":25},"pyGroupEngine":false,"submitHandlers":[],"excel_config_id":"报表ID","hiddenCells":[],"zonedEditionList":[],"rows":{"0":{"cells":{"0":{"rendered":"","text":""},"1":{"merge":[0,2],"style":6,"text":"各地区商品销售额一栏表"}},"height":83},"1":{"cells":{"1":{"rendered":"","lineStart":"lefttop","merge":[1,1],"style":2,"text":"地区|销量|时间"},"3":{"style":8,"text":"#{db.groupRight(year)}年","aggregate":"group","direction":"right"}},"height":40},"2":{"cells":{"3":{"style":8,"text":"#{db.groupRight(mouth)}","aggregate":"group","direction":"right"}},"height":34},"3":{"cells":{"1":{"style":28,"text":"#{db.group(diqu)}","aggregate":"group"},"2":{"style":28,"text":"#{db.group(class)}","aggregate":"group"},"3":{"decimalPlaces":"0","rendered":"","style":31,"text":"#{db.dynamic(sales)}","aggregate":"dynamic"}},"height":38},"4":{"cells":{"1":{"merge":[0,1],"style":24,"text":"总计"},"3":{"style":25,"text":"=SUM(D4)"}},"height":37},"len":100},"rpbar":{"show":true,"pageSize":"","btnList":[]},"groupField":"db.diqu","fixedPrintHeadRows":[],"fixedPrintTailRows":[],"displayConfig":{},"fillFormInfo":{"layout":{"direction":"horizontal","width":200,"height":45}},"background":false,"name":"sheet1","styles":[{"bgcolor":"#5b9cd6"},{"bgcolor":"#5b9cd6","color":"#ffffff"},{"border":{"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]},"bgcolor":"#5b9cd6","color":"#ffffff"},{"border":{"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]}},{"font":{"size":16}},{"font":{"size":16,"bold":true}},{"align":"center","font":{"size":16,"bold":true}},{"border":{"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]},"align":"center"},{"border":{"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]},"bgcolor":"#5b9cd6","color":"#ffffff","align":"center"},{"bgcolor":"#9cc2e6"},{"bgcolor":"#9cc2e6","align":"center"},{"align":"center"},{"bgcolor":"#9cc2e6","format":"number"},{"bgcolor":"#9cc2e6","format":"number","align":"center"},{"border":{"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]},"align":"center","font":{"size":9}},{"border":{"top":["thin","#000"],"left":["thin","#000"],"bottom":["thin","#000"],"right":["thin","#000"]},"bgcolor":"#5b9cd6","color":"#ffffff"},{"bgcolor":"#5b9cd6","color":"#ffffff","align":"center"},{"border":{"top":["thin","#000"],"left":["thin","#000"],"bottom":["thin","#000"],"right":["thin","#000"]},"bgcolor":"#5b9cd6","color":"#ffffff","align":"center"},{"border":{"top":["thin","#000"],"left":["thin","#000"],"bottom":["thin","#000"],"right":["thin","#000"]},"align":"center","font":{"size":9}},{"border":{"top":["thin","#000"],"left":["thin","#000"],"bottom":["thin","#000"],"right":["thin","#000"]},"bgcolor":"#9cc2e6","align":"center"},{"border":{"top":["thin","#000"],"left":["thin","#000"],"bottom":["thin","#000"],"right":["thin","#000"]},"bgcolor":"#9cc2e6","format":"number","align":"center"},{"border":{"top":["thin","#000"],"left":["thin","#000"],"bottom":["thin","#000"],"right":["thin","#000"]},"bgcolor":"#5b9cd6","color":"#fe0000"},{"color":"#fe0000"},{"color":"#ffffff"},{"border":{"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]},"bgcolor":"#9cc2e6","align":"center"},{"border":{"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]},"bgcolor":"#9cc2e6","format":"number","align":"center"},{"border":{"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]},"underline":true,"align":"center","font":{"size":9}},{"border":{"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]},"underline":false,"align":"center","font":{"size":9}},{"border":{"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]},"bgcolor":"#d7f2f9","align":"center","font":{"size":9}},{"border":{"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]},"format":"number","align":"center","font":{"size":9}},{"border":{"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]},"bgcolor":"#ffff01","format":"number","align":"center","font":{"size":9}},{"border":{"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]},"bgcolor":"#ffffff","format":"number","align":"center","font":{"size":9}}],"fillFormStyle":"default","isGroup":true,"freezeLineColor":"rgb(185, 185, 185)","merges":["B1:D1","B2:C3","B5:C5"]}
```

---

## 示例2：区域省份按月销售统计（纵向+横向组合）

行头纵向分组（区域+省份），列头横向分组（月份），多个动态值字段（销售额+捐赠）。

### 效果预览

```
┌────────┬────────┬──────────────────┬──────────────────┬───
│        │        │       1月        │       2月        │ ← groupRight(month)
│ 区域   │ 省份   ├────────┬─────────┼────────┬─────────┤
│        │        │ 销售额 │ 捐赠    │ 销售额 │ 捐赠    │ ← dynamic(sales), dynamic(gift)
├────────┼────────┼────────┼─────────┼────────┼─────────┤
│ 华南   │ 广东   │ 50000  │ 2000    │ 60000  │ 2500    │ ← group(region) + group(province)
│        │ 广西   │ 35000  │ 1500    │ 42000  │ 1800    │
│ 华东   │ 江苏   │ 45000  │ 1800    │ 55000  │ 2200    │
└────────┴────────┴────────┴─────────┴────────┴─────────┘
```

### 核心语法

| 部分 | 语法 | 说明 |
|------|------|------|
| 行头（纵向分组） | `#{db.group(region)}`, `#{db.group(province)}` | 纵向合并相同值 |
| 列头（横向分组） | `#{db.groupRight(month)}` | 横向展开为动态列 |
| 数据区域（动态值） | `#{db.dynamic(sales)}`, `#{db.dynamic(gift)}` | 填充交叉单元格，每个横向分组值下重复展开 |

### 完整 JSON

```json
{
    "rows": {
        "1": {
            "cells": {"1": {"text": "区域销售统计", "style": 5, "merge": [0, 7]}},
            "height": 45
        },
        "2": {
            "cells": {
                "1": {"text": "区域", "style": 4},
                "2": {"text": "省份", "style": 4},
                "3": {"text": "#{area.groupRight(month)}", "style": 4,
                      "aggregate": "group", "direction": "right"}
            },
            "height": 34
        },
        "3": {
            "cells": {
                "1": {"text": "#{area.group(region)}", "style": 2, "aggregate": "group"},
                "2": {"text": "#{area.group(province)}", "style": 2, "aggregate": "group"},
                "3": {"text": "#{area.dynamic(sales)}", "style": 2},
                "4": {"text": "#{area.dynamic(gift)}", "style": 2}
            }
        },
        "len": 200
    },
    "cols": {"1": {"width": 80}, "2": {"width": 80}, "3": {"width": 100}, "4": {"width": 100}, "len": 100},
    "merges": ["B1:I1"]
}
```

---

## 示例3：省份月度销售统计（纯横向多级）

月份和省份都横向展开（groupRight），销售额为动态值。无纵向分组。

### 效果预览

```
              省份月度销售统计
┌────────┬────────┬────────┬────────┬────────┬───
│ 月份   │  1月   │  1月   │  1月   │  2月   │ ← groupRight(month)
│ 省份   │ 广东省 │ 江苏省 │ 浙江省 │ 广东省 │ ← groupRight(province)
│ 销售额 │ 85000  │ 72000  │ 65000  │ 92000  │ ← dynamic(sales)
└────────┴────────┴────────┴────────┴────────┴───
```

### 完整 JSON

```json
{
    "rows": {
        "1": {
            "cells": {"1": {"text": "省份月度销售统计", "style": 5, "merge": [0, 7]}},
            "height": 45
        },
        "2": {
            "cells": {
                "1": {"text": "月份", "style": 4},
                "2": {"text": "#{pms.groupRight(month)}", "style": 4,
                      "aggregate": "group", "direction": "right"}
            },
            "height": 34
        },
        "3": {
            "cells": {
                "1": {"text": "省份", "style": 4},
                "2": {"text": "#{pms.groupRight(province)}", "style": 4,
                      "aggregate": "group", "direction": "right"}
            },
            "height": 34
        },
        "4": {
            "cells": {
                "1": {"text": "销售额", "style": 2},
                "2": {"text": "#{pms.dynamic(sales)}", "style": 2}
            }
        },
        "len": 200
    },
    "cols": {"1": {"width": 80}, "2": {"width": 100}, "len": 100},
    "merges": ["B1:I1"]
}
```

---

## 示例4：交叉报表（年度学生成绩）

**场景：** 年度横向展开，班级+学生纵向分组，考试总成绩为交叉值
**参考文档：** https://help.jimureport.com/datareport/crossReport
**数据集类型：** JSON 数据集（dbType: "3"）

### 效果预览

```
┌─────────────────────────────────────────────┐
│           年度学生成绩交叉报表                  │
├──────┬──────┬────────┬────────┬────────┤
│班级\学生    │ 2022年 │ 2023年 │ 2024年 │ ← groupRight(year)
│  成绩\年度  │        │        │        │   斜线表头
├──────┼──────┼────────┼────────┼────────┤
│      │ 张三 │  580   │  612   │  645   │
│ 一班 │ 李四 │  520   │  558   │  590   │ ← group(class_name) + group(student)
│      │ 王五 │  495   │  530   │  562   │   + dynamic(total_score)
├──────┼──────┼────────┼────────┼────────┤
│ 二班 │ 赵六 │  610   │  635   │  668   │
│      │ ...  │  ...   │  ...   │  ...   │
├──────┴──────┼────────┼────────┼────────┤
│    总计      │=SUM(D3)│        │        │
└─────────────┴────────┴────────┴────────┘
```

### 核心语法

| 行 | 字段 | 语法 | 属性 |
|----|------|------|------|
| Row 1 | year | `#{score.groupRight(year)}年` | `aggregate:"group"`, `direction:"right"` |
| Row 2 | class_name | `#{score.group(class_name)}` | `aggregate:"group"` |
| Row 2 | student | `#{score.group(student)}` | `aggregate:"group"` |
| Row 2 | total_score | `#{score.dynamic(total_score)}` | `aggregate:"dynamic"` |
| Row 3 | 总计 | `=SUM(D3)` | — |

### 完整 JSON

```json
{
    "rows": {
        "0": {
            "cells": {
                "0": {"rendered": "", "text": ""},
                "1": {"merge": [0, 2], "style": 6, "text": "年度学生成绩交叉报表"}
            },
            "height": 70
        },
        "1": {
            "cells": {
                "1": {"rendered": "", "lineStart": "lefttop", "merge": [0, 1], "style": 2,
                      "text": "班级\\学生|成绩|年度"},
                "3": {"style": 8, "text": "#{score.groupRight(year)}年",
                      "aggregate": "group", "direction": "right"}
            },
            "height": 45
        },
        "2": {
            "cells": {
                "1": {"style": 9, "text": "#{score.group(class_name)}", "aggregate": "group"},
                "2": {"style": 9, "text": "#{score.group(student)}", "aggregate": "group"},
                "3": {"decimalPlaces": "0", "rendered": "", "style": 10,
                      "text": "#{score.dynamic(total_score)}", "aggregate": "dynamic"}
            },
            "height": 35
        },
        "3": {
            "cells": {
                "1": {"merge": [0, 1], "style": 11, "text": "总计"},
                "3": {"style": 12, "text": "=SUM(D3)"}
            },
            "height": 35
        },
        "len": 100
    },
    "cols": {"0": {"width": 36}, "1": {"width": 80}, "2": {"width": 80}, "3": {"width": 90}, "len": 100},
    "merges": ["B1:D1", "B2:C2", "B4:C4"],
    "isGroup": true,
    "groupField": "score.class_name",
    "styles": [
        {"bgcolor": "#5b9cd6"},
        {"bgcolor": "#5b9cd6", "color": "#ffffff"},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}, "bgcolor": "#5b9cd6", "color": "#ffffff"},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}},
        {"font": {"size": 16}},
        {"font": {"size": 16, "bold": true}},
        {"align": "center", "font": {"size": 16, "bold": true}},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}, "align": "center"},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}, "bgcolor": "#5b9cd6", "color": "#ffffff", "align": "center"},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}, "bgcolor": "#9cc2e6", "align": "center"},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}, "align": "center", "font": {"size": 9}},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}, "bgcolor": "#9cc2e6", "align": "center"},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}, "bgcolor": "#9cc2e6", "format": "number", "align": "center"}
    ]
}
```

### 关键样式索引

| 索引 | 效果 | 用途 |
|------|------|------|
| 2 | 深蓝底白字+边框 | 斜线表头 |
| 6 | 居中+加粗16号 | 标题行 |
| 8 | 深蓝底白字+居中+边框 | 横向表头（年度） |
| 9 | 浅蓝底+居中+边框 | 纵向分组（班级、学生） |
| 10 | 白底+居中+9号字+边框 | dynamic 数据值 |
| 11/12 | 浅蓝底+居中+边框 | 总计标签/总计值 |

### 与多级循环表头的区别

| 特性 | 交叉报表（本示例） | 多级循环表头（示例1） |
|------|-----------------|-------------------|
| 横向表头层数 | 1层（year） | 2层（year + mouth） |
| 纵向分组 | 有（class_name + student） | 有（diqu + class） |
| 斜线表头 | 2格合并（班级\学生\成绩\年度） | 4格合并（地区\销量\时间） |
| 适用场景 | 简单行列交叉 | 多级动态列头 |

---

## 示例5：区域销售统计（横向分组 + 列标题 + compute 小计）

**场景：** 月份横向展开，区域+省纵向分组，每个月份下有销售/赠送/比例/小计四列
**数据表：** `area_sales_stats`：region(区域), province(省), month(月份), sales(销售额), donation(捐赠), ratio(比例)

### 效果预览

```
┌────────────────────────────────────────────────────────────┐
│                      区域销售统计                             │
├──────┬──────┬──────────────────────┬──────────────────────┤
│  地区        │        1月           │        2月           │ ← groupRight(month) merge[0,3]
│     销售额   ├──────┬──────┬───┬────┼──────┬──────┬───┬────┤
│             │ 销售 │ 赠送 │比例│小计│ 销售 │ 赠送 │比例│小计│ ← 列标题行
├──────┼──────┼──────┼──────┼───┼────┼──────┼──────┼───┼────┤
│ 华南 │ 广东 │85000 │3400  │4.0│88400│92000│3680 │4.0│95680│
│      │ 广西 │45000 │1800  │4.0│46800│52000│2080 │4.0│54080│
│ 华东 │ 江苏 │72000 │2880  │4.0│74880│68000│2720 │4.0│70720│
│      │ 浙江 │65000 │2600  │4.0│67600│71000│2840 │4.0│73840│
│ 华北 │ 北京 │98000 │3920  │4.0│...  │...  │...  │...│...  │
│      │ 河北 │42000 │1680  │4.0│...  │...  │...  │...│...  │
└──────┴──────┴──────┴──────┴───┴────┴──────┴──────┴───┴────┘
```

### rows 布局

| 行号 | 用途 | 关键配置 |
|------|------|---------|
| 0 | 标题 | `merge:[0,3]` |
| 1 | 斜线表头 + groupRight(month) | `lineStart:"lefttop"`, `merge:[1,1]`; groupRight `merge:[0,3]` 合并4列 |
| 2 | 列标题（销售/赠送/比例/小计） | 蓝底白字表头样式 |
| 3 | 数据行 | group(region) + group(province) + dynamic(sales) + dynamic(donation) + dynamic(ratio) + compute(sales+donation) |

### 核心配置

**groupRight 合并规则：** 下方有4个字段（sales, donation, ratio, compute），所以 `merge: [0, 3]` 合并4列。

**compute 小计：** `#{area.compute(sales+donation)}` 在每个月份分组内自动计算。

### 完整 JSON

```json
{
    "rows": {
        "0": {
            "cells": {
                "0": {"rendered": "", "text": ""},
                "1": {"merge": [0, 3], "style": 6, "text": "区域销售统计"}
            },
            "height": 70
        },
        "1": {
            "cells": {
                "1": {"rendered": "", "lineStart": "lefttop", "merge": [1, 1], "style": 2,
                      "text": "地区|销售额|时间"},
                "3": {"style": 8, "text": "#{area.groupRight(month)}",
                      "aggregate": "group", "direction": "right", "merge": [0, 3]}
            },
            "height": 40
        },
        "2": {
            "cells": {
                "3": {"style": 8, "text": "销售"},
                "4": {"style": 8, "text": "赠送"},
                "5": {"style": 8, "text": "比例"},
                "6": {"style": 8, "text": "小计"}
            },
            "height": 34
        },
        "3": {
            "cells": {
                "1": {"style": 9, "text": "#{area.group(region)}", "aggregate": "group"},
                "2": {"style": 9, "text": "#{area.group(province)}", "aggregate": "group"},
                "3": {"decimalPlaces": "2", "rendered": "", "style": 10,
                      "text": "#{area.dynamic(sales)}", "aggregate": "dynamic"},
                "4": {"decimalPlaces": "2", "style": 10,
                      "text": "#{area.dynamic(donation)}", "aggregate": "dynamic"},
                "5": {"decimalPlaces": "2", "style": 10,
                      "text": "#{area.dynamic(ratio)}", "aggregate": "dynamic"},
                "6": {"decimalPlaces": "2", "style": 10,
                      "text": "#{area.compute(sales+donation)}"}
            },
            "height": 35
        },
        "len": 100
    },
    "cols": {"0": {"width": 36}, "1": {"width": 80}, "2": {"width": 80}, "3": {"width": 90}, "4": {"width": 90}, "5": {"width": 70}, "6": {"width": 90}, "len": 100},
    "merges": ["B1:E1", "B2:C3"],
    "isGroup": true,
    "groupField": "area.region",
    "styles": [
        {"bgcolor": "#5b9cd6"},
        {"bgcolor": "#5b9cd6", "color": "#ffffff"},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}, "bgcolor": "#5b9cd6", "color": "#ffffff"},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}},
        {"font": {"size": 16}},
        {"font": {"size": 16, "bold": true}},
        {"align": "center", "font": {"size": 16, "bold": true}},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}, "align": "center"},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}, "bgcolor": "#5b9cd6", "color": "#ffffff", "align": "center"},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}, "bgcolor": "#9cc2e6", "align": "center"},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}, "align": "center", "font": {"size": 9}},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}, "bgcolor": "#9cc2e6", "align": "center"},
        {"border": {"top": ["thin","#d8d8d8"], "left": ["thin","#d8d8d8"], "bottom": ["thin","#d8d8d8"], "right": ["thin","#d8d8d8"]}, "bgcolor": "#9cc2e6", "format": "number", "align": "center"}
    ]
}
```

### 关键点

1. **groupRight merge 列数 = 下方 dynamic/compute 字段数** — 本例有4个字段（sales, donation, ratio, compute），所以 `merge: [0, 3]`
2. **斜线表头 merge 行数 = 列标题行数 + 1** — 本例列标题占1行，斜线表头 `merge: [1, 1]` 跨2行2列
3. **列标题行跟随 groupRight 循环** — "销售/赠送/比例/小计"会在每个月份下重复
4. **compute 表达式** — `#{area.compute(sales+donation)}` 支持 `+` `-` `*` `/` 四则运算
5. **中文文本需要确保 UTF-8** — Python 写入时用 `ensure_ascii=False` + `.encode('utf-8')`，避免 unicode 转义导致乱码

---

## 特殊规则（适用所有示例）

1. **动态列之前的列字段必须设置成纵向分组（group）** — 行头字段不能是普通字段
2. **横向分组下必须有动态列（dynamic）** — groupRight 行下方必须有 dynamic 字段
3. **动态列数据必须设置成动态属性** — 值字段必须用 `dynamic()` 语法
4. **第一条数据必须完整** — 数据集第一条记录必须包含所有横向维度
5. **最多3级动态表头** — groupRight 最多嵌套3层
6. **dynamic 值行样式与数据一致** — 用普通数据样式，不要用表头样式
7. **所有边框颜色保持一致** — 统一用 `#d8d8d8` 浅灰，不要混用 `#000`
8. **groupRight merge 合并列数** — `merge: [0, N-1]`，N = 下方 dynamic/compute 字段数
9. **中文文本 UTF-8** — Python 调用 API 时必须 `json.dumps(data, ensure_ascii=False).encode('utf-8')`，避免斜线表头等中文文本变成乱码

---

## 示例6：API 数据集交叉报表（地区→品类纵向 + 月份横向，已验证可用）

**场景：** 地区→品类双层纵向分组，月份横向动态展开，销售额为交叉值。**数据来源为 API 接口（dbType="1"），非 SQL。**
**验证时间：** 2026-04-02，调用 `http://api.jeecg.com/mock/26/groupsub`，3步全部 success=True。

### 效果预览

```
┌──────────────────────────────────────────────────┐
│            区域品类月度销售交叉报表                  │
├──────┬──────┬──────┬──────┬──────┬──────┬──────┤
│ 地区  │ 品类  │  1月  │  2月  │ ...  │ 12月  │  ← groupRight(mouth)
├──────┼──────┼──────┼──────┼──────┼──────┼──────┤
│      │ 饮料  │  840 │   33 │ ...  │  348 │
│ 东部  │ 点心  │  393 │  310 │ ...  │  348 │  ← group(diqu) + group(class)
│      │ ...  │  ... │  ... │ ...  │  ... │     + dynamic(sales)
├──────┼──────┼──────┼──────┼──────┼──────┤
│      总计    │=SUM  │      │ ...  │      │
└──────────────┴──────┴──────┴──────┴──────┘
```

### API 数据集（dbType="1"）关键参数

```python
db_data = {
    "dbType": "1",          # API 数据集，不是 SQL
    "dbDynSql": api_url,    # 与 apiUrl 相同
    "apiUrl": api_url,      # 设计器 UI「Api地址」读取此字段
    "apiMethod": "0",       # "0"=GET, "1"=POST
    "isList": "1",
    "isPage": "0",          # 交叉报表必须不分页
    "fieldList": [          # 手动定义字段（API数据集不能用 queryFieldBySql）
        {"fieldName": "diqu",  "fieldText": "地区",  "widgetType": "String", "orderNum": 1, "tableIndex": 0, "extJson": "", "dictCode": ""},
        {"fieldName": "class", "fieldText": "品类",  "widgetType": "String", "orderNum": 2, "tableIndex": 0, "extJson": "", "dictCode": ""},
        {"fieldName": "year",  "fieldText": "年份",  "widgetType": "String", "orderNum": 3, "tableIndex": 0, "extJson": "", "dictCode": ""},
        {"fieldName": "mouth", "fieldText": "月份",  "widgetType": "String", "orderNum": 4, "tableIndex": 0, "extJson": "", "dictCode": ""},
        {"fieldName": "sales", "fieldText": "销售额", "widgetType": "String", "orderNum": 5, "tableIndex": 0, "extJson": "", "dictCode": ""},
    ],
    "paramList": []
}
```

> **注意：** API 数据集不支持 `queryFieldBySql`，字段必须手动定义。

### rows 布局（rows 从 "0" 开始，code_row N → merge UI行 N+1）

| code_row | 用途 | 关键属性 |
|----------|------|---------|
| "0" | 标题 `merge:[0,2]` → merge `B1:D1` | style 4 |
| "1" | 表头：地区\|品类\|`#{groupsub.groupRight(mouth)}` | `aggregate:"group"`, `direction:"right"` |
| "2" | 数据：`group(diqu)` \| `group(class)` \| `dynamic(sales)` | `aggregate:"group"` / `"dynamic"` |
| "3" | 总计 `merge:[0,1]` → merge `B4:C4` + `=SUM(D3)` | style 5 |

### 完整 rows / cols / merges / styles

```python
styles = [
    # 0 border only
    {"border": {"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]}},
    # 1 border + center
    {"border": {"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]}, "align":"center"},
    # 2 data: border + center + valign
    {"border": {"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]}, "align":"center","valign":"middle"},
    # 3 header: #5b9cd6 blue bg + white
    {"border": {"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]}, "align":"center","valign":"middle","bgcolor":"#5b9cd6","color":"#ffffff"},
    # 4 title: light blue + dark blue + bold 14
    {"border": {"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]}, "align":"center","valign":"middle","bgcolor":"#E6F2FF","color":"#0066CC","font":{"bold":True,"size":14}},
    # 5 total: mid-blue #9cc2e6
    {"border": {"top":["thin","#d8d8d8"],"left":["thin","#d8d8d8"],"bottom":["thin","#d8d8d8"],"right":["thin","#d8d8d8"]}, "align":"center","valign":"middle","bgcolor":"#9cc2e6","color":"#333333"},
]

rows = {
    "0": {
        "cells": {"1": {"text": "区域品类月度销售交叉报表", "style": 4, "merge": [0, 2]}},
        "height": 50
    },
    "1": {
        "cells": {
            "1": {"text": "地区", "style": 3},
            "2": {"text": "品类", "style": 3},
            "3": {"text": "#{groupsub.groupRight(mouth)}", "style": 3,
                  "aggregate": "group", "direction": "right"}
        },
        "height": 34
    },
    "2": {
        "cells": {
            "1": {"text": "#{groupsub.group(diqu)}",   "style": 2, "aggregate": "group"},
            "2": {"text": "#{groupsub.group(class)}",  "style": 2, "aggregate": "group"},
            "3": {"text": "#{groupsub.dynamic(sales)}","style": 2, "aggregate": "dynamic"}
        }
    },
    "3": {
        "cells": {
            "1": {"text": "总计", "style": 5, "merge": [0, 1]},
            "3": {"text": "=SUM(D3)", "style": 5}   # D3 = data行 code_row"2" → UI行3
        },
        "height": 34
    },
    "len": 200
}

cols = {
    "0": {"width": 20},   # A 左边距
    "1": {"width": 80},   # B 地区
    "2": {"width": 80},   # C 品类
    "3": {"width": 70},   # D 月份动态列起始
    "len": 100
}

merges = ["B1:D1", "B4:C4"]
# B1:D1 → code_row"0" 标题（N=0, UI行=1）
# B4:C4 → code_row"3" 总计（N=3, UI行=4）
```

### 报表级分组与打印配置

```python
save_data = {
    # ... 其他字段 ...
    "isGroup": True,
    "groupField": "groupsub.diqu",   # 格式：dbCode.字段名（非 db.字段名）
    "printConfig": {
        "paper": "A3", "width": 297, "height": 420,
        "layout": "landscape",        # 横向，适应月份多列
        "definition": 1, "isBackend": False,
        "marginX": 10, "marginY": 10, "printCallBackUrl": ""
    },
    # ...
}
```

### 执行步骤（3步，全部 success=True）

```
Step 1: POST /jmreport/save       空报表（rows={"len":200}）→ 获取并锁定 report_id
Step 2: POST /jmreport/saveDb     API数据集，isPage="0"，手动定义 fieldList
Step 3: POST /jmreport/save       完整设计（rows/cols/styles/merges/isGroup/groupField）
```

> `/jmreport/save` 不在签名接口列表中，**无需 X-Sign / X-TIMESTAMP**。
> `/jmreport/saveDb` 同样不需要签名。
> 签名只用于 `queryFieldBySql`、`executeSelectApi` 等查询类接口。

### 为已有报表添加查询条件（日期类型，yyyy-MM 年月选择器）

**需求：** 给交叉报表添加按年月筛选的查询条件。

**执行步骤（2步）：**

```
Step 1: POST /jmreport/saveDb    更新 paramList，添加日期查询参数
Step 2: POST /jmreport/save      重建完整报表设计，开启 querySetting.izOpenQueryBar
```

**paramList 日期参数配置：**

```python
param_list = [{
    "paramName": "mouth",         # 与数据字段名一致
    "paramTxt": "年月",            # 查询栏显示标签
    "widgetType": "date",         # 日期控件
    "searchMode": 1,              # paramList 日期类型固定用 1（输入框）
    "searchFlag": 1,              # 启用查询
    "searchFormat": "yyyy-MM",    # 年月选择器（不是 MM，那样只有月份）
    "paramValue": "",             # 无默认值
    "dictCode": "",
    "orderNum": 1
}]
```

> **常见 searchFormat：** `yyyy-MM-dd`(日期) / `yyyy-MM`(年月) / `yyyy`(年) / `MM`(月) / `yyyy-MM-dd HH:mm:ss`(日期时间)

**save 请求体中开启查询栏：**

```python
save_body = {
    # ... 完整报表设计字段 ...
    "querySetting": {"izOpenQueryBar": True, "izDefaultQuery": True},
}
```

### 踩坑记录：编辑报表设计时不要用 `get + spread + save`

**错误做法：**
```python
# ❌ 从 get/{id} 读取 jsonStr，修改 querySetting，再 spread 回 save
report = api_request(f'/jmreport/get/{REPORT_ID}')
design = json.loads(report['result']['jsonStr'])
design['querySetting']['izOpenQueryBar'] = True
save_body = {**design, "designerObj": ...}   # spread 所有字段
api_request('/jmreport/save', save_body)     # ← 可能丢失配置！
```

**问题：** `get/{id}` 返回的 `jsonStr` 可能与 `save` 期望的格式不完全一致，spread 回去后 `querySetting`、`paramList` 等配置会静默丢失。

**正确做法：**
```python
# ✅ 用已知的完整设计重建 save body，不依赖 get 返回值
save_body = {
    "designerObj": json.dumps(designer_obj, ensure_ascii=False),
    "rows": rows,        # 用原始已知的 rows
    "cols": cols,        # 用原始已知的 cols
    "styles": styles,    # ...
    "merges": merges,
    "querySetting": {"izOpenQueryBar": True, "izDefaultQuery": True},
    "isGroup": True,
    "groupField": "groupsub.diqu",
    # ... 其他完整字段 ...
}
```

> **原则：编辑报表时，`saveDb` 更新数据集 + `save` 重建完整设计，两步分开，每步用确定的数据。**
