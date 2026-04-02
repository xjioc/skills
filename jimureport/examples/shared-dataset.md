# 共享数据集报表示例

## 场景说明

创建一个使用共享数据集的普通列表报表。共享数据集名称为「SQL共享数据集」，数据集编码 `demo`，SQL 为 `select * from demo`，报表名称为「SQL共享数据集测试」。

**共享数据集与普通数据集的区别：**
- `izSharedSource: 1`（普通数据集为 0）
- `jimuReportId: ""`（空字符串，不绑定特定报表）
- 创建后需通过 `linkJmReportShareDb` 接口关联到报表

## 完整创建流程

```
Step 1: POST /jmreport/save              → 创建空报表，获取 report_id
Step 2: POST /jmreport/saveDb            → 创建共享数据集（izSharedSource=1, jimuReportId=""）
Step 3: POST /jmreport/source/linkJmReportShareDb → 关联共享数据集到报表
Step 4: POST /jmreport/save              → 保存完整报表设计
```

> **注意：** `linkJmReportShareDb` 不需要签名。

## Step 2: 创建共享数据集（saveDb）

```json
{
    "izSharedSource": 1,
    "jimuReportId": "",
    "dbCode": "demo",
    "dbChName": "SQL共享数据集",
    "dbType": "0",
    "dbSource": "",
    "jsonData": "",
    "apiConvert": "",
    "isList": "1",
    "isPage": "1",
    "dbDynSql": "select * from demo",
    "fieldList": [
        {"fieldName": "id", "fieldText": "id", "widgetType": "String", "orderNum": 1},
        {"fieldName": "name", "fieldText": "name", "widgetType": "String", "orderNum": 2},
        {"fieldName": "key_word", "fieldText": "key_word", "widgetType": "String", "orderNum": 3},
        {"fieldName": "punch_time", "fieldText": "punch_time", "widgetType": "String", "orderNum": 4},
        {"fieldName": "salary_money", "fieldText": "salary_money", "widgetType": "String", "orderNum": 5},
        {"fieldName": "bonus_money", "fieldText": "bonus_money", "widgetType": "String", "orderNum": 6},
        {"fieldName": "sex", "fieldText": "sex", "widgetType": "String", "orderNum": 7},
        {"fieldName": "age", "fieldText": "age", "widgetType": "String", "orderNum": 8},
        {"fieldName": "birthday", "fieldText": "birthday", "widgetType": "String", "orderNum": 9},
        {"fieldName": "email", "fieldText": "email", "widgetType": "String", "orderNum": 10},
        {"fieldName": "content", "fieldText": "content", "widgetType": "String", "orderNum": 11},
        {"fieldName": "create_by", "fieldText": "create_by", "widgetType": "String", "orderNum": 12},
        {"fieldName": "create_time", "fieldText": "create_time", "widgetType": "String", "orderNum": 13},
        {"fieldName": "update_by", "fieldText": "update_by", "widgetType": "String", "orderNum": 14},
        {"fieldName": "update_time", "fieldText": "update_time", "widgetType": "String", "orderNum": 15},
        {"fieldName": "sys_org_code", "fieldText": "sys_org_code", "widgetType": "String", "orderNum": 16},
        {"fieldName": "tenant_id", "fieldText": "tenant_id", "widgetType": "String", "orderNum": 17},
        {"fieldName": "update_count", "fieldText": "update_count", "widgetType": "String", "orderNum": 18}
    ],
    "paramList": []
}
```

**返回结果：** `result` 是完整的数据集对象，**必须提取 `result['id']`** 用于 Step 3 的关联。

```python
r = api_request('/jmreport/saveDb', shared_db_data)
shared_db_id = r['result']['id']  # 正确：提取 id
# shared_db_id = r['result']      # 错误：result 是完整对象，不是 ID 字符串
```

## Step 3: 关联共享数据集到报表（linkJmReportShareDb）

```json
{
    "jimuReportId": "报表ID",
    "jimuSharedSourceId": "共享数据集ID"
}
```

**接口：** `POST /jmreport/source/linkJmReportShareDb`（不需要签名）

## Step 4: 报表设计 jsonStr

标题行 + 表头行 + 数据绑定行，隐藏系统字段（id、create_by、update_by、sys_org_code、tenant_id、update_count），展示10个业务字段。

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
        "width": 210,
        "height": 297,
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
    "dataRectWidth": 700,
    "isViewContentHorizontalCenter": false,
    "autofilter": {},
    "validations": [],
    "cols": {
        "0": {"width": 25},
        "1": {"width": 100},
        "2": {"width": 100},
        "3": {"width": 120},
        "4": {"width": 100},
        "5": {"width": 100},
        "6": {"width": 80},
        "7": {"width": 80},
        "8": {"width": 100},
        "9": {"width": 150},
        "10": {"width": 150},
        "len": 100
    },
    "area": { "sri": 0, "sci": 0, "eri": 0, "eci": 0, "width": 100, "height": 25 },
    "pyGroupEngine": false,
    "submitHandlers": [],
    "hiddenCells": [],
    "zonedEditionList": [],
    "rows": {
        "1": {
            "cells": {
                "1": {"text": "SQL共享数据集测试", "style": 5, "merge": [0, 9], "height": 50}
            },
            "height": 50
        },
        "2": {
            "cells": {
                "1": {"text": "名称", "style": 4},
                "2": {"text": "关键词", "style": 4},
                "3": {"text": "打卡时间", "style": 4},
                "4": {"text": "薪资", "style": 4},
                "5": {"text": "奖金", "style": 4},
                "6": {"text": "性别", "style": 4},
                "7": {"text": "年龄", "style": 4},
                "8": {"text": "生日", "style": 4},
                "9": {"text": "邮箱", "style": 4},
                "10": {"text": "内容", "style": 4}
            },
            "height": 34
        },
        "3": {
            "cells": {
                "1": {"text": "#{demo.name}", "style": 2},
                "2": {"text": "#{demo.key_word}", "style": 2},
                "3": {"text": "#{demo.punch_time}", "style": 2},
                "4": {"text": "#{demo.salary_money}", "style": 2},
                "5": {"text": "#{demo.bonus_money}", "style": 2},
                "6": {"text": "#{demo.sex}", "style": 2},
                "7": {"text": "#{demo.age}", "style": 2},
                "8": {"text": "#{demo.birthday}", "style": 2},
                "9": {"text": "#{demo.email}", "style": 2},
                "10": {"text": "#{demo.content}", "style": 2}
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
        {"border": {"bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"]}},
        {"border": {"bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"]}, "align": "center"},
        {"border": {"bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"]}, "align": "center", "valign": "middle"},
        {"border": {"bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"]}, "align": "center", "valign": "middle", "bgcolor": "#01b0f1"},
        {"border": {"bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"]}, "align": "center", "valign": "middle", "bgcolor": "#01b0f1", "color": "#ffffff"},
        {"border": {"bottom": ["thin","#000"], "top": ["thin","#000"], "left": ["thin","#000"], "right": ["thin","#000"]}, "align": "center", "valign": "middle", "font": {"bold": true, "size": 14}, "bgcolor": "#E6F2FF", "color": "#0066CC"}
    ],
    "fillFormStyle": "default",
    "freezeLineColor": "rgb(185, 185, 185)",
    "merges": ["B2:K2"]
}
```

## 结构要点

### rows 布局

| 行号 | 用途 | style | 说明 |
|------|------|-------|------|
| 1 | 标题行 | 5（淡蓝底深蓝字加粗14号） | `merge: [0, 9]` 合并10列，`height: 50` |
| 2 | 表头行 | 4（蓝底白字） | `height: 34`，10个业务字段中文名 |
| 3 | 数据行 | 2（居中+垂直居中） | `#{demo.字段名}` 绑定 |

### 与普通数据集的关键区别

| 项目 | 普通数据集 | 共享数据集 |
|------|-----------|-----------|
| `izSharedSource` | `0` | `1` |
| `jimuReportId` | 报表ID | `""`（空字符串） |
| 关联方式 | saveDb 时自动关联 | 需额外调用 `linkJmReportShareDb` |
| saveDb 返回值 | ID 字符串 | 完整对象，需提取 `result['id']` |

### 完整 Python 脚本流程

```python
# Step 1: 创建空报表
report_id = gen_id()
r1 = api_request('/jmreport/save', {
    "designerObj": json.dumps({"id": report_id, "name": "SQL共享数据集测试", ...}),
    "rows": {"len": 200}, "cols": {"len": 100}, ...
})

# Step 2: 创建共享数据集
r2 = api_request('/jmreport/saveDb', {
    "izSharedSource": 1,
    "jimuReportId": "",       # 空字符串！
    "dbCode": "demo",
    "dbChName": "SQL共享数据集",
    "dbType": "0",
    "dbDynSql": "select * from demo",
    "fieldList": [...],       # queryFieldBySql 返回的字段
    ...
})
shared_db_id = r2['result']['id']  # 提取 ID

# Step 3: 关联（不需要签名）
r3 = api_request('/jmreport/source/linkJmReportShareDb', {
    "jimuReportId": report_id,
    "jimuSharedSourceId": shared_db_id
})

# Step 4: 保存报表设计
r4 = api_request('/jmreport/save', {
    "designerObj": json.dumps(designer_obj),
    "rows": rows_data,       # 包含标题+表头+数据绑定行
    "cols": cols_data,
    "styles": styles,
    "merges": merges,
    ...
})
```

### 相关接口（共享数据集管理）

| 操作 | 接口 | 需要签名 |
|------|------|---------|
| 查询共享数据集列表 | `GET /jmreport/source/getJmReportSharedDbPageList?pageSize=10&pageNo=1&name=` | 否 |
| 创建共享数据集 | `POST /jmreport/saveDb`（`izSharedSource=1`） | 否 |
| 修改共享数据集 | `POST /jmreport/saveDb`（传 `id` = 更新） | 否 |
| 删除共享数据集 | `POST /jmreport/source/delShareDbByDbId`，请求体 `{"id": "共享数据集ID"}` | 否 |
| 关联到报表 | `POST /jmreport/source/linkJmReportShareDb` | 否 |
