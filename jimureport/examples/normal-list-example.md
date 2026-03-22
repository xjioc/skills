# 普通列表报表示例

## 场景说明

一个标准的普通列表报表，数据集编码为 `aa`，SQL为 `select * from demo`，展示6个字段：id、name、key_word、punch_time、salary_money、bonus_money。

- 表头行（第1行）：蓝底白字，行高34px
- 数据行（第2行）：居中+垂直居中，通过 `#{aa.字段名}` 绑定数据

## 完整 jsonStr

```json
{
    "loopBlockList": [],
    "querySetting": {
        "izOpenQueryBar": false,
        "izDefaultQuery": true
    },
    "recordSubTableOrCollection": {
        "group": [],
        "record": [],
        "range": []
    },
    "printConfig": {
        "paper": "A4",
        "width": 210,
        "height": 297,
        "definition": 1,
        "isBackend": false,
        "marginX": 10,
        "marginY": 10,
        "layout": "portrait",
        "printCallBackUrl": ""
    },
    "hidden": {
        "rows": [],
        "cols": [],
        "conditions": {
            "rows": {},
            "cols": {}
        }
    },
    "queryFormSetting": {
        "useQueryForm": false,
        "dbKey": "",
        "idField": ""
    },
    "dbexps": [],
    "dicts": [],
    "fillFormToolbar": {
        "show": true,
        "btnList": ["save", "subTable_add", "verify", "subTable_del", "print", "close", "first", "prev", "next", "paging", "total", "last", "exportPDF", "exportExcel", "exportWord"]
    },
    "freeze": "A1",
    "dataRectWidth": 700,
    "isViewContentHorizontalCenter": false,
    "autofilter": {},
    "validations": [],
    "cols": {
        "len": 100
    },
    "area": {
        "sri": 12,
        "sci": 3,
        "eri": 12,
        "eci": 3,
        "width": 100,
        "height": 25
    },
    "pyGroupEngine": false,
    "submitHandlers": [],
    "excel_config_id": "1193766682428530688",
    "hiddenCells": [],
    "zonedEditionList": [],
    "rows": {
        "1": {
            "cells": {
                "1": { "text": "id", "style": 4 },
                "2": { "text": "name", "style": 4 },
                "3": { "text": "key_word", "style": 4 },
                "4": { "text": "punch_time", "style": 4 },
                "5": { "text": "salary_money", "style": 4 },
                "6": { "text": "bonus_money", "style": 4 }
            },
            "height": 34
        },
        "2": {
            "cells": {
                "1": { "text": "#{aa.id}", "style": 2 },
                "2": { "text": "#{aa.name}", "style": 2 },
                "3": { "text": "#{aa.key_word}", "style": 2 },
                "4": { "text": "#{aa.punch_time}", "style": 2 },
                "5": { "text": "#{aa.salary_money}", "style": 2 },
                "6": { "text": "#{aa.bonus_money}", "style": 2 }
            }
        },
        "len": 200
    },
    "rpbar": {
        "show": true,
        "pageSize": "",
        "btnList": []
    },
    "fixedPrintHeadRows": [],
    "fixedPrintTailRows": [],
    "displayConfig": {},
    "fillFormInfo": {
        "layout": {
            "direction": "horizontal",
            "width": 200,
            "height": 45
        }
    },
    "background": false,
    "name": "sheet1",
    "styles": [
        {
            "border": {
                "bottom": ["thin", "#000"],
                "top": ["thin", "#000"],
                "left": ["thin", "#000"],
                "right": ["thin", "#000"]
            }
        },
        {
            "border": {
                "bottom": ["thin", "#000"],
                "top": ["thin", "#000"],
                "left": ["thin", "#000"],
                "right": ["thin", "#000"]
            },
            "align": "center"
        },
        {
            "border": {
                "bottom": ["thin", "#000"],
                "top": ["thin", "#000"],
                "left": ["thin", "#000"],
                "right": ["thin", "#000"]
            },
            "align": "center",
            "valign": "middle"
        },
        {
            "border": {
                "bottom": ["thin", "#000"],
                "top": ["thin", "#000"],
                "left": ["thin", "#000"],
                "right": ["thin", "#000"]
            },
            "align": "center",
            "valign": "middle",
            "bgcolor": "#01b0f1"
        },
        {
            "border": {
                "bottom": ["thin", "#000"],
                "top": ["thin", "#000"],
                "left": ["thin", "#000"],
                "right": ["thin", "#000"]
            },
            "align": "center",
            "valign": "middle",
            "bgcolor": "#01b0f1",
            "color": "#ffffff"
        }
    ],
    "fillFormStyle": "default",
    "freezeLineColor": "rgb(185, 185, 185)",
    "merges": []
}
```

## 结构要点

### rows 布局

| 行号 | 用途 | style | 说明 |
|------|------|-------|------|
| 1 | 表头行 | 4（蓝底白字） | `height: 34`，text为字段显示名 |
| 2 | 数据行 | 2（居中+垂直居中） | text为 `#{数据集编码.字段名}` |

### styles 索引对照

| 索引 | 边框 | 水平对齐 | 垂直对齐 | 背景色 | 字体色 | 典型用途 |
|------|------|---------|---------|--------|--------|---------|
| 0 | thin #000 | — | — | — | — | 基础单元格 |
| 1 | thin #000 | center | — | — | — | 居中文本 |
| 2 | thin #000 | center | middle | — | — | **数据行** |
| 3 | thin #000 | center | middle | #01b0f1 | — | 蓝底表头(无白字) |
| 4 | thin #000 | center | middle | #01b0f1 | #ffffff | **表头行(推荐)** |

### 数据绑定规则

- 数据集编码 `aa` 对应 saveDb 时的 `dbCode: "aa"`
- 绑定语法: `#{aa.字段名}` — 字段名来自 fieldList 中的 `fieldName`
- 列号从 1 开始（0列通常留空）

### 对应的数据集配置

```json
{
    "jimuReportId": "1193766682428530688",
    "dbCode": "aa",
    "dbChName": "aa",
    "dbType": "0",
    "dbSource": "",
    "isList": "1",
    "isPage": "1",
    "dbDynSql": "select * from demo",
    "fieldList": [
        { "fieldName": "id", "fieldText": "id", "widgetType": "String", "orderNum": 0 },
        { "fieldName": "name", "fieldText": "name", "widgetType": "String", "orderNum": 1 },
        { "fieldName": "key_word", "fieldText": "key_word", "widgetType": "String", "orderNum": 2 },
        { "fieldName": "punch_time", "fieldText": "punch_time", "widgetType": "String", "orderNum": 3 },
        { "fieldName": "salary_money", "fieldText": "salary_money", "widgetType": "String", "orderNum": 4 },
        { "fieldName": "bonus_money", "fieldText": "bonus_money", "widgetType": "String", "orderNum": 5 }
    ],
    "paramList": []
}
```

### 正确的 /jmreport/save 请求格式

> **关键：jsonStr 内容（rows、cols、styles 等）必须放在请求体顶层，和 `designerObj` 同级。禁止嵌套在 `designerObj.jsonStr` 中，否则后端会清空 rows 数据。**
>
> 后端 `saveReport` 逻辑：`json.remove("designerObj")` 后，剩余的顶层 JSON 直接作为 jsonStr 存入数据库。

```json
{
    "designerObj": {
        "id": "1193766682428530688",
        "name": "普通列表示例",
        "type": "0",
        "template": 0,
        "delFlag": 0,
        "viewCount": 0,
        "updateCount": 0,
        "submitForm": 0,
        "reportName": "普通列表示例"
    },
    "loopBlockList": [],
    "querySetting": { "izOpenQueryBar": false, "izDefaultQuery": true },
    "recordSubTableOrCollection": { "group": [], "record": [], "range": [] },
    "printConfig": { "paper": "A4", "width": 210, "height": 297, "definition": 1, "isBackend": false, "marginX": 10, "marginY": 10, "layout": "portrait", "printCallBackUrl": "" },
    "hidden": { "rows": [], "cols": [], "conditions": { "rows": {}, "cols": {} } },
    "queryFormSetting": { "useQueryForm": false, "dbKey": "", "idField": "" },
    "dbexps": [], "dicts": [],
    "fillFormToolbar": { "show": true, "btnList": ["save", "subTable_add", "verify", "subTable_del", "print", "close", "first", "prev", "next", "paging", "total", "last", "exportPDF", "exportExcel", "exportWord"] },
    "freeze": "A1",
    "dataRectWidth": 700,
    "isViewContentHorizontalCenter": false,
    "autofilter": {},
    "validations": [],
    "cols": { "len": 100 },
    "area": { "sri": 12, "sci": 3, "eri": 12, "eci": 3, "width": 100, "height": 25 },
    "pyGroupEngine": false,
    "submitHandlers": [],
    "excel_config_id": "1193766682428530688",
    "hiddenCells": [],
    "zonedEditionList": [],
    "rows": {
        "1": {
            "cells": {
                "1": { "text": "id", "style": 4 },
                "2": { "text": "name", "style": 4 },
                "3": { "text": "key_word", "style": 4 },
                "4": { "text": "punch_time", "style": 4 },
                "5": { "text": "salary_money", "style": 4 },
                "6": { "text": "bonus_money", "style": 4 }
            },
            "height": 34
        },
        "2": {
            "cells": {
                "1": { "text": "#{aa.id}", "style": 2 },
                "2": { "text": "#{aa.name}", "style": 2 },
                "3": { "text": "#{aa.key_word}", "style": 2 },
                "4": { "text": "#{aa.punch_time}", "style": 2 },
                "5": { "text": "#{aa.salary_money}", "style": 2 },
                "6": { "text": "#{aa.bonus_money}", "style": 2 }
            }
        },
        "len": 200
    },
    "rpbar": { "show": true, "pageSize": "", "btnList": [] },
    "fixedPrintHeadRows": [],
    "fixedPrintTailRows": [],
    "displayConfig": {},
    "fillFormInfo": { "layout": { "direction": "horizontal", "width": 200, "height": 45 } },
    "background": false,
    "name": "sheet1",
    "styles": [
        { "border": { "bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"] } },
        { "border": { "bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"] }, "align": "center" },
        { "border": { "bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"] }, "align": "center", "valign": "middle" },
        { "border": { "bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"] }, "align": "center", "valign": "middle", "bgcolor": "#01b0f1" },
        { "border": { "bottom": ["thin", "#000"], "top": ["thin", "#000"], "left": ["thin", "#000"], "right": ["thin", "#000"] }, "align": "center", "valign": "middle", "bgcolor": "#01b0f1", "color": "#ffffff" }
    ],
    "fillFormStyle": "default",
    "freezeLineColor": "rgb(185, 185, 185)",
    "merges": []
}
```
