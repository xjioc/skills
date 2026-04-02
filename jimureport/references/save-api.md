# 积木报表 /jmreport/save 接口结构参考

## 1. 接口说明

```
POST /jmreport/save
Header: X-Access-Token: <token>
Content-Type: application/json
```

新建报表 / 更新报表内容均调用此接口。请求体由两部分组成：
- **`designerObj`**：报表元数据（id、名称、类型等）
- **根级 sheet 字段**：单元格数据、图表、样式等

---

## 2. 完整请求体结构

```python
save_payload = {
    # ── 报表元数据 ──────────────────────────────────────────
    "designerObj": {               # 对象，不是字符串！
        "id": report_id,           # 雪花ID字符串
        "code": report_code,       # 时间戳字符串，如 "20260402150627"
        "name": report_name,       # 报表名称
        "reportName": report_name, # 与 name 相同
        "type": "0",               # 分类ID，"0" = 默认，或传文件夹的ID字符串
        "template": 0,
        "delFlag": 0,
        "viewCount": 0,
        "updateCount": 0,
        "submitForm": 0,
        # 以下字段服务端返回时带有，提交时可不传（服务端会自动填充）：
        # "jsonStr": "...",        # 服务端序列化的上次保存状态，新建时不需要
        # "createBy": "admin",
        # "createTime": "...",
        # "updateBy": null,
        # "updateTime": null,
        # "tenantId": "0",
        # "note": null, "status": null, "apiUrl": null, ...
    },

    # ── Sheet 基础配置 ───────────────────────────────────────
    "name": "sheet1",
    "freeze": "A1",
    "freezeLineColor": "rgb(185, 185, 185)",
    "sheetId": "default",
    "sheetName": "默认Sheet",
    "sheetOrder": "0",
    "excel_config_id": report_id,  # 等于 designerObj.id

    # ── 单元格数据 ───────────────────────────────────────────
    # rows 只需包含有内容的行，空行不用写
    "rows": {
        "len": 200,                # 总行数上限
        # 普通数据行示例：
        "0": {
            "cells": {
                "0": {"text": "字段标题", "style": 0},
                "1": {"text": "#{db.field_name}"},
            }
        },
        # 图层占位行（图表/图片所在行，text 固定为一个空格）：
        # "2": {
        #     "cells": {
        #         "0": {"text": " ", "virtual": "chart_abc123"},
        #         "1": {"text": " ", "virtual": "chart_abc123"},
        #     }
        # },
    },
    "cols": {"len": 100},          # 总列数上限

    # ── 样式与合并 ───────────────────────────────────────────
    "styles": [],                  # 样式对象数组，单元格 style 字段引用下标
    "merges": [],                  # 合并区域数组，格式 "A1:C1"

    # ── 图层组件（图表/图片等）───────────────────────────────
    # 这些字段放在根级，不在 rows 里
    "chartList": [],               # 图表组件列表，见 chart-binddata.md
    "imgList": [],                 # 图片组件列表
    "barcodeList": [],             # 条形码组件列表
    "qrcodeList": [],              # 二维码组件列表
    "displayConfig": {},           # 单元格内嵌组件配置（条码/二维码inline模式）

    # ── 打印配置 ─────────────────────────────────────────────
    "printConfig": {
        "paper": "A4",
        "width": 210, "height": 297,
        "definition": 1,
        "isBackend": False,
        "marginX": 10, "marginY": 10,
        "layout": "portrait",      # "portrait"=纵向, "landscape"=横向
        "printCallBackUrl": ""
    },

    # ── 分页工具栏 ───────────────────────────────────────────
    "rpbar": {
        "show": True,
        "pageSize": "",            # 每页行数，空字符串=默认
        "btnList": []
    },

    # ── 填报工具栏 ───────────────────────────────────────────
    "fillFormToolbar": {
        "show": True,
        "btnList": ["save","subTable_add","verify","subTable_del","print",
                    "close","first","prev","next","paging","total","last",
                    "exportPDF","exportExcel","exportWord"]
    },

    # ── 查询配置 ─────────────────────────────────────────────
    "querySetting": {"izOpenQueryBar": False, "izDefaultQuery": True},
    "queryFormSetting": {"useQueryForm": False, "dbKey": "", "idField": ""},

    # ── 其他必传字段 ─────────────────────────────────────────
    "validations": [],
    "autofilter": {},
    "dbexps": [],
    "dicts": [],
    "loopBlockList": [],
    "zonedEditionList": [],
    "fixedPrintHeadRows": [],
    "fixedPrintTailRows": [],
    "hiddenCells": [],
    "submitHandlers": [],
    "hidden": {"rows": [], "cols": [], "conditions": {"rows": {}, "cols": {}}},
    "fillFormInfo": {"layout": {"direction": "horizontal", "width": 200, "height": 45}},
    "recordSubTableOrCollection": {"group": [], "record": [], "range": []},
    "area": False,
    "background": False,
    "pyGroupEngine": False,
    "isViewContentHorizontalCenter": False,
    "fillFormStyle": "default",
    "dataRectWidth": 700,
}
```

---

## 3. 关键注意事项

### designerObj 格式
- 浏览器发送的是**对象**，服务端接受时也可以是 JSON 字符串（`json.dumps(obj)`），两种均可
- 新建报表时只需传最小字段（id/code/name/type/template 等），无需传 `jsonStr`
- `jsonStr` 是服务端上次保存时序列化的状态，**服务端会根据根级 sheet 字段自动更新它**

### chartList 图表组件（浏览器实测正确格式，2026-04-02）

放在**根级**，不在 rows 里。每个条目的关键字段：

```python
{
    "row": 0,          # 图表左上角行（0-based）
    "col": 0,          # 图表左上角列（0-based）
    "colspan": 7,      # 列跨度（col_end - col + 1），不是 0！
    "rowspan": 14,     # 行跨度（row_end - row + 1），不是 0！
    "width": 650,      # int，不是字符串 "650"
    "height": 350,     # int，不是字符串 "350"
    "config": "...",   # json.dumps(echarts_option) — ECharts option JSON字符串
    "extData": {       # dict 对象（不是 JSON 字符串！）
        "chartId": "bar.background",   # 实际图表类型
        "chartType": "bar.simple"      # 浏览器固定发 bar.simple，不影响渲染
    },
    "layer_id": "BWKtHvbIwCLihX49",   # 与 rows 中 virtual 值一致
    "offsetX": 0, "offsetY": 0,
    "url": "",
    "backgroud": {     # dict 对象（不是空字符串！注意拼写 backgroud）
        "enabled": False, "color": "#fff", "image": ""
    },
    "virtualCellRange": [[0,0],[0,1],[0,2],[0,3],[0,4],[0,5],[0,6]]
    # 只标图表第一行（浏览器行为），图表完整区域由 colspan/rowspan 定义
}
```

**常见错误：**
- `extData` 写成 `json.dumps(...)` 字符串 → 图表渲染异常
- `backgroud` 写成 `""` → 背景配置丢失
- `colspan`/`rowspan` 写成 0 → 图表尺寸不对
- `width`/`height` 写成字符串 → 可能被忽略

### rows 写法
```python
# 只写有内容的行，未定义的行自动为空
rows = {
    "len": 200,
    "0": {"cells": {"0": {"text": "标题"}}},  # 第1行
    "5": {"cells": {"0": {"text": "#{db.name}"}}},  # 第6行（中间的行不用写）
}
```

### 响应格式
```json
{"success": true, "message": "保存成功！", "code": 200, "result": null}
```
失败时 `success: false`，`message` 包含错误原因。

---

## 4. 最小新建报表示例

```python
def build_minimal_save(report_id, report_name):
    return {
        "designerObj": {
            "id": report_id, "code": str(int(time.time()*1000)),
            "name": report_name, "reportName": report_name,
            "type": "0", "template": 0, "delFlag": 0,
            "viewCount": 0, "updateCount": 0, "submitForm": 0
        },
        "name": "sheet1", "freeze": "A1",
        "freezeLineColor": "rgb(185, 185, 185)",
        "excel_config_id": report_id,
        "sheetId": "default", "sheetName": "默认Sheet", "sheetOrder": "0",
        "rows": {"len": 200}, "cols": {"len": 100},
        "styles": [], "merges": [],
        "chartList": [], "imgList": [], "barcodeList": [], "qrcodeList": [],
        "displayConfig": {}, "validations": [], "autofilter": {},
        "dbexps": [], "dicts": [], "loopBlockList": [], "zonedEditionList": [],
        "fixedPrintHeadRows": [], "fixedPrintTailRows": [],
        "hiddenCells": [], "submitHandlers": [],
        "hidden": {"rows": [], "cols": [], "conditions": {"rows": {}, "cols": {}}},
        "fillFormInfo": {"layout": {"direction": "horizontal", "width": 200, "height": 45}},
        "recordSubTableOrCollection": {"group": [], "record": [], "range": []},
        "printConfig": {"paper": "A4", "width": 210, "height": 297, "definition": 1,
                        "isBackend": False, "marginX": 10, "marginY": 10,
                        "layout": "portrait", "printCallBackUrl": ""},
        "rpbar": {"show": True, "pageSize": "", "btnList": []},
        "fillFormToolbar": {"show": True, "btnList": ["save","subTable_add","verify",
            "subTable_del","print","close","first","prev","next","paging","total",
            "last","exportPDF","exportExcel","exportWord"]},
        "querySetting": {"izOpenQueryBar": False, "izDefaultQuery": True},
        "queryFormSetting": {"useQueryForm": False, "dbKey": "", "idField": ""},
        "area": False, "background": False, "pyGroupEngine": False,
        "isViewContentHorizontalCenter": False, "fillFormStyle": "default",
        "dataRectWidth": 700,
    }
```
